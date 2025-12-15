import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "../lib/axios";

export interface Message {
	id: string;
	role: "user" | "assistant" | "system";
	content: string;
	created_at: string;
	is_saved?: boolean;
}

export interface Chat {
	id: string;
	title: string;
	created_at: string;
	updated_at: string;
	messages: Message[];
}

export interface ModelCapabilities {
	vision: boolean;
	fast: boolean;
	code: boolean;
	free: boolean;
}

export interface AIModel {
	id: string;
	name: string;
	description: string;
	context_length: number;
	capabilities: ModelCapabilities;
}

import { useTeamStore } from "./teams";

export const useChatStore = defineStore("chat", () => {
	const currentChat = ref<Chat | null>(null);
	const chatHistory = ref<Chat[]>([]);
	const isStreaming = ref(false);
	
	// Model management state
	const availableModels = ref<AIModel[]>([]);
	const selectedModel = ref("google/gemini-2.0-flash-exp:free");
	const modelsError = ref<string | null>(null);
	const isLoadingModels = ref(false);

	// Message interaction state
	const messageVotes = ref<Record<string, 'up' | 'down' | null>>({});

	async function sendMessage(
		content: string,
		chatId?: string,
	) {
		isStreaming.value = true;
		
		// Optimistically add user message if we have a current chat
		if (currentChat.value) {
			const userMsg: Message = {
				id: Date.now().toString(),
				role: 'user',
				content: content,
				created_at: new Date().toISOString()
			};
			currentChat.value.messages.push(userMsg);
		}

		try {
            const teamStore = useTeamStore();
            let url = "/api/chat/send/";
            if (teamStore.currentWorkspace) {
                url += `?workspace=${teamStore.currentWorkspace.id}`;
            }

			const response = await axios.post(
				url,
				{
					content,
					chatId,
					model: selectedModel.value, // Use selected model
				},
				{
					responseType: "text",
				},
			);

			// Check for new chat ID in headers
			const newChatId = response.headers['chat-id'];
			
			// If this was a new chat (no chatId passed) and we got a new ID
			if (!chatId && newChatId) {
				// Initialize current chat if it doesn't exist
				if (!currentChat.value) {
					currentChat.value = {
						id: newChatId,
						title: content.substring(0, 30),
						created_at: new Date().toISOString(),
						updated_at: new Date().toISOString(),
						messages: [
							{
								id: Date.now().toString(),
								role: 'user',
								content: content,
								created_at: new Date().toISOString()
							}
						]
					};
				} else if (currentChat.value.id !== newChatId) {
					// Update ID if it was a temp placeholder (though we usually start null)
					currentChat.value.id = newChatId;
				}
				
				// Refresh chat history to show new chat in sidebar
				getChatHistory();
			}

			// Response is streaming text
			const fullResponse = response.data;
			
			// Add assistant message to current chat
			if (currentChat.value) {
				const assistantMsg: Message = {
					id: Date.now().toString(), // Temporary ID
					role: 'assistant',
					content: fullResponse,
					created_at: new Date().toISOString()
				};
				currentChat.value.messages.push(assistantMsg);
			}

			return fullResponse;
		} catch (error) {
			console.error("Send message failed", error);
			return null;
		} finally {
			isStreaming.value = false;
		}
	}

	async function getChatHistory() {
		try {
            const teamStore = useTeamStore();
            let url = "/api/chat/history/";
            if (teamStore.currentWorkspace) {
                url += `?workspace=${teamStore.currentWorkspace.id}`;
            }
			const response = await axios.get(url);
			chatHistory.value = response.data;
		} catch (error) {
			console.error("Get chat history failed", error);
		}
	}

	async function loadChat(chatId: string) {
		try {
			const response = await axios.get(`/api/chat/${chatId}/`);
			currentChat.value = response.data;
		} catch (error) {
			console.error("Load chat failed", error);
		}
	}

	function clearCurrentChat() {
		currentChat.value = null;
	}

	async function fetchModels() {
		isLoadingModels.value = true;
		modelsError.value = null;
		
		try {
			const response = await axios.get("/api/models/");
			availableModels.value = response.data.models || [];
			
			// If there was a backend error (using fallback), show warning
			if (response.data.error) {
				modelsError.value = response.data.error;
			}
		} catch (error: any) {
			console.error("Failed to fetch models", error);
			modelsError.value = error.response?.data?.error || "Failed to load models. Please check your connection and try again.";
			availableModels.value = [];
		} finally {
			isLoadingModels.value = false;
		}
	}

	async function retryFetchModels() {
		await fetchModels();
	}

	function setSelectedModel(modelId: string) {
		selectedModel.value = modelId;
	}

	async function copyToClipboard(content: string) {
		try {
			await navigator.clipboard.writeText(content);
			return true;
		} catch (error) {
			console.error("Failed to copy to clipboard", error);
			return false;
		}
	}

	function voteMessage(messageId: string, vote: 'up' | 'down') {
		// Toggle vote: if same vote, remove it; if different vote, replace it
		if (messageVotes.value[messageId] === vote) {
			messageVotes.value[messageId] = null;
		} else {
			messageVotes.value[messageId] = vote;
		}
	}

	return {
		currentChat,
		chatHistory,
		isStreaming,
		availableModels,
		selectedModel,
		modelsError,
		isLoadingModels,
		messageVotes,
		sendMessage,
		getChatHistory,
		loadChat,
		clearCurrentChat,
		fetchModels,
		retryFetchModels,
		setSelectedModel,
		copyToClipboard,
		voteMessage,
	};
});
