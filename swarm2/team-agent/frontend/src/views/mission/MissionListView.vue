<template>
  <AppLayout>
    <div class="mission-list">
      <div class="page-header">
        <div>
          <h1 class="page-title">Missions</h1>
          <p class="page-subtitle">
            Manage and monitor your workflow missions
          </p>
        </div>
        <Button
          label="Create Mission"
          icon="pi pi-plus"
          @click="navigateToCreate"
        />
      </div>

      <!-- Filter Tabs -->
      <TabView v-model:activeIndex="currentTab" class="mission-tabs">
        <TabPanel :header="`All (${allMissions.length})`"></TabPanel>
        <TabPanel :header="`Active (${activeMissions.length})`"></TabPanel>
        <TabPanel :header="`Completed (${completedMissions.length})`"></TabPanel>
        <TabPanel :header="`Failed (${failedMissions.length})`"></TabPanel>
      </TabView>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <ProgressSpinner />
        <p>Loading missions...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredMissions.length === 0" class="empty-state">
        <i class="pi pi-inbox empty-icon"></i>
        <h3>{{ emptyStateMessage }}</h3>
        <p>{{ emptyStateSubtext }}</p>
        <Button
          v-if="currentTab === 0"
          label="Create Your First Mission"
          icon="pi pi-plus"
          @click="navigateToCreate"
        />
      </div>

      <!-- Mission Grid -->
      <div v-else class="mission-grid">
        <MissionCard
          v-for="mission in filteredMissions"
          :key="mission.mission_id"
          :mission="mission"
          :workflow="getWorkflowForMission(mission.mission_id)"
        />
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import ProgressSpinner from 'primevue/progressspinner'
import AppLayout from '@/components/layout/AppLayout.vue'
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

<style scoped>
.mission-list {
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

.mission-tabs {
  margin-bottom: 2rem;
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

.mission-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .mission-grid {
    grid-template-columns: 1fr;
  }
}
</style>
