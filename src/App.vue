<template>
  <a-layout style="min-height: 100vh">
    <!-- 头部 -->
    <a-layout-header style="background: #fff; padding: 0 8px;">
      <AppHeader />
    </a-layout-header>

    <!-- 主内容区：只放图谱/文档 -->
    <a-layout-content style="padding: 8px; height: calc(100vh - 64px - 16px);">
      <GraphPanel />
    </a-layout-content>

    <!-- 悬浮按钮：打开聊天 -->
    <a-float-button
      @click="showChatModal = true"
      icon="message"
      type="primary"
      style="left: 24px; bottom: 24px; z-index: 1000;"
    />

    <!-- 聊天模态框 -->
    <a-modal
      v-model:open="showChatModal"
      title="知识问答"
      :width="1024"
      :footer="null"
      :mask-closable="true"
      :keyboard="true"
      centered
      destroy-on-close
    >
      <ChatPanel style="height: 500px;" />
    </a-modal>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import GraphPanel from './components/GraphPanel.vue'
import ChatPanel from './components/ChatPanel.vue'

// 控制聊天模态框显示
const showChatModal = ref(false)
</script>

<style>
/* 可选：优化 ChatPanel 在 Modal 中的滚动 */
:deep(.ant-modal-body) {
  padding: 0;
}
</style>