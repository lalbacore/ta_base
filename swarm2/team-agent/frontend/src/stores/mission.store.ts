import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MissionSpec, WorkflowStatus, Breakpoint } from '@/types/mission.types'

export const useMissionStore = defineStore('mission', () => {
  // State
  const missions = ref<Map<string, MissionSpec>>(new Map())
  const workflows = ref<Map<string, WorkflowStatus>>(new Map())
  const breakpoints = ref<Map<string, Breakpoint>>(new Map())
  const activeWorkflowId = ref<string | null>(null)

  // Getters
  const activeMissions = computed(() =>
    Array.from(workflows.values()).filter(w => w.status === 'running')
  )

  const completedMissions = computed(() =>
    Array.from(workflows.values()).filter(w => w.status === 'completed')
  )

  const pendingBreakpoints = computed(() =>
    Array.from(breakpoints.values()).filter(b => b.status === 'pending')
  )

  // Actions
  async function submitMission(mission: MissionSpec): Promise<string> {
    // TODO: API call
    missions.value.set(mission.mission_id, mission)
    return mission.mission_id
  }

  async function fetchWorkflowStatus(workflowId: string): Promise<WorkflowStatus | null> {
    // TODO: API call
    return workflows.value.get(workflowId) || null
  }

  async function approveBreakpoint(breakpointId: string, optionIndex: number): Promise<void> {
    // TODO: API call
    const breakpoint = breakpoints.value.get(breakpointId)
    if (breakpoint) {
      breakpoint.status = 'approved'
    }
  }

  async function rejectBreakpoint(breakpointId: string): Promise<void> {
    // TODO: API call
    const breakpoint = breakpoints.value.get(breakpointId)
    if (breakpoint) {
      breakpoint.status = 'rejected'
    }
  }

  return {
    missions,
    workflows,
    breakpoints,
    activeWorkflowId,
    activeMissions,
    completedMissions,
    pendingBreakpoints,
    submitMission,
    fetchWorkflowStatus,
    approveBreakpoint,
    rejectBreakpoint
  }
})
