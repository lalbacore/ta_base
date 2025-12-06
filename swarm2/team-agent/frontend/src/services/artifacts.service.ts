import apiClient from './api.client'
import type { Manifest, VerificationResult } from '@/types/artifacts.types'

export class ArtifactsService {
  async getWorkflowManifest(workflowId: string): Promise<Manifest> {
    const response = await apiClient.get(`/workflow/${workflowId}/manifest`)
    return response.data
  }

  async getWorkflowArtifacts(workflowId: string): Promise<any[]> {
    const response = await apiClient.get(`/workflow/${workflowId}/artifacts`)
    return response.data
  }

  async verifyArtifact(artifactData: any): Promise<VerificationResult> {
    const response = await apiClient.post('/artifact/verify', artifactData)
    return response.data
  }

  async verifyManifest(manifest: Manifest): Promise<VerificationResult> {
    const response = await apiClient.post('/manifest/verify', manifest)
    return response.data
  }

  async exportManifest(workflowId: string, format: 'json' | 'text'): Promise<string> {
    const response = await apiClient.get(`/workflow/${workflowId}/manifest/export`, {
      params: { format }
    })
    return response.data
  }
}

export default new ArtifactsService()
