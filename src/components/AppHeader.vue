<template>
  <div style="display: flex; justify-content: space-between; align-items: center; padding: 0 16px;">
    <!-- 左侧标题 -->
    <div style="font-size: 18px; font-weight: bold;">My Vue App</div>

    <!-- 右侧菜单区 -->
    <div style="display: flex; align-items: center; gap: 16px;">
      <!-- 水平菜单 -->
      <a-menu
        v-model:selectedKeys="current"
        mode="horizontal"
        :items="items"
        style="border-bottom: none;"
      />

      <!-- 用户头像菜单 -->
      <a-dropdown>
        <template #content>
          <a-menu>
            <a-menu-item key="1">个人中心</a-menu-item>
            <a-menu-item key="2">退出登录</a-menu-item>
          </a-menu>
        </template>
        <a-avatar style="background-color: #87d068; cursor: pointer;">U</a-avatar>
      </a-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '@/stores/useChatStore'

const store = useChatStore()
const current = ref(['botMenu'])

// 当前机器人名称
const currentBotName = computed(() => {
  const bot = store.bots.find(b => b.id === store.activeBotId)
  return bot ? bot.name : '选择机器人'
})

// 菜单项配置
const items = computed(() => [
  {
    key: 'botMenu',
    label: `🤖 ${currentBotName.value}`,
    children: store.bots.map(bot => ({
      key: `bot-${bot.id}`,
      label: `🤖 ${bot.name}`,
      onClick: () => store.switchBot(bot.id)
    }))
  },
  {
    key: 'docs',
    label: '📄 文档中心',
    onClick: () => console.log('跳转到文档中心')
  },
  {
    key: 'about',
    label: 'ℹ️ 关于',
    onClick: () => console.log('跳转到关于页面')
  }
])
</script>
