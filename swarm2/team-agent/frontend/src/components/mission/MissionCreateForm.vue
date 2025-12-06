<template>
  <form @submit.prevent="handleSubmit" class="mission-create-form">
    <div class="form-section">
      <!-- Mission Description -->
      <div class="form-field" :class="{ 'p-invalid': errors.description }">
        <label for="description" class="required">Mission Description</label>
        <Textarea
          id="description"
          v-model="form.description"
          placeholder="Describe what you want the agents to accomplish..."
          rows="4"
          @blur="validateField('description')"
          :invalid="!!errors.description"
        />
        <small v-if="errors.description" class="p-error">
          {{ errors.description }}
        </small>
        <small v-else class="p-text-secondary">
          Provide a clear description of the mission objectives
        </small>
      </div>

      <!-- Required Capabilities -->
      <div class="form-field" :class="{ 'p-invalid': errors.required_capabilities }">
        <label>Required Capabilities</label>

        <Button
          label="Add Capability"
          icon="pi pi-plus"
          size="small"
          outlined
          @click="addCapability"
          class="mb-3"
        />

        <div
          v-for="(cap, index) in form.required_capabilities"
          :key="index"
          class="capability-item"
        >
          <div class="capability-header">
            <Dropdown
              v-model="cap.capability_type"
              :options="capabilityTypes"
              optionLabel="label"
              optionValue="value"
              placeholder="Select capability type"
              class="flex-1"
            />
            <Button
              icon="pi pi-times"
              severity="danger"
              text
              rounded
              @click="removeCapability(index)"
              aria-label="Remove capability"
            />
          </div>

          <div class="capability-params">
            <div class="form-field">
              <label>Min Trust Score</label>
              <InputNumber
                v-model="cap.min_trust_score"
                :min="0"
                :max="100"
                :step="5"
              />
            </div>

            <div class="form-field">
              <label>Max Cost</label>
              <InputNumber
                v-model="cap.max_cost"
                :min="0"
                :step="10"
              />
            </div>
          </div>
        </div>

        <small v-if="errors.required_capabilities" class="p-error">
          {{ errors.required_capabilities }}
        </small>
      </div>

      <!-- Mission Parameters -->
      <div class="form-row">
        <div class="form-field">
          <label>Min Trust Score</label>
          <InputNumber
            v-model="form.min_trust_score"
            :min="0"
            :max="100"
            :step="5"
          />
          <small class="p-text-secondary">
            Minimum trust score required (0-100)
          </small>
        </div>

        <div class="form-field">
          <label>Max Cost</label>
          <InputNumber
            v-model="form.max_cost"
            :min="0"
            :step="50"
          />
          <small class="p-text-secondary">
            Maximum allowed cost (leave empty for unlimited)
          </small>
        </div>
      </div>

      <!-- Breakpoints -->
      <div class="form-field">
        <label>Breakpoints</label>
        <div class="breakpoints-list">
          <div v-for="bp in breakpointOptions" :key="bp.value" class="field-checkbox">
            <Checkbox
              v-model="form.breakpoints"
              :inputId="bp.value"
              :value="bp.value"
            />
            <label :for="bp.value">{{ bp.label }}</label>
          </div>
        </div>
        <small class="p-text-secondary">
          Select stages where human approval is required
        </small>
      </div>

      <!-- Auto-Approval Settings -->
      <Panel header="Auto-Approval Settings" class="auto-approve-panel">
        <div class="form-field">
          <div class="field-checkbox">
            <Checkbox
              v-model="form.auto_approve_trusted"
              inputId="autoApprove"
              :binary="true"
            />
            <label for="autoApprove">Auto-approve high-trust agents</label>
          </div>
        </div>

        <div v-if="form.auto_approve_trusted" class="form-field">
          <label>Auto-Approve Threshold</label>
          <Slider
            v-model="form.auto_approve_threshold"
            :min="0"
            :max="100"
            :step="5"
            class="mb-2"
          />
          <small class="p-text-secondary">
            Trust score ≥ {{ form.auto_approve_threshold }} will auto-approve
          </small>
        </div>
      </Panel>

      <!-- Submit Buttons -->
      <div class="form-actions">
        <Button
          label="Cancel"
          severity="secondary"
          text
          @click="handleCancel"
        />
        <Button
          type="submit"
          label="Submit Mission"
          icon="pi pi-check"
          :loading="isSubmitting"
          :disabled="!isFormValid"
        />
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Slider from 'primevue/slider'
import Panel from 'primevue/panel'
import { useMissionStore } from '@/stores/mission.store'
import type { MissionSpec, BreakpointType } from '@/types/mission.types'

const router = useRouter()
const missionStore = useMissionStore()

const capabilityTypes = [
  { label: 'Code Generation', value: 'code_generation' },
  { label: 'Code Review', value: 'code_review' },
  { label: 'Testing', value: 'testing' },
  { label: 'Security Audit', value: 'security_audit' },
  { label: 'Documentation', value: 'documentation' },
  { label: 'Deployment', value: 'deployment' },
  { label: 'Monitoring', value: 'monitoring' },
  { label: 'Data Analysis', value: 'data_analysis' }
]

const breakpointOptions = [
  { label: 'Capability Selection - Require approval for capability choices', value: 'capability_selection' },
  { label: 'Design Approval - Review architecture before building', value: 'design_approval' },
  { label: 'Build Approval - Review implementation before deployment', value: 'build_approval' },
  { label: 'Review Approval - Confirm code review results', value: 'review_approval' }
]

const form = reactive({
  description: '',
  required_capabilities: [] as Array<{
    capability_type: string
    min_trust_score?: number
    max_cost?: number
  }>,
  min_trust_score: 75,
  max_cost: undefined as number | undefined,
  breakpoints: [] as BreakpointType[],
  auto_approve_trusted: true,
  auto_approve_threshold: 90
})

const errors = reactive({
  description: '',
  required_capabilities: ''
})

const isSubmitting = ref(false)

const isFormValid = computed(() => {
  return (
    form.description.trim().length > 0 &&
    !errors.description &&
    !errors.required_capabilities
  )
})

function addCapability() {
  form.required_capabilities.push({
    capability_type: '',
    min_trust_score: 70,
    max_cost: undefined
  })
}

function removeCapability(index: number) {
  form.required_capabilities.splice(index, 1)
}

function validateField(field: string) {
  if (field === 'description') {
    if (!form.description.trim()) {
      errors.description = 'Mission description is required'
    } else if (form.description.length < 10) {
      errors.description = 'Description must be at least 10 characters'
    } else {
      errors.description = ''
    }
  }
}

async function handleSubmit() {
  // Validate all fields
  validateField('description')

  if (!isFormValid.value) {
    return
  }

  isSubmitting.value = true

  try {
    const missionSpec: MissionSpec = {
      mission_id: `mission_${Date.now()}`,
      description: form.description,
      required_capabilities: form.required_capabilities.filter(c => c.capability_type),
      max_cost: form.max_cost,
      min_trust_score: form.min_trust_score,
      breakpoints: form.breakpoints,
      auto_approve_trusted: form.auto_approve_trusted,
      auto_approve_threshold: form.auto_approve_threshold
    }

    const result = await missionStore.submitMission(missionSpec)

    // Navigate to mission detail view
    router.push(`/missions/${result}`)
  } catch (error) {
    console.error('Failed to submit mission:', error)
    // TODO: Show error toast
  } finally {
    isSubmitting.value = false
  }
}

function handleCancel() {
  router.push('/missions')
}
</script>

<style scoped>
.mission-create-form {
  max-width: 900px;
  margin: 0 auto;
}

.form-section {
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
  font-weight: 600;
  color: #334155;
}

.form-field label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.capability-item {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.capability-header {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  margin-bottom: 1rem;
}

.capability-header .flex-1 {
  flex: 1;
}

.capability-params {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.capability-params .form-field label {
  font-size: 0.875rem;
  font-weight: 500;
}

.breakpoints-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field-checkbox label {
  font-weight: 400 !important;
  cursor: pointer;
  margin: 0;
}

.auto-approve-panel {
  background-color: #eff6ff;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

small.p-error {
  color: #ef4444;
}

small.p-text-secondary {
  color: #64748b;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 0.75rem;
}
</style>
