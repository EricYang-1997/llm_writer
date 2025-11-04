# -*- coding: utf-8 -*-
import os
from typing import Literal
from neo4j import GraphDatabase  # 用于清库 & 检查节点数
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.core import Document, Settings
from llama_index.core.indices.property_graph import PropertyGraphIndex, SchemaLLMPathExtractor
from llama_index.core import Settings, StorageContext,load_index_from_storage
os.environ["OPENAI_API_KEY"] = "dummy"  # 防止任何 OpenAI 回退

# ===================== 配置区（按需修改） =====================

DASHSCOPE_API_KEY = "sk-a8ca287e30304c23803c3910fffc76d2"
API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# 按事件拆分的《水浒传》文本
TEXT_SEGMENTS = [
    """
    【背景】北宋末年，朝廷腐败，奸臣当道，民不聊生。表面上天下太平，实则豪强横行、官府贪暴，百姓怨声载道。
    """,
    """
    【林冲上梁山】八十万禁军教头林冲本安分守己，却因高俅之子高衙内觊觎其妻，遭陷害误入白虎堂，被刺配沧州。
    途中屡遭追杀，最终在风雪山神庙手刃仇敌，彻底与朝廷决裂，投奔梁山。
    """,
    """
    【宋江领导与招安】晁盖身亡后，宋江成为首领。他素怀忠义，虽聚义梁山，却始终心向朝廷，主张“只反贪官，不反皇帝”。
    在他的带领下，梁山好汉屡败官军，打出“替天行道”的杏黄旗，招揽天下英雄，终成一百零八将齐聚水泊的盛况。
    """,
    """
    【主题】《水浒传》以群像叙事展现乱世中个体的命运沉浮。
    这些好汉并非完人，但皆因世道不公而被逼至绝境。
    他们的聚义，是对压迫的反抗；他们的招安，是忠义与现实的撕裂；他们的结局，则是对“替天行道”理想在腐朽体制下难以实现的悲凉写照。
    """
]
# 1) 配置百炼 LLM，并绑定为全局
llm = OpenAILike(
    model="qwen-max",
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    is_chat_model=True,
    timeout=300,
)
# 2) Embedding（把维度设成与你的 Memgraph 向量索引一致，比如 1536）
embed_model = OpenAILikeEmbedding(
    model_name="text-embedding-v4",  # 注意是 model_name= 而非 model=
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    dimensions=1536              # 若你的索引是 1024/2048，则改成对应维度
)
Settings.embed_model = embed_model  
# 3) 连接 Memgraph

documents = [Document(text=t.strip()) for t in TEXT_SEGMENTS]

EntityTypes = Literal["PERSON", "EVENT", "ORGANIZATION", "CONCEPT", "LOCATION"]
RelationTypes = Literal[
    "PARTICIPATES_IN", "LEADS", "CAUSES", "OPPOSES", "SUCCEEDS",
    "DIES_IN", "ADVOCATES", "BETRAYS", "LOCATED_AT", "MENTIONS",
    "OCCURS_IN", "EXILED_TO"  # ← 加入更精确的关系
]
extractor = SchemaLLMPathExtractor(
    llm=llm,
    # possible_entities=EntityTypes,
    # possible_relations=RelationTypes,
    max_triplets_per_chunk=40,
    strict=False  # 强制遵守 schema
)

# ===================== 构建图谱（含清库）=====================
def build_graph_index():
    print("🧼 正在清空 Memgraph 并重建图谱...")
    driver = GraphDatabase.driver("bolt://localhost:7688", auth=None)
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        session.run("DROP ALL INDEXES;")
    driver.close()
    print("✅ 图库已清空")
    graph_store = MemgraphPropertyGraphStore(
        url="bolt://localhost:7688",
        database="memgraph",
        username="", password="" 
    )
    index = PropertyGraphIndex.from_documents(
        documents,
        llm=llm,
        embed_model=embed_model,
        kg_extractors=[extractor],
        property_graph_store=graph_store,
        show_progress=True,
        storage_context = StorageContext.from_defaults(graph_store=graph_store)

    )
    print("✅ 图谱构建并持久化完成！")

    # 🔍 立即验证：直接查图数据库
    print("\n🔍 验证图数据库中是否存在'风雪山神庙手刃仇敌'节点...")
    driver = GraphDatabase.driver("bolt://localhost:7688", auth=None)
    with driver.session() as session:
        result = session.run("""
            MATCH (e:EVENT {name: "风雪山神庙手刃仇敌"})
            RETURN e.name AS name, e.embedding IS NOT NULL AS has_embedding
        """)
        record = result.single()
        if record:
            print(f"✅ 节点存在，name: {record['name']}, 有 embedding: {record['has_embedding']}")
        else:
            print("❌ 节点不存在！")

        # 验证是否连接到林冲
        result2 = session.run("""
            MATCH (p:PERSON {name: "林冲"})-[r]->(e:EVENT {name: "风雪山神庙手刃仇敌"})
            RETURN count(r) AS rel_count
        """)
        rel_count = result2.single()["rel_count"]
        print(f"✅ 林冲 → 事件 的关系数量: {rel_count}")
    driver.close()

    # 🔍 立即验证：用 retriever 检索
    print("\n🔍 验证 retriever 能否检索到该事件...")
    index._embed_model = embed_model
    index._llm = llm
    index._use_async = False
    Settings.embed_model  = embed_model 
    Settings.llm = llm 
    retriever = index.as_retriever(
        include_text=True,
        include_graph=True,
        similarity_top_k=10,
    )
    Settings.embed_model  = embed_model  
    Settings.llm = llm 
    nodes = retriever.retrieve("风雪山神庙手刃仇敌")
    print(f"✅ retriever 检索到节点数量: {len(nodes)}")
    for node in nodes:
        print(f"  - {node.metadata.get('name', 'N/A')}")

    nodes = retriever.retrieve("风雪山神庙")
    print(f"✅ retriever 检索到节点数量: {len(nodes)}")
    for node in nodes:
        print(f"  - {node.metadata.get('name', 'N/A')}")

    return index

# ===================== 加载已有图谱 =====================
def load_existing_graph_index():
    print("📂 从磁盘加载持久化图谱...")
    # ✅ 从 persist_dir 自动加载全部存储组件
    graph_store = MemgraphPropertyGraphStore(
        url="bolt://localhost:7688",
        database="memgraph",
        username="", password="" 
    )
    print("✅ 图谱索引加载成功！")
    index = PropertyGraphIndex.from_existing(
        storage_context=StorageContext.from_defaults(graph_store=graph_store),
        llm=llm,
        embed_model=embed_model,
        property_graph_store=graph_store,
    )
    return index

# ===================== 循环对话 =====================
def chat_with_graph(index):
    print("\n🔍 直接测试 retriever（输入 /q 退出）")
    Settings.embed_model  = embed_model  
    Settings.llm = llm 
    retriever = index.as_retriever(
        include_text=True,
        include_graph=True,
        similarity_top_k=10,
        graph_traversal_depth=3,
    )
    while True:
        query = input("Q> ").strip()
        if not query or query.lower() in ("quit", "exit", "/q"):
            break
        
        nodes = retriever.retrieve(query)
        print(f"🎯 检索到 {len(nodes)} 个节点:")
        for i, node in enumerate(nodes):
            name = node.metadata.get("name", "N/A")
            print(f"  {i+1}. {name} (type: {node.metadata.get('type', 'unknown')})")
        print()

# ===================== 主程序 =====================
if __name__ == "__main__":
    REBUILD_GRAPH = False
    if REBUILD_GRAPH:
        build_graph_index()
    else:
        index = load_existing_graph_index()
        chat_with_graph(index)