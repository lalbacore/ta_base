<template>
  
    <div class="dashboard">
      <h1 class="dashboard-title">Dashboard</h1>

      <div class="stats-grid">
        <StatCard
          title="Active Missions"
          value="0"
          icon="🎯"
          color-scheme="blue"
        />
        <StatCard
          title="Average Trust Score"
          value="0"
          icon="🔒"
          color-scheme="green"
        />
        <StatCard
          title="Certificates Expiring"
          value="0"
          icon="⚠️"
          color-scheme="orange"
        />
      </div>

      <p class="welcome-text">
        Welcome to Team Agent Platform - Multi-Agent Orchestration System
      </p>
    </div>
  
</template>

<script setup lang="ts">
import StatCard from '@/components/dashboard/StatCard.vue'
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.welcome-text {
  color: #64748b;
  font-size: 1rem;
  line-height: 1.5;
}
</style>
