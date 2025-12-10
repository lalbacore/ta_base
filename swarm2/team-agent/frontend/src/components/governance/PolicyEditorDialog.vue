<template>
  <Dialog
    v-model:visible="isVisible"
    :header="editMode ? 'Edit Policy' : 'Create New Policy'"
    :modal="true"
    :style="{ width: '600px' }"
    @hide="onClose"
  >
    <div class="policy-form">
      <!-- Policy Metadata -->
      <div class="form-section">
        <h3>Policy Information</h3>

        <div class="form-field">
          <label for="policy-name">Policy Name *</label>
          <InputText
            id="policy-name"
            v-model="formData.name"
            placeholder="e.g., Production, Development, Strict"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="policy-description">Description</label>
          <Textarea
            id="policy-description"
            v-model="formData.description"
            placeholder="Describe the purpose of this policy..."
            rows="3"
            class="w-full"
          />
        </div>
      </div>

      <!-- Trust Settings -->
      <div class="form-section">
        <h3>Trust & Approval Settings</h3>

        <div class="form-field">
          <label for="min-trust">Minimum Trust Score: {{ formData.min_trust_score }}%</label>
          <Slider
            id="min-trust"
            v-model="formData.min_trust_score"
            :min="0"
            :max="100"
            class="w-full"
          />
        </div>

        <div class="form-field">
          <label for="auto-approve">Auto-Approve Threshold: {{ formData.auto_approve_threshold }}%</label>
          <Slider
            id="auto-approve"
            v-model="formData.auto_approve_threshold"
            :min="0"
            :max="100"
            class="w-full"
          />
        </div>
      </div>

      <!-- Cost Settings -->
      <div class="form-section">
        <h3>Cost Constraints</h3>

        <div class="form-field">
          <label for="max-cost">Maximum Cost Per Mission (Tokens)</label>
          <InputNumber
            id="max-cost"
            v-model="formData.max_cost_per_mission"
            :min="0"
            suffix=" Tokens"
            showButtons
            class="w-full"
          />
        </div>
      </div>

      <!-- Review Requirements -->
      <div class="form-section">
        <h3>Review Requirements</h3>

        <div class="form-field-checkbox">
          <Checkbox
            id="security-review"
            v-model="formData.require_security_review"
            :binary="true"
          />
          <label for="security-review">Require Security Review</label>
        </div>

        <div class="form-field-checkbox">
          <Checkbox
            id="code-review"
            v-model="formData.require_code_review"
            :binary="true"
          />
          <label for="code-review">Require Code Review</label>
        </div>

        <div class="form-field-checkbox">
          <Checkbox
            id="breakpoints"
            v-model="formData.enable_breakpoints"
            :binary="true"
          />
          <label for="breakpoints">Enable Breakpoints</label>
        </div>
      </div>

      <!-- Language Settings -->
      <div class="form-section">
        <h3>Allowed Languages</h3>

        <div class="form-field">
          <MultiSelect
            v-model="formData.allowed_languages"
            :options="availableLanguages"
            placeholder="Select allowed languages"
            display="chip"
            class="w-full"
          />
        </div>
      </div>
    </div>

    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="onClose"
        severity="secondary"
        text
      />
      <Button
        :label="editMode ? 'Save Changes' : 'Create Policy'"
        icon="pi pi-check"
        @click="onSubmit"
        :loading="isSaving"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Slider from 'primevue/slider'
import Checkbox from 'primevue/checkbox'
import MultiSelect from 'primevue/multiselect'
import type { Policy } from '@/types/governance.types'

interface Props {
  visible: boolean
  policy?: Policy | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'save', policy: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isVisible = ref(props.visible)
const isSaving = ref(false)
const editMode = ref(false)

const availableLanguages = [
  'python',
  'javascript',
  'typescript',
  'go',
  'rust',
  'java',
  'c',
  'cpp',
  'csharp',
  'ruby',
  'php',
  'swift',
  'kotlin'
]

const formData = ref({
  name: '',
  description: '',
  min_trust_score: 75,
  require_security_review: true,
  require_code_review: true,
  allowed_languages: ['python', 'javascript', 'typescript', 'go', 'rust'],
  max_cost_per_mission: 500,
  auto_approve_threshold: 90,
  enable_breakpoints: true
})

watch(() => props.visible, (newVal) => {
  isVisible.value = newVal
  if (newVal) {
    if (props.policy) {
      editMode.value = true
      formData.value = {
        name: props.policy.name,
        description: props.policy.description || '',
        min_trust_score: props.policy.min_trust_score,
        require_security_review: props.policy.require_security_review,
        require_code_review: props.policy.require_code_review,
        allowed_languages: props.policy.allowed_languages,
        max_cost_per_mission: props.policy.max_cost_per_mission,
        auto_approve_threshold: props.policy.auto_approve_threshold,
        enable_breakpoints: props.policy.enable_breakpoints
      }
    } else {
      editMode.value = false
      resetForm()
    }
  }
})

watch(isVisible, (newVal) => {
  emit('update:visible', newVal)
})

function resetForm() {
  formData.value = {
    name: '',
    description: '',
    min_trust_score: 75,
    require_security_review: true,
    require_code_review: true,
    allowed_languages: ['python', 'javascript', 'typescript', 'go', 'rust'],
    max_cost_per_mission: 500,
    auto_approve_threshold: 90,
    enable_breakpoints: true
  }
}

function onClose() {
  isVisible.value = false
  resetForm()
}

async function onSubmit() {
  if (!formData.value.name.trim()) {
    return
  }

  isSaving.value = true
  try {
    emit('save', formData.value)
    onClose()
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.policy-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-section h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e2e8f0;
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

.form-field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.form-field-checkbox label {
  font-weight: 500;
  color: #1e293b;
  font-size: 0.875rem;
  cursor: pointer;
}

.w-full {
  width: 100%;
}
</style>
