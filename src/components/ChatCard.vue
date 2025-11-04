<!-- ChatCard.vue -->
<template>
  <a-modal
    :open="localOpen"
    :title="`${activeBot.name}（${activeBot.id}）`"
    :width="1200"
    :footer="null"
    :mask-closable="true"
    :keyboard="true"
    centered
    @cancel="handleClose"
    wrap-class-name="chat-modal"
    destroy-on-close
  >
  
    <!-- Prompt 编辑 -->
    <a-textarea
      v-model:value="activeBot.prompt"
      :rows="2"
      placeholder="自定义系统提示词..."
      style="margin-bottom: 12px"
      @change="savePrompt"
    />

    <!-- 聊天内容区域 -->
    <div
      ref="chatContainer"
      class="chat-messages"
    >
      <div
        v-for="(msg, i) in activeBot.messages"
        :key="i + '-' + refreshKey"
        :class="msg.role === 'user' ? 'msg-user' : 'msg-ai'"
      >
        <a-space align="start">
          <a-tag :color="msg.role === 'user' ? 'blue' : 'green'">
            {{ msg.role === 'user' ? '你' : 'AI' }}
          </a-tag>
          <div class="msg-content">
            <p>{{ msg.content }}</p>
          </div>
          <a-button
            v-if="!loading"
            type="text"
            danger
            size="small"
            @click="deleteMessage(i)"
          >
            🗑
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 输入框 -->
    <div style="margin-top: 12px;">
      <a-input-search
        v-model:value="input"
        enter-button="发送"
        placeholder="请输入你的问题..."
        @search="sendMessage"
        :loading="loading"
        ref="inputRef"
      />
    </div>
  </a-modal>
</template>

<script setup>
import { ref, nextTick, watch,defineProps} from 'vue'
import OpenAI from 'openai'
import { useChatStore } from '../stores/useChatStore.js'

// 使用 Store
const store = useChatStore()
const activeBot = store.getActiveBot() // 直接获取当前 bot（确保有默认值）

const input = ref('')
const loading = ref(false)

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})

// 控制模态框显示（双向绑定）
const localOpen = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  localOpen.value = val
})



// 关闭处理
const handleClose = () => {
  localOpen.value = false
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const container = chatContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

// Refs
const chatContainer = ref(null)
const inputRef = ref(null)
const refreshKey = ref(0)

// 聚焦输入框
watch(localOpen, (newVal) => {
  if (newVal) {
    nextTick(() => {
      inputRef.value?.focus()
    })
    scrollToBottom()
  }
}, { immediate: true })

// 保存 Prompt
const savePrompt = () => {
  store.updatePrompt(activeBot.id, activeBot.prompt)
}

// 删除消息
const deleteMessage = (index) => {
  store.deleteMessage(activeBot.id, index)
  refreshKey.value++
}

// 初始化 OpenAI
const openai = new OpenAI({
  apiKey: "sk-a8ca287e30304c23803c3910fffc76d2",
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  dangerouslyAllowBrowser: true,
})

// 发送消息
async function sendMessage() {
  if (!input.value.trim() || loading.value) return

  const userMsg = { role: "user", content: input.value }
  store.addMessage(activeBot.id, userMsg)
  input.value = ""
  loading.value = true

  // 构造上下文
  const messages = [
    { role: "system", content: activeBot.prompt },
    ...activeBot.messages
  ]

  try {
    const stream = await openai.chat.completions.create({
      model: "qwen-plus",
      messages,
      stream: true,
    })

    // 添加 AI 消息占位
    const aiMsg = { role: "assistant", content: "" }
    store.addMessage(activeBot.id, aiMsg)

    // 流式输出
    for await (const chunk of stream) {
      const delta = chunk.choices?.[0]?.delta?.content
      if (delta) {
        aiMsg.content += delta
        refreshKey.value++ // 强制刷新
        await nextTick()
      }
    }
  } catch (err) {
    console.error("API Error:", err)
    store.addMessage(activeBot.id, {
      role: "assistant",
      content: "抱歉，AI 服务暂时不可用，请稍后再试。"
    })
  } finally {
    loading.value = false
    store.saveAll() // 保存到 localStorage
    scrollToBottom()
  }
}
</script>

<style scoped>
.chat-messages {
  height: 800px;
  width: 100%;
  overflow-y: auto;
  border: 1px solid #eee;
  padding: 12px;
  margin-bottom: 16px;
  background-color: #fafafa;
  border-radius: 6px;
}

.msg-user {
  text-align: right;
  margin-bottom: 12px;
}

.msg-ai {
  text-align: left;
  margin-bottom: 12px;
}

.msg-content {
  max-width: 100%;
  display: inline-block;
  text-align: left;
  word-break: break-word;
}

.msg-content p {
  margin: 0;
  white-space: pre-wrap;
}
</style>

<style>
.chat-modal .ant-modal-body {
  padding: 20px;
}
</style>