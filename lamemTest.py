import os
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.core import Document
from llama_index.core.indices.property_graph import PropertyGraphIndex, SchemaLLMPathExtractor
from llama_index.core import Settings

# 建议用环境变量而不是硬编码
os.environ["DASHSCOPE_API_KEY"] = "sk-a8ca287e30304c23803c3910fffc76d2"

# 1) 配置百炼 LLM，并绑定为全局
llm = OpenAILike(
    model="qwen-plus",
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    is_chat_model=True
)
Settings.llm = llm  # ★ 关键：避免回退到 OpenAI

# 2) Embedding（把维度设成与你的 Memgraph 向量索引一致，比如 1536）
embed_model = OpenAILikeEmbedding(
    model_name="text-embedding-v4",  # 注意是 model= 而非 model_name=
    api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    dimensions=1536              # 若你的索引是 1024/2048，则改成对应维度
)

# 3) 连接 Memgraph
graph_store = MemgraphPropertyGraphStore(
    url="bolt://localhost:7688",
    database="memgraph",
    username="", password="" 
)

# 4) 文档
text = """
李氏家族起源于陇西。李世民是李渊的次子，母亲是窦皇后。李世民的长兄是李建成，李元吉是他们的弟弟。李世民娶了长孙皇后，唐太宗去世后，由第九子李治继位，是为唐高宗。
"""
extractor = SchemaLLMPathExtractor(
    llm=llm,
    max_triplets_per_chunk=20,
    strict=False,   # 放宽校验，避免因 schema 过严丢三元组
)
documents = [Document(text=text)]

# 5) 建索引
index = PropertyGraphIndex.from_documents(
    documents,
    embed_model=embed_model,
    kg_extractors=[extractor],
    property_graph_store=graph_store,
    show_progress=True,
)

retriever = index.as_retriever(
    include_text=True,
    # 关键调参：
    graph_traversal_depth=2,     # 多跳一点
    similarity_top_k=8           # 提高召回
)

nodes = retriever.retrieve("唐太宗去世后由谁继位？")
print("retrieved:", len(nodes))
for i, n in enumerate(nodes[:5], 1):
    print(i, n.node_id, getattr(n, "text", "")[:80])

# 6) 查询（用与文本匹配的问题）
qe = index.as_query_engine(include_text=True)
resp = qe.query("唐太宗去世后由谁继位？")
print(resp)
