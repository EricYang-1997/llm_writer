# -*- coding: utf-8 -*-
import os
from llama_index.core import Settings, StorageContext
from llama_index.core.indices.knowledge_graph import KnowledgeGraphIndex
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding

# ===================== 全局配置 =====================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-a8ca287e30304c23803c3910fffc76d2")
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"

LLM_MODEL = "qwen-plus"
EMBED_MODEL = "text-embedding-v4"

# Neo4j 配置（请按你的实际密码修改！）
NEO4J_URL = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "ygy1997666"  # ←←← 重要：改成你的实际密码！

# 示例中文文本
TEXT = """
在北宋末年，朝廷腐败，奸臣当道，民不聊生。表面上天下太平，实则豪强横行、官府贪暴，百姓怨声载道。正是在这乱世之中，一百零八位好汉因各自不同的遭遇，被逼上梁山泊，聚义结盟，共举“替天行道”大旗，反抗不公，劫富济贫，成为震动天下的“梁山泊义军”。
故事始于东京汴梁。八十万禁军教头林冲本安分守己，却因高俅之子高衙内觊觎其妻，遭陷害误入白虎堂，被刺配沧州。途中屡遭追杀，最终在风雪山神庙手刃仇敌，彻底与朝廷决裂，投奔梁山。与此同时，鲁智深原为提辖官，因打抱不平三拳打死镇关西，遁入空门，却仍不改豪侠本色，一路行侠仗义，终上梁山。还有因失陷花石纲而流落江湖的杨志、被官府逼得家破人亡的武松、因怒杀西门庆为兄报仇而刺配孟州的他，都在命运的驱使下走上反抗之路。
梁山泊起初只是零星草寇聚集之地，后经晁盖、宋江等人相继领导，逐步壮大。晁盖劫取生辰纲，引来官府围剿，幸得宋江通风报信，众人得以脱险，共上梁山。晁盖身亡后，宋江成为首领。他素怀忠义，虽聚义梁山，却始终心向朝廷，主张“只反贪官，不反皇帝”。在他的带领下，梁山好汉屡败官军，声势日隆，打出“替天行道”的杏黄旗，招揽天下英雄，终成一百零八将齐聚水泊的盛况——三十六天罡，七十二地煞，各有其能，各怀其志。
然而，梁山的壮大引来朝廷忌惮。在经历多次征讨与招安拉锯后，宋江接受朝廷招安，率众为国效力。他们先征辽国，再平田虎、王庆、方腊等割据势力。虽屡建奇功，却伤亡惨重。昔日兄弟或战死沙场，或心灰意冷隐退江湖。最终，朝廷仍视梁山为隐患，以御酒赐毒，宋江、卢俊义等核心头领相继被害。李逵饮毒酒殉主，吴用、花荣自缢于宋江墓前，梁山义军终归尘土。
《水浒传》以群像叙事展现乱世中个体的命运沉浮。这些好汉并非完人，或粗鲁暴烈，或狡黠多诈，或优柔寡断，但皆因世道不公而被逼至绝境。他们的聚义，是对压迫的反抗；他们的招安，是忠义与现实的撕裂；他们的结局，则是对“替天行道”理想在腐朽体制下难以实现的悲凉写照。全书既有快意恩仇的豪情，也有对体制、人性与命运的深刻叩问。
"""

# ===================== 初始化 LlamaIndex =====================
def setup_llama_index():
    # LLM（Qwen via DashScope OpenAI 兼容）
    llm = OpenAILike(
        model=LLM_MODEL,
        api_key=DASHSCOPE_API_KEY,
        api_base=DASHSCOPE_API_BASE,
        temperature=0,
        max_tokens=512,
        is_chat_model=True,
    )

    # Embedding
    embed_model = OpenAILikeEmbedding(
        model_name=EMBED_MODEL,
        api_key=DASHSCOPE_API_KEY,
        api_base=DASHSCOPE_API_BASE,
    )

    Settings.llm = llm
    Settings.embed_model = embed_model

    # Neo4j 图存储（原生支持）
    graph_store = Neo4jGraphStore(
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        url=NEO4J_URL,
        database="neo4j",  # 默认数据库名
    )

    return graph_store

# ===================== ① 构建知识图谱 =====================
from llama_index.core import PromptTemplate

CHINESE_KG_TRIPLET_EXTRACT_PROMPT = PromptTemplate(
"""
你是一个世界级的知识图谱构建引擎。请从以下文本中提取所有**明确陈述的、非冗余的**事实三元组，格式为（主体, 谓词, 客体）。

#### 📌 提取规则
1. **仅提取文本中直接说明的事实**，禁止推理、假设、常识补充。
2. **主体和客体必须是命名实体或具体概念**，如：
   - 人名：李世民、爱因斯坦
   - 机构：清华大学、NASA
   - 产品：iPhone 15、MySQL
   - 地点：北京、太平洋
   - 事件：第二次世界大战、上市
   - 抽象概念：光合作用、通货膨胀
   - ❌ 禁止使用代词（他、它、该系统）、模糊词（某公司、一位科学家）
3. **谓词必须是动词或动宾短语**，清晰表达关系，如：
   - 正确：`出生于`、`开发了`、`导致`、`属于`、`发布于`、`治疗`
   - 错误：`是`、`有`、`相关`（除非原文明确使用）
4. **保留关键限定信息**：
   - 原文：“苹果公司于2023年发布了iPhone 15”  
     → 三元组：(iPhone 15, 发布于, 2023年) 和 (iPhone 15, 由公司发布, 苹果公司)
5. **一个事实只输出一个最精准的三元组**，避免重复。
6. **输出格式**：
   - 每行一个三元组，严格使用：(主体, 谓词, 客体)
   - 不要序号、不要解释、不要Markdown

#### 🌰 示例
输入：「特斯拉由埃隆·马斯克领导，其总部位于美国得克萨斯州。Model Y 是该公司2020年推出的SUV。」
输出：
(特斯拉, 领导者, 埃隆·马斯克)
(特斯拉, 总部位于, 美国得克萨斯州)
(Model Y, 属于公司, 特斯拉)
(Model Y, 推出于, 2020年)
(Model Y, 车型, SUV)

#### 🔍 现在处理以下文本：
{text}

三元组：
"""
)
def build_kg_index():
    print("🧱 正在清空并重建 Neo4j 图谱...")

    graph_store = setup_llama_index()

    # 清空现有图（谨慎！）
    from neo4j import GraphDatabase
    driver = GraphDatabase. driver(NEO4J_URL, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    with driver.session(database="neo4j") as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()
    print("✅ 旧图已清空")

    # 创建文档
    from llama_index.core.schema import Document
    doc = Document(text=TEXT)

    storage_context = StorageContext.from_defaults(graph_store=graph_store)
    index = KnowledgeGraphIndex.from_documents(
        [doc],
        storage_context=storage_context,
        max_triplets_per_chunk=15,
        include_embeddings=False,  # 若需向量混合检索可设为 True
        show_progress=True,
        kg_triplet_extract_prompt=CHINESE_KG_TRIPLET_EXTRACT_PROMPT,
    )

    print("✅ 图谱已写入 Neo4j")
    return index

# ===================== ② 图谱问答 =====================
def kg_chat(index):
    print("\n💬 进入图谱问答模式（输入 /q 退出）")
    while True:
        query = input("Q> ").strip()
        if not query or query.lower() in ("/q", "quit", "exit"):
            break

        try:
            query_engine = index.as_query_engine(
                include_text=False,        # 仅用图谱
                response_mode="tree_summarize",
                verbose=True,
            )
            response = query_engine.query(query)
            print("A>", str(response).strip(), "\n")
        except Exception as e:
            print("❌ 出错：", e, "\n")

# ===================== 主程序 =====================
if __name__ == "__main__":
    index = build_kg_index()
    kg_chat(index)