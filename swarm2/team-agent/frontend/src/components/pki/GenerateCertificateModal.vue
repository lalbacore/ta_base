<template>
  <Dialog
    :visible="isOpen"
    @update:visible="handleClose"
    modal
    :style="{ width: '600px' }"
    :header="'Generate New Certificate'"
  >
    <div class="generate-cert-form">
      <Message severity="info" :closable="false">
        Generate a new certificate for a trust domain. This will create a certificate signed by the Root CA.
      </Message>

      <div class="form-field">
        <label for="domain" class="required">Trust Domain</label>
        <Dropdown
          id="domain"
          v-model="form.domain"
          :options="domainOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select domain"
          class="w-full"
        />
        <small class="field-help">The trust domain for this certificate</small>
      </div>

      <div class="form-field">
        <label for="subject">Subject (CN)</label>
        <InputText
          id="subject"
          v-model="form.subject"
          placeholder="e.g., Team Agent Execution"
          class="w-full"
        />
      </div>

      <div class="form-field">
        <label for="keySize">Key Size</label>
        <SelectButton
          id="keySize"
          v-model="form.keySize"
          :options="keySizeOptions"
          optionLabel="label"
          optionValue="value"
        />
        <small class="field-help">Larger keys are more secure but slower</small>
      </div>

      <div class="form-field">
        <label for="algorithm">Signature Algorithm</label>
        <Dropdown
          id="algorithm"
          v-model="form.algorithm"
          :options="algorithmOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Select algorithm"
          class="w-full"
        />
      </div>

      <div class="form-field">
        <label for="validityDays">Validity Period (Days)</label>
        <InputNumber
          id="validityDays"
          v-model="form.validityDays"
          :min="30"
          :max="3650"
          :step="30"
          showButtons
          class="w-full"
        />
        <small class="field-help">How long until the certificate expires</small>
      </div>

      <div class="form-summary">
        <h4>Certificate Summary</h4>
        <div class="summary-item">
          <span>Domain:</span>
          <strong>{{ form.domain || 'Not selected' }}</strong>
        </div>
        <div class="summary-item">
          <span>Subject:</span>
          <strong>{{ form.subject || 'Default' }}</strong>
        </div>
        <div class="summary-item">
          <span>Key Size:</span>
          <strong>{{ form.keySize }} bits</strong>
        </div>
        <div class="summary-item">
          <span>Valid For:</span>
          <strong>{{ form.validityDays }} days ({{ Math.floor(form.validityDays / 365) }} year{{ Math.floor(form.validityDays / 365) !== 1 ? 's' : '' }})</strong>
        </div>
      </div>
    </div>

    <template #footer>
      <Button label="Cancel" severity="secondary" text @click="handleClose" />
      <Button
        label="Generate Certificate"
        icon="pi pi-check"
        :loading="isGenerating"
        :disabled="!form.domain"
        @click="handleGenerate"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import SelectButton from 'primevue/selectbutton'
import Message from 'primevue/message'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'generate', certData: any): void
}>()

const isGenerating = ref(false)

const form = reactive({
  domain: '',
  subject: '',
  keySize: 2048,
  algorithm: 'SHA256-RSA',
  validityDays: 365
})

const domainOptions = [
  { label: 'Root CA', value: 'root' },
  { label: 'Government', value: 'government' },
  { label: 'Execution', value: 'execution' },
  { label: 'Logging', value: 'logging' },
  { label: 'Custom', value: 'custom' }
]

const keySizeOptions = [
  { label: '2048', value: 2048 },
  { label: '4096', value: 4096 }
]

const algorithmOptions = [
  { label: 'SHA256-RSA', value: 'SHA256-RSA' },
  { label: 'SHA384-RSA', value: 'SHA384-RSA' },
  { label: 'SHA512-RSA', value: 'SHA512-RSA' }
]

function handleClose() {
  emit('close')
  resetForm()
}

function resetForm() {
  form.domain = ''
  form.subject = ''
  form.keySize = 2048
  form.algorithm = 'SHA256-RSA'
  form.validityDays = 365
}

async function handleGenerate() {
  isGenerating.value = true

  try {
    // Emit the certificate generation request
    const certData = {
      domain: form.domain,
      subject: form.subject || `Team Agent ${form.domain.charAt(0).toUpperCase() + form.domain.slice(1)}`,
      key_size: form.keySize,
      algorithm: form.algorithm,
      validity_days: form.validityDays
    }

    emit('generate', certData)
    handleClose()
  } catch (error) {
    console.error('Failed to generate certificate:', error)
  } finally {
    isGenerating.value = false
  }
}
</script>

<style scoped>
.generate-cert-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field label {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
}

.form-field label.required::after {
  content: ' *';
  color: #ef4444;
}

.field-help {
  color: #64748b;
  font-size: 0.75rem;
}

.w-full {
  width: 100%;
}

.form-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
}

.form-summary h4 {
  margin: 0 0 0.75rem 0;
  color: #1e293b;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-size: 0.875rem;
}

.summary-item span {
  color: #64748b;
}

.summary-item strong {
  color: #1e293b;
}
</style>
