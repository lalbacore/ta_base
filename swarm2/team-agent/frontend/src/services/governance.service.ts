import apiClient from './api.client'
import type { PolicyConfig, GovernanceDecision, ApprovalGate } from '@/types/governance.types'

export class GovernanceService {
  async getPolicyConfig(): Promise<PolicyConfig> {
    const response = await apiClient.get('/policy/config')
    return response.data
  }

  async updatePolicyConfig(config: Partial<PolicyConfig>): Promise<void> {
    await apiClient.put('/policy/config', config)
  }

  async getDecisions(limit?: number): Promise<GovernanceDecision[]> {
    const response = await apiClient.get('/governance/decisions', { params: { limit } })
    return response.data
  }

  async approveGate(gateId: string): Promise<void> {
    await apiClient.post(`/approval/${gateId}/action`, { action: 'approve' })
  }

  async rejectGate(gateId: string, reason?: string): Promise<void> {
    await apiClient.post(`/approval/${gateId}/action`, { action: 'reject', reason })
  }

  async getPendingGates(): Promise<ApprovalGate[]> {
    const response = await apiClient.get('/approval/pending')
    return response.data
  }
}

export default new GovernanceService()
