<template>
  <div class="flex h-screen w-full bg-[#0a0a0a] text-white font-sans overflow-hidden">
    <!-- Main Content -->
    <main class="flex-1 flex flex-col relative bg-[#0a0a0a] max-w-7xl mx-auto w-full">
      
      <!-- Top Bar -->
      <header class="flex flex-col gap-4 px-8 py-6 border-b border-zinc-800">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
             <h1 class="text-2xl font-semibold">
                {{ currentWorkspace ? `${currentWorkspace.name} Analytics` : 'Personal Analytics' }}
             </h1>
          </div>
        </div>
      </header>

      <!-- Content Area -->
      <div v-if="isLoading" class="flex justify-center py-12">
           <div class="animate-spin h-8 w-8 border-2 border-zinc-600 border-t-white rounded-full"></div>
      </div>
      
      <div v-else-if="stats" class="flex-1 overflow-y-auto p-8 space-y-8">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-6">
                <p class="text-sm text-zinc-400 mb-1">Total Spend (Est.)</p>
                <p class="text-3xl font-bold text-white">${{ stats.total_cost.toFixed(4) }}</p>
            </div>
            <div class="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-6">
                <p class="text-sm text-zinc-400 mb-1">Total Requests</p>
                <p class="text-3xl font-bold text-white">{{ stats.total_requests }}</p>
            </div>
            <div class="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-6">
                <p class="text-sm text-zinc-400 mb-1">Top Model</p>
                <p class="text-xl font-bold text-white truncate">{{ topModelName }}</p>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Usage by User Bar Chart -->
            <div class="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4">Cost by User</h3>
                <div class="relative h-64">
                    <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
                </div>
            </div>

             <!-- Usage by Model Table -->
             <div class="bg-[#1a1a1a] border border-zinc-800 rounded-xl p-6">
                <h3 class="text-lg font-semibold mb-4">Usage by Model</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left text-zinc-400">
                        <thead class="text-xs text-zinc-500 uppercase bg-zinc-900/50">
                            <tr>
                                <th class="px-4 py-3 rounded-l-lg">Model</th>
                                <th class="px-4 py-3">Requests</th>
                                <th class="px-4 py-3 rounded-r-lg text-right">Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="model in stats.usage_by_model" :key="model.model_name" class="border-b border-zinc-800/50 last:border-0 hover:bg-white/5">
                                <td class="px-4 py-3 font-medium text-white">{{ model.model_name }}</td>
                                <td class="px-4 py-3">{{ model.request_count }}</td>
                                <td class="px-4 py-3 text-right text-indigo-400">${{ model.total_cost.toFixed(4) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
      </div>
       
       <div v-else class="flex flex-col items-center justify-center flex-1 text-zinc-500">
          <p>Select a workspace to view analytics.</p>
       </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useTeamStore } from '../stores/teams';
import { useAnalyticsStore } from '../stores/analytics';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import { Bar } from 'vue-chartjs';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const teamStore = useTeamStore();
const analyticsStore = useAnalyticsStore();
const { currentWorkspace } = storeToRefs(teamStore);
const { stats, isLoading } = storeToRefs(analyticsStore);

const loadData = () => {
    // If we have a workspace, use its ID. If not, pass undefined for "Personal" (handled by store/API logic)
    // Actually, checking store logic: fetchDashboard(workspaceId?: number).
    // Note: If currentWorkspace is null, we pass undefined, API returns personal logs.
    const wsId = currentWorkspace.value ? currentWorkspace.value.id : undefined;
    analyticsStore.fetchDashboard(wsId);
};

onMounted(() => {
    loadData();
});

watch(currentWorkspace, () => {
    loadData();
});

const chartData = computed(() => {
    if (!stats.value) return null;
    
    // Sort top 5 users by cost
    const topUsers = [...stats.value.usage_by_user].sort((a,b) => b.total_cost - a.total_cost).slice(0, 10);

    return {
        labels: topUsers.map(u => u.user__username),
        datasets: [
            {
                label: 'Estimated Cost ($)',
                backgroundColor: '#6366f1', // Indigo 500
                data: topUsers.map(u => u.total_cost),
                borderRadius: 4
            }
        ]
    };
});

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { display: false },
        tooltip: {
             callbacks: {
                 label: (context: any) => `Cost: $${context.raw.toFixed(4)}`
             }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            grid: { color: '#27272a' }, // zinc-800
            ticks: { color: '#a1a1aa' } // zinc-400
        },
        x: {
            grid: { display: false },
            ticks: { color: '#a1a1aa' }
        }
    }
};

const topModelName = computed(() => {
    if (!stats.value || stats.value.usage_by_model.length === 0) return 'N/A';
    // Find model with highest cost (or requests? usually cost is more detailed, but requests is simpler. Let's do requests for "Most Used")
    // Wait, prompt says "Most used model name". "Most used" usually implies requests. "Top Model" in analytics usually implies spend. 
    // Let's sort by request_count.
    const sorted = [...stats.value.usage_by_model].sort((a,b) => b.request_count - a.request_count);
    return sorted[0].model_name;
});
</script>
