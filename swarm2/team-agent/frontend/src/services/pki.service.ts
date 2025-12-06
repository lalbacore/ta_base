import apiClient from './api.client'
import type { Certificate, CRLData, TrustDomain, RevocationInfo, LifecycleStatus } from '@/types/pki.types'

export class PKIService {
  async getAllCertificates(): Promise<Certificate[]> {
    const response = await apiClient.get('/pki/status')
    return response.data.certificates || []
  }

  async getCertificate(domain: TrustDomain): Promise<Certificate> {
    const response = await apiClient.get(`/pki/certificate/${domain}`)
    return response.data
  }

  async renewCertificate(domain: TrustDomain): Promise<void> {
    await apiClient.post(`/pki/renew/${domain}`)
  }

  async rotateCertificate(domain: TrustDomain): Promise<any> {
    const response = await apiClient.post(`/pki/certificate/${domain}/rotate`)
    return response.data
  }

  async revokeCertificate(serialNumber: string, reason: string, domain?: string): Promise<any> {
    const response = await apiClient.post(`/pki/certificate/${serialNumber}/revoke`, {
      reason,
      revoked_by: 'admin',
      domain
    })
    return response.data
  }

  async getRevokedCertificates(domain?: string, limit = 100): Promise<RevocationInfo[]> {
    const params = new URLSearchParams()
    if (domain) params.append('domain', domain)
    params.append('limit', limit.toString())

    const response = await apiClient.get(`/pki/revoked?${params.toString()}`)
    return response.data.revoked_certificates || []
  }

  async getLifecycleStatus(): Promise<LifecycleStatus> {
    const response = await apiClient.get('/pki/lifecycle/status')
    return response.data
  }

  async autoRenewCertificates(dryRun = false): Promise<any> {
    const response = await apiClient.post('/pki/lifecycle/auto-renew', { dry_run: dryRun })
    return response.data
  }

  async simulateRenewal(): Promise<any> {
    const response = await apiClient.get('/pki/lifecycle/simulate')
    return response.data
  }

  async getCRL(): Promise<CRLData> {
    const response = await apiClient.get('/pki/crl')
    return response.data
  }
}

export default new PKIService()
