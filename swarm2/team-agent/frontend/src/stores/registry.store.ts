import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Capability, Provider, RegistryStatistics, CapabilityFilters } from '@/types/registry.types'

export const useRegistryStore = defineStore('registry', () => {
  // State
  const capabilities = ref<Capability[]>([])
  const providers = ref<Provider[]>([])
  const statistics = ref<RegistryStatistics | null>(null)
  const filters = ref<CapabilityFilters>({})
  const isLoading = ref(false)

  // Getters
  const filteredCapabilities = computed(() => capabilities.value)

  const capabilitiesByType = computed(() => {
    const byType: Record<string, Capability[]> = {}
    capabilities.value.forEach(cap => {
      if (!byType[cap.capability_type]) {
        byType[cap.capability_type] = []
      }
      byType[cap.capability_type].push(cap)
    })
    return byType
  })

  const highTrustCapabilities = computed(() =>
    capabilities.value.filter(c => c.trust_score >= 90)
  )

  // Actions
  async function fetchCapabilities(newFilters?: CapabilityFilters): Promise<void> {
    const registryService = await import('@/services/registry.service')
    isLoading.value = true
    try {
      if (newFilters) {
        filters.value = newFilters
      }
      capabilities.value = await registryService.default.getAllCapabilities(filters.value)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchProviders(): Promise<void> {
    const registryService = await import('@/services/registry.service')
    providers.value = await registryService.default.getAllProviders()
  }

  async function fetchStatistics(): Promise<void> {
    const registryService = await import('@/services/registry.service')
    statistics.value = await registryService.default.getStatistics()
  }

  async function revokeCapability(capabilityId: string): Promise<void> {
    const registryService = await import('@/services/registry.service')
    await registryService.default.revokeCapability(capabilityId)
    // Refresh capabilities after revocation
    await fetchCapabilities()
  }

  function setFilters(newFilters: CapabilityFilters): void {
    filters.value = newFilters
  }

  function clearFilters(): void {
    filters.value = {}
  }

  return {
    capabilities,
    providers,
    statistics,
    filters,
    isLoading,
    filteredCapabilities,
    capabilitiesByType,
    highTrustCapabilities,
    fetchCapabilities,
    fetchProviders,
    fetchStatistics,
    revokeCapability,
    setFilters,
    clearFilters
  }
})
