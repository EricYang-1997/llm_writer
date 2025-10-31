<template>
  <div id="container" class="graph-container"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import {Graph} from '@antv/g6';

// 模拟图数据（你可以替换成自己的 data）
const graphData = ref({
  nodes: [
    { id: 'node1', cluster: 'A' },
    { id: 'node2', cluster: 'A' },
    { id: 'node3', cluster: 'B' },
    { id: 'node4', cluster: 'B' },
  ],
  edges: [
    { source: 'node1', target: 'node2' },
    { source: 'node3', target: 'node4' },
    { source: 'node1', target: 'node3' },
  ],
});

let graph = null;

const initGraph = () => {
  const container = document.getElementById('container');
  if (!container) return;

  // 清除已有实例（防止重复创建）
  if (graph) {
    graph.destroy();
  }

  graph = new Graph({
    container: 'container',
    width: container.scrollWidth,
    height: container.scrollHeight ,
    data: graphData.value,
    node: {
      style: {
          size: (datum) => datum.id.length * 2 + 10,
          label: false,
          labelText: (datum) => datum.id,
          labelBackground: true,
          icon: false,
          iconFontFamily: 'iconfont',
          iconText: '\ue6f6',
          iconFill: '#fff',
      },
      palette: {
          type: 'group',
          field: (datum) => datum.id,
          color: ['#1783FF', '#00C9C9', '#F08F56', '#D580FF'],
      },
    },
    layout: {
      type: 'force',
      linkDistance: 50,
      clustering: true,
      nodeClusterBy: 'cluster',
      clusterNodeStrength: 70,
    },
    autoFit: 'view',
    behaviors: ['zoom-canvas', 'drag-canvas', 'drag-element',
      {
        type: 'click-select',
        degree: 1,
        state: 'selected', // 选中的状态
        neighborState: 'active', // 相邻节点附着状态
        unselectedState: 'inactive', // 未选中节点状态
        multiple: true,
        trigger: ['shift'],
      },
    ],
    plugins: [
    {key: 'grid-line', type: 'grid-line', follow: false },
    {type: 'legend',nodeField: 'cluster',edgeField: 'cluster',},
    {type: 'minimap',size: [240, 160],},
    {
      type: 'background',
      width: '100%',
      height: '100%',
      // backgroundImage:
      //   'url(https://mdn.alipayobjects.com/huamei_qa8qxu/afts/img/A*0Qq0ToQm1rEAAAAAAAAAAAAADmJ7AQ/original)',
      backgroundRepeat: 'no-repeat',
      backgroundSize: 'cover',
      opacity: 0.2,
    },
    // {
    //   type: 'watermark',
    //   text: '知识图谱',
    //   textFontSize: 14,
    //   textFontFamily: 'Microsoft YaHei',
    //   fill: 'rgba(0, 0, 0, 0.1)',
    //   rotate: Math.PI / 12,
    // },
    {
      type: 'snapline',
      key: 'snapline',
      verticalLineStyle: { stroke: '#F08F56', lineWidth: 2 },
      horizontalLineStyle: { stroke: '#17C76F', lineWidth: 2 },
      autoSnap: false,
    },
    {
      type: 'contextmenu',
      trigger: 'contextmenu', // 'click' or 'contextmenu'
      onRightClick: (v) => {
        alert('You have clicked the「' + v + '」item');
      },
      getItems: () => {
        return [
          { name: '展开一度关系', value: 'spread' },
          { name: '查看详情', value: 'detail' },
        ];
      },
      enable: (e) => e.targetType === 'node',
    },
    {
      type: 'tooltip',
      trigger: 'hover',
      getContent: (e, items) => {
        let result = `<h4>Custom Content</h4>`;
        items.forEach((item) => {
          result += `<p>Type: ${item.data.description}</p>`;
        });
        return result;
      },
    },
    {
      type: 'toolbar',
      position: 'top-left',
      onClick: (item) => {
      switch (item) {
        // —————— 缩放相关 ——————
        case 'zoom-in':
          graph.zoomBy(1.2);
          break;
        case 'zoom-out':
          graph.zoomBy(1 / 1.2);
          break;
        case 'reset':
          graph.fitView(); 
          break;


      default:
        alert('item clicked:' + item);
    }
      },
      getItems: () => {
        // G6 内置了 9 个 icon，分别是 zoom-in、zoom-out、redo、undo、edit、delete、auto-fit、export、reset
        return [
          { id: 'zoom-in', value: 'zoom-in' },
          { id: 'zoom-out', value: 'zoom-out' },
          { id: 'redo', value: 'redo' },
          { id: 'undo', value: 'undo' },
          { id: 'edit', value: 'edit' },
          { id: 'delete', value: 'delete' },
          { id: 'auto-fit', value: 'auto-fit' },
          { id: 'export', value: 'export' },
          { id: 'reset', value: 'reset' },
        ];
      },
    },
  ],
  });

  graph.render();
};
const handleResize = () => {
  if (graph) {
    const container = document.getElementById('container');
    graph.setSize(container.scrollWidth, container.scrollHeight || 500);
  }
};

onMounted(() => {
  initGraph();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (graph) {
    graph.destroy();
    graph = null;
  }
  window.removeEventListener('resize', handleResize);
});

// 如果 graphData 是响应式的（比如从 props 或 API 获取），可以 watch 它
watch(graphData, () => {
  if (graph) {
    graph.changeData(graphData.value);
  }
});
</script>

<style scoped>
.graph-container {
  width: 100%;
  height: 90vh;
  border: 1px solid #eee;
  background-color: #fafafa;
}
</style>