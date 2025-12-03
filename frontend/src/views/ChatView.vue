<template>
  <div class="flex h-screen w-full bg-[#0a0a0a] text-white font-sans overflow-hidden">
    
    <!-- Sidebar -->
    <aside 
      v-show="isSidebarOpen"
      class="flex flex-col w-64 bg-[#1a1a1a] border-r border-zinc-800/50 flex-shrink-0 transition-all duration-300"
    >
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded-full bg-white flex items-center justify-center">
            <span class="text-black text-xs font-bold">T</span>
          </div>
          <span class="font-semibold">Tethr AI</span>
        </div>
        <div class="flex gap-1">
          <button class="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"/><rect width="7" height="7" x="14" y="3" rx="1"/><rect width="7" height="7" x="14" y="14" rx="1"/><rect width="7" height="7" x="3" y="14" rx="1"/></svg>
          </button>
          <button @click="startNewChat" class="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          </button>
          <button class="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>
          </button>
          <button class="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
          </button>
        </div>
      </div>

      <!-- Chat History -->
      <div class="flex-1 overflow-y-auto px-3 py-2">
        <div class="text-xs text-zinc-500 mb-2 px-2">Last 7 days</div>
        <ul>
          <li 
            v-for="chat in chatHistory" 
            :key="chat.id"
            @click="loadChat(chat.id)"
            :class="[
              'px-3 py-2 text-sm hover:bg-zinc-800 rounded cursor-pointer truncate transition mb-1',
              currentChat?.id === chat.id ? 'bg-zinc-800 text-white' : 'text-zinc-400'
            ]"
          >
            {{ chat.title || 'Untitled Chat' }}
          </li>
          <li v-if="chatHistory.length === 0" class="px-3 py-2 text-xs text-zinc-500 mt-2">
            You have reached the end of your chat history.
          </li>
        </ul>
      </div>

      <!-- Guest Account Card -->
      <div class="p-3 border-t border-zinc-800">
        <div class="bg-[#2a2a2a] rounded-lg p-4 mb-3">
          <h3 class="font-semibold text-sm mb-1">Guest Account</h3>
          <p class="text-xs text-zinc-400 mb-3">Limited to 2 messages. Sign up for unlimited access.</p>
          <div class="flex gap-2">
            <button class="flex-1 bg-white text-black text-xs font-semibold py-2 rounded hover:bg-zinc-200 transition">Sign up</button>
            <button class="flex-1 bg-transparent border border-zinc-600 text-white text-xs font-semibold py-2 rounded hover:bg-zinc-800 transition">Sign in</button>
          </div>
        </div>

        <!-- User Profile -->
        <button @click="handleLogout" class="w-full flex items-center justify-between p-2 hover:bg-zinc-800 rounded transition group">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 bg-zinc-700 rounded flex items-center justify-center text-xs">
              {{ user?.username?.charAt(0).toUpperCase() || 'G' }}
            </div>
            <span class="text-sm">{{ user?.username || 'Guest' }}</span>
          </div>
          <svg class="text-zinc-500 group-hover:text-zinc-300" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col relative bg-[#0a0a0a]">
      
      <!-- Top Bar -->
      <header class="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <div class="flex items-center gap-2">
          <button @click="toggleSidebar" class="p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white rounded transition">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/></svg>
          </button>
        </div>
        <div class="absolute left-1/2 transform -translate-x-1/2">
          <span class="text-sm text-zinc-400">{{ currentChat?.title || 'New Chat' }}</span>
        </div>
        <button class="p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white rounded transition">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>
        </button>
      </header>

      <!-- Messages Area -->
      <div class="flex-1 flex flex-col items-center justify-center px-4 overflow-y-auto">
        <!-- Empty State -->
        <div v-if="!currentChat || currentChat.messages.length === 0" class="max-w-3xl w-full">
          <div class="text-center mb-8">
            <h1 class="text-3xl font-semibold mb-2">Hello there!</h1>
            <p class="text-zinc-500 text-lg">How can I help you today?</p>
          </div>

          <!-- Suggestion Chips -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
            <button 
              v-for="chip in suggestionChips" 
              :key="chip.id"
              @click="userInput = chip.text"
              class="text-left p-4 rounded-xl border border-zinc-700 bg-[#2a2a2a] hover:bg-[#333] text-sm transition"
            >
              {{ chip.text }}
            </button>
          </div>
        </div>

        <!-- Chat Messages -->
        <div v-else class="max-w-4xl w-full space-y-4 py-8 px-4">
          <div v-for="message in currentChat.messages" :key="message.id">
            <!-- User Message (Right-aligned) -->
            <div v-if="message.role === 'user'" class="flex justify-end items-start gap-2">
              <div class="bg-blue-600 text-white rounded-3xl px-4 py-2.5 max-w-[80%]">
                {{ message.content }}
              </div>
              <button 
                @click="handleCopy(message.content)"
                class="p-1.5 text-zinc-500 hover:text-zinc-300 transition opacity-0 group-hover:opacity-100"
                title="Copy"
              >
                <Copy :size="14" />
              </button>
            </div>

            <!-- AI Message (Left-aligned) -->
            <div v-else class="flex items-start gap-3 group">
              <div class="flex-shrink-0 pt-1">
                <Sparkles :size="18" class="text-zinc-400" />
              </div>
              <div class="flex-1 min-w-0">
                <div 
                  class="text-zinc-100 mb-2 prose prose-invert prose-sm max-w-none break-words prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent prose-headings:font-semibold prose-a:text-blue-400 hover:prose-a:text-blue-300 prose-ul:my-2 prose-li:my-0.5" 
                  v-html="renderMarkdown(message.content)"
                ></div>
                <div class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    @click="handleCopy(message.content)"
                    class="p-1.5 text-zinc-500 hover:text-zinc-300 transition rounded"
                    title="Copy"
                  >
                    <Copy :size="16" />
                  </button>
                  <button 
                    @click="handleVote(message.id, 'up')"
                    :class="[
                      'p-1.5 transition rounded',
                      messageVotes[message.id] === 'up' 
                        ? 'text-blue-500 bg-blue-500/10' 
                        : 'text-zinc-500 hover:text-zinc-300'
                    ]"
                    title="Good response"
                  >
                    <ThumbsUp :size="16" />
                  </button>
                  <button 
                    @click="handleVote(message.id, 'down')"
                    :class="[
                      'p-1.5 transition rounded',
                      messageVotes[message.id] === 'down' 
                        ? 'text-red-500 bg-red-500/10' 
                        : 'text-zinc-500 hover:text-zinc-300'
                    ]"
                    title="Bad response"
                  >
                    <ThumbsDown :size="16" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Streaming Message -->
          <div v-if="streamingMessage" class="flex items-start gap-3">
            <div class="flex-shrink-0 pt-1">
              <Sparkles :size="18" class="text-zinc-400" />
            </div>
            <div class="flex-1 min-w-0">
              <div 
                class="text-zinc-100 prose prose-invert prose-sm max-w-none break-words prose-p:leading-relaxed prose-pre:p-0 prose-pre:bg-transparent prose-headings:font-semibold prose-a:text-blue-400 hover:prose-a:text-blue-300 prose-ul:my-2 prose-li:my-0.5" 
                v-html="renderMarkdown(streamingMessage)"
              ></div>
              <div class="inline-block w-1.5 h-4 bg-zinc-400 ml-1 animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t border-zinc-800 p-4">
        <div class="max-w-4xl mx-auto">
          <div class="relative bg-[#1a1a1a] rounded-2xl border border-zinc-700/50 focus-within:border-zinc-600/50 shadow-lg">
            <div class="flex items-center gap-2 px-4 py-3">
              <textarea 
                v-model="userInput"
                placeholder="Send a message..." 
                class="flex-1 bg-transparent text-white placeholder-zinc-500 resize-none outline-none max-h-32 text-[15px]"
                rows="1"
                @keydown.enter.exact.prevent="handleSendMessage"
                :disabled="isStreaming"
              ></textarea>

              <button 
                @click="handleSendMessage"
                :disabled="!userInput.trim() || isStreaming"
                :class="[
                  'p-2.5 rounded-full transition flex items-center justify-center',
                  userInput.trim() && !isStreaming 
                    ? 'bg-white text-black hover:bg-zinc-200' 
                    : 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
                ]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="m22 2-7 20-4-9-9-4 20-7z"/></svg>
              </button>
            </div>

            <!-- Model Selector -->
            <div class="px-4 pb-3 pt-2 border-t border-zinc-800/30">
              <ModelSelector />
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from "pinia";
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { useChatStore } from "../stores/chat";
import ModelSelector from "../components/ModelSelector.vue";
import { Copy, ThumbsUp, ThumbsDown, Sparkles } from 'lucide-vue-next';
import { Marked } from 'marked';
import { markedHighlight } from "marked-highlight";
import hljs from 'highlight.js';
import 'highlight.js/styles/github-dark.css';

const authStore = useAuthStore();
const chatStore = useChatStore();
const router = useRouter();

const { user } = storeToRefs(authStore);
const { currentChat, chatHistory, isStreaming, messageVotes } = storeToRefs(chatStore);

const userInput = ref("");
const streamingMessage = ref("");
const isSidebarOpen = ref(true);
const copySuccess = ref(false);

// Configure marked with syntax highlighting
const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    }
  })
);

marked.setOptions({
  breaks: true,
  gfm: true,
});

const renderMarkdown = (content: string) => {
  return marked.parse(content) as string;
};

const handleCopy = async (content: string) => {
  const success = await chatStore.copyToClipboard(content);
  if (success) {
    copySuccess.value = true;
    setTimeout(() => {
      copySuccess.value = false;
    }, 2000);
  }
};

const handleVote = (messageId: string, vote: 'up' | 'down') => {
  chatStore.voteMessage(messageId, vote);
};

const suggestionChips = [
	{ id: 1, text: "What are the advantages of using Next.js?" },
	{ id: 2, text: "Write code to demonstrate Dijkstra's algorithm" },
	{ id: 3, text: "Help me write an essay about Silicon Valley" },
	{ id: 4, text: "What is the weather in San Francisco?" },
];

onMounted(async () => {
	await chatStore.getChatHistory();
});

const toggleSidebar = () => {
	isSidebarOpen.value = !isSidebarOpen.value;
};

const startNewChat = () => {
	chatStore.clearCurrentChat();
};

const loadChat = async (chatId: string) => {
	await chatStore.loadChat(chatId);
};

const handleSendMessage = async () => {
	if (!userInput.value.trim() || isStreaming.value) return;

	const content = userInput.value;
	userInput.value = "";

	streamingMessage.value = "Thinking...";
	const response = await chatStore.sendMessage(content, currentChat.value?.id);
	streamingMessage.value = response || "Error";

	setTimeout(async () => {
		await chatStore.getChatHistory();
		streamingMessage.value = "";
	}, 1000);
};

const handleLogout = async () => {
	await authStore.logout();
	router.push("/login");
};
</script>

<style scoped>
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #3f3f46;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #52525b;
}
</style>
