<template>
  <Card class="stat-card">
    <template #content>
      <div class="stat-header">
        <span class="stat-icon">{{ icon }}</span>
        <Tag :severity="getSeverity(colorScheme)">{{ title }}</Tag>
      </div>
      <div class="stat-value" :class="`stat-${colorScheme}`">
        {{ value }}
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import Card from 'primevue/card'
import Tag from 'primevue/tag'

defineProps<{
  title: string
  value: string | number
  icon: string
  colorScheme: string
}>()

function getSeverity(colorScheme: string): string {
  const severityMap: Record<string, string> = {
    blue: 'info',
    green: 'success',
    orange: 'warning',
    red: 'danger',
    gray: 'secondary'
  }
  return severityMap[colorScheme] || 'info'
}
</script>

<style scoped>
.stat-card {
  height: 100%;
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
}

.stat-blue {
  color: #3b82f6;
}

.stat-green {
  color: #10b981;
}

.stat-orange {
  color: #f59e0b;
}

.stat-red {
  color: #ef4444;
}

.stat-gray {
  color: #6b7280;
}
</style>
