<template>
  <Card class="trust-metrics-card">
    <template #content>
      <div class="metrics-grid">
        <div class="metric-item">
          <div class="metric-icon" :class="`icon-${color}`">
            <i :class="icon"></i>
          </div>
          <div class="metric-content">
            <div class="metric-label">{{ label }}</div>
            <div class="metric-value">{{ formattedValue }}</div>
            <div v-if="subtitle" class="metric-subtitle">{{ subtitle }}</div>
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'

interface Props {
  label: string
  value: number | string
  icon: string
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple'
  format?: 'number' | 'percentage' | 'decimal' | 'string'
  subtitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: 'blue',
  format: 'number'
})

const formattedValue = computed(() => {
  const val = props.value

  if (typeof val === 'string') return val

  switch (props.format) {
    case 'percentage':
      return `${(val * 100).toFixed(0)}%`
    case 'decimal':
      return val.toFixed(1)
    case 'number':
      return val.toLocaleString()
    default:
      return val.toString()
  }
})
</script>

<style scoped>
.trust-metrics-card {
  height: 100%;
}

.trust-metrics-card :deep(.p-card-body) {
  padding: 1.5rem;
}

.trust-metrics-card :deep(.p-card-content) {
  padding: 0;
}

.metrics-grid {
  display: flex;
  align-items: center;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.icon-blue {
  background: #dbeafe;
  color: #2563eb;
}

.icon-green {
  background: #d1fae5;
  color: #059669;
}

.icon-orange {
  background: #fed7aa;
  color: #ea580c;
}

.icon-red {
  background: #fee2e2;
  color: #dc2626;
}

.icon-purple {
  background: #e9d5ff;
  color: #9333ea;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.metric-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.metric-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
}
</style>
