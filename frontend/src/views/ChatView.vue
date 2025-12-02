<template>
  <div class="flex h-screen bg-background">
    <!-- Sidebar -->
    <div class="w-64 bg-sidebar border-r border-sidebar-border p-4 flex flex-col">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-lg font-bold text-sidebar-foreground">TethrAI</h2>
        <button @click="handleLogout" class="text-sm text-sidebar-foreground/70 hover:text-sidebar-foreground">
          Logout
        </button>
      </div>
      <button
        @click="startNewChat"
        class="mb-4 px-4 py-2 bg-sidebar-primary text-sidebar-primary-foreground rounded-md hover:bg-sidebar-primary/90 transition"
      >
        + New Chat
      </button>
      <div class="flex-1 overflow-y-auto">
        <div v-for="chat in chatHistory" :key="chat.id" class="mb-2">
          <button
            @click="loadChat(chat.id)"
            class="w-full text-left px-3 py-2 rounded-md text-sm text-sidebar-foreground hover:bg-sidebar-accent transition"
            :class="{ 'bg-sidebar-accent': currentChat?.id === chat.id }"
          >
            {{ chat.title || 'Untitled Chat' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col">
      <!-- Messages -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4">
        <div v-if="!currentChat || currentChat.messages.length === 0" class="text-center text-muted-foreground mt-20">
          <h1 class="text-4xl font-bold mb-4">Welcome to TethrAI</h1>
          <p>Start a conversation by typing a message below.</p>
        </div>
        <div v-for="message in currentChat?.messages" :key="message.id" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
          <div
            class="max-w-[70%] px-4 py-3 rounded-lg"
            :class="message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted text-foreground'"
          >
            <div class="whitespace-pre-wrap">{{ message.content }}</div>
          </div>
        </div>
        <div v-if="streamingMessage" class="flex justify-start">
          <div class="max-w-[70%] px-4 py-3 rounded-lg bg-muted text-foreground">
            <div class="whitespace-pre-wrap">{{ streamingMessage }}</div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="p-4 border-t border-border">
        <form @submit.prevent="handleSendMessage" class="flex gap-2">
          <input
            v-model="messageInput"
            type="text"
            placeholder="Type a message..."
            class="flex-1 px-4 py-2 bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            :disabled="isStreaming"
          />
          <button
            type="submit"
            class="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition disabled:opacity-50"
            :disabled="isStreaming || !messageInput.trim()"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const chatStore = useChatStore()
const router = useRouter()

const { currentChat, chatHistory, isStreaming } = storeToRefs(chatStore)

const messageInput = ref('')
const streamingMessage = ref('')

onMounted(async () => {
  await chatStore.getChatHistory()
})

async function handleSendMessage() {
  if (!messageInput.value.trim()) return

  const content = messageInput.value
  messageInput.value = ''

  // Note: This is a simplified implementation
  // In a real app, you'd need to handle streaming properly
  streamingMessage.value = 'Thinking...'
  const response = await chatStore.sendMessage(content, currentChat.value?.id)
  streamingMessage.value = response || 'Error'
  
  // Reload chat history after sending
  setTimeout(async () => {
    await chatStore.getChatHistory()
    streamingMessage.value = ''
  }, 1000)
}

function startNewChat() {
  chatStore.clearCurrentChat()
}

async function loadChat(chatId: string) {
  await chatStore.loadChat(chatId)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>
