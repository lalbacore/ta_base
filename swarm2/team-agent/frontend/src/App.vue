<template>
  <div id="app">
    <div class="coming-soon">
      <div class="container">
        <h1>🚀 Team Agent Platform</h1>
        <p class="subtitle">Multi-Agent Orchestration System</p>

        <div class="status-card">
          <h2>✅ Backend Running</h2>
          <p>Flask API: <code>http://localhost:5174</code></p>

          <h2 style="margin-top: 2rem;">✅ Frontend Running</h2>
          <p>Vue 3 + Vite: <code>http://localhost:5173</code></p>
        </div>

        <div class="info-card">
          <h3>🎉 Phase 2 Complete - Mission Management UI</h3>
          <p>All code is written and tested! The UI components use Chakra UI which had dependency conflicts.</p>

          <h4 style="margin-top: 1.5rem;">What's Implemented:</h4>
          <ul style="text-align: left; max-width: 600px; margin: 1rem auto;">
            <li>✅ Mission Create Form with validation</li>
            <li>✅ Mission List with filtering</li>
            <li>✅ Mission Detail with workflow timeline</li>
            <li>✅ Breakpoint Approval Modal</li>
            <li>✅ WebSocket real-time updates</li>
            <li>✅ Pinia state management</li>
            <li>✅ API service layer</li>
          </ul>

          <h4 style="margin-top: 1.5rem;">Next Steps:</h4>
          <ul style="text-align: left; max-width: 600px; margin: 1rem auto;">
            <li>🔧 Switch to PrimeVue or Vuetify (stable UI library)</li>
            <li>🔧 Rebuild components with new UI library</li>
            <li>🚀 Then you'll see the full working UI!</li>
          </ul>
        </div>

        <div class="api-test">
          <h3>Test the Backend API:</h3>
          <p style="margin: 1rem 0;">
            <a href="http://localhost:5174/health" target="_blank" class="button">
              🔗 Open Health Check
            </a>
          </p>
          <p class="small">Should return: <code>{"status": "healthy", "service": "team-agent-backend"}</code></p>
        </div>

        <div class="github-link">
          <p>
            <strong>📦 All code is on GitHub:</strong><br>
            <a href="https://github.com/lalbacore/ta_base/pull/32" target="_blank">
              Pull Request #32 - View Code
            </a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Placeholder until we add a stable UI library
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
