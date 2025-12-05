<template>
  <c-box p="8">
    <c-flex justify="space-between" align="center" mb="6">
      <c-box>
        <c-heading mb="2">Missions</c-heading>
        <c-text color="gray.600">
          Manage and monitor your workflow missions
        </c-text>
      </c-box>
      <c-button color-scheme="blue" @click="navigateToCreate">
        + Create Mission
      </c-button>
    </c-flex>

    <!-- Filter Tabs -->
    <c-tabs variant="enclosed" mb="6" @change="handleTabChange">
      <c-tab-list>
        <c-tab>All ({{ allMissions.length }})</c-tab>
        <c-tab>Active ({{ activeMissions.length }})</c-tab>
        <c-tab>Completed ({{ completedMissions.length }})</c-tab>
        <c-tab>Failed ({{ failedMissions.length }})</c-tab>
      </c-tab-list>
    </c-tabs>

    <!-- Loading State -->
    <c-box v-if="isLoading" text-align="center" py="12">
      <c-spinner size="xl" color="blue.500" mb="4" />
      <c-text color="gray.600">Loading missions...</c-text>
    </c-box>

    <!-- Empty State -->
    <c-box
      v-else-if="filteredMissions.length === 0"
      p="12"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
      bg="gray.50"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        {{ emptyStateMessage }}
      </c-text>
      <c-text color="gray.400" mb="4">
        {{ emptyStateSubtext }}
      </c-text>
      <c-button
        v-if="currentTab === 0"
        color-scheme="blue"
        @click="navigateToCreate"
      >
        Create Your First Mission
      </c-button>
    </c-box>

    <!-- Mission Grid -->
    <c-simple-grid
      v-else
      columns="{ base: 1, md: 2, lg: 3 }"
      spacing="6"
    >
      <MissionCard
        v-for="mission in filteredMissions"
        :key="mission.mission_id"
        :mission="mission"
        :workflow="getWorkflowForMission(mission.mission_id)"
      />
    </c-simple-grid>
  </c-box>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  CBox,
  CFlex,
  CHeading,
  CButton,
  CText,
  CTabs,
  CTabList,
  CTab,
  CSimpleGrid,
  CSpinner
} from '@chakra-ui/vue-next'
import { useMissionStore } from '@/stores/mission.store'
import MissionCard from '@/components/mission/MissionCard.vue'

const router = useRouter()
const missionStore = useMissionStore()

const isLoading = ref(false)
const currentTab = ref(0)

const allMissions = computed(() => Array.from(missionStore.missions.values()))

const activeMissions = computed(() =>
  allMissions.value.filter(mission => {
    const workflow = missionStore.workflows.get(mission.mission_id)
    return workflow?.status === 'running' || workflow?.status === 'paused'
  })
)

const completedMissions = computed(() =>
  allMissions.value.filter(mission => {
    const workflow = missionStore.workflows.get(mission.mission_id)
    return workflow?.status === 'completed'
  })
)

const failedMissions = computed(() =>
  allMissions.value.filter(mission => {
    const workflow = missionStore.workflows.get(mission.mission_id)
    return workflow?.status === 'failed'
  })
)

const filteredMissions = computed(() => {
  switch (currentTab.value) {
    case 1:
      return activeMissions.value
    case 2:
      return completedMissions.value
    case 3:
      return failedMissions.value
    default:
      return allMissions.value
  }
})

const emptyStateMessage = computed(() => {
  switch (currentTab.value) {
    case 1:
      return 'No active missions'
    case 2:
      return 'No completed missions'
    case 3:
      return 'No failed missions'
    default:
      return 'No missions yet'
  }
})

const emptyStateSubtext = computed(() => {
  switch (currentTab.value) {
    case 1:
      return 'Active missions will appear here when they are running'
    case 2:
      return 'Completed missions will appear here'
    case 3:
      return 'Failed missions will appear here'
    default:
      return 'Click "Create Mission" to start your first workflow'
  }
})

function getWorkflowForMission(missionId: string) {
  return missionStore.workflows.get(missionId)
}

function handleTabChange(index: number) {
  currentTab.value = index
}

function navigateToCreate() {
  router.push('/missions/create')
}

onMounted(async () => {
  isLoading.value = true
  try {
    await Promise.all([
      missionStore.listMissions(),
      missionStore.listWorkflows()
    ])
  } catch (error) {
    console.error('Failed to load missions:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
