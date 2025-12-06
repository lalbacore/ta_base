<template>
  <div class="lifecycle-alerts">
    <div class="alerts-header">
      <h3>Certificate Lifecycle Status</h3>
      <Button
        v-if="lifecycleStatus && lifecycleStatus.requires_action > 0"
        label="Auto-Renew All"
        icon="pi pi-refresh"
        severity="warning"
        size="small"
        @click="handleAutoRenew"
        :loading="autoRenewing"
      />
    </div>

    <div class="alert-badges" v-if="lifecycleStatus">
      <div
        v-for="(count, status) in lifecycleStatus.summary"
        :key="status"
        :class="['badge-card', status]"
        @click="handleBadgeClick(status)"
      >
        <div class="badge-icon">
          <i :class="getBadgeIcon(status)"></i>
        </div>
        <div class="badge-content">
          <div class="badge-count">{{ count }}</div>
          <div class="badge-label">{{ formatStatus(status) }}</div>
        </div>
      </div>
    </div>

    <div class="alerts-list" v-if="lifecycleStatus && lifecycleStatus.alerts.length > 0">
      <Message
        v-for="(alert, index) in lifecycleStatus.alerts"
        :key="index"
        :severity="getAlertSeverity(alert.severity)"
        :closable="false"
      >
        <strong>{{ alert.domain.toUpperCase() }}</strong>: {{ alert.message }}
        ({{ alert.days_until_expiry }} days)
      </Message>
    </div>

    <div class="last-updated" v-if="lastUpdated">
      Last updated: {{ formatTimestamp(lastUpdated) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Button from 'primevue/button'
import Message from 'primevue/message'
import type { LifecycleStatus } from '@/types/pki.types'
import pkiService from '@/services/pki.service'

const emit = defineEmits(['filter-by-status', 'refresh'])

const lifecycleStatus = ref<LifecycleStatus | null>(null)
const lastUpdated = ref<Date | null>(null)
const autoRenewing = ref(false)
let refreshInterval: number | null = null

async function loadLifecycleStatus() {
  try {
    lifecycleStatus.value = await pkiService.getLifecycleStatus()
    lastUpdated.value = new Date()
  } catch (error) {
    console.error('Failed to load lifecycle status:', error)
  }
}

async function handleAutoRenew() {
  if (!confirm('Auto-renew all expiring certificates? This will rotate certificates that are expired, critical, or expiring soon.')) {
    return
  }

  autoRenewing.value = true
  try {
    const result = await pkiService.autoRenewCertificates(false)
    console.log('Auto-renew result:', result)

    // Refresh status after renewal
    await loadLifecycleStatus()
    emit('refresh')

    alert(`Successfully renewed ${result.summary?.successful || 0} certificate(s)`)
  } catch (error) {
    console.error('Auto-renew failed:', error)
    alert('Auto-renewal failed. Check console for details.')
  } finally {
    autoRenewing.value = false
  }
}

function handleBadgeClick(status: string) {
  emit('filter-by-status', status)
}

function getBadgeIcon(status: string): string {
  const icons = {
    expired: 'pi pi-times-circle',
    critical: 'pi pi-exclamation-triangle',
    expiring_soon: 'pi pi-info-circle',
    warning: 'pi pi-exclamation-circle',
    valid: 'pi pi-check-circle'
  }
  return icons[status as keyof typeof icons] || 'pi pi-info-circle'
}

function formatStatus(status: string): string {
  const labels = {
    expired: 'Expired',
    critical: 'Critical (<7d)',
    expiring_soon: 'Expiring Soon (<30d)',
    warning: 'Warning (<90d)',
    valid: 'Valid'
  }
  return labels[status as keyof typeof labels] || status
}

function getAlertSeverity(severity: string): 'error' | 'warn' | 'info' {
  const severityMap = {
    expired: 'error' as const,
    critical: 'error' as const,
    expiring_soon: 'warn' as const,
    warning: 'info' as const
  }
  return severityMap[severity as keyof typeof severityMap] || 'info'
}

function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString()
}

onMounted(() => {
  loadLifecycleStatus()
  // Auto-refresh every 60 seconds
  refreshInterval = window.setInterval(() => {
    loadLifecycleStatus()
  }, 60000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

defineExpose({
  refresh: loadLifecycleStatus
})
</script>

<style scoped>
.lifecycle-alerts {
  margin-bottom: 2rem;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.alerts-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
}

.alert-badges {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.badge-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: var(--surface-card);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.badge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.badge-card.expired {
  border-color: #ef4444;
}

.badge-card.expired .badge-icon {
  color: #ef4444;
}

.badge-card.critical {
  border-color: #f97316;
}

.badge-card.critical .badge-icon {
  color: #f97316;
}

.badge-card.expiring_soon {
  border-color: #eab308;
}

.badge-card.expiring_soon .badge-icon {
  color: #eab308;
}

.badge-card.warning {
  border-color: #3b82f6;
}

.badge-card.warning .badge-icon {
  color: #3b82f6;
}

.badge-card.valid {
  border-color: #22c55e;
}

.badge-card.valid .badge-icon {
  color: #22c55e;
}

.badge-icon {
  font-size: 2rem;
}

.badge-content {
  flex: 1;
}

.badge-count {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.badge-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.last-updated {
  text-align: right;
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  font-style: italic;
}
</style>
