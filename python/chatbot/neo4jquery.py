# -*- coding: utf-8 -*-
import asyncio
import os
import re
from typing import Any, Dict, Generator, List, Literal
from neo4j import GraphDatabase  # 用于清库 & 检查节点数
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
# === 替换导入 ===
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.core import Document, Settings, StorageContext
from llama_index.core.indices.property_graph import PropertyGraphIndex, SchemaLLMPathExtractor
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.vector_stores.milvus.utils import BM25BuiltInFunction
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader
import llama_index.core
from llama_index.core.tools import RetrieverTool
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.chat_engine.types import ChatMessage

from graph import read_docx_to_graph_nodes

# llama_index.core.set_global_handler("simple")

os.environ["OPENAI_API_KEY"] = "dummy"  # 防止任何 OpenAI 回退
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# ===================== 配置区（按需修改） =====================

DASHSCOPE_API_KEY = "sk-a8ca287e30304c23803c3910fffc76d2"
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 1) 配置百炼 LLM，并绑定为全局
llm = OpenAILike(
    model="qwen-plus",
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    is_chat_model=True,
    timeout=300,
)

embed_model = OpenAILikeEmbedding(
    model_name="text-embedding-v4",
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    dimensions=1536
)



# === 替换为 Neo4jPropertyGraphStore ===
graph_store = Neo4jPropertyGraphStore(
    username="neo4j",          # ← 根据你的 Neo4j 设置修改
    password="ygy1997666",  # ← 默认首次登录后必须修改
    url="bolt://127.0.0.1:7687",  # Neo4j 默认 bolt 端口是 7687（不是 7688）
    database="neo4j",          # 默认数据库名
)

REBUILD_GRAPH = False   

if REBUILD_GRAPH:
    storage_context = StorageContext.from_defaults(property_graph_store=graph_store)
else:
    storage_context = StorageContext.from_defaults(property_graph_store=graph_store, persist_dir="./storage")
    llm = Ollama(model="qwen3:8b", base_url="http://192.168.2.122:11434",request_timeout=300,thinking=False) 

Settings.llm = llm  
Settings.embed_model = embed_model  

# ===================== 构建图谱（含清库）=====================

def build_graph_index():
    # 清空数据库（Neo4j 兼容）
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "ygy1997666"))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n;")
        session.run("""
            CALL apoc.schema.assert({},{},true) YIELD label, key
            RETURN *
        """)
    driver.close()

    extractor = SchemaLLMPathExtractor(
        llm=llm,
        max_triplets_per_chunk=3,
        num_workers=10,
        strict=False  
    )
    nodes = read_docx_to_graph_nodes("./docs/test.docx", graph_store)

    index = PropertyGraphIndex(
        nodes=nodes,
        llm=llm,
        use_async=False,
        embed_model=embed_model,
        kg_extractors=[extractor],
        property_graph_store=graph_store,
        storage_context=storage_context,
        show_progress=True,
        embed_kg_nodes=True,
    )

    nodes = index.property_graph_store.get()
    storage_context.persist(persist_dir="./storage")
    graph_store.persist(persist_path="./storage/property_graph_store.json")

    for node in nodes:
        print(node)
    print(f"🎯 图谱共 {len(nodes)} 个节点:")
    return index   

# ===================== 加载已有图谱 =====================
def load_existing_graph_index():
    print("✅ 图谱索引加载成功！")
    storage_context.persist(persist_dir="./storage")
    graph_store.persist(persist_path="./storage/property_graph_store.json")
    index = PropertyGraphIndex.from_existing(
        llm=llm,
        embed_model=embed_model,
        property_graph_store=graph_store,
        storage_context=storage_context,
        use_async=False,
        embed_kg_nodes=True,
    )
    nodes = index.property_graph_store.get()
    print(f"🎯 图谱共 {len(nodes)} 个节点:")
    return index

# ===================== 循环对话 =====================

def create_agent():
    """
    根据查询文本从图索引中获取单次响应。
    """
    # 设置全局模型
    Settings.embed_model = embed_model  
    Settings.llm = llm
    index = load_existing_graph_index()
    # 创建图感知检索器
    retriever = index.as_retriever(
        include_text=True,
        include_graph=True,
        similarity_top_k=10,
        graph_traversal_depth=10,
    )

    # 将检索器包装为工具
    retriever_tool = RetrieverTool.from_defaults(
        retriever=retriever,
        name="graph_retriever",
        description="Useful for retrieving information from the knowledge graph."
    )
    # 创建 FunctionAgent
    agent = ReActAgent(
        tools=[retriever_tool],  # 使用工具列表
        llm=llm
    )
    
    return agent


class LlamaIndexChatWrapper:
    def __init__(self, index):
        self.index = index
        # 注意：llm 需要从外部传入或在方法中获取
        # self.llm = llm  # 假设 llm 已定义

    def chat(self, messages: List[Dict[str, str]], stream: bool = False):
        if not messages:
            raise ValueError("messages 不能为空")

        # 拆分：最后一条是用户当前问题，前面的是历史
        if len(messages) == 1:
            chat_history = []
            current_query = messages[0]["content"]
        else:
            chat_history = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in messages[:-1]
            ]
            current_query = messages[-1]["content"]

        if stream:
            return self._stream_response(current_query, chat_history)
        else:
            return self._sync_response(current_query, chat_history)

    def _sync_response(self, query: str, chat_history: List[ChatMessage]) -> str:
        """同步响应"""
        chat_engine = self.index.as_chat_engine(
            # llm=self.llm,  # 如果需要，取消注释
            similarity_top_k=10,
            graph_traversal_depth=10,
            chat_history=chat_history,
        )
        response = chat_engine.chat(query)
        return str(response)

    def _stream_response(self, query: str, chat_history: List[ChatMessage]) -> Generator[str, None, None]:
        if not query.strip():
            yield "抱歉，我没收到有效的问题。请重新提问。"
            return

        chat_engine = self.index.as_chat_engine(
            chat_history=chat_history,
            streaming=True
        )
        response_gen = chat_engine.stream_chat(query)

        for token in response_gen.response_gen:
            if token:  # 只有非空token才输出
                yield token

        yield " [DONE]"

# 使用示例
def create_chat_completion(messages: List[Dict[str, str]], stream: bool = True):
    """
    封装函数，模拟 client.chat.completions.create
    """
    wrapper = LlamaIndexChatWrapper(index=load_existing_graph_index())
    
    if stream:
        return wrapper.chat(messages, stream=True)
    else:
        return wrapper.chat(messages, stream=False)

def test():
    """测试函数"""
    # 第一轮对话
    test_messages_1 = [
        {"role": "user", "content": "你好"}
    ]
    
    print("第一轮 - 测试流式输出:")
    stream_gen = create_chat_completion(test_messages_1, stream=True)
    full_response_1 = ""
    for chunk in stream_gen:
        print(f"流式块: {chunk}", end="")
        full_response_1 += chunk if chunk not in [" [DONE]\n\n"] else ""
    print("\n" + "="*50)
    
    # 第二轮对话（带上下文）
    test_messages_2 = [
        {"role": "user", "content": "你好"}, 
        {"role": "assistant", "content": full_response_1.strip()},  # 上轮回复
        {"role": "user", "content": "刚才我问了什么？"}  # 当前问题
    ]
    
    print("第二轮 - 测试上下文:")
    sync_response_2 = create_chat_completion(test_messages_2, stream=False)
    print(f"带上下文的响应: {sync_response_2}")
    print("="*50)
    
    # 验证上下文是否生效
    print("验证：模型应能回答'刚才我问了什么' -> '你好'")

# ===================== 主程序 =====================
if __name__ == "__main__":
    if REBUILD_GRAPH:
        build_graph_index()

    else:
        test()
