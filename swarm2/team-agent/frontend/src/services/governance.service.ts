import apiClient from './api.client'
import type { Policy, PolicyConfig, GovernanceDecision, ComplianceReport } from '@/types/governance.types'

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

  // Policy CRUD Methods

  async getAllPolicies(): Promise<Policy[]> {
    const response = await apiClient.get('/governance/policies')
    return response.data
  }

  async getPolicy(policyId: number): Promise<Policy> {
    const response = await apiClient.get(`/governance/policies/${policyId}`)
    return response.data
  }

  async createPolicy(policyData: Omit<Policy, 'id' | 'created_at' | 'updated_at' | 'is_active'>): Promise<Policy> {
    const response = await apiClient.post('/governance/policies', policyData, {
      headers: {
        'X-Agent-Role': 'government'
      }
    })
    return response.data
  }

  async updatePolicy(policyId: number, policyData: Partial<Policy>): Promise<Policy> {
    const response = await apiClient.put(`/governance/policies/${policyId}`, policyData, {
      headers: {
        'X-Agent-Role': 'government'
      }
    })
    return response.data
  }

  async deletePolicy(policyId: number): Promise<void> {
    await apiClient.delete(`/governance/policies/${policyId}`, {
      headers: {
        'X-Agent-Role': 'government'
      }
    })
  }

  async activatePolicy(policyId: number): Promise<Policy> {
    const response = await apiClient.post(`/governance/policies/${policyId}/activate`, {}, {
      headers: {
        'X-Agent-Role': 'government'
      }
    })
    return response.data
  }
}

export default new GovernanceService()
