# -*- coding: utf-8 -*-
import os
from typing import List

# 1) LangChain 基础
from langchain_community.chat_models import ChatTongyi          # 百炼对话模型（Qwen系列）
from langchain_community.embeddings import DashScopeEmbeddings  # 百炼向量
from langchain_core.documents import Document
from langchain_experimental.graph_transformers import LLMGraphTransformer

# 2) Memgraph × LangChain 集成
from langchain_memgraph.graphs.memgraph import MemgraphLangChain
from langchain_memgraph.chains.graph_qa import MemgraphQAChain


# ===================== 全局配置 =====================
# 建议在 shell 中： export DASHSCOPE_API_KEY="sk-xxxx"
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-a8ca287e30304c23803c3910fffc76d2")

# 百炼模型（Qwen）
LLM_MODEL = "qwen-plus"
EMBED_MODEL = "text-embedding-v4"   # 仅在你要用向量时需要，这里不强制用

# Memgraph 连接
MEMGRAPH_URL = "bolt://localhost:7687"
MEMGRAPH_USER = ""       # 默认为空
MEMGRAPH_PASSWORD = ""   # 默认为空

# 示例中文文档（你也可以改成文件读取）
TEXT = """
李氏家族起源于陇西。李世民是李渊的次子，母亲是窦皇后。
李建成是李世民的长兄，李元吉是他们的弟弟。李世民娶了长孙皇后。
唐太宗去世后，由第九子李治继位，是为唐高宗。李治娶了武则天，武则天后来称帝。
"""

# ===================== 工具函数 =====================
def get_llm():
    """构造百炼聊天模型（Qwen）。"""
    # ChatTongyi 会自动读取环境变量 DASHSCOPE_API_KEY
    return ChatTongyi(model=LLM_MODEL, temperature=0)

def get_embeddings():
    """如需要向量检索时可用。本示例不强依赖，可按需启用。"""
    return DashScopeEmbeddings(model=EMBED_MODEL)

def connect_graph() -> MemgraphLangChain:
    """连接 Memgraph（LangChain 适配器）。"""
    graph = MemgraphLangChain(
        url=MEMGRAPH_URL,
        username=MEMGRAPH_USER,
        password=MEMGRAPH_PASSWORD,
        refresh_schema=False,   # 初次建库前一般关掉，写完再 refresh
    )
    return graph

# ===================== ① 新建/重建图谱（抽取→写库） =====================
def new_graph():
    """
    只在有新文档时执行一次：
    - 用 LLMGraphTransformer 将文本抽成 GraphDocument
    - 写入 Memgraph
    - 刷新 schema，供 NL→Cypher 用
    """
    llm = get_llm()
    graph = connect_graph()

    # 可选：清空旧图（谨慎使用）
    try:
        graph.query("STORAGE MODE IN_MEMORY_ANALYTICAL")
        graph.query("DROP GRAPH")
        graph.query("STORAGE MODE IN_MEMORY_TRANSACTIONAL")
        print("✅ 已清空旧图")
    except Exception as e:
        print("（清库可忽略）", e)

    # 文档 → GraphDocument
    docs: List[Document] = [Document(page_content=TEXT)]
    transformer = LLMGraphTransformer(llm=llm)
    graph_documents = transformer.convert_to_graph_documents(docs)

    # 写入 Memgraph
    graph.add_graph_documents(graph_documents, include_source=True)
    graph.refresh_schema()  # 写完刷新 schema，让 QA 链更稳
    print("✅ 图谱构建完成并写入 Memgraph")

    # 简单测试：给一问
    qa = MemgraphQAChain.from_llm(llm, graph=graph, allow_dangerous_requests=True, verbose=True)
    print("测试问答：", qa.invoke({"query": "唐太宗去世后由谁继位？"}))

# ===================== ② 图谱对话（只查，不抽取） =====================
def graph_chat():
    """
    日常使用：只基于已存在图谱对话。
    不会再做抽取/写库，直接用 NL→Cypher 的 QA 链。
    """
    llm = get_llm()
    graph = connect_graph()

    # 不重建、不写入，只创建 QA 链即可
    qa = MemgraphQAChain.from_llm(llm, graph=graph,allow_dangerous_requests=True, verbose=True)

    print("\n进入图谱对话模式（/q 退出）")
    while True:
        q = input("Q> ").strip()
        if not q or q.lower() in ("/q", "exit", "quit"):
            break
        try:
            ans = qa.invoke({"query": q})
            # 部分版本返回 dict 或 str，这里统一打印
            print("A>", ans if isinstance(ans, str) else ans.get("result", ans), "\n")
        except Exception as e:
            print("❌ 出错：", e, "\n")

# ===================== 主入口（手动注释切换） =====================
if __name__ == "__main__":
    # 只需手动注释/取消注释来切换 ↓↓↓
    new_graph()   # 🧱 第一次或有新文档时运行一次
    graph_chat()    # 💬 日常对话（不会重建图谱）
