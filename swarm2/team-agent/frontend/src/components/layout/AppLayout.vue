<template>
  <div class="app-layout">
    <!-- Header -->
    <header class="app-header">
      <h1 class="app-title">Team Agent Platform</h1>
      <span class="app-subtitle">Multi-Agent Orchestration</span>
    </header>

    <!-- Main Container -->
    <div class="app-main">
      <!-- Sidebar -->
      <nav class="app-sidebar">
        <div class="nav-links">
          <NavLink to="/" icon="📊">Dashboard</NavLink>
          <NavLink to="/missions" icon="🎯">Missions</NavLink>
          <NavLink to="/agents" icon="🤖">Agents</NavLink>
          <NavLink to="/pki" icon="🔐">PKI Management</NavLink>
          <NavLink to="/registry" icon="📋">Registry</NavLink>
          <NavLink to="/governance" icon="⚖️">Governance</NavLink>
          <NavLink to="/artifacts" icon="📦">Artifacts</NavLink>
          <NavLink to="/providers" icon="🌐">Networks</NavLink>
          <NavLink to="/logs" icon="📝">Logs</NavLink>
        </div>
      </nav>

      <!-- Content Area -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import NavLink from './NavLink.vue'
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background-color: #1e293b;
  color: white;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.app-subtitle {
  font-size: 0.875rem;
  opacity: 0.9;
}

.app-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.app-sidebar {
  width: 250px;
  background-color: #f8fafc;
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  padding: 1rem;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-content {
  flex: 1;
  overflow-y: auto;
  background-color: #ffffff;
  padding: 1.5rem;
}
</style>
