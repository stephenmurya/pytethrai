import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface Chat {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: Message[]
}

export const useChatStore = defineStore('chat', () => {
  const currentChat = ref<Chat | null>(null)
  const chatHistory = ref<Chat[]>([])
  const isStreaming = ref(false)

  async function sendMessage(content: string, chatId?: string, model: string = 'google/gemini-2.0-flash-exp:free') {
    isStreaming.value = true
    try {
      const response = await axios.post('/api/chat/send/', {
        content,
        chatId,
        model,
      }, {
        responseType: 'text',
      })

      // Response is streaming text
      return response.data
    } catch (error) {
      console.error('Send message failed', error)
      return null
    } finally {
      isStreaming.value = false
    }
  }

  async function getChatHistory() {
    try {
      const response = await axios.get('/api/chat/history/')
      chatHistory.value = response.data
    } catch (error) {
      console.error('Get chat history failed', error)
    }
  }

  async function loadChat(chatId: string) {
    try {
      const response = await axios.get(`/api/chat/${chatId}/`)
      currentChat.value = response.data
    } catch (error) {
      console.error('Load chat failed', error)
    }
  }

  function clearCurrentChat() {
    currentChat.value = null
  }

  return {
    currentChat,
    chatHistory,
    isStreaming,
    sendMessage,
    getChatHistory,
    loadChat,
    clearCurrentChat,
  }
})
