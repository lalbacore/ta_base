<template>
  <AppLayout>
    <router-view />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.coming-soon {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}

.container {
  max-width: 800px;
  text-align: center;
  color: white;
}

h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.status-card,
.info-card,
.api-test,
.github-link {
  background: white;
  color: #333;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

h2 {
  color: #667eea;
  margin-bottom: 1rem;
}

h3 {
  color: #667eea;
  margin-bottom: 1rem;
}

h4 {
  color: #764ba2;
  font-size: 1.1rem;
}

code {
  background: #f4f4f4;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #e83e8c;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 0.5rem 0;
  font-size: 1rem;
}

.button {
  display: inline-block;
  background: #667eea;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: background 0.3s ease;
}

.button:hover {
  background: #764ba2;
}

.small {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.5rem;
}

a {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

a:hover {
  text-decoration: underline;
}
</style>
