<template>
  <div class="revoked-certificates">
    <div class="revoked-header">
      <div class="header-left">
        <h3>Revoked Certificates</h3>
        <Tag :value="`${revokedCerts.length} revoked`" severity="danger" />
      </div>
      <div class="header-controls">
        <Dropdown
          v-model="selectedDomain"
          :options="domainOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="All Domains"
          @change="handleDomainFilter"
          class="domain-filter"
        />
        <Button
          label="Refresh"
          icon="pi pi-refresh"
          size="small"
          @click="loadRevokedCertificates"
          :loading="loading"
        />
      </div>
    </div>

    <DataTable
      :value="revokedCerts"
      :loading="loading"
      :paginator="revokedCerts.length > 10"
      :rows="10"
      :rowsPerPageOptions="[10, 25, 50]"
      stripedRows
      showGridlines
      responsiveLayout="scroll"
      filterDisplay="row"
      v-model:filters="filters"
      :globalFilterFields="['serial_number', 'trust_domain', 'reason', 'revoked_by']"
    >
      <template #empty>
        <div class="empty-state">
          <i class="pi pi-check-circle" style="font-size: 3rem; color: var(--green-500)"></i>
          <p>No revoked certificates</p>
        </div>
      </template>

      <Column field="serial_number" header="Serial Number" :sortable="true" style="min-width: 200px">
        <template #body="{ data }">
          <code class="serial-code">{{ data.serial_number }}</code>
        </template>
        <template #filter="{ filterModel, filterCallback }">
          <InputText
            v-model="filterModel.value"
            type="text"
            @input="filterCallback()"
            placeholder="Search serial"
            class="p-column-filter"
          />
        </template>
      </Column>

      <Column field="trust_domain" header="Domain" :sortable="true" style="min-width: 120px">
        <template #body="{ data }">
          <Tag :value="data.trust_domain.toUpperCase()" :severity="getDomainSeverity(data.trust_domain)" />
        </template>
      </Column>

      <Column field="reason" header="Reason" :sortable="true" style="min-width: 150px">
        <template #body="{ data }">
          <Tag :value="formatReason(data.reason)" :severity="getReasonSeverity(data.reason)" />
        </template>
      </Column>

      <Column field="revoked_by" header="Revoked By" :sortable="true" style="min-width: 120px">
        <template #body="{ data }">
          <span class="revoked-by">{{ data.revoked_by || 'N/A' }}</span>
        </template>
      </Column>

      <Column field="revocation_date" header="Revocation Date" :sortable="true" style="min-width: 180px">
        <template #body="{ data }">
          {{ formatDate(data.revocation_date) }}
        </template>
      </Column>

      <Column field="cert_subject" header="Subject" style="min-width: 200px">
        <template #body="{ data }">
          <span class="cert-subject">{{ data.cert_subject || 'N/A' }}</span>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { FilterMatchMode } from 'primevue/api'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dropdown from 'primevue/dropdown'
import InputText from 'primevue/inputtext'
import type { RevocationInfo } from '@/types/pki.types'
import pkiService from '@/services/pki.service'

const revokedCerts = ref<RevocationInfo[]>([])
const loading = ref(false)
const selectedDomain = ref<string | null>(null)
const filters = ref({
  serial_number: { value: null, matchMode: FilterMatchMode.CONTAINS },
  trust_domain: { value: null, matchMode: FilterMatchMode.EQUALS },
  reason: { value: null, matchMode: FilterMatchMode.EQUALS },
  revoked_by: { value: null, matchMode: FilterMatchMode.CONTAINS }
})

const domainOptions = [
  { label: 'All Domains', value: null },
  { label: 'Government', value: 'government' },
  { label: 'Execution', value: 'execution' },
  { label: 'Logging', value: 'logging' }
]

async function loadRevokedCertificates() {
  loading.value = true
  try {
    revokedCerts.value = await pkiService.getRevokedCertificates(
      selectedDomain.value || undefined,
      100
    )
  } catch (error) {
    console.error('Failed to load revoked certificates:', error)
  } finally {
    loading.value = false
  }
}

function handleDomainFilter() {
  loadRevokedCertificates()
}

function getDomainSeverity(domain: string): string {
  const severities: Record<string, string> = {
    government: 'danger',
    execution: 'warning',
    logging: 'info'
  }
  return severities[domain] || 'secondary'
}

function getReasonSeverity(reason: string): string {
  const severities: Record<string, string> = {
    KEY_COMPROMISE: 'danger',
    CA_COMPROMISE: 'danger',
    AFFILIATION_CHANGED: 'warning',
    SUPERSEDED: 'info',
    CESSATION_OF_OPERATION: 'secondary',
    CERTIFICATE_HOLD: 'warning',
    PRIVILEGE_WITHDRAWN: 'warning',
    UNSPECIFIED: 'secondary'
  }
  return severities[reason] || 'secondary'
}

function formatReason(reason: string): string {
  return reason.replace(/_/g, ' ')
}

function formatDate(dateString: string): string {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch {
    return dateString
  }
}

onMounted(() => {
  loadRevokedCertificates()
})

defineExpose({
  refresh: loadRevokedCertificates
})
</script>

<style scoped>
.revoked-certificates {
  margin-top: 2rem;
}

.revoked-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
}

.header-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.domain-filter {
  min-width: 180px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-color-secondary);
}

.empty-state p {
  margin-top: 1rem;
  font-size: 1.1rem;
}

.serial-code {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  background: var(--surface-100);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: var(--primary-color);
}

.revoked-by {
  font-weight: 500;
}

.cert-subject {
  font-size: 0.9rem;
  color: var(--text-color-secondary);
}
</style>
