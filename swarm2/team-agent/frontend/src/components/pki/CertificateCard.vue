<template>
  <Card class="certificate-card">
    <template #header>
      <div class="card-header">
        <div class="cert-title">
          <i class="pi pi-shield" :class="getStatusIconClass()"></i>
          <h3>{{ formatDomainName(certificate.domain) }}</h3>
        </div>
        <Tag :severity="getStatusSeverity()" class="status-tag">
          {{ getStatusLabel() }}
        </Tag>
      </div>
    </template>

    <template #content>
      <div class="cert-details">
        <div class="detail-row">
          <span class="detail-label">Subject:</span>
          <span class="detail-value">{{ certificate.subject }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Issuer:</span>
          <span class="detail-value">{{ certificate.issuer }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Serial Number:</span>
          <span class="detail-value code">{{ certificate.serial_number }}</span>
        </div>
        <Divider />
        <div class="detail-row">
          <span class="detail-label">Valid From:</span>
          <span class="detail-value">{{ formatDate(certificate.valid_from) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Valid To:</span>
          <span class="detail-value">{{ formatDate(certificate.valid_to) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Time Remaining:</span>
          <span class="detail-value" :class="getExpiryClass()">
            {{ getTimeRemaining() }}
          </span>
        </div>
        <Divider />
        <div class="detail-row">
          <span class="detail-label">Key Size:</span>
          <span class="detail-value">{{ certificate.key_size }} bits</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">Algorithm:</span>
          <span class="detail-value">{{ certificate.signature_algorithm }}</span>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="card-actions">
        <Button
          label="Renew"
          icon="pi pi-refresh"
          size="small"
          :disabled="certificate.status === 'revoked'"
          @click="handleRenew"
        />
        <Button
          label="Rotate"
          icon="pi pi-sync"
          severity="secondary"
          size="small"
          :disabled="certificate.status === 'revoked'"
          @click="handleRotate"
        />
        <Button
          label="Revoke"
          icon="pi pi-ban"
          severity="danger"
          size="small"
          :disabled="certificate.status === 'revoked'"
          @click="handleRevoke"
        />
        <Button
          label="Details"
          icon="pi pi-info-circle"
          text
          size="small"
          @click="handleViewDetails"
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

interface Certificate {
  domain: string
  subject: string
  issuer: string
  serial_number: string
  valid_from: string
  valid_to: string
  status: string
  key_size: number
  signature_algorithm: string
}

interface Props {
  certificate: Certificate
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'renew', domain: string): void
  (e: 'rotate', domain: string): void
  (e: 'revoke', domain: string): void
  (e: 'view-details', certificate: Certificate): void
}>()

function formatDomainName(domain: string): string {
  return domain.charAt(0).toUpperCase() + domain.slice(1) + ' CA'
}

function getStatusSeverity(): string {
  const statusMap: Record<string, string> = {
    valid: 'success',
    expiring_soon: 'warning',
    expired: 'danger',
    revoked: 'danger'
  }
  return statusMap[props.certificate.status] || 'secondary'
}

function getStatusLabel(): string {
  const labelMap: Record<string, string> = {
    valid: 'Valid',
    expiring_soon: 'Expiring Soon',
    expired: 'Expired',
    revoked: 'Revoked'
  }
  return labelMap[props.certificate.status] || 'Unknown'
}

function getStatusIconClass(): string {
  const classMap: Record<string, string> = {
    valid: 'icon-valid',
    expiring_soon: 'icon-warning',
    expired: 'icon-expired',
    revoked: 'icon-revoked'
  }
  return classMap[props.certificate.status] || ''
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getTimeRemaining(): string {
  const now = new Date()
  const expiry = new Date(props.certificate.valid_to)
  const diffMs = expiry.getTime() - now.getTime()

  if (diffMs < 0) return 'Expired'

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Expires today'
  if (diffDays === 1) return '1 day'
  if (diffDays < 30) return `${diffDays} days`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`
  return `${Math.floor(diffDays / 365)} year(s)`
}

function getExpiryClass(): string {
  const now = new Date()
  const expiry = new Date(props.certificate.valid_to)
  const diffDays = Math.floor((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) return 'expiry-critical'
  if (diffDays < 7) return 'expiry-critical'
  if (diffDays < 30) return 'expiry-warning'
  return 'expiry-good'
}

function handleRenew() {
  emit('renew', props.certificate.domain)
}

function handleRotate() {
  emit('rotate', props.certificate.domain)
}

function handleRevoke() {
  emit('revoke', props.certificate.domain)
}

function handleViewDetails() {
  emit('view-details', props.certificate)
}
</script>

<style scoped>
.certificate-card {
  height: 100%;
  transition: box-shadow 0.3s;
}

.certificate-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 0;
}

.cert-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cert-title h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.cert-title .pi {
  font-size: 1.5rem;
}

.icon-valid {
  color: #10b981;
}

.icon-warning {
  color: #f59e0b;
}

.icon-expired,
.icon-revoked {
  color: #ef4444;
}

.status-tag {
  font-weight: 600;
}

.cert-details {
  padding: 0.5rem 0;
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
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.detail-value.code {
  font-family: 'Courier New', monospace;
  background: #f1f5f9;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.expiry-good {
  color: #10b981;
  font-weight: 600;
}

.expiry-warning {
  color: #f59e0b;
  font-weight: 600;
}

.expiry-critical {
  color: #ef4444;
  font-weight: 700;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  padding: 0 1.5rem 1.5rem;
}

:deep(.p-divider) {
  margin: 0.75rem 0;
}
</style>
