<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1 class="page-title">Team Agent Dashboard</h1>
        <p class="page-subtitle">
          Multi-Agent Orchestration Platform - Overview
        </p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <ProgressSpinner />
      <p>Loading dashboard data...</p>
    </div>

    <div v-else>
      <!-- Main Stats Grid -->
      <div class="stats-grid">
        <!-- Missions Stats -->
        <Card class="stat-card missions-card">
          <template #content>
            <div class="stat-header">
              <div class="stat-icon-wrapper missions">
                <i class="pi pi-flag"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">Total Missions</div>
                <div class="stat-value">{{ missionStats.total }}</div>
                <div class="stat-detail">
                  {{ missionStats.active }} active • {{ missionStats.completed }} completed
                </div>
              </div>
            </div>
          </template>
          <template #footer>
            <router-link to="/missions" class="view-all-link">
              <i class="pi pi-arrow-right"></i> View Missions
            </router-link>
          </template>
        </Card>

        <!-- Trust Stats -->
        <Card class="stat-card trust-card">
          <template #content>
            <div class="stat-header">
              <div class="stat-icon-wrapper trust">
                <i class="pi pi-shield"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">Avg Trust Score</div>
                <div class="stat-value">{{ trustStats.averageScore.toFixed(1) }}</div>
                <div class="stat-detail">
                  {{ trustStats.totalAgents }} agents • {{ trustStats.highTrust }} high trust
                </div>
              </div>
            </div>
          </template>
          <template #footer>
            <router-link to="/trust" class="view-all-link">
              <i class="pi pi-arrow-right"></i> View Trust Dashboard
            </router-link>
          </template>
        </Card>

        <!-- PKI Stats -->
        <Card class="stat-card pki-card">
          <template #content>
            <div class="stat-header">
              <div class="stat-icon-wrapper pki">
                <i class="pi pi-lock"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">Certificate Status</div>
                <div class="stat-value">{{ pkiStats.total }}</div>
                <div class="stat-detail" :class="pkiStats.expiring > 0 ? 'warning-text' : ''">
                  {{ pkiStats.valid }} valid • {{ pkiStats.expiring }} expiring soon
                </div>
              </div>
            </div>
          </template>
          <template #footer>
            <router-link to="/pki" class="view-all-link">
              <i class="pi pi-arrow-right"></i> Manage Certificates
            </router-link>
          </template>
        </Card>

        <!-- Registry Stats -->
        <Card class="stat-card registry-card">
          <template #content>
            <div class="stat-header">
              <div class="stat-icon-wrapper registry">
                <i class="pi pi-box"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">Capabilities</div>
                <div class="stat-value">{{ registryStats.totalCapabilities }}</div>
                <div class="stat-detail">
                  {{ registryStats.totalProviders }} providers • {{ registryStats.averageTrustScore.toFixed(1) }} avg trust
                </div>
              </div>
            </div>
          </template>
          <template #footer>
            <router-link to="/registry" class="view-all-link">
              <i class="pi pi-arrow-right"></i> Browse Registry
            </router-link>
          </template>
        </Card>

        <!-- Artifacts Stats -->
        <Card class="stat-card artifacts-card">
          <template #content>
            <div class="stat-header">
              <div class="stat-icon-wrapper artifacts">
                <i class="pi pi-file"></i>
              </div>
              <div class="stat-content">
                <div class="stat-label">Total Artifacts</div>
                <div class="stat-value">{{ artifactStats.totalArtifacts }}</div>
                <div class="stat-detail">
                  ${{ artifactStats.totalEarnings }} earned • {{ artifactStats.totalDownloads }} downloads
                </div>
              </div>
            </div>
          </template>
          <template #footer>
            <router-link to="/artifacts" class="view-all-link">
              <i class="pi pi-arrow-right"></i> View Artifacts
            </router-link>
          </template>
        </Card>
      </div>

      <!-- Secondary Stats Row -->
      <div class="secondary-stats">
        <Card>
          <template #content>
            <div class="mini-stat">
              <i class="pi pi-chart-line stat-mini-icon"></i>
              <div>
                <div class="mini-stat-value">{{ registryStats.totalInvocations }}</div>
                <div class="mini-stat-label">Total Invocations</div>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #content>
            <div class="mini-stat">
              <i class="pi pi-exclamation-triangle stat-mini-icon"></i>
              <div>
                <div class="mini-stat-value">{{ trustStats.securityIncidents }}</div>
                <div class="mini-stat-label">Security Incidents</div>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #content>
            <div class="mini-stat">
              <i class="pi pi-ban stat-mini-icon"></i>
              <div>
                <div class="mini-stat-value">{{ pkiStats.revoked }}</div>
                <div class="mini-stat-label">Revoked Certificates</div>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #content>
            <div class="mini-stat">
              <i class="pi pi-dollar stat-mini-icon"></i>
              <div>
                <div class="mini-stat-value">\${{ registryStats.averagePrice.toFixed(0) }}</div>
                <div class="mini-stat-label">Avg Capability Price</div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Quick Actions -->
      <Card class="quick-actions-card">
        <template #header>
          <h2>Quick Actions</h2>
        </template>
        <template #content>
          <div class="quick-actions-grid">
            <Button
              label="Create Mission"
              icon="pi pi-plus"
              @click="() => $router.push('/missions/create')"
              class="action-button"
            />
            <Button
              label="Generate Certificate"
              icon="pi pi-shield"
              severity="secondary"
              @click="() => $router.push('/pki')"
              class="action-button"
            />
            <Button
              label="Browse Capabilities"
              icon="pi pi-box"
              severity="info"
              @click="() => $router.push('/registry')"
              class="action-button"
            />
            <Button
              label="View Trust Scores"
              icon="pi pi-chart-bar"
              severity="help"
              @click="() => $router.push('/trust')"
              class="action-button"
            />
          </div>
        </template>
      </Card>

      <!-- System Health Summary -->
      <div class="health-grid">
        <Card>
          <template #header>
            <h3>Mission Health</h3>
          </template>
          <template #content>
            <div class="health-metrics">
              <div class="health-metric">
                <span>Success Rate:</span>
                <ProgressBar 
                  :value="missionStats.successRate * 100" 
                  :showValue="true"
                  :pt="{ value: { style: 'background: #10b981' } }"
                />
              </div>
              <div class="health-stat-row">
                <span>Running:</span>
                <strong>{{ missionStats.running }}</strong>
              </div>
              <div class="health-stat-row">
                <span>Failed:</span>
                <strong class="failed-count">{{ missionStats.failed }}</strong>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #header>
            <h3>Trust Distribution</h3>
          </template>
          <template #content>
            <div class="health-metrics">
              <div class="trust-distribution">
                <div class="trust-tier">
                  <span class="trust-tier-label">High Trust (≥90):</span>
                  <Tag severity="success">{{ trustStats.highTrust }} agents</Tag>
                </div>
                <div class="trust-tier">
                  <span class="trust-tier-label">Medium Trust (75-89):</span>
                  <Tag severity="info">{{ trustStats.mediumTrust }} agents</Tag>
                </div>
                <div class="trust-tier">
                  <span class="trust-tier-label">Low Trust (<75):</span>
                  <Tag severity="warning">{{ trustStats.lowTrust }} agents</Tag>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #header>
            <h3>Certificate Health</h3>
          </template>
          <template #content>
            <div class="health-metrics">
              <div class="health-stat-row">
                <span>Valid:</span>
                <Tag severity="success">{{ pkiStats.valid }}</Tag>
              </div>
              <div class="health-stat-row">
                <span>Expiring Soon:</span>
                <Tag :severity="pkiStats.expiring > 0 ? 'warning' : 'success'">
                  {{ pkiStats.expiring }}
                </Tag>
              </div>
              <div class="health-stat-row">
                <span>Revoked:</span>
                <Tag :severity="pkiStats.revoked > 0 ? 'danger' : 'success'">
                  {{ pkiStats.revoked }}
                </Tag>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import { useMissionStore } from '@/stores/mission.store'
import { useTrustStore } from '@/stores/trust.store'
import { usePKIStore } from '@/stores/pki.store'
import { useRegistryStore } from '@/stores/registry.store'
import axios from 'axios'

const router = useRouter()
const missionStore = useMissionStore()
const trustStore = useTrustStore()
const pkiStore = usePKIStore()
const registryStore = useRegistryStore()

const isLoading = ref(true)
const allArtifacts = ref<any[]>([])

// Mission Statistics
const missionStats = computed(() => {
  const missions = Array.from(missionStore.missions.values())
  const workflows = Array.from(missionStore.workflows.values())
  
  return {
    total: missions.length,
    active: workflows.filter(w => w.status === 'running').length,
    completed: workflows.filter(w => w.status === 'completed').length,
    running: workflows.filter(w => w.status === 'running').length,
    failed: workflows.filter(w => w.status === 'failed').length,
    paused: workflows.filter(w => w.status === 'paused').length,
    successRate: workflows.length > 0 
      ? workflows.filter(w => w.status === 'completed').length / workflows.length
      : 0
  }
})

// Trust Statistics
const trustStats = computed(() => {
  const agents = Array.from(trustStore.agents.values())
  const avgScore = agents.length > 0
    ? agents.reduce((sum, a) => sum + a.trust_score, 0) / agents.length
    : 0
  
  return {
    totalAgents: agents.length,
    averageScore: avgScore,
    highTrust: agents.filter(a => a.trust_score >= 90).length,
    mediumTrust: agents.filter(a => a.trust_score >= 75 && a.trust_score < 90).length,
    lowTrust: agents.filter(a => a.trust_score < 75).length,
    securityIncidents: agents.reduce((sum, a) => sum + a.security_incidents, 0)
  }
})

// PKI Statistics
const pkiStats = computed(() => {
  const certs = Array.from(pkiStore.certificates.values())
  
  return {
    total: certs.length,
    valid: certs.filter(c => c.status === 'valid').length,
    expiring: pkiStore.expiringCertificates.length,
    revoked: pkiStore.revokedCertificates.length
  }
})

// Registry Statistics
const registryStats = computed(() => {
  return {
    totalCapabilities: registryStore.statistics?.total_capabilities || 0,
    totalProviders: registryStore.statistics?.total_providers || 0,
    averageTrustScore: registryStore.statistics?.average_trust_score || 0,
    averagePrice: registryStore.statistics?.average_price || 0,
    totalInvocations: registryStore.statistics?.total_invocations || 0
  }
})

// Artifact Statistics
const artifactStats = computed(() => {
  // Calculate total earnings and downloads using mock data
  let totalEarnings = 0
  let totalDownloads = 0

  allArtifacts.value.forEach(artifact => {
    const hash = artifact.name.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0)
    totalEarnings += (hash % 500) + 100
    totalDownloads += (hash % 1000) + 50
  })

  return {
    totalArtifacts: allArtifacts.value.length,
    totalEarnings: totalEarnings,
    totalDownloads: totalDownloads,
    averageReputation: allArtifacts.value.length > 0 ? 85 : 0
  }
})

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([
      missionStore.fetchMissions(),
      missionStore.fetchWorkflows(),
      trustStore.fetchAllAgents(),
      pkiStore.fetchAllCertificates(),
      registryStore.fetchStatistics()
    ])

    // Load artifacts for all workflows
    const workflows = Array.from(missionStore.workflows.values())
    const artifactPromises = workflows.map(async workflow => {
      try {
        const response = await axios.get(`/api/workflow/${workflow.workflow_id}/artifacts`)
        return response.data
      } catch (error) {
        console.error(`Failed to load artifacts for ${workflow.workflow_id}:`, error)
        return []
      }
    })

    const artifactArrays = await Promise.all(artifactPromises)
    allArtifacts.value = artifactArrays.flat()
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1600px;
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
  padding: 6rem 0;
  color: #64748b;
}

.loading-state p {
  margin-top: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stat-icon-wrapper.missions {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon-wrapper.trust {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.stat-icon-wrapper.pki {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-icon-wrapper.registry {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-icon-wrapper.artifacts {
  background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-detail {
  font-size: 0.875rem;
  color: #64748b;
}

.warning-text {
  color: #f59e0b;
  font-weight: 600;
}

.view-all-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
  transition: gap 0.2s;
}

.view-all-link:hover {
  gap: 0.75rem;
}

.secondary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-mini-icon {
  font-size: 2rem;
  color: #667eea;
}

.mini-stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e293b;
}

.mini-stat-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quick-actions-card {
  margin-bottom: 2rem;
}

.quick-actions-card h2 {
  margin: 0;
  padding: 1.5rem 1.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-button {
  width: 100%;
}

.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.health-grid h3 {
  margin: 0;
  padding: 1.5rem 1.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}

.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.health-metric {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.health-metric span {
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
}

.health-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.health-stat-row:last-child {
  border-bottom: none;
}

.health-stat-row span {
  font-size: 0.875rem;
  color: #64748b;
}

.health-stat-row strong {
  color: #1e293b;
  font-weight: 600;
}

.failed-count {
  color: #ef4444;
}

.trust-distribution {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.trust-tier {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
}

.trust-tier-label {
  font-size: 0.875rem;
  color: #64748b;
}
</style>
