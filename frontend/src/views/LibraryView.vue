<template>
  <div class="flex h-screen w-full bg-[#0a0a0a] text-white font-sans overflow-hidden">
    <!-- Main Content -->
    <main class="flex-1 flex flex-col relative bg-[#0a0a0a] max-w-7xl mx-auto w-full">
      
      <!-- Top Bar -->
      <header class="flex flex-col gap-4 px-8 py-6 border-b border-zinc-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <router-link to="/" class="p-2 -ml-2 text-zinc-400 hover:text-white hover:bg-zinc-800 rounded transition">
              <ArrowLeft :size="20" />
            </router-link>
            <h1 class="text-2xl font-semibold">Knowledge Base</h1>
          </div>
        </div>

        <div class="flex items-center justify-between gap-4">
          <!-- Search -->
          <div class="relative flex-1 max-w-md">
            <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search library..." 
              class="w-full bg-[#1a1a1a] border border-zinc-700/50 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-zinc-500 transition"
            />
          </div>

          <!-- Tabs -->
          <div class="flex bg-[#1a1a1a] p-1 rounded-lg border border-zinc-800">
            <button 
              v-for="tab in tabs" 
              :key="tab.value"
              @click="activeTab = tab.value"
              :class="[
                'px-4 py-1.5 text-sm font-medium rounded-md transition',
                activeTab === tab.value ? 'bg-zinc-700 text-white shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
              ]"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>
      </header>

      <!-- Content Area -->
      <div class="flex-1 overflow-y-auto p-8">
        <div v-if="isLoading" class="flex justify-center py-12">
          <div class="animate-spin h-8 w-8 border-2 border-zinc-600 border-t-white rounded-full"></div>
        </div>

        <div v-else-if="filteredItems.length === 0" class="text-center py-20">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-zinc-800 mb-4">
            <Book :size="32" class="text-zinc-500" />
          </div>
          <h3 class="text-lg font-medium text-white mb-1">No items found</h3>
          <p class="text-zinc-500">Try adjusting your search or filters.</p>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="item in filteredItems" 
            :key="item.id"
            class="group bg-[#1a1a1a] border border-zinc-800 hover:border-zinc-700 rounded-xl p-5 transition flex flex-col h-full"
          >
            <div class="flex items-start justify-between mb-3">
              <div class="flex items-center gap-2">
                 <span :class="[
                   'text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider',
                   item.item_type === 'PROMPT' ? 'bg-blue-500/10 text-blue-400' : 
                   item.item_type === 'TEMPLATE' ? 'bg-purple-500/10 text-purple-400' : 'bg-green-500/10 text-green-400'
                 ]">
                   {{ item.item_type }}
                 </span>
                 <span class="text-xs text-zinc-500">{{ formatDate(item.created_at) }}</span>
              </div>
              <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                <button @click="editItem(item)" class="p-1.5 text-zinc-500 hover:text-white hover:bg-zinc-700 rounded" title="Edit">
                  <SquarePen :size="14" />
                </button>
                <button @click="copyItem(item.content)" class="p-1.5 text-zinc-500 hover:text-white hover:bg-zinc-700 rounded" title="Copy">
                  <Copy :size="14" />
                </button>
                <button @click="deleteItem(item.id)" class="p-1.5 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded" title="Delete">
                  <Trash2 :size="14" />
                </button>
              </div>
            </div>

            <h3 class="font-semibold text-lg mb-2 line-clamp-1" :title="item.title">{{ item.title }}</h3>
            
            <p class="text-sm text-zinc-400 line-clamp-4 mb-4 flex-1 font-mono bg-zinc-900/50 p-3 rounded-lg">
              {{ item.content }}
            </p>

            <button 
              @click="useItem(item)"
              class="w-full flex items-center justify-center gap-2 bg-zinc-800 hover:bg-zinc-700 text-white text-sm font-medium py-2.5 rounded-lg transition"
            >
              <Play :size="14" />
              Use Prompt
            </button>
          </div>
        </div>
      </div>
    </main>
    
    <EditLibraryItemModal 
        :item="editingItem" 
        :is-open="!!editingItem" 
        @close="editingItem = null" 
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useLibraryStore, type LibraryItem } from '../stores/library';
import { useTeamStore } from '../stores/teams';
import { Search, ArrowLeft, Trash2, Copy, Play, Book, SquarePen } from 'lucide-vue-next';
import EditLibraryItemModal from '../components/EditLibraryItemModal.vue';

const router = useRouter();
const libraryStore = useLibraryStore();
const teamStore = useTeamStore();
const { filteredItems, isLoading, searchQuery, activeTab } = storeToRefs(libraryStore);
const { currentWorkspace } = storeToRefs(teamStore);

const editingItem = ref<LibraryItem | null>(null);

const tabs = [
  { label: 'All', value: 'ALL' },
  { label: 'Prompts', value: 'PROMPT' },
  { label: 'Templates', value: 'TEMPLATE' },
] as const;

onMounted(() => {
  libraryStore.fetchItems();
});

// Refetch when workspace changes
watch(currentWorkspace, () => {
    libraryStore.fetchItems();
});

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

const copyItem = async (content: string) => {
  await navigator.clipboard.writeText(content);
  // Optional: show toast
};

const deleteItem = async (id: number) => {
  if (confirm('Are you sure you want to delete this item?')) {
    await libraryStore.deleteItem(id);
  }
};

const editItem = (item: LibraryItem) => {
    editingItem.value = item;
};


const useItem = (item: LibraryItem) => {
  // Navigate to chat and pre-fill
  router.push({
    name: 'chat',
    query: { prompt: item.content }
  });
};
</script>
