<template>
  <AppLayout>
    <div class="trust-dashboard">
      <h1 class="page-title">Trust Scoring Dashboard</h1>

      <Message severity="info" :closable="false">
        <div class="info-content">
          <h3>Trust Scoring System</h3>
          <p>This dashboard will display agent reputation and trust scores based on workflow execution history, success rates, and security compliance.</p>
        </div>
      </Message>

      <div class="placeholder-content">
        <i class="pi pi-shield placeholder-icon"></i>
        <h3>No Agent Trust Data Available</h3>
        <p>Trust scores will appear here once agents start executing workflows</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/components/layout/AppLayout.vue'
import Message from 'primevue/message'
</script>

<style scoped>
.trust-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

.info-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.info-content p {
  margin: 0;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  margin-top: 2rem;
}

.placeholder-icon {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.placeholder-content h3 {
  font-size: 1.25rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.placeholder-content p {
  color: #94a3b8;
}
</style>
