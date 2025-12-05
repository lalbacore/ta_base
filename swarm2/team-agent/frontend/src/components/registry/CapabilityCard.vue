<template>
  <Card class="capability-card">
    <template #header>
      <div class="card-header">
        <div class="capability-title">
          <i class="pi pi-box" :class="getTypeIconClass()"></i>
          <h3>{{ capability.name }}</h3>
        </div>
        <Tag :severity="getTrustSeverity()" class="trust-tag">
          <i class="pi pi-shield"></i> {{ capability.trust_score }}
        </Tag>
      </div>
    </template>

    <template #content>
      <div class="capability-details">
        <p class="description">{{ capability.description }}</p>

        <Divider />

        <div class="detail-row">
          <span class="detail-label">Provider:</span>
          <span class="detail-value">{{ capability.provider_name }}</span>
        </div>
        
        <div class="detail-row">
          <span class="detail-label">Type:</span>
          <span class="detail-value">{{ formatType(capability.capability_type) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">Price:</span>
          <span class="detail-value price">${{ capability.price.toFixed(2) }}</span>
        </div>

        <Divider />

        <div class="metrics-grid">
          <div class="metric">
            <span class="metric-label">Reputation</span>
            <Rating :modelValue="capability.reputation" :readonly="true" :cancel="false" />
          </div>
          
          <div class="metric">
            <span class="metric-label">Success Rate</span>
            <span class="metric-value success">{{ (capability.success_rate * 100).toFixed(0) }}%</span>
          </div>

          <div class="metric">
            <span class="metric-label">Invocations</span>
            <span class="metric-value">{{ capability.invocations }}</span>
          </div>
        </div>

        <div class="tags">
          <Chip v-for="tag in capability.tags" :key="tag" :label="tag" class="tag-chip" />
        </div>
      </div>
    </template>

    <template #footer>
      <div class="card-actions">
        <Button
          label="View Details"
          icon="pi pi-info-circle"
          size="small"
          text
          @click="handleViewDetails"
        />
        <Button
          label="Select"
          icon="pi pi-check"
          size="small"
          @click="handleSelect"
        />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Button from 'primevue/button'
import Divider from 'primevue/divider'
import Rating from 'primevue/rating'
import Chip from 'primevue/chip'
import type { Capability } from '@/types/registry.types'

interface Props {
  capability: Capability
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'select', capability: Capability): void
  (e: 'view-details', capability: Capability): void
}>()

function getTrustSeverity(): string {
  if (props.capability.trust_score >= 90) return 'success'
  if (props.capability.trust_score >= 75) return 'info'
  if (props.capability.trust_score >= 60) return 'warning'
  return 'danger'
}

function getTypeIconClass(): string {
  const typeMap: Record<string, string> = {
    code_generation: 'icon-code',
    security_audit: 'icon-security',
    testing: 'icon-test',
    deployment: 'icon-deploy',
    monitoring: 'icon-monitor'
  }
  return typeMap[props.capability.capability_type] || 'icon-default'
}

function formatType(type: string): string {
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function handleViewDetails() {
  emit('view-details', props.capability)
}

function handleSelect() {
  emit('select', props.capability)
}
</script>

<style scoped>
.capability-card {
  height: 100%;
  transition: box-shadow 0.3s, transform 0.2s;
}

.capability-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 0;
}

.capability-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.capability-title h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.capability-title .pi {
  font-size: 1.5rem;
  color: #667eea;
}

.trust-tag {
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.capability-details {
  padding: 0.5rem 0;
}

.description {
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.detail-label {
  font-weight: 500;
  color: #64748b;
  font-size: 0.875rem;
}

.detail-value {
  color: #1e293b;
  font-size: 0.875rem;
}

.detail-value.price {
  font-weight: 700;
  color: #667eea;
  font-size: 1rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1rem 0;
}

.metric {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #64748b;
  text-align: center;
}

.metric-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.metric-value.success {
  color: #10b981;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.tag-chip {
  font-size: 0.75rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  padding: 0 1.5rem 1.5rem;
}

:deep(.p-divider) {
  margin: 0.75rem 0;
}

:deep(.p-rating .p-rating-icon) {
  font-size: 0.875rem;
}
</style>
