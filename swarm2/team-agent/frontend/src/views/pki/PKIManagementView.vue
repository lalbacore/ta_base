<template>
  <div class="pki-management">
    <div class="page-header">
      <div>
        <h1 class="page-title">PKI Management</h1>
        <p class="page-subtitle">
          Manage certificates, monitor expiration, and maintain trust domains
        </p>
      </div>
    </div>

    <!-- Lifecycle Alerts Component -->
    <LifecycleAlerts
      ref="lifecycleAlertsRef"
      @filter-by-status="handleFilterByStatus"
      @refresh="loadCertificates"
    />

    <!-- Tabs for different views -->
    <TabView v-model:activeIndex="activeTab" class="pki-tabs">
      <!-- Active Certificates Tab -->
      <TabPanel header="Active Certificates">
        <div class="tab-content">
          <!-- Loading State -->
          <div v-if="isLoading" class="loading-state">
            <ProgressSpinner />
            <p>Loading certificates...</p>
          </div>

          <!-- Certificates Grid -->
          <div v-else-if="filteredCerts.length > 0" class="certificates-section">
            <div class="section-header">
              <h2>{{ getSectionTitle() }}</h2>
              <Button
                label="Clear Filter"
                icon="pi pi-times"
                text
                size="small"
                v-if="statusFilter"
                @click="clearFilter"
              />
            </div>
            <div class="certificates-grid">
              <CertificateCard
                v-for="cert in filteredCerts"
                :key="cert.domain"
                :certificate="cert"
                @renew="handleRenew"
                @rotate="handleRotateClick"
                @revoke="handleRevokeClick"
                @view-details="handleViewDetails"
              />
            </div>
          </div>

          <!-- Empty State -->
          <div v-else class="empty-state">
            <i class="pi pi-shield empty-icon"></i>
            <h3>No Certificates Found</h3>
            <p v-if="statusFilter">No certificates match the selected status filter</p>
            <p v-else>Certificates are automatically generated for all trust domains when the PKI initializes</p>
          </div>
        </div>
      </TabPanel>

      <!-- Revoked Certificates Tab -->
      <TabPanel header="Revoked Certificates">
        <RevokedCertificatesView ref="revokedCertsRef" />
      </TabPanel>
    </TabView>

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

    <!-- Rotate Confirmation Dialog -->
    <Dialog
      v-model:visible="showRotateDialog"
      modal
      header="Rotate Certificate"
      :style="{ width: '500px' }"
    >
      <div class="rotate-dialog">
        <Message severity="warn" :closable="false">
          Rotating a certificate generates a new key pair and revokes the old certificate.
          This is more secure than renewal but requires updating all services using this certificate.
        </Message>

        <div class="cert-info">
          <div><strong>Domain:</strong> {{ selectedCert?.domain }}</div>
          <div><strong>Current Serial:</strong> {{ selectedCert?.serial }}</div>
          <div><strong>Days Until Expiry:</strong> {{ selectedCert?.days_until_expiry }} days</div>
        </div>

        <p class="confirm-text">Are you sure you want to rotate this certificate?</p>
      </div>

      <template #footer>
        <Button label="Cancel" severity="secondary" text @click="showRotateDialog = false" />
        <Button
          label="Rotate Certificate"
          severity="warning"
          icon="pi pi-refresh"
          :loading="isRotating"
          @click="handleConfirmRotate"
        />
      </template>
    </Dialog>

    <!-- Revoke Confirmation Dialog -->
    <Dialog
      v-model:visible="showRevokeDialog"
      modal
      header="Revoke Certificate"
      :style="{ width: '500px' }"
    >
      <div class="revoke-dialog">
        <Message severity="error" :closable="false">
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
          <div><strong>Serial:</strong> {{ selectedCert?.serial }}</div>
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
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import CertificateCard from '@/components/pki/CertificateCard.vue'
import LifecycleAlerts from '@/components/pki/LifecycleAlerts.vue'
import RevokedCertificatesView from '@/components/pki/RevokedCertificatesView.vue'
import pkiService from '@/services/pki.service'

const toast = useToast()

const isLoading = ref(false)
const showDetailsDialog = ref(false)
const showRotateDialog = ref(false)
const showRevokeDialog = ref(false)
const isRotating = ref(false)
const isRevoking = ref(false)
const selectedCert = ref<any>(null)
const revocationReason = ref('')
const activeTab = ref(0)
const statusFilter = ref<string | null>(null)
const lifecycleAlertsRef = ref<any>(null)
const revokedCertsRef = ref<any>(null)

const allCerts = ref<any[]>([])

const revocationReasons = [
  { label: 'Key Compromise', value: 'KEY_COMPROMISE' },
  { label: 'CA Compromise', value: 'CA_COMPROMISE' },
  { label: 'Affiliation Changed', value: 'AFFILIATION_CHANGED' },
  { label: 'Superseded', value: 'SUPERSEDED' },
  { label: 'Cessation of Operation', value: 'CESSATION_OF_OPERATION' }
]

const filteredCerts = computed(() => {
  if (!statusFilter.value) return allCerts.value

  const statusMap: Record<string, string[]> = {
    expired: ['expired'],
    critical: ['critical'],
    expiring_soon: ['expiring_soon'],
    warning: ['warning'],
    valid: ['valid']
  }

  const allowedStatuses = statusMap[statusFilter.value] || []
  return allCerts.value.filter(cert => allowedStatuses.includes(cert.status))
})

async function loadCertificates() {
  isLoading.value = true
  try {
    allCerts.value = await pkiService.getAllCertificates()
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
}

function handleFilterByStatus(status: string) {
  statusFilter.value = status
  activeTab.value = 0 // Switch to certificates tab
}

function clearFilter() {
  statusFilter.value = null
}

function getSectionTitle(): string {
  if (!statusFilter.value) return 'All Certificates'

  const titles: Record<string, string> = {
    expired: 'Expired Certificates',
    critical: 'Critical Certificates (< 7 days)',
    expiring_soon: 'Expiring Soon (< 30 days)',
    warning: 'Warning (< 90 days)',
    valid: 'Valid Certificates'
  }

  return titles[statusFilter.value] || 'Certificates'
}

async function handleRenew(domain: string) {
  try {
    await pkiService.renewCertificate(domain as any)
    toast.add({
      severity: 'success',
      summary: 'Certificate Renewed',
      detail: `Certificate for ${domain} has been renewed`,
      life: 3000
    })
    await loadCertificates()
    lifecycleAlertsRef.value?.refresh()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Renewal Failed',
      detail: 'Failed to renew certificate',
      life: 3000
    })
  }
}

function handleRotateClick(domain: string) {
  selectedCert.value = allCerts.value.find(c => c.domain === domain)
  showRotateDialog.value = true
}

async function handleConfirmRotate() {
  if (!selectedCert.value) return

  isRotating.value = true
  try {
    const result = await pkiService.rotateCertificate(selectedCert.value.domain)
    toast.add({
      severity: 'success',
      summary: 'Certificate Rotated',
      detail: `Certificate for ${selectedCert.value.domain} has been rotated`,
      life: 5000
    })
    showRotateDialog.value = false
    selectedCert.value = null
    await loadCertificates()
    lifecycleAlertsRef.value?.refresh()
    revokedCertsRef.value?.refresh()
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Rotation Failed',
      detail: 'Failed to rotate certificate',
      life: 3000
    })
  } finally {
    isRotating.value = false
  }
}

function handleRevokeClick(domain: string) {
  selectedCert.value = allCerts.value.find(c => c.domain === domain)
  showRevokeDialog.value = true
}

async function handleConfirmRevoke() {
  if (!selectedCert.value || !revocationReason.value) {
    toast.add({
      severity: 'warn',
      summary: 'Missing Information',
      detail: 'Please select a revocation reason',
      life: 3000
    })
    return
  }

  isRevoking.value = true
  try {
    await pkiService.revokeCertificate(
      selectedCert.value.serial,
      revocationReason.value,
      selectedCert.value.domain
    )
    toast.add({
      severity: 'success',
      summary: 'Certificate Revoked',
      detail: `Certificate for ${selectedCert.value.domain} has been revoked`,
      life: 3000
    })
    showRevokeDialog.value = false
    selectedCert.value = null
    revocationReason.value = ''
    await loadCertificates()
    lifecycleAlertsRef.value?.refresh()
    revokedCertsRef.value?.refresh()
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

function handleViewDetails(cert: any) {
  selectedCert.value = cert
  showDetailsDialog.value = true
}

onMounted(() => {
  loadCertificates()
})
</script>

<style scoped>
.pki-management {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.pki-tabs {
  margin-top: 2rem;
}

.tab-content {
  min-height: 400px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.certificates-section {
  margin-top: 1rem;
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-color-secondary);
}

.loading-state p {
  margin-top: 1rem;
  font-size: 1.1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: var(--text-color-secondary);
}

.empty-icon {
  font-size: 4rem;
  color: var(--surface-400);
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.empty-state p {
  margin: 0 0 1.5rem 0;
}

/* Dialog Styles */
.cert-details {
  padding: 1rem 0;
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
  background: var(--surface-50);
  border-radius: 6px;
}

.detail-label {
  font-weight: 600;
  color: var(--text-color);
}

.detail-value {
  color: var(--text-color-secondary);
  word-break: break-all;
}

.detail-value.mono {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.status-valid {
  background: #d1fae5;
  color: #065f46;
}

.status-expiring_soon {
  background: #fef3c7;
  color: #92400e;
}

.status-critical {
  background: #fed7aa;
  color: #9a3412;
}

.status-expired {
  background: #fee2e2;
  color: #991b1b;
}

.rotate-dialog,
.revoke-dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.cert-info {
  padding: 1rem;
  background: var(--surface-100);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.confirm-text {
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 600;
  color: var(--text-color);
}

.w-full {
  width: 100%;
}

@media (max-width: 768px) {
  .pki-management {
    padding: 1rem;
  }

  .certificates-grid {
    grid-template-columns: 1fr;
  }

  .detail-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
</style>
