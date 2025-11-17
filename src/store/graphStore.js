// graph-store.js
class GraphStore {
  constructor() {
    this.graphRef = null;
    this.selectedNode = null; // 直接存储选中的节点
    this.listeners = new Map();
  }

  setGraphInstance(graph) {
    this.graphRef = graph;

    if (graph) {
      // 节点点击事件
      graph.on("node:click", (event) => {
        console.log("Node click event:", event);

        const { target } = event;
        this.selectedNode = graph.getNodeData(target.id);
        this.notifyNodeClick(this.selectedNode);
      });

      // 画布点击事件 - 用于清除选中状态
      graph.on("canvas:click", (event) => {
        console.log("Canvas click event:", event);

        const graphNodes = this.graphRef.getData().nodes;

        // 遍历所有节点，查找当前选中的节点
        for (const node of graphNodes) {
          if (node && node.data && node.data.selected === true) {
            // 打印当前选中节点的 ID
            console.log("Previous selected node ID:", node.id);

            // 更新该节点的选中状态为 false
            this.graphRef.updateNodeData([
              {
                id: node.id,
                data: { selected: false },
              },
            ]);
            break; // 找到并处理后退出循环
          }
        }

        // 清除本地选中节点记录
        this.selectedNode = null;
        // 通知所有监听者节点已取消选中
        this.notifyNodeClick(null);
      });
    }
  }

  // 获取选中的节点
  getSelectedNode() {
    return this.selectedNode;
  }

  // 清除选中状态
  clearSelectedNode() {
    this.selectedNode = null;
  }

  notifyNodeClick(nodeData) {
    if (this.listeners.has("nodeClick")) {
      const callbacks = this.listeners.get("nodeClick");
      callbacks.forEach((callback) => callback(nodeData));
    }
  }

  checkIdInGraphNodes(targetId) {
    const graphNodes = this.graphRef.getData().nodes;
    console.log("节点数据:", graphNodes);

    // 使用find方法，找到匹配项时立即返回，提高性能
    const foundNode = graphNodes.find(
      (node) => node && node.id !== undefined && node.id === targetId
    );

    return foundNode || null;
  }

  // ... 其他方法
  createOrUpdateNode(nodeData) {
    if (this.graphRef) {
      const node = {
        id: nodeData.id || `node_${Date.now()}`,
        style: { x: 100, y: 100 },
        data: nodeData,
      };
      const exist_node = this.checkIdInGraphNodes(nodeData.id);
      console.log(exist_node);
      if (!exist_node) {
        this.graphRef.addNodeData([node]);
      } else {
        node.style = exist_node.style;
        this.graphRef.updateNodeData([node]);
      }
      this.graphRef.draw();
    }
  }

  removeNode(nodeData) {
    if (this.graphRef) {
      const exist_node = this.checkIdInGraphNodes(nodeData.id);
      if (exist_node) {
        var nodes = this.graphRef.getData().nodes;
        console.log(nodes);
        this.graphRef.removeNodeData([nodeData.id]);
        nodes = this.graphRef.getData().nodes;
        console.log(nodes);
      }
      this.graphRef.draw();
    }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType).add(callback);
  }

  off(eventType, callback) {
    if (this.listeners.has(eventType)) {
      this.listeners.get(eventType).delete(callback);
    }
  }

  getGraph() {
    return this.graphRef;
  }
}

export const graphStore = new GraphStore();
