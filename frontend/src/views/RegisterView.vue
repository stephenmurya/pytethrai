<template>
  <div class="min-h-screen flex items-center justify-center bg-[#212121]">
    <div class="w-full max-w-md p-8 space-y-6 bg-[#2a2a2a] rounded-2xl border border-zinc-800">
      <div class="text-center">
        <div class="w-12 h-12 bg-white rounded-full mx-auto mb-4 flex items-center justify-center">
          <span class="text-black text-xl font-bold">T</span>
        </div>
        <h1 class="text-3xl font-bold text-white">Create an account</h1>
        <p class="text-zinc-400 mt-2">Get started with Tethr AI</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-zinc-300 mb-2">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            class="w-full px-4 py-3 bg-[#171717] border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Choose a username"
          />
        </div>
        <div>
          <label for="email" class="block text-sm font-medium text-zinc-300 mb-2">Email (optional)</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="w-full px-4 py-3 bg-[#171717] border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="your@email.com"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-zinc-300 mb-2">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-3 bg-[#171717] border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Create a password"
          />
        </div>
        <div v-if="error" class="text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg p-3">{{ error }}</div>
        <button
          type="submit"
          class="w-full px-4 py-3 bg-white text-black font-semibold rounded-lg hover:bg-zinc-200 transition"
        >
          Sign up
        </button>
      </form>
      
      <div class="text-center text-sm text-zinc-400">
        Already have an account?
        <router-link to="/login" class="text-blue-400 hover:text-blue-300 font-medium">Sign in</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const error = ref("");

async function handleRegister() {
	error.value = "";
	const result = await authStore.register(
		username.value,
		password.value,
		email.value,
	);
	if (result.success) {
		router.push("/");
	} else {
		error.value = result.error || "Registration failed";
	}
}
</script>
