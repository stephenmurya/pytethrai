<template>
  <div class="relative">
    <button 
      @click="isOpen = !isOpen"
      class="flex items-center gap-2 hover:bg-zinc-800 rounded-lg p-2 transition w-full text-left group"
    >
      <div class="w-8 h-8 flex flex-shrink-0 items-center justify-center bg-indigo-600 rounded-lg text-white font-bold text-sm">
        {{ currentWorkspace ? currentWorkspace.name.substring(0, 2).toUpperCase() : 'P' }}
      </div>
      <div class="flex-1 min-w-0">
        <div class="font-semibold text-sm truncate">
            {{ currentWorkspace ? currentWorkspace.name : 'Personal View' }}
        </div>
        <div class="text-[10px] text-zinc-500 group-hover:text-zinc-400">
            {{ currentWorkspace ? 'Workspace' : 'Private' }}
        </div>
      </div>
      <ChevronDown :size="14" class="text-zinc-500" />
    </button>

    <!-- Dropdown -->
    <div 
      v-if="isOpen"
      class="absolute top-full left-0 w-64 mt-2 bg-[#1a1a1a] border border-zinc-700 rounded-xl shadow-xl z-50 overflow-hidden transform"
    >
      <!-- Workspaces List -->
      <div class="py-1 max-h-60 overflow-y-auto">
        <button 
          @click="select(null)"
          class="w-full flex items-center gap-3 px-4 py-2 hover:bg-zinc-800 transition"
        >
            <div class="w-6 h-6 rounded bg-zinc-700 flex items-center justify-center text-xs">P</div>
            <span class="text-sm">Personal View</span>
            <Check v-if="!currentWorkspace" :size="14" class="ml-auto text-indigo-400" />
        </button>

         <div v-if="workspaces.length > 0" class="border-t border-zinc-700/50 my-1"></div>

        <button 
          v-for="ws in workspaces" 
          :key="ws.id"
          @click="select(ws)"
          class="w-full flex items-center gap-3 px-4 py-2 hover:bg-zinc-800 transition"
        >
           <div class="w-6 h-6 rounded bg-indigo-900/50 text-indigo-400 flex items-center justify-center text-[10px] font-bold">
               {{ ws.name.substring(0, 2).toUpperCase() }}
           </div>
           <span class="text-sm truncate">{{ ws.name }}</span>
           <Check v-if="currentWorkspace?.id === ws.id" :size="14" class="ml-auto text-indigo-400" />
        </button>
      </div>

      <!-- Actions -->
      <div class="border-t border-zinc-700 bg-zinc-800/50 p-1">
        <button 
          @click="showCreateModal = true; isOpen = false"
          class="w-full flex items-center gap-2 px-3 py-2 text-xs text-zinc-400 hover:text-white hover:bg-zinc-700/50 rounded transition"
        >
          <Plus :size="14" />
          Create New Workspace
        </button>
        <button 
           @click="showJoinModal = true; isOpen = false"
           class="w-full flex items-center gap-2 px-3 py-2 text-xs text-zinc-400 hover:text-white hover:bg-zinc-700/50 rounded transition"
        >
          <Link :size="14" />
          Join Workspace
        </button>
        <button 
           v-if="currentWorkspace"
           @click="showInviteModal = true; isOpen = false"
           class="w-full flex items-center gap-2 px-3 py-2 text-xs text-zinc-400 hover:text-white hover:bg-zinc-700/50 rounded transition"
        >
          <UserPlus :size="14" />
          Invite Members
        </button>
      </div>
    </div>

    <!-- Backdrop -->
    <div v-if="isOpen" @click="isOpen = false" class="fixed inset-0 z-40"></div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="bg-[#1a1a1a] border border-zinc-700 rounded-xl p-6 w-full max-w-sm shadow-2xl">
            <h3 class="text-lg font-semibold mb-4">Create Workspace</h3>
            <input v-model="newWorkspaceName" placeholder="Workspace Name" class="w-full bg-black/30 border border-zinc-700 rounded p-2 mb-4 text-sm" />
            <div class="flex justify-end gap-2">
                <button @click="showCreateModal = false" class="px-3 py-1.5 text-sm text-zinc-400 hover:text-white">Cancel</button>
                <button @click="handleCreate" class="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded">Create</button>
            </div>
        </div>
    </div>
    
    <!-- Join Modal -->
    <div v-if="showJoinModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="bg-[#1a1a1a] border border-zinc-700 rounded-xl p-6 w-full max-w-sm shadow-2xl">
            <h3 class="text-lg font-semibold mb-4">Join Workspace</h3>
            <p class="text-xs text-zinc-400 mb-4">Paste the invite token provided by your workspace admin.</p>
            <input v-model="inviteToken" placeholder="Invite Token (UUID)" class="w-full bg-black/30 border border-zinc-700 rounded p-2 mb-4 text-sm" />
            <div class="flex justify-end gap-2">
                <button @click="showJoinModal = false" class="px-3 py-1.5 text-sm text-zinc-400 hover:text-white">Cancel</button>
                <button @click="handleJoin" class="px-3 py-1.5 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded">Join</button>
            </div>
        </div>
    </div>

     <!-- Invite Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div class="bg-[#1a1a1a] border border-zinc-700 rounded-xl p-6 w-full max-w-md shadow-2xl">
            <h3 class="text-lg font-semibold mb-2">Invite Members</h3>
            <p class="text-xs text-zinc-400 mb-4">Share this token with users you want to invite to <strong>{{ currentWorkspace?.name }}</strong>.</p>
            
            <div class="bg-black/30 border border-zinc-700 rounded-lg p-3 flex items-center justify-between gap-2 mb-6">
                <code class="text-sm font-mono text-zinc-300 truncate">{{ currentWorkspace?.invite_token }}</code>
                <button 
                  @click="copyInviteToken"
                  class="p-2 hover:bg-zinc-700 rounded text-zinc-400 hover:text-white transition"
                  title="Copy Token"
                >
                    <Copy v-if="!copied" :size="16" />
                    <Check v-else :size="16" class="text-green-500" />
                </button>
            </div>

            <div class="flex justify-end gap-2">
                <button @click="showInviteModal = false" class="px-3 py-1.5 text-sm bg-zinc-700 hover:bg-zinc-600 text-white rounded">Close</button>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useTeamStore, type Workspace } from '../stores/teams';
import { storeToRefs } from 'pinia';
import { ChevronDown, Check, Plus, Link, UserPlus, Copy } from 'lucide-vue-next';

const teamStore = useTeamStore();
const { workspaces, currentWorkspace } = storeToRefs(teamStore);

const isOpen = ref(false);
const showCreateModal = ref(false);
const showJoinModal = ref(false);
const showInviteModal = ref(false);
const copied = ref(false);
const newWorkspaceName = ref("");
const inviteToken = ref("");

const select = (ws: Workspace | null) => {
    teamStore.selectWorkspace(ws);
    isOpen.value = false;
};

const handleCreate = async () => {
    if(!newWorkspaceName.value) return;
    const success = await teamStore.createWorkspace(newWorkspaceName.value);
    if(success) {
        showCreateModal.value = false;
        newWorkspaceName.value = "";
    }
};

const handleJoin = async () => {
     if(!inviteToken.value) return;
     const success = await teamStore.joinWorkspace(inviteToken.value);
     if(success) {
         showJoinModal.value = false;
         inviteToken.value = "";
     } else {
         alert("Invalid token or failed to join.");
     }
}

const copyInviteToken = async () => {
    if (currentWorkspace.value?.invite_token) {
        await navigator.clipboard.writeText(currentWorkspace.value.invite_token);
        copied.value = true;
        setTimeout(() => copied.value = false, 2000);
    }
};

onMounted(() => {
    teamStore.fetchWorkspaces();
});
</script>
