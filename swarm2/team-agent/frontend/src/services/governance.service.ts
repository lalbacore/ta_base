import apiClient from './api.client'
import type { PolicyConfig, GovernanceDecision, ComplianceReport } from '@/types/governance.types'

export class GovernanceService {
  async getPolicyConfig(): Promise<PolicyConfig> {
    const response = await apiClient.get('/governance/config')
    return response.data
  }

  async updatePolicyConfig(config: PolicyConfig): Promise<void> {
    await apiClient.put('/governance/config', config)
  }

  async getDecisions(limit: number = 50): Promise<GovernanceDecision[]> {
    const response = await apiClient.get(`/governance/governance/decisions?limit=${limit}`)
    return response.data
  }

  async checkMissionCompliance(missionData: any): Promise<ComplianceReport> {
    const response = await apiClient.post('/governance/check-compliance', missionData)
    return response.data
  }
}

export default new GovernanceService()
