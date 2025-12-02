<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <div class="w-full max-w-md p-8 space-y-6 bg-card rounded-lg shadow-lg border border-border">
      <h1 class="text-3xl font-bold text-center text-foreground">Login</h1>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-foreground">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            class="mt-1 block w-full px-3 py-2 bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div>
          <label for="password" class="block text-sm font-medium text-foreground">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="mt-1 block w-full px-3 py-2 bg-background border border-input rounded-md text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div v-if="error" class="text-destructive text-sm">{{ error }}</div>
        <button
          type="submit"
          class="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition"
        >
          Login
        </button>
      </form>
      <div class="text-center text-sm">
        Don't have an account?
        <router-link to="/register" class="text-primary hover:underline">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

async function handleLogin() {
  error.value = ''
  const result = await authStore.login(username.value, password.value)
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error || 'Login failed'
  }
}
</script>
