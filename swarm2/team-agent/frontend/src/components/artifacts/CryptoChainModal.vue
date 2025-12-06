<template>
  <Dialog
    :visible="isOpen"
    :header="`Crypto Chain: ${artifactName}`"
    :style="{ width: '90vw', height: '90vh' }"
    modal
    :closable="true"
    @update:visible="(val) => !val && handleClose()"
  >
    <div class="crypto-chain-container">
      <!-- Header Stats -->
      <div class="chain-stats">
        <div class="stat-card" :class="chainData?.chain_integrity ? 'success' : 'danger'">
          <i :class="chainData?.chain_integrity ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"></i>
          <div>
            <div class="stat-label">Chain Integrity</div>
            <div class="stat-value">{{ chainData?.chain_integrity ? 'VERIFIED' : 'COMPROMISED' }}</div>
          </div>
        </div>

        <div class="stat-card">
          <i class="pi pi-shield"></i>
          <div>
            <div class="stat-label">Overall Trust Score</div>
            <div class="stat-value">{{ chainData?.overall_trust_score }}%</div>
          </div>
        </div>

        <div class="stat-card" :class="weakLinkSeverity">
          <i class="pi pi-link"></i>
          <div>
            <div class="stat-label">Weak Links</div>
            <div class="stat-value">{{ chainData?.weak_links?.length || 0 }}</div>
          </div>
        </div>

        <div class="stat-card">
          <i class="pi pi-sitemap"></i>
          <div>
            <div class="stat-label">Chain Nodes</div>
            <div class="stat-value">{{ chainData?.graph?.nodes?.length || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- Graph Visualization -->
      <Card class="graph-card">
        <template #content>
          <div ref="networkContainer" class="network-container"></div>
        </template>
      </Card>

      <!-- Weak Links & Violations -->
      <div v-if="chainData?.weak_links && chainData.weak_links.length > 0" class="weak-links-panel">
        <h4>
          <i class="pi pi-exclamation-triangle"></i>
          Security Issues Detected
        </h4>
        <div class="weak-link-list">
          <Message
            v-for="(link, index) in chainData.weak_links"
            :key="index"
            :severity="getSeverityType(link.severity)"
            :closable="false"
          >
            <strong>{{ link.type.replace(/_/g, ' ').toUpperCase() }}</strong>: {{ link.message }}
          </Message>
        </div>
      </div>

      <!-- Simulate Breaks (Easter Egg Controls) -->
      <div class="break-simulator">
        <h4>
          <i class="pi pi-bolt"></i>
          Break Crypto Chain (Simulation)
        </h4>
        <div class="break-buttons">
          <Button
            label="Trust Violation"
            icon="pi pi-user-minus"
            severity="warning"
            size="small"
            @click="simulateBreak('trust_violation')"
          />
          <Button
            label="Invalid Signature"
            icon="pi pi-times-circle"
            severity="danger"
            size="small"
            @click="simulateBreak('signature_invalid')"
          />
          <Button
            label="Checksum Mismatch"
            icon="pi pi-exclamation-circle"
            severity="danger"
            size="small"
            @click="simulateBreak('checksum_mismatch')"
          />
          <Button
            label="Unverified Registry"
            icon="pi pi-lock-open"
            severity="warning"
            size="small"
            @click="simulateBreak('unverified_registry')"
          />
          <Button
            label="Reset"
            icon="pi pi-refresh"
            severity="secondary"
            size="small"
            @click="loadCryptoChain"
          />
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import Dialog from 'primevue/dialog'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Message from 'primevue/message'
import { Network } from 'vis-network'
import axios from 'axios'

const props = defineProps<{
  isOpen: boolean
  workflowId: string
  artifactName: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const chainData = ref<any>(null)
const networkContainer = ref<HTMLElement | null>(null)
const network = ref<Network | null>(null)

const weakLinkSeverity = computed(() => {
  const count = chainData.value?.weak_links?.length || 0
  if (count === 0) return 'success'
  if (count <= 2) return 'warning'
  return 'danger'
})

async function loadCryptoChain() {
  try {
    const response = await axios.get(
      `/api/crypto-chain/artifact/${props.workflowId}/${props.artifactName}`
    )
    chainData.value = response.data
    await nextTick()
    renderGraph()
  } catch (error) {
    console.error('Failed to load crypto chain:', error)
  }
}

async function simulateBreak(breakType: string) {
  try {
    const response = await axios.post(
      `/api/crypto-chain/simulate-break/${props.workflowId}/${props.artifactName}/${breakType}`
    )
    chainData.value = response.data
    await nextTick()
    renderGraph()
  } catch (error) {
    console.error('Failed to simulate break:', error)
  }
}

function renderGraph() {
  if (!networkContainer.value || !chainData.value) return

  const nodes = chainData.value.graph.nodes.map((node: any) => ({
    id: node.id,
    label: formatNodeLabel(node),
    title: formatNodeTooltip(node),
    shape: getNodeShape(node.type),
    color: getNodeColor(node),
    font: {
      color: '#ffffff',
      size: 14,
      face: 'Inter, sans-serif'
    },
    size: 25
  }))

  const edges = chainData.value.graph.edges.map((edge: any, index: number) => ({
    id: index,
    from: edge.from,
    to: edge.to,
    label: edge.label,
    arrows: 'to',
    color: {
      color: edge.verified ? '#10b981' : '#ef4444',
      highlight: edge.verified ? '#059669' : '#dc2626'
    },
    width: edge.verified ? 3 : 2,
    dashes: !edge.verified,
    font: {
      size: 12,
      align: 'middle',
      background: 'rgba(255, 255, 255, 0.9)',
      strokeWidth: 0
    }
  }))

  const options = {
    nodes: {
      borderWidth: 3,
      borderWidthSelected: 4,
      shadow: true
    },
    edges: {
      smooth: {
        type: 'cubicBezier',
        forceDirection: 'horizontal',
        roundness: 0.4
      }
    },
    layout: {
      hierarchical: {
        direction: 'LR',
        sortMethod: 'directed',
        levelSeparation: 200,
        nodeSpacing: 150
      }
    },
    physics: {
      enabled: false
    },
    interaction: {
      hover: true,
      tooltipDelay: 100
    }
  }

  // Create network
  network.value = new Network(
    networkContainer.value,
    { nodes, edges },
    options
  )

  // Highlight weak links on click
  network.value.on('selectNode', (params) => {
    const nodeId = params.nodes[0]
    highlightWeakLinks(nodeId)
  })
}

function formatNodeLabel(node: any): string {
  switch (node.type) {
    case 'agent':
      return `Agent\\nTrust: ${node.trust_score}%`
    case 'artifact':
      return `Artifact\\n${node.name}`
    case 'manifest':
      return `Manifest\\n${node.verified ? '✓ Signed' : '✗ Unsigned'}`
    case 'registry':
      return `Registry\\n${node.published ? '✓ Published' : '✗ Pending'}`
    case 'verification':
      return `Verification\\n${node.all_checks_passed ? '✓ Passed' : '✗ Failed'}`
    default:
      return node.label || node.type
  }
}

function formatNodeTooltip(node: any): string {
  const parts = [
    `<b>${node.label}</b>`,
    `Type: ${node.type}`,
  ]

  if (node.trust_score !== undefined) {
    parts.push(`Trust Score: ${node.trust_score}%`)
  }
  if (node.sha256) {
    parts.push(`SHA256: ${node.sha256.substring(0, 16)}...`)
  }
  if (node.signature) {
    parts.push(`Signature: ${node.signature}`)
  }
  if (node.total_operations !== undefined) {
    parts.push(`Operations: ${node.total_operations}`)
  }

  return parts.join('<br/>')
}

function getNodeShape(type: string): string {
  switch (type) {
    case 'agent': return 'diamond'
    case 'artifact': return 'box'
    case 'manifest': return 'ellipse'
    case 'registry': return 'database'
    case 'verification': return 'star'
    default: return 'dot'
  }
}

function getNodeColor(node: any): any {
  // Check if node is involved in weak links
  const hasWeakLink = chainData.value.weak_links?.some(
    (link: any) => link.node_id === node.id
  )

  if (hasWeakLink) {
    return {
      background: '#ef4444',
      border: '#b91c1c',
      highlight: { background: '#dc2626', border: '#991b1b' }
    }
  }

  switch (node.type) {
    case 'agent':
      return node.status === 'trusted'
        ? { background: '#8b5cf6', border: '#6d28d9', highlight: { background: '#7c3aed', border: '#5b21b6' } }
        : { background: '#ef4444', border: '#b91c1c', highlight: { background: '#dc2626', border: '#991b1b' } }
    case 'artifact':
      return { background: '#3b82f6', border: '#1d4ed8', highlight: { background: '#2563eb', border: '#1e40af' } }
    case 'manifest':
      return node.verified
        ? { background: '#10b981', border: '#059669', highlight: { background: '#059669', border: '#047857' } }
        : { background: '#f59e0b', border: '#d97706', highlight: { background: '#d97706', border: '#b45309' } }
    case 'registry':
      return node.published
        ? { background: '#06b6d4', border: '#0891b2', highlight: { background: '#0891b2', border: '#0e7490' } }
        : { background: '#64748b', border: '#475569', highlight: { background: '#475569', border: '#334155' } }
    case 'verification':
      return node.all_checks_passed
        ? { background: '#10b981', border: '#059669', highlight: { background: '#059669', border: '#047857' } }
        : { background: '#ef4444', border: '#b91c1c', highlight: { background: '#dc2626', border: '#991b1b' } }
    default:
      return { background: '#64748b', border: '#475569', highlight: { background: '#475569', border: '#334155' } }
  }
}

function highlightWeakLinks(nodeId: string) {
  const weakLinks = chainData.value.weak_links?.filter(
    (link: any) => link.node_id === nodeId || link.from === nodeId || link.to === nodeId
  )

  if (weakLinks && weakLinks.length > 0) {
    console.log('Weak links for node:', weakLinks)
  }
}

function getSeverityType(severity: string): string {
  switch (severity) {
    case 'critical': return 'error'
    case 'high': return 'warn'
    case 'warning': return 'warn'
    default: return 'info'
  }
}

function handleClose() {
  if (network.value) {
    network.value.destroy()
    network.value = null
  }
  emit('close')
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadCryptoChain()
  }
})

onMounted(() => {
  if (props.isOpen) {
    loadCryptoChain()
  }
})
</script>

<style scoped>
.crypto-chain-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: calc(90vh - 120px);
}

.chain-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 8px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
}

.stat-card.success {
  background: #ecfdf5;
  border-color: #10b981;
}

.stat-card.warning {
  background: #fef3c7;
  border-color: #f59e0b;
}

.stat-card.danger {
  background: #fef2f2;
  border-color: #ef4444;
}

.stat-card i {
  font-size: 2rem;
  color: #64748b;
}

.stat-card.success i {
  color: #10b981;
}

.stat-card.warning i {
  color: #f59e0b;
}

.stat-card.danger i {
  color: #ef4444;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.graph-card {
  flex: 1;
  min-height: 400px;
}

.network-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #ffffff;
  border-radius: 8px;
}

.weak-links-panel {
  max-height: 200px;
  overflow-y: auto;
}

.weak-links-panel h4 {
  margin: 0 0 1rem 0;
  color: #dc2626;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.weak-link-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.break-simulator {
  padding: 1rem;
  background: #f1f5f9;
  border-radius: 8px;
  border: 1px dashed #cbd5e1;
}

.break-simulator h4 {
  margin: 0 0 1rem 0;
  font-size: 0.875rem;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.break-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
</style>
