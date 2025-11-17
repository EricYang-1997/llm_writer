DASHSCOPE_API_KEY = "sk-a8ca287e30304c23803c3910fffc76d2"
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.indices.property_graph import PropertyGraphIndex, SchemaLLMPathExtractor
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.ollama import Ollama
from llama_index.core import  Settings
from llama_index.core.schema import Document
from llama_index.core.graph_stores.types import KG_NODES_KEY, KG_RELATIONS_KEY

import asyncio

llm = OpenAILike(
    model="qwen-max",
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    is_chat_model=True,
    timeout=300,
)
# llm = Ollama(model="qwen3:8b", base_url="http://192.168.2.122:11434",request_timeout=300,thinking=False) 


embed_model = OpenAILikeEmbedding(
    model_name="text-embedding-v4",
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    dimensions=1536
)

Settings.llm = llm  
Settings.embed_model = embed_model  

graph_store = MemgraphPropertyGraphStore(
    url="bolt://localhost:7688",
    username="memgraph",
    password="",
)

index = PropertyGraphIndex.from_existing(
    llm=llm,
    embed_model=embed_model,
    property_graph_store=graph_store,
    use_async=False,
    embed_kg_nodes=True,
)
query_engine = index.as_query_engine()
tool = QueryEngineTool.from_defaults(query_engine=query_engine, name="graph_tool", description="知识图谱检索")

# 创建图谱查询工具
agent = ReActAgent(tools=[tool], llm=llm)
ctx = Context(agent)


async def story_gen_with_memory_async(prompt: str, expected_prefix: str) -> str:
    """利用图谱记忆的生成器"""
    response = await agent.run(user_msg=prompt, ctx=ctx)
    print(response)
    return response

def story_gen_with_memory(prompt: str, expected_prefix: str) -> str:
    """同步包装"""
    return str(asyncio.run(story_gen_with_memory_async(prompt, expected_prefix)))


def insert_story_outline_to_graph(outline_text: str):
    """使用SchemaLLMPathExtractor解析并存入知识图谱"""
    # 定义图谱schema
    
    # 创建SchemaLLMPathExtractor
    path_extractor = SchemaLLMPathExtractor(
        llm=llm,
        max_triplets_per_chunk=5,
        strict=False  
    )
    
    # 解析大纲文本
    nodes = path_extractor([Document(text=outline_text)])
    
    entities = []
    relations = []
    for node in nodes:
        entities.extend(node.metadata.get(KG_NODES_KEY, []))
        relations.extend(node.metadata.get(KG_RELATIONS_KEY, []))

    index.property_graph_store.upsert_nodes(entities)
    index.property_graph_store.upsert_relations(relations)
    
    print(f"已插入 {len(entities)} 个实体和 {len(relations)} 个关系")


# 使用示例
outline = "记者追查城市断电事件"
prompt = f"根据大纲 `{outline}`，生成3个细纲节点，格式：`(细纲)-[...]`，仅输出结果。"
scene_outline = story_gen_with_memory(prompt, "(细纲)")
insert_story_outline_to_graph(scene_outline)
