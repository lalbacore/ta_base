<template>
  <div class="pki-management">
    <div class="page-header">
      <div>
        <h1 class="page-title">PKI Management</h1>
        <p class="page-subtitle">
          Manage certificates, monitor expiration, and maintain trust domains
        </p>
      </div>
      <Button
        label="Generate Certificate"
        icon="pi pi-plus"
        @click="showGenerateModal = true"
      />
    </div>

    <!-- Alert for expiring certificates -->
    <Message v-if="expiringSoon.length > 0" severity="warn" :closable="false">
      <div class="warning-content">
        <strong>{{ expiringSoon.length }} certificate(s) expiring soon!</strong>
        <p>{{ expiringSoon.map(c => c.domain).join(', ') }} - Take action before they expire.</p>
      </div>
    </Message>

    <!-- Summary Cards -->
    <div class="summary-grid">
      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon valid">
              <i class="pi pi-check-circle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Valid Certificates</div>
              <div class="summary-value">{{ validCerts.length }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon warning">
              <i class="pi pi-exclamation-triangle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Expiring Soon</div>
              <div class="summary-value">{{ expiringSoon.length }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon danger">
              <i class="pi pi-times-circle"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Revoked</div>
              <div class="summary-value">{{ pkiStore.revokedCertificates.length }}</div>
            </div>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <div class="summary-card">
            <div class="summary-icon info">
              <i class="pi pi-shield"></i>
            </div>
            <div class="summary-content">
              <div class="summary-label">Total Certificates</div>
              <div class="summary-value">{{ allCerts.length }}</div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading certificates...</p>
    </div>

    <!-- Certificates Grid -->
    <div v-else-if="allCerts.length > 0" class="certificates-section">
      <h2>Certificates</h2>
      <div class="certificates-grid">
        <CertificateCard
          v-for="cert in allCerts"
          :key="cert.domain"
          :certificate="cert"
          @renew="handleRenew"
          @rotate="handleRotate"
          @revoke="handleRevokeClick"
          @view-details="handleViewDetails"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <i class="pi pi-shield empty-icon"></i>
      <h3>No Certificates Found</h3>
      <p>Generate a new certificate to get started</p>
      <Button
        label="Generate Certificate"
        icon="pi pi-plus"
        @click="showGenerateModal = true"
      />
    </div>

    <!-- Generate Certificate Modal -->
    <GenerateCertificateModal
      :is-open="showGenerateModal"
      @close="showGenerateModal = false"
      @generate="handleGenerate"
    />

    <!-- Certificate Details Dialog -->
    <Dialog
      v-model:visible="showDetailsDialog"
      modal
      :header="`Certificate Details - ${selectedCert?.domain}`"
      :style="{ width: '700px' }"
    >
      <div class="cert-details" v-if="selectedCert">
        <div class="details-grid">
          <div class="detail-row">
            <span class="detail-label">Domain:</span>
            <span class="detail-value">{{ selectedCert.domain }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Status:</span>
            <span class="detail-value">
              <span :class="'status-badge status-' + selectedCert.status">
                {{ selectedCert.status }}
              </span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Serial Number:</span>
            <span class="detail-value mono">{{ selectedCert.serial }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Subject:</span>
            <span class="detail-value mono">{{ selectedCert.subject }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Issuer:</span>
            <span class="detail-value mono">{{ selectedCert.issuer }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Valid From:</span>
            <span class="detail-value">{{ selectedCert.not_before }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Valid Until:</span>
            <span class="detail-value">{{ selectedCert.not_after }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Days Until Expiry:</span>
            <span class="detail-value">{{ selectedCert.days_until_expiry }} days</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Provider:</span>
            <span class="detail-value">{{ selectedCert.provider }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Provider Type:</span>
            <span class="detail-value">{{ selectedCert.provider_type }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Close" @click="showDetailsDialog = false" />
      </template>
    </Dialog>

    <!-- Revoke Confirmation Dialog -->
    <Dialog
      v-model:visible="showRevokeDialog"
      modal
      :header="'Revoke Certificate'"
      :style="{ width: '500px' }"
    >
      <div class="revoke-dialog">
        <Message severity="warn" :closable="false">
          Are you sure you want to revoke this certificate? This action cannot be undone.
        </Message>

        <div class="form-field">
          <label for="revocationReason">Revocation Reason</label>
          <Dropdown
            id="revocationReason"
            v-model="revocationReason"
            :options="revocationReasons"
            optionLabel="label"
            optionValue="value"
            placeholder="Select reason"
            class="w-full"
          />
        </div>

        <div class="cert-info">
          <div><strong>Domain:</strong> {{ selectedCert?.domain }}</div>
          <div><strong>Serial:</strong> {{ selectedCert?.serial_number }}</div>
        </div>
      </div>

      <template #footer>
        <Button label="Cancel" severity="secondary" text @click="showRevokeDialog = false" />
        <Button
          label="Revoke Certificate"
          severity="danger"
          icon="pi pi-ban"
          :loading="isRevoking"
          @click="handleConfirmRevoke"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import { usePKIStore } from '@/stores/pki.store'
import CertificateCard from '@/components/pki/CertificateCard.vue'
import GenerateCertificateModal from '@/components/pki/GenerateCertificateModal.vue'

const toast = useToast()
const pkiStore = usePKIStore()

const isLoading = ref(false)
const showGenerateModal = ref(false)
const showDetailsDialog = ref(false)
const showRevokeDialog = ref(false)
const isRevoking = ref(false)
const selectedCert = ref<any>(null)
const revocationReason = ref('')

const revocationReasons = [
  { label: 'Key Compromise', value: 'key_compromise' },
  { label: 'CA Compromise', value: 'ca_compromise' },
  { label: 'Affiliation Changed', value: 'affiliation_changed' },
  { label: 'Superseded', value: 'superseded' },
  { label: 'Cessation of Operation', value: 'cessation_of_operation' }
]

const allCerts = computed(() => Array.from(pkiStore.certificates.values()))
const validCerts = computed(() => pkiStore.validCertificates)
const expiringSoon = computed(() => pkiStore.expiringCertificates)

async function handleRenew(domain: string) {
  try {
    await pkiStore.renewCertificate(domain as any)
    toast.add({
      severity: 'success',
      summary: 'Certificate Renewed',
      detail: `Certificate for ${domain} has been renewed`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Renewal Failed',
      detail: 'Failed to renew certificate',
      life: 3000
    })
  }
}

async function handleRotate(domain: string) {
  try {
    await pkiStore.rotateCertificate(domain as any)
    toast.add({
      severity: 'success',
      summary: 'Certificate Rotated',
      detail: `Certificate for ${domain} has been rotated with a new key`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Rotation Failed',
      detail: 'Failed to rotate certificate',
      life: 3000
    })
  }
}

function handleRevokeClick(domain: string) {
  selectedCert.value = allCerts.value.find(c => c.domain === domain)
  showRevokeDialog.value = true
}

async function handleConfirmRevoke() {
  if (!selectedCert.value || !revocationReason.value) return

  isRevoking.value = true
  try {
    await pkiStore.revokeCertificate(selectedCert.value.serial_number, revocationReason.value)
    toast.add({
      severity: 'success',
      summary: 'Certificate Revoked',
      detail: `Certificate for ${selectedCert.value.domain} has been revoked`,
      life: 3000
    })
    showRevokeDialog.value = false
    selectedCert.value = null
    revocationReason.value = ''
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Revocation Failed',
      detail: 'Failed to revoke certificate',
      life: 3000
    })
  } finally {
    isRevoking.value = false
  }
}

async function handleGenerate(certData: any) {
  try {
    await pkiStore.generateCertificate(certData)
    toast.add({
      severity: 'success',
      summary: 'Certificate Generated',
      detail: `New certificate for ${certData.domain} has been created`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Generation Failed',
      detail: 'Failed to generate certificate',
      life: 3000
    })
  }
}

function handleViewDetails(cert: any) {
  console.log('View details:', cert)
  selectedCert.value = cert
  showDetailsDialog.value = true
}

onMounted(async () => {
  isLoading.value = true
  try {
    await pkiStore.fetchAllCertificates()
  } catch (error) {
    console.error('Failed to load certificates:', error)
    toast.add({
      severity: 'error',
      summary: 'Load Failed',
      detail: 'Failed to load certificates',
      life: 3000
    })
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.pki-management {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.page-subtitle {
  color: #64748b;
  margin: 0;
}

.warning-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.warning-content strong {
  font-size: 1rem;
}

.warning-content p {
  margin: 0;
  font-size: 0.875rem;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.summary-icon.valid {
  background: #d1fae5;
  color: #059669;
}

.summary-icon.warning {
  background: #fed7aa;
  color: #ea580c;
}

.summary-icon.danger {
  background: #fee2e2;
  color: #dc2626;
}

.summary-icon.info {
  background: #dbeafe;
  color: #2563eb;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}

.summary-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #1e293b;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6rem 0;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
}

.certificates-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 1.5rem;
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  background-color: #f8fafc;
  margin-top: 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.revoke-dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}

.cert-info {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  font-size: 0.875rem;
}

.cert-info div {
  padding: 0.25rem 0;
  color: #64748b;
}

.cert-info strong {
  color: #1e293b;
}

/* Certificate Details Dialog */
.cert-details {
  padding: 0.5rem 0;
}

.details-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 1rem;
  padding: 0.75rem;
  border-bottom: 1px solid #f1f5f9;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #64748b;
  font-size: 0.875rem;
}

.detail-value {
  color: #1e293b;
  font-size: 0.875rem;
  word-break: break-all;
}

.detail-value.mono {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.8125rem;
  background: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-valid {
  background: #dcfce7;
  color: #166534;
}

.status-expiring_soon {
  background: #fef3c7;
  color: #92400e;
}

.status-expired {
  background: #fee2e2;
  color: #991b1b;
}
</style>
