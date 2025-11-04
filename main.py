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
    【鲁智深行侠】鲁智深原为提辖官，因打抱不平三拳打死镇关西，遁入空门，却仍不改豪侠本色，一路行侠仗义，终上梁山。
    """,
    """
    【杨志与武松】还有因失陷花石纲而流落江湖的杨志、被官府逼得家破人亡的武松、因怒杀西门庆为兄报仇而刺配孟州的他，
    都在命运的驱使下走上反抗之路。
    """,
    """
    【晁盖与生辰纲】梁山泊起初只是零星草寇聚集之地。晁盖劫取生辰纲，引来官府围剿，幸得宋江通风报信，众人得以脱险，共上梁山。
    """,
    """
    【宋江领导与招安】晁盖身亡后，宋江成为首领。他素怀忠义，虽聚义梁山，却始终心向朝廷，主张“只反贪官，不反皇帝”。
    在他的带领下，梁山好汉屡败官军，打出“替天行道”的杏黄旗，招揽天下英雄，终成一百零八将齐聚水泊的盛况。
    """,
    """
    【征方腊与结局】梁山的壮大引来朝廷忌惮。宋江接受朝廷招安，率众为国效力。
    他们先征辽国，再平田虎、王庆、方腊等割据势力。虽屡建奇功，却伤亡惨重。
    朝廷仍视梁山为隐患，以御酒赐毒，宋江、卢俊义等核心头领相继被害。
    李逵饮毒酒殉主，吴用、花荣自缢于宋江墓前，梁山义军终归尘土。
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
Settings.llm = llm  # ★ 关键：避免回退到 OpenAI

# 2) Embedding（把维度设成与你的 Memgraph 向量索引一致，比如 1536）
embed_model = OpenAILikeEmbedding(
    model_name="text-embedding-v4",  # 注意是 model_name= 而非 model=
    api_base=API_BASE,
    api_key=DASHSCOPE_API_KEY,
    dimensions=1536              # 若你的索引是 1024/2048，则改成对应维度
)
Settings.embed_model = embed_model  # ★ 关键：避免回退到 OpenAI

# 3) 连接 Memgraph
graph_store = MemgraphPropertyGraphStore(
    url="bolt://localhost:7688",
    database="memgraph",
    username="", password="" 
)
documents = [Document(text=t.strip()) for t in TEXT_SEGMENTS]

EntityTypes = Literal["PERSON", "EVENT", "ORGANIZATION", "CONCEPT", "LOCATION"]
RelationTypes = Literal[
    "PARTICIPATES_IN", "LEADS", "CAUSES", "OPPOSES", "SUCCEEDS",
    "DIES_IN", "ADVOCATES", "BETRAYS", "LOCATED_AT", "MENTIONS",
    "OCCURS_IN", "EXILED_TO"  # ← 加入更精确的关系
]
extractor = SchemaLLMPathExtractor(
    llm=llm,
    possible_entities=EntityTypes,
    possible_relations=RelationTypes,
    max_triplets_per_chunk=40,
    strict=False  # 强制遵守 schema
)
storage_context = StorageContext.from_defaults(graph_store=graph_store)

# ===================== 构建图谱（含清库）=====================
def build_graph_index():
    print("🧼 正在清空 Memgraph 并重建图谱...")
    # 清库
    driver = GraphDatabase.driver("bolt://localhost:7688", auth=None)
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()
    print("✅ 图库已清空")


    index = PropertyGraphIndex.from_documents(
        documents,
        llm=llm,
        storage_context=storage_context,
        embed_model=embed_model,
        kg_extractors=[extractor],
        property_graph_store=graph_store,
        show_progress=True,
    )
    index.storage_context.persist(persist_dir="./storage")
    print("✅ 图谱构建完成！")
    return 


# ===================== 加载已有图谱 =====================
def load_existing_graph_index():
    print("📂 从磁盘加载持久化图谱...")
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage",
        graph_store=graph_store  # 仍连接 Memgraph
    )
    index = load_index_from_storage(storage_context)
    print("✅ 图谱索引加载成功！")
    return index

# ===================== 循环对话 =====================
def chat_with_graph(index):
    print("\n🔍 直接测试 retriever（输入 /q 退出）")
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