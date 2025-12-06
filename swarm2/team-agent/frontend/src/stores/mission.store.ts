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
    const missionService = await import('@/services/mission.service')
    const result = await missionService.default.submitMission(mission)

    missions.value.set(result.mission_id, mission)

    // Create initial workflow status
    workflows.value.set(result.mission_id, {
      workflow_id: result.mission_id,
      mission_id: result.mission_id,
      status: 'pending',
      current_stage: 'initializing',
      progress: 0,
      stages: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })

    return result.mission_id
  }

  async function fetchWorkflowStatus(workflowId: string): Promise<WorkflowStatus | null> {
    const missionService = await import('@/services/mission.service')
    const status = await missionService.default.getWorkflowStatus(workflowId)

    if (status) {
      workflows.value.set(workflowId, status)
      return status
    }

    return workflows.value.get(workflowId) || null
  }

  async function approveBreakpoint(breakpointId: string, optionIndex: number): Promise<void> {
    const missionService = await import('@/services/mission.service')
    await missionService.default.approveBreakpoint(breakpointId, optionIndex)

    const breakpoint = breakpoints.value.get(breakpointId)
    if (breakpoint) {
      breakpoint.status = 'approved'
    }
  }

  async function rejectBreakpoint(breakpointId: string): Promise<void> {
    const missionService = await import('@/services/mission.service')
    await missionService.default.rejectBreakpoint(breakpointId)

    const breakpoint = breakpoints.value.get(breakpointId)
    if (breakpoint) {
      breakpoint.status = 'rejected'
    }
  }

  async function listMissions(): Promise<void> {
    const missionService = await import('@/services/mission.service')
    const missionList = await missionService.default.listMissions()

    missionList.forEach(mission => {
      missions.value.set(mission.mission_id, mission)
    })
  }

  async function listWorkflows(): Promise<void> {
    const missionService = await import('@/services/mission.service')
    const workflowList = await missionService.default.listWorkflows()

    workflowList.forEach(workflow => {
      workflows.value.set(workflow.workflow_id, workflow)
    })
  }

  // Aliases for compatibility
  const fetchMissions = listMissions
  const fetchWorkflows = listWorkflows

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
    rejectBreakpoint,
    listMissions,
    listWorkflows,
    fetchMissions,
    fetchWorkflows
  }
})
