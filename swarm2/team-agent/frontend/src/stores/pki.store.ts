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
    // TODO: API call
  }

  async function renewCertificate(domain: TrustDomain): Promise<void> {
    // TODO: API call
  }

  async function rotateCertificate(domain: TrustDomain): Promise<void> {
    // TODO: API call
  }

  async function revokeCertificate(serialNumber: string, reason: string): Promise<void> {
    // TODO: API call
    revokedCertificates.value.push(serialNumber)
  }

  async function fetchCRL(): Promise<void> {
    // TODO: API call
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
    fetchCRL
  }
})
