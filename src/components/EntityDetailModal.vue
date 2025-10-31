<template>
  <div>
    <!-- 实体列表（示例：可替换为你的图谱节点点击触发） -->
    <a-space wrap>
      <a-button
        v-for="entity in mockEntities"
        :key="entity.id"
        @click="openModal(entity)"
      >
        {{ entity.name }}
      </a-button>
    </a-space>

    <!-- 弹窗：左上角固定位置的大框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="null"
      :footer="null"
      :closable="true"
      width="800px"
      :body-style="{ padding: '0' }"
      :mask-closable="true"
      wrap-class-name="entity-detail-modal"
      @cancel="modalVisible = false"
    >
      <!-- 顶部：实体信息 -->
      <div class="entity-header">
        <h2>{{ currentEntity?.name || '实体详情' }}</h2>
        <a-descriptions size="small" :column="2" bordered>
          <a-descriptions-item
            v-for="(value, key) in currentEntity?.attributes"
            :key="key"
            :label="key"
          >
            {{ value }}
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <!-- 底部：表格 -->
      <a-table
        :columns="columns"
        :data-source="tableData"
        :pagination="false"
        size="small"
        style="margin-top: 16px"
      />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

// 模拟实体数据（实际中可能来自图谱点击事件）
const mockEntities = [
  {
    id: 'e1',
    name: '张三',
    attributes: {
      年龄: 28,
      职业: '工程师',
      城市: '北京',
      部门: '技术部',
    },
    tableData: [
      { id: '1', content: '完成项目A' },
      { id: '2', content: '修复系统漏洞' },
    ],
  },
  {
    id: 'e2',
    name: '李四',
    attributes: {
      年龄: 35,
      职业: '产品经理',
      城市: '上海',
      部门: '产品部',
    },
    tableData: [
      { id: '1', content: '需求评审' },
      { id: '2', content: '用户调研' },
      { id: '3', content: 'PRD撰写' },
    ],
  },
];

const modalVisible = ref(false);
const currentEntity = ref(null);

const openModal = (entity) => {
  currentEntity.value = entity;
  modalVisible.value = true;
};

// 表格列定义
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '内容', dataIndex: 'content', key: 'content' },
];

// 表格数据（从当前实体中取）
const tableData = computed(() => {
  return currentEntity.value?.tableData || [];
});
</script>

<style scoped>
/* 弹窗左上角定位 */
:deep(.entity-detail-modal .ant-modal) {
  position: fixed;
  top: 20px;
  left: 20px;
  padding: 0;
  margin: 0;
  max-width: calc(100% - 40px);
}

.entity-header {
  padding: 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #eee;
}

.entity-header h2 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #1d39c4;
}
</style>