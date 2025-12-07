<template>
  <div class="artifacts-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">Artifacts & Manifests</h1>
        <p class="page-subtitle">
          View workflow artifacts, verify signatures, and publish to registry
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading artifacts...</p>
    </div>

    <div v-else>
      <!-- Workflows with Artifacts -->
      <div v-for="workflow in workflowsWithArtifacts" :key="workflow.workflow_id" class="workflow-card">
        <Card>
          <template #header>
            <div class="workflow-header">
              <div>
                <h3>{{ workflow.workflow_id }}</h3>
                <Tag :severity="getStatusSeverity(workflow.status)" class="status-tag">
                  {{ workflow.status }}
                </Tag>
              </div>
              <div class="workflow-meta">
                <div class="meta-item">
                  <i class="pi pi-file"></i>
                  <span>{{ workflow.artifacts?.length || 0 }} artifacts</span>
                </div>
                <div class="meta-item">
                  <i class="pi pi-calendar"></i>
                  <span>{{ formatDate(workflow.created_at) }}</span>
                </div>
              </div>
            </div>
          </template>

          <template #content>
            <!-- Artifacts List -->
            <div v-if="workflow.artifacts && workflow.artifacts.length > 0" class="artifacts-list">
              <div v-for="artifact in workflow.artifacts" :key="artifact.name" class="artifact-item">
                <div class="artifact-info">
                  <div class="artifact-header">
                    <i :class="getFileIcon(artifact.type)" class="file-icon"></i>
                    <div class="artifact-details">
                      <h4>{{ artifact.name }}</h4>
                      <div class="artifact-stats">
                        <span class="stat">
                          <i class="pi pi-check-circle"></i>
                          Verified
                        </span>
                        <span class="stat">
                          <i class="pi pi-database"></i>
                          {{ formatBytes(artifact.size) }}
                        </span>
                        <span class="stat checksum">
                          <i class="pi pi-shield"></i>
                          {{ artifact.sha256_checksum?.substring(0, 12) }}...
                        </span>
                        <Tag 
                          :severity="getProvenanceSeverity(artifact.provenance_score)" 
                          v-tooltip="'Provenance Score: ' + (artifact.provenance_score * 100) + '% AI Generated'"
                        >
                          {{ getProvenanceLabel(artifact.provenance_score) }}
                        </Tag>
                      </div>
                    </div>
                  </div>

                  <!-- Mock reputation/earnings data -->
                  <div class="artifact-metrics">
                    <div class="metric">
                      <span class="metric-label">Reputation</span>
                      <span class="metric-value">{{ getMockReputation(artifact.name) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">Earnings</span>
                      <span class="metric-value">${{ getMockEarnings(artifact.name) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">Downloads</span>
                      <span class="metric-value">{{ getMockDownloads(artifact.name) }}</span>
                    </div>
                  </div>
                </div>

                <div class="artifact-actions">
                  <Button
                    label="View"
                    icon="pi pi-eye"
                    size="small"
                    outlined
                    @click="viewArtifact(workflow.workflow_id, artifact)"
                  />
                  <Button
                    label="Verify"
                    icon="pi pi-shield"
                    size="small"
                    severity="info"
                    outlined
                    @click="verifyCryptoChain(workflow.workflow_id, artifact)"
                  />
                  <Button
                    label="Publish"
                    icon="pi pi-upload"
                    size="small"
                    severity="success"
                    outlined
                    @click="publishArtifact(workflow.workflow_id, artifact)"
                  />
                </div>
              </div>
            </div>

            <div v-else class="no-artifacts">
              <i class="pi pi-inbox"></i>
              <p>No artifacts generated yet</p>
            </div>
          </template>
        </Card>
      </div>

      <!-- Empty State -->
      <div v-if="workflowsWithArtifacts.length === 0" class="empty-state">
        <i class="pi pi-file placeholder-icon"></i>
        <h3>No Workflows Found</h3>
        <p>Submit a mission to generate artifacts</p>
        <Button
          label="Create Mission"
          icon="pi pi-plus"
          @click="() => $router.push('/missions/create')"
        />
      </div>
    </div>

    <!-- Crypto Chain Modal -->
    <CryptoChainModal
      :is-open="showCryptoChain"
      :workflow-id="selectedWorkflowId"
      :artifact-name="selectedArtifact?.name || ''"
      @close="showCryptoChain = false"
    />

    <!-- Publish Artifact Modal -->
    <PublishArtifactModal
      v-if="showPublishModal"
      :is-open="showPublishModal"
      :workflow-id="selectedWorkflowId"
      :artifact-name="selectedArtifact?.name || ''"
      @close="showPublishModal = false"
      @published="handleArtifactPublished"
    />

    <!-- Artifact Detail Dialog - Shows artifact content -->
    <Dialog
      v-model:visible="showDetailDialog"
      :header="selectedArtifact?.name"
      :style="{ width: '80vw', maxWidth: '1200px' }"
      modal
    >
      <div v-if="selectedArtifact" class="artifact-detail">
        <TabView>
            <!-- Original Details Tab -->
            <TabPanel header="Details">
                <div class="detail-grid">
                  <div class="detail-item">
                    <span class="label">File Type:</span>
                    <span class="value">{{ selectedArtifact.type }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Size:</span>
                    <span class="value">{{ formatBytes(selectedArtifact.size) }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="label">Verified:</span>
                    <Tag severity="success">
                      <i class="pi pi-check"></i> Yes
                    </Tag>
                  </div>
                  <div class="detail-item">
                    <span class="label">SHA256 Checksum:</span>
                    <span class="value checksum-full">{{ selectedArtifact.sha256_checksum }}</span>
                  </div>
                </div>

                <!-- Content Preview -->
                <div v-if="selectedArtifact.content" class="content-preview">
                  <h4>Content Preview</h4>
                  <pre><code>{{ selectedArtifact.content }}</code></pre>
                </div>
            </TabPanel>

            <!-- Turing Tape Tab -->
            <TabPanel header="Turing Tape Logs">
                <div class="turing-tape-container">
                    <div v-if="loadingTuringTape">Loading cryptographic chain...</div>
                    <pre v-else class="turing-tape-log">{{ turingTapeContent }}</pre>
                </div>
            </TabPanel>
        </TabView>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
// import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ProgressSpinner from 'primevue/progressspinner'
import { useMissionStore } from '@/stores/mission.store'
import { useRegistryStore } from '@/stores/registry.store'
import CryptoChainModal from '@/components/artifacts/CryptoChainModal.vue'
import PublishArtifactModal from '@/components/artifacts/PublishArtifactModal.vue'
import axios from 'axios'

// const router = useRouter() // Unused
const missionStore = useMissionStore()
// const registryStore = useRegistryStore() // Unused

const isLoading = ref(true)
const showDetailDialog = ref(false)
const showCryptoChain = ref(false)
const showPublishModal = ref(false)
const selectedArtifact = ref<any>(null)
const selectedWorkflowId = ref<string>('')
const workflowArtifacts = ref<Map<string, any[]>>(new Map())
const loadingTuringTape = ref(false)
const turingTapeContent = ref('')

const workflowsWithArtifacts = computed(() => {
  const workflows = Array.from(missionStore.workflows.values())
  return workflows.map(workflow => ({
    ...workflow,
    artifacts: workflowArtifacts.value.get(workflow.workflow_id) || []
  }))
})

async function loadArtifacts() {
  isLoading.value = true
  try {
    // Load workflows first
    await missionStore.fetchWorkflows()

    // Load artifacts for each workflow
    const workflows = Array.from(missionStore.workflows.values())
    for (const workflow of workflows) {
      try {
        const response = await axios.get(`/api/workflow/${workflow.workflow_id}/artifacts`)
        workflowArtifacts.value.set(workflow.workflow_id, response.data)
      } catch (error) {
        console.error(`Failed to load artifacts for ${workflow.workflow_id}:`, error)
        workflowArtifacts.value.set(workflow.workflow_id, [])
      }
    }
  } catch (error) {
    console.error('Failed to load artifacts:', error)
  } finally {
    isLoading.value = false
  }
}

function viewArtifact(workflowId: string, artifact: any) {
  selectedArtifact.value = artifact
  selectedWorkflowId.value = workflowId
  showDetailDialog.value = true
  fetchTuringTape(workflowId)
}

async function fetchTuringTape(workflowId: string) {
    loadingTuringTape.value = true
    try {
        const response = await axios.get(`/api/crypto-chain/workflow/${workflowId}/manifest/text`)
        turingTapeContent.value = response.data
    } catch (e) {
        console.error("Failed to fetch Turing Tape", e)
        turingTapeContent.value = "Failed to load cryptographic chain logs."
    } finally {
        loadingTuringTape.value = false
    }
}

function verifyCryptoChain(workflowId: string, artifact: any) {
  selectedArtifact.value = artifact
  selectedWorkflowId.value = workflowId
  showCryptoChain.value = true  // Show crypto chain verification
}

function publishArtifact(workflowId: string, artifact: any) {
  selectedArtifact.value = artifact
  selectedWorkflowId.value = workflowId
  showPublishModal.value = true
}

function handleArtifactPublished(result: any) {
    // Show success message with storage details
    let message = `✅ Published to ${result.storage_backend.toUpperCase()}!\n\nID: ${result.storage_identifier}`
    if (result.encrypted) {
        message += `\n\n🔒 ENCRYPTED\nKey: ${result.encryption_key || 'Derived from password'}`
        if (result.warning) message += `\n${result.warning}`
    }
    alert(message)
    console.log('Publication result:', result)
}

function getFileIcon(type: string): string {
  const iconMap: Record<string, string> = {
    'py': 'pi pi-file-code',
    'js': 'pi pi-code',
    'ts': 'pi pi-code',
    'json': 'pi pi-file',
    'md': 'pi pi-file-edit',
    'txt': 'pi pi-file',
  }
  return iconMap[type] || 'pi pi-file'
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

function getStatusSeverity(status: string): string {
  const severityMap: Record<string, string> = {
    'completed': 'success',
    'running': 'info',
    'failed': 'danger',
    'paused': 'warning',
    'pending': 'secondary'
  }
  return severityMap[status] || 'secondary'
}

function getProvenanceLabel(score: number): string {
  if (score === 1.0) return 'AI Native'
  if (score >= 0.5) return 'Hybrid'
  return 'Human Native'
}

function getProvenanceSeverity(score: number): string {
  if (score === 1.0) return 'success'
  if (score >= 0.5) return 'warning'
  return 'info'
}

// Mock data generators
function getMockReputation(filename: string): number {
  const hash = filename.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return 75 + (hash % 20)
}

function getMockEarnings(filename: string): number {
  const hash = filename.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return (hash % 500) + 100
}

function getMockDownloads(filename: string): number {
  const hash = filename.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
  return (hash % 1000) + 50
}

onMounted(() => {
  loadArtifacts()
})
</script>

<style scoped>
.artifacts-view {
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

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 0;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
}

.workflow-card {
  margin-bottom: 2rem;
}

.workflow-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.workflow-header h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.status-tag {
  margin-top: 0.5rem;
}

.workflow-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.artifacts-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.artifact-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  transition: all 0.2s;
}

.artifact-item:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.artifact-info {
  flex: 1;
}

.artifact-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.file-icon {
  font-size: 2rem;
  color: #667eea;
  margin-top: 0.25rem;
}

.artifact-details h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.artifact-stats {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #64748b;
}

.stat i {
  color: #10b981;
}

.stat.checksum {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.artifact-metrics {
  display: flex;
  gap: 2rem;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.metric-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.artifact-actions {
  display: flex;
  gap: 0.5rem;
}

.no-artifacts {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
}

.no-artifacts i {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
}

.placeholder-icon {
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

.artifact-detail {
  padding: 1rem 0;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-item .label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 500;
}

.detail-item .value {
  font-size: 1rem;
  color: #1e293b;
}

.checksum-full {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  word-break: break-all;
}

.content-preview {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
}

.content-preview h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  color: #1e293b;
}

.content-preview pre {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.content-preview code {
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #1e293b;
}
</style>
