import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Capability, CapabilityProvider, CapabilitySearchFilters, CapabilityMatchResult } from '@/types/registry.types'

export const useRegistryStore = defineStore('registry', () => {
  // State
  const capabilities = ref<Capability[]>([])
  const providers = ref<CapabilityProvider[]>([])
  const matches = ref<CapabilityMatchResult[]>([])
  const searchFilters = ref<CapabilitySearchFilters>({})
  const statistics = ref({
    total_capabilities: 0,
    total_providers: 0,
    total_invocations: 0
  })

  // Getters
  const filteredCapabilities = computed(() => {
    let result = capabilities.value

    if (searchFilters.value.capability_type) {
      result = result.filter(c => c.capability_type === searchFilters.value.capability_type)
    }

    if (searchFilters.value.min_trust_score) {
      result = result.filter(c => c.trust_score >= searchFilters.value.min_trust_score!)
    }

    if (searchFilters.value.max_price) {
      result = result.filter(c => c.price <= searchFilters.value.max_price!)
    }

    return result
  })

  const topProviders = computed(() =>
    providers.value.sort((a, b) => b.reputation - a.reputation).slice(0, 10)
  )

  // Actions
  async function fetchCapabilities(): Promise<void> {
    // TODO: API call
  }

  async function fetchProviders(): Promise<void> {
    // TODO: API call
  }

  async function discoverCapabilities(requirements: any): Promise<Capability[]> {
    // TODO: API call
    return []
  }

  async function matchCapabilities(requirements: any): Promise<CapabilityMatchResult[]> {
    // TODO: API call
    return []
  }

  async function revokeCapability(capabilityId: string): Promise<void> {
    // TODO: API call
  }

  function updateSearchFilters(filters: CapabilitySearchFilters): void {
    searchFilters.value = { ...searchFilters.value, ...filters }
  }

  return {
    capabilities,
    providers,
    matches,
    searchFilters,
    statistics,
    filteredCapabilities,
    topProviders,
    fetchCapabilities,
    fetchProviders,
    discoverCapabilities,
    matchCapabilities,
    revokeCapability,
    updateSearchFilters
  }
})
