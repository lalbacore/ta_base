<template>
  <c-box as="form" @submit.prevent="handleSubmit">
    <c-v-stack spacing="6" align="stretch">
      <!-- Mission Description -->
      <c-form-control :is-invalid="errors.description" is-required>
        <c-form-label>Mission Description</c-form-label>
        <c-textarea
          v-model="form.description"
          placeholder="Describe what you want the agents to accomplish..."
          rows="4"
          @blur="validateField('description')"
        />
        <c-form-error-message v-if="errors.description">
          {{ errors.description }}
        </c-form-error-message>
        <c-form-helper-text>
          Provide a clear description of the mission objectives
        </c-form-helper-text>
      </c-form-control>

      <!-- Required Capabilities -->
      <c-form-control :is-invalid="errors.required_capabilities">
        <c-form-label>Required Capabilities</c-form-label>
        <c-v-stack spacing="3">
          <c-button
            size="sm"
            left-icon="+"
            variant="outline"
            @click="addCapability"
          >
            Add Capability
          </c-button>

          <c-box
            v-for="(cap, index) in form.required_capabilities"
            :key="index"
            p="4"
            border="1px"
            border-color="gray.200"
            border-radius="md"
          >
            <c-h-stack spacing="3" mb="3">
              <c-select
                v-model="cap.capability_type"
                placeholder="Select capability type"
                flex="1"
              >
                <option value="code_generation">Code Generation</option>
                <option value="code_review">Code Review</option>
                <option value="testing">Testing</option>
                <option value="security_audit">Security Audit</option>
                <option value="documentation">Documentation</option>
                <option value="deployment">Deployment</option>
                <option value="monitoring">Monitoring</option>
                <option value="data_analysis">Data Analysis</option>
              </c-select>
              <c-icon-button
                aria-label="Remove capability"
                icon="close"
                size="sm"
                color-scheme="red"
                variant="ghost"
                @click="removeCapability(index)"
              />
            </c-h-stack>

            <c-simple-grid columns="2" spacing="3">
              <c-form-control>
                <c-form-label font-size="sm">Min Trust Score</c-form-label>
                <c-number-input
                  v-model="cap.min_trust_score"
                  :min="0"
                  :max="100"
                  :step="5"
                />
              </c-form-control>

              <c-form-control>
                <c-form-label font-size="sm">Max Cost</c-form-label>
                <c-number-input
                  v-model="cap.max_cost"
                  :min="0"
                  :step="10"
                />
              </c-form-control>
            </c-simple-grid>
          </c-box>
        </c-v-stack>
        <c-form-error-message v-if="errors.required_capabilities">
          {{ errors.required_capabilities }}
        </c-form-error-message>
      </c-form-control>

      <!-- Mission Parameters -->
      <c-simple-grid columns="2" spacing="4">
        <c-form-control>
          <c-form-label>Min Trust Score</c-form-label>
          <c-number-input
            v-model="form.min_trust_score"
            :min="0"
            :max="100"
            :step="5"
          />
          <c-form-helper-text>
            Minimum trust score required (0-100)
          </c-form-helper-text>
        </c-form-control>

        <c-form-control>
          <c-form-label>Max Cost</c-form-label>
          <c-number-input
            v-model="form.max_cost"
            :min="0"
            :step="50"
          />
          <c-form-helper-text>
            Maximum allowed cost (leave empty for unlimited)
          </c-form-helper-text>
        </c-form-control>
      </c-simple-grid>

      <!-- Breakpoints -->
      <c-form-control>
        <c-form-label>Breakpoints</c-form-label>
        <c-checkbox-group v-model="form.breakpoints">
          <c-v-stack spacing="2" align="start">
            <c-checkbox value="capability_selection">
              Capability Selection - Require approval for capability choices
            </c-checkbox>
            <c-checkbox value="design_approval">
              Design Approval - Review architecture before building
            </c-checkbox>
            <c-checkbox value="build_approval">
              Build Approval - Review implementation before deployment
            </c-checkbox>
            <c-checkbox value="review_approval">
              Review Approval - Confirm code review results
            </c-checkbox>
          </c-v-stack>
        </c-checkbox-group>
        <c-form-helper-text>
          Select stages where human approval is required
        </c-form-helper-text>
      </c-form-control>

      <!-- Auto-Approval Settings -->
      <c-box p="4" bg="blue.50" border-radius="md">
        <c-v-stack spacing="3" align="stretch">
          <c-checkbox v-model="form.auto_approve_trusted">
            Auto-approve high-trust agents
          </c-checkbox>

          <c-form-control v-if="form.auto_approve_trusted">
            <c-form-label>Auto-Approve Threshold</c-form-label>
            <c-slider
              v-model="form.auto_approve_threshold"
              :min="0"
              :max="100"
              :step="5"
            >
              <c-slider-track>
                <c-slider-filled-track />
              </c-slider-track>
              <c-slider-thumb />
            </c-slider>
            <c-text font-size="sm" color="gray.600" mt="1">
              Trust score ≥ {{ form.auto_approve_threshold }} will auto-approve
            </c-text>
          </c-form-control>
        </c-v-stack>
      </c-box>

      <!-- Submit Buttons -->
      <c-h-stack spacing="3" justify="flex-end">
        <c-button variant="ghost" @click="handleCancel">
          Cancel
        </c-button>
        <c-button
          type="submit"
          color-scheme="blue"
          :is-loading="isSubmitting"
          :is-disabled="!isFormValid"
        >
          Submit Mission
        </c-button>
      </c-h-stack>
    </c-v-stack>
  </c-box>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  CBox,
  CVStack,
  CHStack,
  CButton,
  CFormControl,
  CFormLabel,
  CFormErrorMessage,
  CFormHelperText,
  CTextarea,
  CSelect,
  CNumberInput,
  CCheckbox,
  CCheckboxGroup,
  CSlider,
  CSliderTrack,
  CSliderFilledTrack,
  CSliderThumb,
  CText,
  CSimpleGrid,
  CIconButton
} from '@chakra-ui/vue-next'
import { useMissionStore } from '@/stores/mission.store'
import type { MissionSpec, BreakpointType } from '@/types/mission.types'

const router = useRouter()
const missionStore = useMissionStore()

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
