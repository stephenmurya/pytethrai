import { defineStore } from "pinia";
import { ref, computed } from "vue";
import axios from "../lib/axios";

export interface Tag {
    id: number;
    name: string;
    color: string;
}

export interface LibraryItem {
    id: number;
    title: string;
    content: string;
    item_type: 'PROMPT' | 'TEMPLATE' | 'CONVERSATION';
    tags: Tag[];
    created_at: string;
    updated_at: string;
    is_template: boolean;
    visibility: 'PRIVATE' | 'WORKSPACE' | 'SUBTEAM';
    workspace: number | null;
    subteam: number | null;
}

import { useTeamStore } from "./teams";

export const useLibraryStore = defineStore("library", () => {
    const items = ref<LibraryItem[]>([]);
    const isLoading = ref(false);
    const searchQuery = ref("");
    const activeTab = ref<'ALL' | 'PROMPT' | 'TEMPLATE'>('ALL');

    const filteredItems = computed(() => {
        let result = items.value;

        // Filter by Tab
        if (activeTab.value !== 'ALL') {
            result = result.filter(item => item.item_type === activeTab.value);
        }

        // Filter by Search
        if (searchQuery.value.trim()) {
            const query = searchQuery.value.toLowerCase();
            result = result.filter(item => 
                item.title.toLowerCase().includes(query) || 
                item.content.toLowerCase().includes(query)
            );
        }

        return result;
    });

    async function fetchItems() {
        const teamStore = useTeamStore();
        isLoading.value = true;
        try {
            let url = "/api/knowledge/library/";
            if (teamStore.currentWorkspace) {
                url += `?workspace=${teamStore.currentWorkspace.id}`;
            }
            const response = await axios.get(url);
            items.value = response.data;
        } catch (error) {
            console.error("Failed to fetch library items", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function updateItem(id: number, payload: Partial<LibraryItem>) {
        try {
            const response = await axios.patch(`/api/knowledge/library/${id}/`, payload);
            const index = items.value.findIndex(item => item.id === id);
            if (index !== -1) {
                // Update local item
                items.value[index] = { ...items.value[index], ...response.data };
            }
            return true;
        } catch (error) {
            console.error("Failed to update item", error);
            return false;
        }
    }

    async function deleteItem(id: number) {
        try {
            await axios.delete(`/api/knowledge/library/${id}/`);
            items.value = items.value.filter(item => item.id !== id);
        } catch (error) {
            console.error("Failed to delete item", error);
        }
    }

    return {
        items,
        isLoading,
        searchQuery,
        activeTab,
        filteredItems,
        fetchItems,
        updateItem,
        deleteItem
    };
});
