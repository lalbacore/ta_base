<template>
  <c-box p="8">
    <!-- Header -->
    <c-flex justify="space-between" align="start" mb="6">
      <c-box>
        <c-button
          variant="ghost"
          size="sm"
          left-icon="←"
          mb="3"
          @click="handleBack"
        >
          Back to Missions
        </c-button>
        <c-h-stack spacing="3" mb="2">
          <c-heading>{{ missionId }}</c-heading>
          <c-badge
            v-if="workflow"
            :color-scheme="statusColorScheme"
            font-size="md"
            px="3"
            py="1"
          >
            {{ workflow.status }}
          </c-badge>
        </c-h-stack>
        <c-text color="gray.600" v-if="mission">
          {{ mission.description }}
        </c-text>
      </c-box>

      <c-menu>
        <c-menu-button
          as="c-button"
          variant="outline"
          size="sm"
        >
          Actions
        </c-menu-button>
        <c-menu-list>
          <c-menu-item @click="handleRefresh">
            Refresh Status
          </c-menu-item>
          <c-menu-item
            v-if="workflow?.status === 'paused'"
            @click="handleResume"
          >
            Resume Workflow
          </c-menu-item>
          <c-menu-divider />
          <c-menu-item color="red.500" @click="handleCancel">
            Cancel Mission
          </c-menu-item>
        </c-menu-list>
      </c-menu>
    </c-flex>

    <!-- Loading State -->
    <c-box v-if="isLoading" text-align="center" py="12">
      <c-spinner size="xl" color="blue.500" mb="4" />
      <c-text color="gray.600">Loading mission details...</c-text>
    </c-box>

    <!-- Error State -->
    <c-alert v-else-if="error" status="error" border-radius="md" mb="6">
      <c-alert-icon />
      <c-alert-description>
        {{ error }}
      </c-alert-description>
    </c-alert>

    <!-- Content -->
    <c-grid
      v-else
      template-columns="{ base: '1fr', lg: '2fr 1fr' }"
      gap="6"
    >
      <!-- Main Content -->
      <c-v-stack spacing="6" align="stretch">
        <!-- Progress Overview -->
        <c-box
          p="6"
          bg="white"
          border="1px"
          border-color="gray.200"
          border-radius="lg"
          box-shadow="sm"
        >
          <c-heading size="md" mb="4">Progress Overview</c-heading>

          <c-flex justify="space-between" mb="2">
            <c-text font-weight="medium">Overall Progress</c-text>
            <c-text font-weight="bold" :color="progressColor">
              {{ workflow?.progress || 0 }}%
            </c-text>
          </c-flex>

          <c-progress
            :value="workflow?.progress || 0"
            :color-scheme="progressColorScheme"
            size="lg"
            border-radius="full"
            mb="4"
          />

          <c-text font-size="sm" color="gray.600">
            Current Stage: {{ formatStageName(workflow?.current_stage || 'none') }}
          </c-text>
        </c-box>

        <!-- Workflow Timeline -->
        <c-box
          p="6"
          bg="white"
          border="1px"
          border-color="gray.200"
          border-radius="lg"
          box-shadow="sm"
        >
          <WorkflowStageTimeline :stages="workflow?.stages || []" />
        </c-box>

        <!-- Pending Breakpoints -->
        <c-box
          v-if="pendingBreakpoints.length > 0"
          p="6"
          bg="orange.50"
          border="1px"
          border-color="orange.200"
          border-radius="lg"
        >
          <c-h-stack spacing="3" mb="4">
            <c-icon name="warning" color="orange.500" />
            <c-heading size="md">Approval Required</c-heading>
          </c-h-stack>

          <c-text mb="4" color="gray.700">
            This workflow requires your approval to continue
          </c-text>

          <c-button color-scheme="orange" @click="handleBreakpointApproval">
            Review & Approve
          </c-button>
        </c-box>
      </c-v-stack>

      <!-- Sidebar -->
      <c-v-stack spacing="6" align="stretch">
        <!-- Mission Details Card -->
        <c-box
          p="6"
          bg="white"
          border="1px"
          border-color="gray.200"
          border-radius="lg"
          box-shadow="sm"
        >
          <c-heading size="sm" mb="4">Mission Details</c-heading>

          <c-v-stack spacing="3" align="stretch">
            <c-box>
              <c-text font-size="xs" color="gray.500" mb="1">
                Created
              </c-text>
              <c-text font-size="sm">
                {{ formatDate(workflow?.created_at) }}
              </c-text>
            </c-box>

            <c-box>
              <c-text font-size="xs" color="gray.500" mb="1">
                Last Updated
              </c-text>
              <c-text font-size="sm">
                {{ formatDate(workflow?.updated_at) }}
              </c-text>
            </c-box>

            <c-divider />

            <c-box>
              <c-text font-size="xs" color="gray.500" mb="1">
                Min Trust Score
              </c-text>
              <c-text font-size="sm" font-weight="bold">
                {{ mission?.min_trust_score || 0 }}
              </c-text>
            </c-box>

            <c-box v-if="mission?.max_cost">
              <c-text font-size="xs" color="gray.500" mb="1">
                Max Cost
              </c-text>
              <c-text font-size="sm" font-weight="bold">
                ${{ mission.max_cost }}
              </c-text>
            </c-box>
          </c-v-stack>
        </c-box>

        <!-- Required Capabilities -->
        <c-box
          v-if="mission?.required_capabilities && mission.required_capabilities.length > 0"
          p="6"
          bg="white"
          border="1px"
          border-color="gray.200"
          border-radius="lg"
          box-shadow="sm"
        >
          <c-heading size="sm" mb="4">Required Capabilities</c-heading>

          <c-v-stack spacing="2" align="stretch">
            <c-badge
              v-for="(cap, index) in mission.required_capabilities"
              :key="index"
              variant="outline"
              color-scheme="blue"
              p="2"
            >
              {{ formatCapabilityType(cap.capability_type) }}
            </c-badge>
          </c-v-stack>
        </c-box>

        <!-- Breakpoints -->
        <c-box
          v-if="mission?.breakpoints && mission.breakpoints.length > 0"
          p="6"
          bg="white"
          border="1px"
          border-color="gray.200"
          border-radius="lg"
          box-shadow="sm"
        >
          <c-heading size="sm" mb="4">Breakpoints</c-heading>

          <c-v-stack spacing="2" align="stretch">
            <c-text
              v-for="(bp, index) in mission.breakpoints"
              :key="index"
              font-size="sm"
            >
              • {{ formatBreakpointType(bp) }}
            </c-text>
          </c-v-stack>
        </c-box>
      </c-v-stack>
    </c-grid>

    <!-- Breakpoint Approval Modal -->
    <BreakpointApprovalModal
      :is-open="showBreakpointModal"
      :breakpoint="currentBreakpoint"
      @close="showBreakpointModal = false"
      @approved="handleBreakpointApproved"
      @rejected="handleBreakpointRejected"
    />
  </c-box>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  CBox,
  CFlex,
  CGrid,
  CHStack,
  CVStack,
  CHeading,
  CText,
  CBadge,
  CButton,
  CProgress,
  CSpinner,
  CAlert,
  CAlertIcon,
  CAlertDescription,
  CDivider,
  CMenu,
  CMenuButton,
  CMenuList,
  CMenuItem,
  CMenuDivider,
  CIcon
} from '@chakra-ui/vue-next'
import { useMissionStore } from '@/stores/mission.store'
import { useWorkflowWebSocket } from '@/composables/useWorkflowWebSocket'
import WorkflowStageTimeline from '@/components/mission/WorkflowStageTimeline.vue'
import BreakpointApprovalModal from '@/components/mission/BreakpointApprovalModal.vue'

const route = useRoute()
const router = useRouter()
const missionStore = useMissionStore()

const missionId = computed(() => route.params.id as string)
const mission = computed(() => missionStore.missions.get(missionId.value))
const workflow = computed(() => missionStore.workflows.get(missionId.value))

const isLoading = ref(false)
const error = ref('')
const refreshInterval = ref<number | null>(null)
const showBreakpointModal = ref(false)
const currentBreakpoint = ref<any>(null)

// Connect to WebSocket for real-time updates
const { isConnected } = useWorkflowWebSocket(missionId.value)

const pendingBreakpoints = computed(() =>
  Array.from(missionStore.breakpoints.values()).filter(
    bp => bp.workflow_id === missionId.value && bp.status === 'pending'
  )
)

const statusColorScheme = computed(() => {
  switch (workflow.value?.status) {
    case 'running':
      return 'blue'
    case 'completed':
      return 'green'
    case 'failed':
      return 'red'
    case 'paused':
      return 'orange'
    default:
      return 'gray'
  }
})

const progressColorScheme = computed(() => {
  const progress = workflow.value?.progress || 0
  if (progress === 100) return 'green'
  if (progress >= 50) return 'blue'
  return 'gray'
})

const progressColor = computed(() => {
  const progress = workflow.value?.progress || 0
  if (progress === 100) return 'green.600'
  if (progress >= 50) return 'blue.600'
  return 'gray.600'
})

async function loadMissionDetails() {
  isLoading.value = true
  error.value = ''

  try {
    await missionStore.fetchWorkflowStatus(missionId.value)
  } catch (err) {
    error.value = 'Failed to load mission details'
    console.error('Error loading mission:', err)
  } finally {
    isLoading.value = false
  }
}

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatCapabilityType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatBreakpointType(type: string): string {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown'
  const date = new Date(dateString)
  return date.toLocaleString()
}

function handleBack() {
  router.push('/missions')
}

async function handleRefresh() {
  await loadMissionDetails()
}

async function handleResume() {
  // TODO: Implement resume workflow
  console.log('Resume workflow:', missionId.value)
}

function handleBreakpointApproval() {
  if (pendingBreakpoints.value.length > 0) {
    currentBreakpoint.value = pendingBreakpoints.value[0]
    showBreakpointModal.value = true
  }
}

function handleBreakpointApproved() {
  showBreakpointModal.value = false
  currentBreakpoint.value = null
  loadMissionDetails()
}

function handleBreakpointRejected() {
  showBreakpointModal.value = false
  currentBreakpoint.value = null
  loadMissionDetails()
}

function handleCancel() {
  // TODO: Implement cancel mission
  console.log('Cancel mission:', missionId.value)
}

onMounted(async () => {
  await loadMissionDetails()

  // Set up auto-refresh every 5 seconds for active workflows
  if (workflow.value?.status === 'running') {
    refreshInterval.value = window.setInterval(() => {
      loadMissionDetails()
    }, 5000)
  }
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>
