import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Certificate, CRLData, CertificateAuditLog, TrustDomain } from '@/types/pki.types'

export const usePKIStore = defineStore('pki', () => {
  // State
  const certificates = ref<Map<TrustDomain, Certificate>>(new Map())
  const crlData = ref<CRLData | null>(null)
  const auditLog = ref<CertificateAuditLog[]>([])
  const revokedCertificates = ref<string[]>([])

  // Getters
  const expiringCertificates = computed(() =>
    Array.from(certificates.value.values()).filter(c =>
      c.status === 'expiring' || c.days_until_expiry < 30
    )
  )

  const validCertificates = computed(() =>
    Array.from(certificates.value.values()).filter(c => c.status === 'valid')
  )

  const criticalCertificates = computed(() =>
    Array.from(certificates.value.values()).filter(c => c.days_until_expiry < 7)
  )

  // Actions
  async function fetchAllCertificates(): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    const certs = await pkiService.default.getAllCertificates()

    certificates.value.clear()
    certs.forEach(cert => {
      certificates.value.set(cert.domain as TrustDomain, cert)
    })
  }

  async function renewCertificate(domain: TrustDomain): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    await pkiService.default.renewCertificate(domain)

    // Refresh certificates after renewal
    await fetchAllCertificates()
  }

  async function rotateCertificate(domain: TrustDomain): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    await pkiService.default.rotateCertificate(domain)

    // Refresh certificates after rotation
    await fetchAllCertificates()
  }

  async function revokeCertificate(serialNumber: string, reason: string): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    await pkiService.default.revokeCertificate(serialNumber, reason)

    revokedCertificates.value.push(serialNumber)

    // Refresh certificates after revocation
    await fetchAllCertificates()
  }

  async function fetchCRL(): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    const crl = await pkiService.default.getCRL()
    crlData.value = crl
  }

  async function generateCertificate(certData: any): Promise<void> {
    const pkiService = await import('@/services/pki.service')
    await pkiService.default.generateCertificate(certData)

    // Refresh certificates after generation
    await fetchAllCertificates()
  }

  return {
    certificates,
    crlData,
    auditLog,
    revokedCertificates,
    expiringCertificates,
    validCertificates,
    criticalCertificates,
    fetchAllCertificates,
    renewCertificate,
    rotateCertificate,
    revokeCertificate,
    fetchCRL,
    generateCertificate
  }
})
