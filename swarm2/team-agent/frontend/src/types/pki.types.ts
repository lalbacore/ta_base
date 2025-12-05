export enum TrustDomain {
  ROOT = 'root',
  GOVERNMENT = 'government',
  EXECUTION = 'execution',
  LOGGING = 'logging'
}

export interface Certificate {
  domain: TrustDomain
  subject: string
  issuer: string
  serial_number: string
  not_before: string
  not_after: string
  status: 'valid' | 'expiring' | 'expired' | 'revoked'
  days_until_expiry: number
}

export interface RevocationInfo {
  serial_number: string
  revocation_date: string
  reason: string
  issuer: string
}

export interface CRLData {
  issuer: string
  last_update: string
  next_update: string
  revoked_certificates: RevocationInfo[]
}

export interface CertificateAuditLog {
  event_id: string
  event_type: 'issued' | 'renewed' | 'rotated' | 'revoked'
  domain: TrustDomain
  timestamp: string
  details: any
}
