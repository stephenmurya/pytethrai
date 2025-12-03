<template>
  <div class="relative">
    <!-- Error Banner -->
    <div 
      v-if="modelsError" 
      class="mb-2 px-3 py-2 bg-amber-900/30 border border-amber-700 rounded-lg flex items-center justify-between text-xs"
    >
      <div class="flex items-center gap-2">
        <AlertCircle :size="14" class="text-amber-400" />
        <span class="text-amber-200">{{ modelsError }}</span>
      </div>
      <button 
        @click="handleRetry"
        class="text-amber-400 hover:text-amber-200 font-medium transition"
      >
        Retry
      </button>
    </div>

    <!-- Model Selector Button -->
    <button 
      @click="toggleDropdown"
      :disabled="isLoadingModels"
      class="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-zinc-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <Circle :size="14" v-if="isLoadingModels" class="animate-spin" />
      <Sparkles :size="14" v-else />
      <span>{{ displayModelName }}</span>
      <ChevronDown :size="12" :class="['transition-transform', isOpen ? 'rotate-180' : '']" />
    </button>

    <!-- Dropdown Menu -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div 
        v-if="isOpen" 
        class="absolute bottom-full left-0 mb-2 w-[420px] bg-[#171717] border border-zinc-800 rounded-xl shadow-2xl overflow-hidden z-50"
      >
        <!-- Search Bar -->
        <div class="p-3 border-b border-zinc-800">
          <input 
            v-model="searchQuery"
            type="text"
            placeholder="Search models..."
            class="w-full px-3 py-2 bg-[#2a2a2a] text-white text-sm rounded-lg border border-zinc-700 focus:border-zinc-600 focus:outline-none placeholder-zinc-500"
          />
        </div>

        <!-- Models List -->
        <div class="max-h-96 overflow-y-auto">
          <button
            v-for="model in filteredModels"
            :key="model.id"
            @click="selectModel(model.id)"
            class="w-full px-4 py-3 hover:bg-zinc-800/50 transition text-left flex items-start gap-3 group"
          >
            <!-- Checkmark -->
            <div class="pt-0.5 flex-shrink-0">
              <Check 
                :size="16" 
                :class="[
                  'transition',
                  selectedModel === model.id ? 'text-white opacity-100' : 'text-transparent opacity-0 group-hover:opacity-30'
                ]"
              />
            </div>

            <!-- Model Info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-0.5">
                <h3 class="font-semibold text-white text-sm">{{ model.name }}</h3>
              </div>
              <p class="text-xs text-zinc-400 line-clamp-1">{{ model.description }}</p>
            </div>

            <!-- Capability Icons -->
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <Home 
                v-if="model.capabilities.vision" 
                :size="14" 
                class="text-zinc-400"
                title="Vision support"
              />
              <Zap 
                v-if="model.capabilities.fast" 
                :size="14" 
                class="text-zinc-400"
                title="Fast model"
              />
              <Code 
                v-if="model.capabilities.code" 
                :size="14" 
                class="text-zinc-400"
                title="Code support"
              />
              <Moon 
                v-if="model.capabilities.free" 
                :size="14" 
                class="text-zinc-400"
                title="Free tier"
              />
            </div>
          </button>

          <!-- Empty State -->
          <div 
            v-if="filteredModels.length === 0" 
            class="px-4 py-8 text-center text-zinc-500 text-sm"
          >
            No models found
          </div>
        </div>
      </div>
    </Transition>

    <!-- Click Outside Handler -->
    <div 
      v-if="isOpen" 
      @click="closeDropdown"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useChatStore } from '../stores/chat';
import { 
  Check, 
  ChevronDown, 
  Home, 
  Zap, 
  Code, 
  Moon, 
  AlertCircle,
  Sparkles,
  Circle
} from 'lucide-vue-next';

const chatStore = useChatStore();
const { availableModels, selectedModel, modelsError, isLoadingModels } = storeToRefs(chatStore);

const isOpen = ref(false);
const searchQuery = ref('');

const displayModelName = computed(() => {
  if (isLoadingModels.value) return 'Loading models...';
  
  const selected = availableModels.value.find(m => m.id === selectedModel.value);
  return selected?.name || 'Select model';
});

const filteredModels = computed(() => {
  if (!searchQuery.value) return availableModels.value;
  
  const query = searchQuery.value.toLowerCase();
  return availableModels.value.filter(model => 
    model.name.toLowerCase().includes(query) || 
    model.description.toLowerCase().includes(query) ||
    model.id.toLowerCase().includes(query)
  );
});

const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

const closeDropdown = () => {
  isOpen.value = false;
  searchQuery.value = '';
};

const selectModel = (modelId: string) => {
  chatStore.setSelectedModel(modelId);
  closeDropdown();
};

const handleRetry = () => {
  chatStore.retryFetchModels();
};

onMounted(() => {
  // Fetch models when component mounts
  chatStore.fetchModels();
});
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

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-clamp: 1;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
