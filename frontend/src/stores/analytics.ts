import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "../lib/axios";

export interface DashboardResponse {
    total_cost: number;
    total_requests: number;
    usage_by_user: {
        user__username: string;
        total_cost: number;
        request_count: number;
    }[];
    usage_by_model: {
        model_name: string;
        total_cost: number;
        request_count: number;
    }[];
    daily_usage: {
        date: string;
        cost: number;
        requests: number;
    }[];
}

export const useAnalyticsStore = defineStore("analytics", () => {
    const stats = ref<DashboardResponse | null>(null);
    const isLoading = ref(false);

    async function fetchDashboard(workspaceId?: number) {
        isLoading.value = true;
        try {
            let url = "/api/analytics/dashboard/";
            if (workspaceId) {
                url += `?workspace=${workspaceId}`;
            }
            const response = await axios.get(url);
            stats.value = response.data;
        } catch (error) {
            console.error("Failed to fetch dashboard stats", error);
            stats.value = null;
        } finally {
            isLoading.value = false;
        }
    }

    return {
        stats,
        isLoading,
        fetchDashboard
    };
});
