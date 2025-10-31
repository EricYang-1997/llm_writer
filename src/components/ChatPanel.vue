<!-- ChatCard.vue -->
<template>
  <a-modal
    v-model:open="visible"
    :title="`${activeBot.name}（${activeBot.id}）`"
    :width="600"
    :footer="null"
    :mask-closable="false"
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
import { ref, computed, nextTick, watch,defineProps,defineEmits  } from "vue"
import OpenAI from "openai"
import { useChatStore } from '../stores/useChatStore.js'

const store = useChatStore()
const activeBot = computed(() => store.getActiveBot())

const input = ref("")
const loading = ref(false)
const refreshKey = ref(0)
// Props: 接收外部传入的 bot 数据和控制显示
const props = defineProps({
  modelValue: { type: Boolean, default: false }, // v-model:open
  bot: { type: Object, required: true }
})

const emit = defineEmits(['update:modelValue', 'save-prompt', 'send-message', 'delete-message'])

// 内部状态
const visible = ref(props.modelValue)

// refs
const chatContainer = ref(null)
const inputRef = ref(null)

// 同步 visible 状态到父组件
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 关闭模态框
const handleClose = () => {
  visible.value = false
}



// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

// 聚焦输入框
watch(visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      inputRef.value?.focus()
    })
    scrollToBottom()
  }
})

// 初始化 OpenAI（Qwen 模型）
const openai = new OpenAI({
  apiKey: "sk-a8ca287e30304c23803c3910fffc76d2",
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  dangerouslyAllowBrowser: true,
})

// 保存 Prompt
function savePrompt() {
  store.updatePrompt(activeBot.value.id, activeBot.value.prompt)
}

// 删除一条消息
function deleteMessage(index) {
  store.deleteMessage(activeBot.value.id, index)
  refreshKey.value++
}

// 发送消息
async function sendMessage() {
  if (!input.value.trim()) return
  const userMsg = { role: "user", content: input.value }
  store.addMessage(activeBot.value.id, userMsg)
  input.value = ""
  loading.value = true

  const allMessages = [
    { role: "system", content: activeBot.value.prompt },
    ...activeBot.value.messages,
  ]

  const stream = await openai.chat.completions.create({
    model: "qwen-plus",
    messages: allMessages,
    stream: true,
  })

  // 添加 AI 消息占位
  const aiMsg = { role: "assistant", content: "" }
  store.addMessage(activeBot.value.id, aiMsg)

  // 逐字输出流式内容
  for await (const chunk of stream) {
    const delta = chunk.choices?.[0]?.delta?.content
    if (delta) {
      aiMsg.content += delta
      refreshKey.value++ // 强制刷新
      await nextTick()
    }
  }

  // 保存到本地
  store.saveAll()
  loading.value = false
}
</script>

<style scoped>
p {
  margin: 0;
}
</style>
