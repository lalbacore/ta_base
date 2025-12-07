<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-white">Network Infrastructure</h1>
        <p class="text-gray-400 mt-1">Manage blockchain providers and wallet credentials securely.</p>
      </div>
      <div class="flex gap-3">
        <Button 
          label="Add Wallet" 
          icon="pi pi-wallet" 
          severity="secondary" 
          @click="showWalletModal = true" 
        />
        <Button 
          label="Add Network" 
          icon="pi pi-plus" 
          @click="showAddModal = true" 
        />
      </div>
    </div>

    <!-- Stats / Overview Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card class="bg-gray-800 border-gray-700">
            <template #title><span class="text-gray-400 text-sm uppercase">Active Networks</span></template>
            <template #content>
                <div class="text-3xl font-bold text-white">{{ providers.length }}</div>
            </template>
        </Card>
        <Card class="bg-gray-800 border-gray-700">
            <template #title><span class="text-gray-400 text-sm uppercase">Secure Wallets</span></template>
            <template #content>
                <div class="text-3xl font-bold text-blue-400">{{ wallets.length }}</div>
            </template>
        </Card>
        <Card class="bg-gray-800 border-gray-700">
            <template #title><span class="text-gray-400 text-sm uppercase">System Status</span></template>
            <template #content>
                <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
                    <span class="text-xl font-medium text-green-400">Operational</span>
                </div>
            </template>
        </Card>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
      
      <!-- Network Providers Table -->
      <Card class="bg-gray-800 border-gray-700 h-full">
        <template #title>
            <div class="flex items-center gap-2">
                <i class="pi pi-globe text-purple-400"></i>
                <span>Network Providers</span>
            </div>
        </template>
        <template #content>
            <DataTable 
                :value="providers" 
                :loading="loading" 
                responsiveLayout="scroll"
                class="p-datatable-sm"
                stripedRows
                rowGroupMode="subheader"
                groupRowsBy="meta_data.env"
                sortMode="single"
                sortField="meta_data.env"
                :sortOrder="1"
            >
                <template #empty>No networks configured.</template>
                
                <template #groupheader="slotProps">
                    <div class="flex items-center gap-2 p-2 bg-gray-900">
                        <Tag :value="formatEnvLabel(slotProps.data.meta_data?.env)" :severity="getEnvSeverity(slotProps.data.meta_data?.env)" />
                    </div>
                </template>

                <Column field="name" header="Name">
                    <template #body="slotProps">
                        <span class="font-medium text-white">{{ slotProps.data.name }}</span>
                    </template>
                </Column>
                <Column field="provider_type" header="Type">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.provider_type" severity="info" />
                    </template>
                </Column>
                <Column field="rpc_url" header="RPC URL">
                     <template #body="slotProps">
                        <span class="text-gray-400 font-mono text-xs truncate max-w-[150px] block" :title="slotProps.data.rpc_url">
                            {{ slotProps.data.rpc_url }}
                        </span>
                    </template>
                </Column>
                <Column header="Status" alignFrozen="right" frozen>
                    <template #body="slotProps">
                        <Tag v-if="slotProps.data.is_default" value="Default" severity="success" icon="pi pi-check" />
                        <Tag v-else-if="slotProps.data.meta_data?.local" value="Local" severity="warning" icon="pi pi-cog" />
                    </template>
                </Column>
            </DataTable>
        </template>
      </Card>

      <!-- Wallet Credentials Table -->
       <Card class="bg-gray-800 border-gray-700 h-full">
        <template #title>
            <div class="flex items-center gap-2">
                <i class="pi pi-key text-blue-400"></i>
                <span>Wallet Credentials</span>
            </div>
        </template>
        <template #content>
            <DataTable 
                :value="wallets" 
                :loading="loading" 
                responsiveLayout="scroll"
                class="p-datatable-sm"
                stripedRows
            >
                <template #empty>No wallets configured.</template>
                <Column field="label" header="Label">
                    <template #body="slotProps">
                        <div class="flex flex-col">
                            <span class="font-medium text-white">{{ slotProps.data.label }}</span>
                            <span class="text-xs text-gray-500">{{ slotProps.data.provider_type }}</span>
                        </div>
                    </template>
                </Column>
                <Column field="address" header="Address">
                     <template #body="slotProps">
                        <div class="flex items-center gap-2">
                            <span class="text-gray-400 font-mono text-xs truncate max-w-[180px]">
                                {{ slotProps.data.address }}
                            </span>
                            <i 
                                class="pi pi-copy text-gray-600 hover:text-white cursor-pointer text-xs"
                                @click="copyToClipboard(slotProps.data.address)"
                            ></i>
                        </div>
                    </template>
                </Column>
                 <Column header="Access">
                    <template #body>
                        <Tag value="Encrypted" severity="warning" icon="pi pi-lock" />
                    </template>
                </Column>
            </DataTable>
        </template>
      </Card>
    </div>

    <!-- Add Provider Dialog -->
    <Dialog 
        v-model:visible="showAddModal" 
        header="Add Network Provider" 
        :style="{ width: '450px' }" 
        modal 
        class="p-fluid"
    >
        <div class="field mb-4">
            <label for="name" class="block text-sm font-medium text-gray-400 mb-1">Name</label>
            <InputText id="name" v-model="newProvider.name" required autofocus placeholder="e.g. Optimism Mainnet" />
        </div>
        <div class="field mb-4">
            <label for="type" class="block text-sm font-medium text-gray-400 mb-1">Provider Type</label>
            <Dropdown 
                id="type" 
                v-model="newProvider.provider_type" 
                :options="providerTypes" 
                optionLabel="label" 
                optionValue="value" 
                placeholder="Select a Type" 
            />
        </div>
        <div class="field mb-4">
             <label for="rpc" class="block text-sm font-medium text-gray-400 mb-1">RPC / Gateway URL</label>
             <InputText id="rpc" v-model="newProvider.rpc_url" required placeholder="https://..." />
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="showAddModal = false" />
            <Button label="Save Network" icon="pi pi-check" @click="addProvider" />
        </template>
    </Dialog>

    <!-- Add Wallet Dialog -->
    <Dialog 
        v-model:visible="showWalletModal" 
        header="Add Wallet Credential" 
        :style="{ width: '450px' }" 
        modal 
        class="p-fluid"
    >
        <div class="field mb-4">
            <label for="w-label" class="block text-sm font-medium text-gray-400 mb-1">Label</label>
            <InputText id="w-label" v-model="newWallet.label" required autofocus placeholder="e.g. Deployer Account" />
        </div>
        <div class="field mb-4">
            <label for="w-type" class="block text-sm font-medium text-gray-400 mb-1">Chain Type</label>
            <Dropdown 
                id="w-type" 
                v-model="newWallet.provider_type" 
                :options="providerTypes" 
                optionLabel="label" 
                optionValue="value" 
            />
        </div>
        <div class="field mb-4">
             <label for="w-addr" class="block text-sm font-medium text-gray-400 mb-1">Address</label>
             <InputText id="w-addr" v-model="newWallet.address" required placeholder="0x..." />
        </div>
        <div class="field mb-4">
             <label for="w-key" class="block text-sm font-medium text-gray-400 mb-1">Private Key</label>
             <Password 
                id="w-key" 
                v-model="newWallet.private_key" 
                toggleMask 
                :feedback="false" 
                placeholder="Enter private key safely"
            />
             <small class="text-gray-500">Keys are encrypted at rest using AES-256.</small>
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" text @click="showWalletModal = false" />
            <Button label="Save Credential" icon="pi pi-check" @click="addWallet" />
        </template>
    </Dialog>

    <Toast />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import Password from 'primevue/password'
import Tag from 'primevue/tag'
import Toast from 'primevue/toast'
import axios from 'axios'

const toast = useToast()

interface Provider {
  provider_id: string
  name: string
  provider_type: string
  rpc_url: string
  is_default: boolean
  meta_data?: {
    env?: string
    local?: boolean
    [key: string]: any
  }
}

interface Wallet {
  wallet_id: string
  label: string
  address: string
  provider_type: string
}

const providers = ref<Provider[]>([])
const wallets = ref<Wallet[]>([])
const loading = ref(true)
const showAddModal = ref(false)
const showWalletModal = ref(false)

const providerTypes = [
    { label: 'EVM (Ethereum/Optimism)', value: 'EVM' },
    { label: 'Filecoin', value: 'FILECOIN' },
    { label: 'Storage (IPFS)', value: 'STORAGE' }
]

const newProvider = ref({
  name: '',
  provider_type: 'EVM',
  rpc_url: ''
})

const newWallet = ref({
  label: '',
  provider_type: 'EVM',
  address: '',
  private_key: ''
})

const fetchStats = async () => {
    loading.value = true
    try {
        const [pRes, wRes] = await Promise.all([
             axios.get('http://localhost:5002/api/provider/list'),
             axios.get('http://localhost:5002/api/provider/wallets')
        ])
        
        providers.value = pRes.data
        wallets.value = wRes.data
    } catch (e) {
        console.error("Failed to fetch provider stats", e)
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load network data', life: 3000 })
    } finally {
        loading.value = false
    }
}

const addProvider = async () => {
  try {
     await axios.post('http://localhost:5002/api/provider/add', newProvider.value)
     showAddModal.value = false
     fetchStats()
     newProvider.value = { name: '', provider_type: 'EVM', rpc_url: '' }
     toast.add({ severity: 'success', summary: 'Success', detail: 'Network provider added', life: 3000 })
  } catch(e) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add provider', life: 3000 })
  }
}

const addWallet = async () => {
  try {
     await axios.post('http://localhost:5002/api/provider/add_wallet', newWallet.value)
     showWalletModal.value = false
     fetchStats()
     newWallet.value = { label: '', provider_type: 'EVM', address: '', private_key: '' }
     toast.add({ severity: 'success', summary: 'Success', detail: 'Wallet credential saved secureley', life: 3000 })
  } catch(e) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to add wallet', life: 3000 })
  }
}

const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.add({ severity: 'info', summary: 'Copied', detail: 'Address copied to clipboard', life: 2000 })
}

function formatEnvLabel(env?: string): string {
    if (!env) return 'GENERAL';
    return env.toUpperCase();
}

function getEnvSeverity(env?: string): string {
    switch (env) {
        case 'production': return 'danger';
        case 'qa': return 'warning';
        case 'development': return 'success';
        default: return 'info';
    }
}

onMounted(() => {
    fetchStats()
})
</script>

<style scoped>
.p-card {
    background: #1f2937; /* gray-800 */
    border: 1px solid #374151; /* gray-700 */
}
:deep(.p-card-title) {
    margin-bottom: 0.5rem;
}
:deep(.p-datatable) .p-datatable-thead > tr > th {
    background: #111827; /* gray-900 */
    color: #9ca3af; /* gray-400 */
    border-color: #374151;
}
:deep(.p-datatable) .p-datatable-tbody > tr {
    background: transparent;
    color: #e5e7eb; /* gray-200 */
}
:deep(.p-datatable) .p-datatable-tbody > tr:not(:last-child) > td {
     border-color: #374151;
}
</style>
