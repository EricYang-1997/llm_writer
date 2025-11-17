import React, { useEffect, useRef } from "react";
import {
  ExtensionCategory,
  Graph,
  Polyline,
  register,
} from "@antv/g6";
import { graphStore } from '../store/graphStore.js';
import ChartNode from '../components/chartnode/ChartNode';
class AntLine extends Polyline {
  onCreate() {
    const shape = this.shapeMap.key;
    shape.animate([{ lineDashOffset: -20 }, { lineDashOffset: 0 }], {
      duration: 500,
      iterations: Infinity,
    });
  }
}

// 注册扩展（注意：只注册一次）

const registerExtensions = () => {
  register(ExtensionCategory.EDGE, "ant-line", AntLine);
};

// --- React 组件 ---
interface CenterGraphProps {
  style?: React.CSSProperties;
}

let extensionsRegistered = false;

const CenterGraph: React.FC<CenterGraphProps> = ({ style = {} }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<Graph | null>(null);
  const controlFullscreen = (action: string) => {
    if (action === "open") {
      containerRef.current?.requestFullscreen();
    } else if (action === "exit") {
      document.exitFullscreen();
    }
  };

  useEffect(() => {
    // 防止重复注册
    if (!extensionsRegistered) {
      registerExtensions();
      extensionsRegistered = true;
    }
    const data=[]
    const graph = new Graph({
      container: containerRef.current,
      node: {
        type: "react-node",
        style: {
          component: (data) => <ChartNode data={data} graph={graph} />,
          labelPlacement: "center",
          lineWidth: 1,
          ports: [{ placement: "top" }, { placement: "bottom" }],
          radius: 2,
          shadowBlur: 10,
          shadowColor: "#e0e0e0",
          shadowOffsetX: 3,
          size: [300, 120],
          stroke: "#C0C0C0",
          port: true,
          portR: 4,
          portLineWidth: 1,
          portStroke: "#fff",
        },
      },
      edge: {
        type: "ant-line",
        style: {
          lineDash: [5, 5],
        },
      },
      layout: {
        type: "dagre",
        rankdir: "TB",
        ranksep: 60,
        nodesep: 30,
      },
      autoFit: "view",
      behaviors: [
        {
          type: "click-select",
          degree: 1,
          state: "selected", // 选中的状态
          neighborState: "active", // 相邻节点附着状态
          unselectedState: "inactive", // 未选中节点状态
          multiple: true,
          trigger: ["shift"],
        },
        "drag-element",
        "zoom-canvas",
        "drag-canvas",
        "scroll-canvas",
        "optimize-viewport-transform",
      ],
      plugins: [
        {
          type: "fullscreen",
          key: "fullscreen",
        },
        {
          type: "background",
          width: "100%",
          height: "100%",
          backgroundImage:
            "url(https://mdn.alipayobjects.com/huamei_qa8qxu/afts/img/A*0Qq0ToQm1rEAAAAAAAAAAAAADmJ7AQ/original)",
          backgroundRepeat: "no-repeat",
          backgroundSize: "cover",
          opacity: 0.2,
        },
        {
          type: "contextmenu",
          trigger: "contextmenu", // 'click' or 'contextmenu'
          onClick: (value, target, current) => {
            alert("You have clicked the「" + v + "」item");
          },
          getItems: () => {
            return [
              { name: "新建", value: "detail" },
              { name: "删除", value: "delete" },
            ];
          },
        },
        {
          type: "toolbar",
          position: "top-left",
          // 👇 关键：在 onClick 中使用 graph 实例
          onClick: (item) => {
            const fullscreenPlugin = graph.getPluginInstance("fullscreen");
            switch (item) {
              case "zoom-in":
                graph.zoomBy(1.2); // 放大 20%
                break;
              case "zoom-out":
                graph.zoomBy(0.8); // 缩小到 80%（即缩小 20%）
                break;
              case "auto-fit":
                graph.fitView();
                break;
              case "request-fullscreen":
                fullscreenPlugin.request();
                break;
              case "exit-fullscreen":
                controlFullscreen("exit");
                break;
              case "reset":
                graph.clear();
                graph.setData(data);
                graph.render();
                break;
              // 其他功能可后续扩展
              default:
                console.log("Toolbar item clicked:", item.id);
            }
          },
          getItems: () => {
            // G6 内置了 9 个 icon，分别是 zoom-in、zoom-out、redo、undo、edit、delete、auto-fit、export、reset
            return [
              { id: "zoom-in", value: "zoom-in" },
              { id: "zoom-out", value: "zoom-out" },
              // { id: "redo", value: "redo" },
              // { id: "undo", value: "undo" },
              // { id: "edit", value: "edit" },
              // { id: "delete", value: "delete" },
              { id: "auto-fit", value: "auto-fit" },
              // { id: "export", value: "export" },
              { id: "request-fullscreen", value: "request-fullscreen" },
              { id: "exit-fullscreen", value: "exit-fullscreen" },

              { id: "reset", value: "reset" },
            ];
          },
        },
      ],
    });
    
    graphStore.setGraphInstance(graph);
    
    graph.render();

    return () => {
      if (graphRef.current) {
        graphRef.current.destroy();
        graphRef.current = null;
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: "100%", ...style }}
    />
  );
};

export default CenterGraph;
