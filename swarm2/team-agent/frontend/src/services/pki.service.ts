import apiClient from './api.client'
import type { Certificate, CRLData, TrustDomain, RevocationInfo } from '@/types/pki.types'

export class PKIService {
  async getAllCertificates(): Promise<Certificate[]> {
    const response = await apiClient.get('/pki/status')
    return response.data
  }

  async getCertificate(domain: TrustDomain): Promise<Certificate> {
    const response = await apiClient.get(`/pki/certificate/${domain}`)
    return response.data
  }

  async renewCertificate(domain: TrustDomain): Promise<void> {
    await apiClient.post(`/pki/renew/${domain}`)
  }

  async rotateCertificate(domain: TrustDomain): Promise<void> {
    await apiClient.post(`/pki/rotate/${domain}`)
  }

  async revokeCertificate(serialNumber: string, reason: string): Promise<void> {
    await apiClient.post('/pki/revoke', { serial_number: serialNumber, reason })
  }

  async getRevokedCertificates(): Promise<RevocationInfo[]> {
    const response = await apiClient.get('/pki/revoked')
    return response.data
  }

  async getCRL(): Promise<CRLData> {
    const response = await apiClient.get('/pki/crl')
    return response.data
  }
}

export default new PKIService()
