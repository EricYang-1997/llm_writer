from functools import wraps
import hashlib
import os
import pickle
import dashscope
from http import HTTPStatus
from llama_index.core.graph_stores.types import EntityNode, Relation
from docx import Document
from llama_index.core.schema import TextNode

def parse_content_to_properties(content: str):
    """将文本按行和冒号解析为属性字典"""
    properties = {}
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    for line in lines:
        # 支持中文和英文冒号
        for sep in ['：', ':']:
            if sep in line:
                parts = line.split(sep, 1)  # 只分割一次
                key = parts[0].strip()
                value = parts[1].strip()
                properties[key] = value
                break
    return properties



def read_docx_to_graph_nodes(doc_path, graph_store):
    doc = Document(doc_path)
    
    node_cache = {}        # 存储所有节点：H2/H3/H4/H5/CONTENT
    seen_relations = set()
    last = {"H2": None, "H3": None, "H4": None, "H5": None}
    content_buffer = {"H2": "", "H3": "", "H4": "", "H5": ""}
    
    def add_relation(parent_node, child_node, label="CONTAINS"):
        rel_key = (parent_node.id, label, child_node.id)
        if rel_key not in seen_relations:
            seen_relations.add(rel_key)
            relation = Relation(label=label, source_id=parent_node.id, target_id=child_node.id)
            graph_store.upsert_relations([relation])

    for para in doc.paragraphs:
        style = para.style.name if para.style else "Normal"
        text = para.text.strip()
        if not text:
            continue

        # 处理各级标题（H2-H5）——仅记录标题名，不清空content_buffer["H5"]
        if style == "Heading 2":
            # 保存上一个 H2 的子内容
            if last["H2"]:
                node_cache[last["H2"]] = EntityNode(
                    name=last["H2"],
                    label="SECTION",
                )
                graph_store.upsert_nodes([node_cache[last["H2"]]])

            node_cache[text] = EntityNode(name=text, label="SECTION", properties={})
            graph_store.upsert_nodes([node_cache[text]])
            last["H2"] = text
            last["H3"] = last["H4"] = last["H5"] = None
            content_buffer = {"H2": "", "H3": "", "H4": "", "H5": ""}

        elif style == "Heading 3":
            if last["H3"]:
                node_cache[last["H3"]] = EntityNode(
                    name=last["H3"],
                    label="SUBSECTION",
                )
                graph_store.upsert_nodes([node_cache[last["H3"]]])

            if last["H2"]:
                h3_node = EntityNode(name=text, label="SUBSECTION", properties={})
                node_cache[text] = h3_node
                graph_store.upsert_nodes([h3_node])
                add_relation(node_cache[last["H2"]], h3_node)
            last["H3"] = text
            last["H4"] = last["H5"] = None
            content_buffer["H5"] = ""

        elif style == "Heading 4":
            if last["H4"]:
                node_cache[last["H4"]] = EntityNode(
                    name=last["H4"],
                    label="SUBSUBSECTION",
                )
                graph_store.upsert_nodes([node_cache[last["H4"]]])

            if last["H3"]:
                h4_node = EntityNode(name=text, label="SUBSUBSECTION", properties={})
                node_cache[text] = h4_node
                graph_store.upsert_nodes([h4_node])
                add_relation(node_cache[last["H3"]], h4_node)
            last["H4"] = text
            last["H5"] = None
            content_buffer["H5"] = ""

        elif style == "Heading 5":
            # 处理上一个H5节点（如果有正文内容）
            if last["H5"]:
                content_text = content_buffer["H5"]
                properties = parse_content_to_properties(content_text)                
                # 更新上一个H5节点，添加内容属性
                if last["H5"] in node_cache:
                    old_h5_node = node_cache[last["H5"]]
                    old_h5_node.properties.update({
                        **properties,
                    })
                    graph_store.upsert_nodes([old_h5_node])

            # 创建新的H5节点
            h5_node = EntityNode(
                name=text, 
                label="CONTENT", 
                properties={}  # 暂时空，后续会更新
            )
            node_cache[text] = h5_node
            graph_store.upsert_nodes([h5_node])
            
            if last["H4"]:
                add_relation(node_cache[last["H4"]], h5_node)

            last["H5"] = text
            content_buffer["H5"] = ""

        else:  # 正文段落
            if last["H5"]:
                content_buffer["H5"] += "\n" + text if content_buffer["H5"] else text


    # 处理最后一个 H5 的正文内容
    if last["H5"] and content_buffer["H5"]:
        content_text = content_buffer["H5"]
        properties = parse_content_to_properties(content_text)
        
        # 直接更新H5节点，而不是创建CONTENT节点
        h5_node = node_cache[last["H5"]]
        h5_node.properties.update({
            **properties
        })
        graph_store.upsert_nodes([h5_node])

    nodes_as_standard_nodes = []

    for entity_node in node_cache.values():
        if entity_node.label == "CONTENT":  # 只转换正文节点
            standard_node = TextNode(
                id_=entity_node.id,
                metadata={
                    "name": entity_node.name,
                    "label": entity_node.label,
                    **entity_node.properties
                }
            )
            nodes_as_standard_nodes.append(standard_node)

    return nodes_as_standard_nodes

