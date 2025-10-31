import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const bots = ref([
    { id: 'bot1', name: '心理导师', prompt: '你是一位专业心理咨询师。', messages: [] },
    { id: 'bot2', name: '编程助手', prompt: '你是一个专业的前端开发顾问。', messages: [] },
    { id: 'bot3', name: '绘图助理', prompt: '你可以帮我生成创意绘图提示。', messages: [] },
    { id: 'bot4', name: '写作导师', prompt: '你是一位严谨的写作润色专家。', messages: [] },
  ])

  const activeBotId = ref('bot1')
  const getActiveBot = () => bots.value.find(b => b.id === activeBotId.value)

  function switchBot(id) {
    activeBotId.value = id
  }

  function updatePrompt(id, newPrompt) {
    const bot = bots.value.find(b => b.id === id)
    if (bot) bot.prompt = newPrompt
    saveAll()
  }

  function addMessage(botId, msg) {
    const bot = bots.value.find(b => b.id === botId)
    if (bot) bot.messages.push(msg)
    saveAll()
  }

  function deleteMessage(botId, index) {
    const bot = bots.value.find(b => b.id === botId)
    if (bot) bot.messages.splice(index, 1)
    saveAll()
  }

  // 自动持久化到 localStorage
  function saveAll() {
    localStorage.setItem('chatBots', JSON.stringify(bots.value))
  }
  
  function loadAll() {
    const saved = localStorage.getItem('chatBots')
    if (saved) bots.value = JSON.parse(saved)
  }

  loadAll()

  return { bots, activeBotId, getActiveBot, switchBot, updatePrompt, addMessage, deleteMessage,saveAll }
})
