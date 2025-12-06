import apiClient from './api.client'
import type { MissionSpec, WorkflowStatus } from '@/types/mission.types'

export class MissionService {
  async submitMission(mission: MissionSpec): Promise<{ mission_id: string }> {
    const response = await apiClient.post('/mission/submit', mission)
    return response.data
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowStatus> {
    const response = await apiClient.get(`/mission/workflow/${workflowId}/status`)
    return response.data
  }

  async resumeWorkflow(workflowId: string): Promise<void> {
    await apiClient.post(`/mission/workflow/${workflowId}/resume`)
  }

  async approveBreakpoint(breakpointId: string, optionIndex: number): Promise<void> {
    await apiClient.post(`/mission/breakpoint/${breakpointId}/approve`, { option_index: optionIndex })
  }

  async rejectBreakpoint(breakpointId: string): Promise<void> {
    await apiClient.post(`/mission/breakpoint/${breakpointId}/reject`)
  }

  async listMissions(): Promise<MissionSpec[]> {
    const response = await apiClient.get('/mission/list')
    return response.data
  }

  async listWorkflows(): Promise<WorkflowStatus[]> {
    const response = await apiClient.get('/mission/workflow/list')
    return response.data
  }
}

export default new MissionService()
