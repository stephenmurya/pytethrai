import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "../lib/axios";

export interface User {
	id: number;
	username: string;
	email: string;
}

export const useAuthStore = defineStore("auth", () => {
	const user = ref<User | null>(null);
	const isAuthenticated = ref(false);

	async function login(username: string, password: string) {
		try {
			const response = await axios.post("/api/auth/login/", {
				username,
				password,
			});
			user.value = response.data;
			isAuthenticated.value = true;
			return { success: true };
		} catch (error: any) {
			return {
				success: false,
				error: error.response?.data?.error || "Login failed",
			};
		}
	}

	async function register(
		username: string,
		password: string,
		email: string = "",
	) {
		try {
			const response = await axios.post("/api/auth/register/", {
				username,
				password,
				email,
			});
			user.value = response.data;
			isAuthenticated.value = true;
			return { success: true };
		} catch (error: any) {
			return {
				success: false,
				error: error.response?.data?.error || "Registration failed",
			};
		}
	}

	async function logout() {
		try {
			await axios.post("/api/auth/logout/");
			user.value = null;
			isAuthenticated.value = false;
		} catch (error) {
			console.error("Logout failed", error);
		}
	}

	async function getMe() {
		try {
			const response = await axios.get("/api/auth/me/");
			user.value = response.data;
			isAuthenticated.value = true;
			return true;
		} catch (error) {
			user.value = null;
			isAuthenticated.value = false;
			return false;
		}
	}

	return {
		user,
		isAuthenticated,
		login,
		register,
		logout,
		getMe,
	};
});
