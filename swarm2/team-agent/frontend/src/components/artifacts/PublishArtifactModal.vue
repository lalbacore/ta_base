<template>
  <Dialog 
    :visible="isOpen" 
    @update:visible="$emit('close')"
    header="Publish Artifact" 
    :modal="true" 
    :style="{ width: '500px' }"
  >
    <div class="publish-modal">
      <div class="field">
        <label for="backend" class="font-bold block mb-2">Storage Service</label>
        <Dropdown 
          id="backend"
          v-model="selectedBackend" 
          :options="backends" 
          optionLabel="storage_type" 
          optionValue="storage_type"
          placeholder="Select a storage service"
          class="w-full"
        />
        <small class="text-gray-500" v-if="selectedBackendInfo">
          {{ selectedBackendInfo.info }}
        </small>
      </div>

      <div class="field mt-4">
        <label class="font-bold block mb-2">Security Options</label>
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-2">
            <RadioButton v-model="selectedOption" inputId="opt-sign" name="options" value="sign" />
            <label for="opt-sign">Sign Only (Recommended)</label>
          </div>
          <div class="flex items-center gap-2">
            <RadioButton v-model="selectedOption" inputId="opt-encrypt" name="options" value="encrypt" />
            <label for="opt-encrypt">Encrypt Only</label>
          </div>
          <div class="flex items-center gap-2">
            <RadioButton v-model="selectedOption" inputId="opt-both" name="options" value="encrypt_and_sign" />
            <label for="opt-both">Encrypt & Sign</label>
          </div>
          <div class="flex items-center gap-2">
            <RadioButton v-model="selectedOption" inputId="opt-none" name="options" value="none" />
            <label for="opt-none">None (Plaintext)</label>
          </div>
        </div>
      </div>

      <div class="field mt-4" v-if="isEncryptionSelected">
        <label for="password" class="font-bold block mb-2">Encryption Password (Optional)</label>
        <Password 
          id="password" 
          v-model="password" 
          :feedback="false" 
          placeholder="Leave empty to auto-generate key"
          toggleMask 
          class="w-full"
          inputClass="w-full"
        />
        <small class="text-gray-500">
          If provided, this password will be required to decrypt the artifact.
        </small>
      </div>

      <div class="flex justify-end gap-2 mt-6">
        <Button label="Cancel" severity="secondary" @click="$emit('close')" text />
        <Button 
          label="Publish" 
          icon="pi pi-upload" 
          @click="handlePublish" 
          :loading="loading"
        />
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import RadioButton from 'primevue/radiobutton'
import Password from 'primevue/password'
import axios from 'axios'

const props = defineProps<{
  isOpen: boolean
  workflowId: string
  artifactName: string
}>()

const emit = defineEmits(['close', 'published'])

const backends = ref<any[]>([])
const selectedBackend = ref('local')
const selectedOption = ref('sign')
const password = ref('')
const loading = ref(false)

const selectedBackendInfo = computed(() => {
  return backends.value.find(b => b.storage_type === selectedBackend.value)
})

const isEncryptionSelected = computed(() => {
  return ['encrypt', 'encrypt_and_sign'].includes(selectedOption.value)
})

onMounted(async () => {
  try {
    const response = await axios.get('/api/storage/backends')
    backends.value = response.data
  } catch (e) {
    console.error('Failed to load storage backends', e)
    // Fallback
    backends.value = [
      { storage_type: 'local', info: 'Local Filesystem Storage' },
      { storage_type: 'ipfs', info: 'IPFS Distributed Storage' }
    ]
  }
})

async function handlePublish() {
  loading.value = true
  try {
    const payload = {
      storage_backend: selectedBackend.value,
      options: selectedOption.value,
      encryption_password: password.value || undefined
    }

    const response = await axios.post(
      `/api/workflow/${props.workflowId}/artifact/${props.artifactName}/publish-enhanced`, 
      payload
    )

    emit('published', response.data)
    emit('close')
  } catch (error: any) {
    console.error('Publishing failed', error)
    alert(`Failed to publish: ${error.response?.data?.error || error.message}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.publish-modal {
  padding: 0.5rem;
}
.field {
    margin-bottom: 1.5rem;
}
</style>
