<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="bg-[#1a1a1a] border border-zinc-700 rounded-xl p-6 w-full max-w-lg shadow-2xl flex flex-col max-h-[90vh]">
      <h3 class="text-lg font-semibold mb-4">Edit Item</h3>
      
      <div class="space-y-4 flex-1 overflow-y-auto pr-2">
        <!-- Title -->
        <div>
            <label class="block text-xs text-zinc-400 mb-1">Title</label>
            <input v-model="form.title" class="w-full bg-black/30 border border-zinc-700 rounded p-2 text-sm focus:border-indigo-500 outline-none" />
        </div>

        <!-- Content -->
        <div>
            <label class="block text-xs text-zinc-400 mb-1">Content</label>
            <textarea v-model="form.content" rows="6" class="w-full bg-black/30 border border-zinc-700 rounded p-2 text-sm font-mono focus:border-indigo-500 outline-none"></textarea>
        </div>

        <!-- Visibility (Only if in a workspace) -->
        <div v-if="currentWorkspace">
            <label class="block text-xs text-zinc-400 mb-1">Visibility</label>
            <select v-model="form.visibility" class="w-full bg-black/30 border border-zinc-700 rounded p-2 text-sm focus:border-indigo-500 outline-none">
                <option value="PRIVATE">Private (Only Me)</option>
                <option value="WORKSPACE">Workspace (Everyone in {{ currentWorkspace.name }})</option>
                <option value="SUBTEAM">Sub-team</option>
            </select>
        </div>

        <!-- SubTeam Selector -->
        <div v-if="form.visibility === 'SUBTEAM'">
            <label class="block text-xs text-zinc-400 mb-1">Select Sub-team</label>
            <select v-model="form.subteam" class="w-full bg-black/30 border border-zinc-700 rounded p-2 text-sm focus:border-indigo-500 outline-none">
                <option :value="null" disabled>Select a sub-team</option>
                <option v-for="st in subTeams" :key="st.id" :value="st.id">
                    {{ st.name }}
                </option>
            </select>
            <p v-if="subTeams.length === 0" class="text-xs text-yellow-500 mt-1">No sub-teams found in this workspace.</p>
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-6 pt-4 border-t border-zinc-800">
        <button @click="$emit('close')" class="px-4 py-2 text-sm text-zinc-400 hover:text-white transition">Cancel</button>
        <button @click="handleSave" class="px-4 py-2 text-sm bg-indigo-600 hover:bg-indigo-500 text-white rounded transition">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useTeamStore } from '../stores/teams';
import { useLibraryStore, type LibraryItem } from '../stores/library';
import { storeToRefs } from 'pinia';

const props = defineProps<{
  item: LibraryItem | null;
  isOpen: boolean;
}>();

const emit = defineEmits(['close']);

const teamStore = useTeamStore();
const libraryStore = useLibraryStore();
const { currentWorkspace, subTeams } = storeToRefs(teamStore);

const form = ref({
    title: '',
    content: '',
    visibility: 'PRIVATE' as 'PRIVATE' | 'WORKSPACE' | 'SUBTEAM',
    subteam: null as number | null,
    workspace: null as number | null,
});

// Initialize form when item changes or modal opens
watch(() => props.item, (newItem) => {
    if (newItem) {
        form.value = {
            title: newItem.title,
            content: newItem.content,
            visibility: newItem.visibility || 'PRIVATE',
            subteam: newItem.subteam,
            workspace: newItem.workspace
        };
    }
}, { immediate: true });

const handleSave = async () => {
    if (!props.item) return;

    // Logic to set workspace ID correctly based on visibility
    let workspaceId = props.item.workspace;
    if (form.value.visibility === 'WORKSPACE' || form.value.visibility === 'SUBTEAM') {
        // If switching to shared, assign current workspace if not already assigned
        if (!workspaceId && currentWorkspace.value) {
            workspaceId = currentWorkspace.value.id;
        }
    } else {
        // If Private, technically we don't *have* to remove workspace, but keeping it clean
        // actually, keeping workspace ID on private items is fine (it's essentially "Private in this workspace context")
        // But for now let's leave it as is.
    }

    const payload = {
        title: form.value.title,
        content: form.value.content,
        visibility: form.value.visibility,
        subteam: form.value.subteam,
        workspace: workspaceId
    };

    const success = await libraryStore.updateItem(props.item.id, payload);
    if (success) {
        emit('close');
    }
};
</script>
