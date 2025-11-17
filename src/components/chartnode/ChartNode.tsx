import { register, ExtensionCategory, Graph } from "@antv/g6";
import { ReactNode } from "@antv/g6-extension-react";
import { Card, Flex, Typography, Tag } from "antd";
import { useRef } from "react";

const { Text } = Typography;

// 注册React节点扩展
register(ExtensionCategory.NODE, "react-node", ReactNode);

// 状态颜色映射（根据您的需求调整）
const statusColors = {
  启用: "#17BEBB",
  停用: "#B7AD99",
  反例: "#E36397",
  示例: "#089c21",
};


const ChartNode = ({ data, graph }) => {
  const containerRef = useRef(null);
  const nodeData = data?.data || {};
  const { level ,label, name, status, content,description } = nodeData;
  const handleClick = () => {
    graph.updateNodeData([{ id: data.id, data: { selected: !data.data.selected } }]);
    graph.draw();
  };
  // 根据状态获取标签颜色
  const getStatusTagColor = () => statusColors[status] || "blue";

  const renderDetailNode = () => (
    <Card
      title={
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span>{label}</span>
          <span style={{ color: "#8c8c8c", fontSize: "14px" }}>
            {name}
          </span>{" "}
          {/* 黑灰色的name */}
        </div>
      }
      extra={
        <Tag
          color={getStatusTagColor()}
          style={{
            fontSize: "10px",
            padding: "2px 6px",
            borderRadius: "4px",
          }}
        >
          {status}
        </Tag>
      }
      style={{
        width: "100%",
        height: "100%",
        borderColor: data.data.selected ? 'orange' : '#ddd', // 根据选中状态设置边框颜色

      }}
    >
      <Text
        type="secondary"
        style={{
          fontSize: "14px",
          color: "#666",
          lineHeight: "1.4",
          whiteSpace: "nowrap",
          overflow: "hidden",
          textOverflow: "ellipsis",
        }}
        ellipsis={{ tooltip: content }}
      >
        {description}
      </Text>
    </Card>
  );

  return (
    <div
      ref={containerRef}
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderColor: data.data.selected ? 'orange' : '#ddd', // 根据选中状态设置边框颜色
      }}
      onClick={handleClick}

    >
      {renderDetailNode()}
    </div>
  );
};

export default ChartNode;
