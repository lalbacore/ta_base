export interface Manifest {
  manifest_version: string
  workflow_id: string
  mission: string
  timestamp: string
  roles: Record<string, RoleInfo>
  signatures: Record<string, SignatureInfo>
  artifacts: ArtifactInfo[]
  checksums: Record<string, string>
  verification: VerificationInfo
  manifest_checksum: string
  artifact_count: number
}

export interface RoleInfo {
  status: string
  timestamp: string
}

export interface SignatureInfo {
  signature: string
  signer_id: string
  timestamp: string
}

export interface ArtifactInfo {
  type: string
  name: string
  status: string
  checksum?: string
}

export interface VerificationInfo {
  total_signatures: number
  valid_signatures: number
  missing_signatures: string[]
}

export interface VerificationResult {
  valid: boolean
  errors: string[]
  warnings: string[]
}
