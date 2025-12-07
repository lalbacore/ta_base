<template>
  <div class="governance-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Governance & Policy</h1>
        <p class="page-subtitle">
          Manage policies and ensure mission compliance
        </p>
      </div>
    </div>

    <TabView>
      <!-- Policy Configuration Tab -->
      <TabPanel header="Active Policy">
        <Card>
          <template #content>
            <div v-if="policyConfig" class="policy-grid">
              <div class="policy-item">
                <label>Minimum Trust Score</label>
                <div class="policy-value">
                  <ProgressBar :value="policyConfig.min_trust_score" :showValue="true" />
                </div>
              </div>

              <div class="policy-item">
                <label>Maximum Cost Per Mission</label>
                <div class="policy-value">
                  <span class="cost-value">\${{ policyConfig.max_cost_per_mission }}</span>
                </div>
              </div>

              <div class="policy-item">
                <label>Auto-Approve Threshold</label>
                <div class="policy-value">
                  <ProgressBar :value="policyConfig.auto_approve_threshold" :showValue="true" 
                               :pt="{ value: { style: 'background: #10b981' } }" />
                </div>
              </div>

              <div class="policy-item">
                <label>Security Review Required</label>
                <div class="policy-value">
                  <Tag :severity="policyConfig.require_security_review ? 'success' : 'secondary'">
                    {{ policyConfig.require_security_review ? 'Yes' : 'No' }}
                  </Tag>
                </div>
              </div>

              <div class="policy-item">
                <label>Code Review Required</label>
                <div class="policy-value">
                  <Tag :severity="policyConfig.require_code_review ? 'success' : 'secondary'">
                    {{ policyConfig.require_code_review ? 'Yes' : 'No' }}
                  </Tag>
                </div>
              </div>

              <div class="policy-item">
                <label>Breakpoints Enabled</label>
                <div class="policy-value">
                  <Tag :severity="policyConfig.enable_breakpoints ? 'info' : 'secondary'">
                    {{ policyConfig.enable_breakpoints ? 'Enabled' : 'Disabled' }}
                  </Tag>
                </div>
              </div>

              <div class="policy-item full-width">
                <label>Allowed Languages</label>
                <div class="policy-value">
                  <div class="language-tags">
                    <Chip v-for="lang in policyConfig.allowed_languages" :key="lang" :label="lang" />
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Policy Management Tab -->
      <TabPanel header="⚙️ Policy Management">
        <Card>
          <template #header>
            <div class="policy-management-header">
              <div>
                <h2>Policy Management</h2>
                <p>Create and manage governance policies (Government agents only)</p>
              </div>
              <Button
                label="Create Policy"
                icon="pi pi-plus"
                @click="showPolicyDialog(null)"
                severity="success"
              />
            </div>
          </template>
          <template #content>
            <DataTable
              :value="policies"
              :paginator="true"
              :rows="10"
              responsiveLayout="scroll"
              :loading="isLoadingPolicies"
            >
              <Column field="name" header="Policy Name" sortable>
                <template #body="slotProps">
                  <div class="policy-name-cell">
                    <strong>{{ slotProps.data.name }}</strong>
                    <Tag
                      v-if="slotProps.data.is_active"
                      severity="success"
                      value="ACTIVE"
                      class="active-badge"
                    />
                  </div>
                </template>
              </Column>
              <Column field="description" header="Description">
                <template #body="slotProps">
                  <span class="description-text">{{ slotProps.data.description || '—' }}</span>
                </template>
              </Column>
              <Column field="min_trust_score" header="Min Trust" sortable>
                <template #body="slotProps">
                  <ProgressBar
                    :value="slotProps.data.min_trust_score"
                    :showValue="true"
                    style="width: 100px"
                  />
                </template>
              </Column>
              <Column field="max_cost_per_mission" header="Max Cost" sortable>
                <template #body="slotProps">
                  ${{ slotProps.data.max_cost_per_mission }}
                </template>
              </Column>
              <Column field="allowed_languages" header="Languages">
                <template #body="slotProps">
                  <div class="language-chips">
                    <Chip
                      v-for="lang in slotProps.data.allowed_languages.slice(0, 2)"
                      :key="lang"
                      :label="lang"
                      class="small-chip"
                    />
                    <Chip
                      v-if="slotProps.data.allowed_languages.length > 2"
                      :label="`+${slotProps.data.allowed_languages.length - 2}`"
                      class="small-chip"
                    />
                  </div>
                </template>
              </Column>
              <Column header="Actions" style="width: 200px">
                <template #body="slotProps">
                  <div class="action-buttons">
                    <Button
                      v-if="!slotProps.data.is_active"
                      icon="pi pi-check"
                      @click="activatePolicy(slotProps.data.id)"
                      severity="success"
                      text
                      rounded
                      v-tooltip.top="'Activate'"
                    />
                    <Button
                      icon="pi pi-pencil"
                      @click="showPolicyDialog(slotProps.data)"
                      severity="info"
                      text
                      rounded
                      v-tooltip.top="'Edit'"
                    />
                    <Button
                      v-if="!slotProps.data.is_active"
                      icon="pi pi-trash"
                      @click="confirmDeletePolicy(slotProps.data)"
                      severity="danger"
                      text
                      rounded
                      v-tooltip.top="'Delete'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Decision History Tab -->
      <TabPanel header="Decision History">
        <Card>
          <template #content>
            <DataTable :value="decisions" :paginator="true" :rows="10" responsiveLayout="scroll">
              <Column field="workflow_id" header="Workflow ID" sortable></Column>
              <Column field="decision" header="Decision" sortable>
                <template #body="slotProps">
                  <Tag :severity="slotProps.data.decision === 'approved' ? 'success' : 'danger'">
                    {{ slotProps.data.decision }}
                  </Tag>
                </template>
              </Column>
              <Column field="trust_score" header="Trust Score" sortable>
                <template #body="slotProps">
                  <ProgressBar :value="slotProps.data.trust_score" :showValue="true" 
                               style="width: 120px" />
                </template>
              </Column>
              <Column field="policy_violations" header="Violations" sortable>
                <template #body="slotProps">
                  <Tag :severity="slotProps.data.policy_violations > 0 ? 'danger' : 'success'">
                    {{ slotProps.data.policy_violations }}
                  </Tag>
                </template>
              </Column>
              <Column field="reason" header="Reason"></Column>
              <Column field="timestamp" header="Timestamp">
                <template #body="slotProps">
                  {{ formatDate(slotProps.data.timestamp) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>

      <!-- Compliance Checker Tab (Easter Egg!) -->
      <TabPanel header="🔍 Compliance Checker">
        <Card>
          <template #header>
            <div class="checker-header">
              <i class="pi pi-search"></i>
              <h2>Mission Compliance Checker</h2>
              <p>Test how a mission compares against current policies</p>
            </div>
          </template>
          <template #content>
            <div class="compliance-checker">
              <div class="mission-input-section">
                <h3>Mission Configuration</h3>
                <div class="input-grid">
                  <div class="input-group">
                    <label for="mission-trust">Min Trust Score</label>
                    <InputNumber
                      id="mission-trust"
                      v-model="testMission.min_trust_score"
                      :min="0"
                      :max="100"
                      showButtons
                    />
                  </div>

                  <div class="input-group">
                    <label for="mission-cost">Max Cost</label>
                    <InputNumber
                      id="mission-cost"
                      v-model="testMission.max_cost"
                      :min="0"
                      prefix="$"
                      showButtons
                    />
                  </div>

                  <div class="input-group full-width">
                    <label>Required Capabilities</label>
                    <MultiSelect
                      v-model="testMission.capability_types"
                      :options="capabilityTypes"
                      placeholder="Select capability types"
                      display="chip"
                      class="w-full"
                    />
                  </div>
                </div>

                <Button
                  label="Check Compliance"
                  icon="pi pi-check-circle"
                  @click="checkCompliance"
                  :loading="isChecking"
                  class="check-button"
                />
              </div>

              <!-- Compliance Report -->
              <div v-if="complianceReport" class="compliance-report">
                <div class="report-header" :class="'status-' + complianceReport.status">
                  <div class="status-badge">
                    <i :class="getStatusIcon()"></i>
                    <span>{{ formatStatus(complianceReport.status) }}</span>
                  </div>
                  <div class="compliance-score">
                    <span class="score-label">Compliance Score</span>
                    <span class="score-value">{{ complianceReport.compliance_score }}%</span>
                  </div>
                </div>

                <div class="report-summary">
                  <div class="summary-stat">
                    <i class="pi pi-check-circle" style="color: #10b981"></i>
                    <span>{{ complianceReport.summary.satisfied_count }} Satisfied</span>
                  </div>
                  <div class="summary-stat">
                    <i class="pi pi-exclamation-triangle" style="color: #f59e0b"></i>
                    <span>{{ complianceReport.summary.warnings_count }} Warnings</span>
                  </div>
                  <div class="summary-stat">
                    <i class="pi pi-times-circle" style="color: #ef4444"></i>
                    <span>{{ complianceReport.summary.violations_count }} Violations</span>
                  </div>
                </div>

                <!-- Violations -->
                <div v-if="complianceReport.violations.length > 0" class="policy-section violations">
                  <h4><i class="pi pi-times-circle"></i> Policy Violations</h4>
                  <Message
                    v-for="(violation, idx) in complianceReport.violations"
                    :key="'v-' + idx"
                    severity="error"
                    :closable="false"
                  >
                    <strong>{{ formatPolicyName(violation.policy) }}</strong>
                    <p>{{ violation.message }}</p>
                    <small>Required: {{ violation.required }} | Actual: {{ violation.actual }}</small>
                  </Message>
                </div>

                <!-- Warnings -->
                <div v-if="complianceReport.warnings.length > 0" class="policy-section warnings">
                  <h4><i class="pi pi-exclamation-triangle"></i> Warnings</h4>
                  <Message
                    v-for="(warning, idx) in complianceReport.warnings"
                    :key="'w-' + idx"
                    severity="warn"
                    :closable="false"
                  >
                    <strong>{{ formatPolicyName(warning.policy) }}</strong>
                    <p>{{ warning.message }}</p>
                  </Message>
                </div>

                <!-- Satisfied Policies -->
                <div v-if="complianceReport.satisfied.length > 0" class="policy-section satisfied">
                  <h4><i class="pi pi-check-circle"></i> Satisfied Policies</h4>
                  <Message
                    v-for="(satisfied, idx) in complianceReport.satisfied"
                    :key="'s-' + idx"
                    severity="success"
                    :closable="false"
                  >
                    <strong>{{ formatPolicyName(satisfied.policy) }}</strong>
                    <p>{{ satisfied.message }}</p>
                  </Message>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </TabPanel>

      <!-- Certificate Management Tab (Break the Mesh) -->
      <TabPanel header="🔐 Certificate Management">
        <Card>
          <template #header>
            <div class="checker-header">
              <i class="pi pi-lock"></i>
              <h2>Crypto Chain Management</h2>
              <p>Manage PKI certificates and revocation (Danger Zone)</p>
            </div>
          </template>
          <template #content>
            <DataTable :value="certificatesList" :loading="isLoadingCertificates" responsiveLayout="scroll">
              <Column field="domain" header="Trust Domain" sortable>
                <template #body="slotProps">
                  <div class="domain-badge">
                    <i :class="getDomainIcon(slotProps.data.domain)"></i>
                    <span>{{ formatDomain(slotProps.data.domain) }}</span>
                  </div>
                </template>
              </Column>
              <Column field="serial" header="Serial Number">
                <template #body="slotProps">
                  <code class="serial-code" v-tooltip="slotProps.data.serial">
                    {{ shortenSerial(slotProps.data.serial) }}
                  </code>
                </template>
              </Column>
              <Column field="status" header="Status" sortable>
                <template #body="slotProps">
                  <Tag :severity="getStatusSeverity(slotProps.data.status)" :value="formatStatus(slotProps.data.status)" />
                </template>
              </Column>
              <Column field="not_after" header="Expires">
                 <template #body="slotProps">
                  {{ formatDate(slotProps.data.not_after) }}
                </template>
              </Column>
              <Column header="Actions">
                <template #body="slotProps">
                  <Button 
                    v-if="slotProps.data.status === 'valid' || slotProps.data.status === 'expiring_soon'"
                    label="Revoke" 
                    icon="pi pi-ban" 
                    severity="danger" 
                    class="p-button-sm p-button-outlined"
                    @click="confirmRevocation(slotProps.data)"
                    v-tooltip="'Permanently invalidate this certificate'"
                  />
                  <span v-else class="text-gray-500 italic">Revoked</span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </TabPanel>
    </TabView>

    <!-- Revocation Dialog -->
    <Dialog v-model:visible="showRevokeDialog" header="Confirm Certificate Revocation" :modal="true" class="p-fluid" :style="{ width: '450px' }">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem; color: #ef4444" />
        <div v-if="selectedCertificate">
          <p class="mb-3">Are you sure you want to revoke the certificate for <strong>{{ formatDomain(selectedCertificate.domain) }}</strong>?</p>
          <p class="text-red-500 font-bold mb-4">⚠️ This action cannot be undone. "Breaking the Mesh" will invalidate all artifacts signed by this chain.</p>
          
          <div class="field">
            <label for="reason">Revocation Reason</label>
            <Dropdown 
              id="reason" 
              v-model="revocationReason" 
              :options="revocationReasons" 
              optionLabel="label" 
              optionValue="value" 
              placeholder="Select a reason" 
              class="w-full"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showRevokeDialog = false" />
        <Button label="Revoke Certificate" icon="pi pi-ban" class="p-button-danger" @click="executeRevocation" :loading="isRevoking" />
      </template>
    </Dialog>

    <!-- Policy Editor Dialog -->
    <PolicyEditorDialog
      v-model:visible="showPolicyEditorDialog"
      :policy="selectedPolicy"
      @save="handleSavePolicy"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Card from 'primevue/card'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Chip from 'primevue/chip'
import ProgressBar from 'primevue/progressbar'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import MultiSelect from 'primevue/multiselect'
import Message from 'primevue/message'
import { useGovernanceStore } from '@/stores/governance.store'
import governanceService from '@/services/governance.service'
import { usePKIStore } from '@/stores/pki.store'
import PolicyEditorDialog from '@/components/governance/PolicyEditorDialog.vue'
import type { ComplianceReport, Policy } from '@/types/governance.types'
import Dialog from 'primevue/dialog'
import Dropdown from 'primevue/dropdown'

const toast = useToast()
const confirm = useConfirm()
const governanceStore = useGovernanceStore()
const pkiStore = usePKIStore()

const policyConfig = computed(() => governanceStore.policyConfig)
const policies = computed(() => governanceStore.policies)
const decisions = computed(() => governanceStore.decisions)
const isChecking = ref(false)
const isLoadingPolicies = ref(false)
const complianceReport = ref<ComplianceReport | null>(null)

// Policy Management State
const showPolicyEditorDialog = ref(false)
const selectedPolicy = ref<Policy | null>(null)

const testMission = ref({
  min_trust_score: 80,
  max_cost: 200,
  capability_types: [] as string[]
})

const capabilityTypes = [
  'code_generation',
  'security_audit',
  'testing',
  'deployment',
  'code_review',
  'data_analysis',
  'documentation'
]

async function checkCompliance() {
  isChecking.value = true
  try {
    const missionData = {
      min_trust_score: testMission.value.min_trust_score,
      max_cost: testMission.value.max_cost,
      required_capabilities: testMission.value.capability_types.map(type => ({
        capability_type: type
      }))
    }

    complianceReport.value = await governanceService.checkMissionCompliance(missionData)

    toast.add({
      severity: complianceReport.value.status === 'fully_compliant' ? 'success' : 'warn',
      summary: 'Compliance Check Complete',
      detail: `Score: ${complianceReport.value.compliance_score}%`,
      life: 3000
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Check Failed',
      detail: 'Failed to check compliance',
      life: 3000
    })
  } finally {
    isChecking.value = false
  }
}

function getStatusIcon(): string {
  if (!complianceReport.value) return ''
  const iconMap = {
    fully_compliant: 'pi pi-check-circle',
    compliant_with_warnings: 'pi pi-exclamation-triangle',
    non_compliant: 'pi pi-times-circle'
  }
  return iconMap[complianceReport.value.status]
}

function formatStatus(status: string): string {
  const statusMap: Record<string, string> = {
    fully_compliant: 'Fully Compliant',
    compliant_with_warnings: 'Compliant with Warnings',
    non_compliant: 'Non-Compliant'
  }
  return statusMap[status] || status
}

function formatPolicyName(policy: string): string {
  return policy.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ')
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}


// PKI Management
const isLoadingCertificates = ref(false)
const showRevokeDialog = ref(false)
const selectedCertificate = ref<any>(null)
const isRevoking = ref(false)
const revocationReason = ref('UNSPECIFIED')

const certificatesList = computed(() => Array.from(pkiStore.certificates.values()))

const revocationReasons = [
  { label: 'Unspecified', value: 'UNSPECIFIED' },
  { label: 'Key Compromise', value: 'KEY_COMPROMISE' },
  { label: 'CA Compromise', value: 'CA_COMPROMISE' },
  { label: 'Affiliation Changed', value: 'AFFILIATION_CHANGED' },
  { label: 'Superseded', value: 'SUPERSEDED' },
  { label: 'Cessation of Operation', value: 'CESSATION_OF_OPERATION' },
]

function getDomainIcon(domain: string): string {
  const map: Record<string, string> = {
    government: 'pi pi-verified',
    execution: 'pi pi-cog',
    logging: 'pi pi-book'
  }
  return map[domain] || 'pi pi-file'
}

function formatDomain(domain: string): string {
  return domain.charAt(0).toUpperCase() + domain.slice(1)
}

function shortenSerial(serial: string): string {
  return serial ? `${serial.substring(0, 8)}...` : 'Unknown'
}

function getStatusSeverity(status: string): string {
  switch (status) {
    case 'valid': return 'success'
    case 'expiring_soon': return 'warning'
    case 'expired': 
    case 'revoked': return 'danger'
    default: return 'info'
  }
}

function confirmRevocation(cert: any) {
  selectedCertificate.value = cert
  revocationReason.value = 'UNSPECIFIED'
  showRevokeDialog.value = true
}

async function executeRevocation() {
  if (!selectedCertificate.value) return
  
  isRevoking.value = true
  try {
    await pkiStore.revokeCertificate(selectedCertificate.value.serial, revocationReason.value)
    toast.add({
      severity: 'success',
      summary: 'Certificate Revoked',
      detail: 'The certificate has been permanently revoked.',
      life: 5000
    })
    showRevokeDialog.value = false
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Revocation Failed',
      detail: error.body?.error || 'Failed to revoke certificate',
      life: 5000
    })
  } finally {
    isRevoking.value = false
  }
}

// Policy Management Functions

function showPolicyDialog(policy: Policy | null) {
  selectedPolicy.value = policy
  showPolicyEditorDialog.value = true
}

async function handleSavePolicy(policyData: any) {
  try {
    if (selectedPolicy.value) {
      // Update existing policy
      await governanceStore.updatePolicy(selectedPolicy.value.id, policyData)
      toast.add({
        severity: 'success',
        summary: 'Policy Updated',
        detail: `Policy "${policyData.name}" has been updated`,
        life: 3000
      })
    } else {
      // Create new policy
      await governanceStore.createPolicy(policyData)
      toast.add({
        severity: 'success',
        summary: 'Policy Created',
        detail: `Policy "${policyData.name}" has been created`,
        life: 3000
      })
    }
    await governanceStore.fetchPolicies()
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.response?.data?.error || 'Failed to save policy',
      life: 5000
    })
  }
}

async function activatePolicy(policyId: number) {
  try {
    await governanceStore.activatePolicy(policyId)
    toast.add({
      severity: 'success',
      summary: 'Policy Activated',
      detail: 'The policy has been activated',
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Activation Failed',
      detail: error.response?.data?.error || 'Failed to activate policy',
      life: 5000
    })
  }
}

function confirmDeletePolicy(policy: Policy) {
  confirm.require({
    message: `Are you sure you want to delete the policy "${policy.name}"? This action cannot be undone.`,
    header: 'Delete Policy',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: 'Delete',
    rejectLabel: 'Cancel',
    acceptClass: 'p-button-danger',
    accept: () => deletePolicy(policy.id)
  })
}

async function deletePolicy(policyId: number) {
  try {
    await governanceStore.deletePolicy(policyId)
    toast.add({
      severity: 'success',
      summary: 'Policy Deleted',
      detail: 'The policy has been deleted',
      life: 3000
    })
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Deletion Failed',
      detail: error.response?.data?.error || 'Failed to delete policy',
      life: 5000
    })
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      governanceStore.fetchPolicyConfig(),
      governanceStore.fetchPolicies(),
      governanceStore.fetchDecisions(),
      pkiStore.fetchAllCertificates()
    ])
  } catch (error) {
    console.error('Failed to load governance data:', error)
  }
})
</script>

<style scoped>
.governance-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
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

.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.policy-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.policy-item.full-width {
  grid-column: 1 / -1;
}

.policy-item label {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.875rem;
}

.policy-value {
  display: flex;
  align-items: center;
}

.cost-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.language-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.checker-header {
  padding: 1.5rem;
  text-align: center;
}

.checker-header i {
  font-size: 2.5rem;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.checker-header h2 {
  margin: 0.5rem 0 0.25rem;
  color: #1e293b;
  font-size: 1.5rem;
}

.checker-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.compliance-checker {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.mission-input-section h3 {
  margin-bottom: 1rem;
  color: #1e293b;
  font-size: 1.125rem;
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group.full-width {
  grid-column: 1 / -1;
}

.input-group label {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}

.check-button {
  width: 100%;
}

.compliance-report {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.report-header {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-header.status-fully_compliant {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
}

.report-header.status-compliant_with_warnings {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.report-header.status-non_compliant {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.25rem;
  font-weight: 700;
}

.status-fully_compliant .status-badge {
  color: #059669;
}

.status-compliant_with_warnings .status-badge {
  color: #d97706;
}

.status-non_compliant .status-badge {
  color: #dc2626;
}

.compliance-score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.score-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.score-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1e293b;
}

.report-summary {
  display: flex;
  justify-content: space-around;
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.summary-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #1e293b;
}

.domain-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
}

.serial-code {
    font-family: monospace;
    background: #f1f5f9;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #475569;
}

.summary-stat i {
  font-size: 1.25rem;
}

.policy-section {
  padding: 1.5rem;
}

.policy-section h4 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 1.125rem;
  color: #1e293b;
}

.policy-section.violations h4 {
  color: #dc2626;
}

.policy-section.warnings h4 {
  color: #d97706;
}

.policy-section.satisfied h4 {
  color: #059669;
}

.policy-section :deep(.p-message) {
  margin-bottom: 0.75rem;
}

.policy-section :deep(.p-message:last-child) {
  margin-bottom: 0;
}

.policy-section :deep(.p-message p) {
  margin: 0.25rem 0;
}

.policy-section :deep(.p-message small) {
  color: #64748b;
  font-size: 0.75rem;
}

/* Policy Management Styles */
.policy-management-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.policy-management-header h2 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  color: #1e293b;
}

.policy-management-header p {
  margin: 0;
  color: #64748b;
  font-size: 0.875rem;
}

.policy-name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.active-badge {
  font-size: 0.65rem;
  padding: 0.25rem 0.5rem;
}

.description-text {
  color: #64748b;
  font-size: 0.875rem;
}

.language-chips {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.small-chip {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  justify-content: center;
}
</style>
