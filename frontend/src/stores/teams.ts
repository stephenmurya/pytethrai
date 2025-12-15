import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "../lib/axios";

export interface Workspace {
    id: number;
    name: string;
    slug: string;
    owner: {
        id: number;
        username: string;
    };
    invite_token: string;
    created_at: string;
}

export interface SubTeam {
    id: number;
    name: string;
    description: string;
    workspace: number;
}

export const useTeamStore = defineStore("teams", () => {
    const workspaces = ref<Workspace[]>([]);
    const currentWorkspace = ref<Workspace | null>(null);
    const subTeams = ref<SubTeam[]>([]);
    const isLoading = ref(false);

    async function fetchWorkspaces() {
        isLoading.value = true;
        try {
            const response = await axios.get("/api/teams/workspaces/");
            workspaces.value = response.data;
            
            // Restore selection from localStorage if valid
            const savedId = localStorage.getItem("currentWorkspaceId");
            if (savedId) {
                const found = workspaces.value.find(w => w.id === parseInt(savedId));
                if (found) {
                    currentWorkspace.value = found;
                }
            }
        } catch (error) {
            console.error("Failed to fetch workspaces", error);
        } finally {
            isLoading.value = false;
        }
    }

    async function fetchSubTeams(workspaceId: number) {
        try {
            const response = await axios.get(`/api/teams/subteams/?workspace=${workspaceId}`);
            subTeams.value = response.data;
        } catch (error) {
            console.error("Failed to fetch subteams", error);
            subTeams.value = [];
        }
    }

    async function createWorkspace(name: string) {
        try {
            const response = await axios.post("/api/teams/workspaces/", { name });
            const newWorkspace = response.data;
            workspaces.value.push(newWorkspace);
            selectWorkspace(newWorkspace);
            return true;
        } catch (error) {
            console.error("Failed to create workspace", error);
            return false;
        }
    }

    async function joinWorkspace(token: string) {
        try {
            const response = await axios.post("/api/teams/workspaces/join/", { token });
            if (response.data.workspace) {
                // Refresh list to include new workspace
                await fetchWorkspaces();
                selectWorkspace(workspaces.value.find(w => w.id === response.data.workspace.id) || null);
                return true;
            }
        } catch (error) {
            console.error("Failed to join workspace", error);
            return false;
        }
        return false;
    }

    function selectWorkspace(workspace: Workspace | null) {
        currentWorkspace.value = workspace;
        if (workspace) {
            localStorage.setItem("currentWorkspaceId", workspace.id.toString());
            fetchSubTeams(workspace.id);
        } else {
            localStorage.removeItem("currentWorkspaceId");
            subTeams.value = [];
        }
    }

    return {
        workspaces,
        currentWorkspace,
        subTeams,
        isLoading,
        fetchWorkspaces,
        fetchSubTeams,
        createWorkspace,
        joinWorkspace,
        selectWorkspace
    };
});
