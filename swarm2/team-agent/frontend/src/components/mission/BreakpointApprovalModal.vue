<template>
  <Dialog
    :visible="isOpen"
    @update:visible="handleClose"
    modal
    :style="{ width: '50rem' }"
    :breakpoints="{ '960px': '75vw', '640px': '90vw' }"
  >
    <template #header>
      <h3>Breakpoint Approval Required</h3>
    </template>

    <div class="breakpoint-content">
      <!-- Breakpoint Info -->
      <div class="info-banner">
        <div class="info-header">
          <Tag severity="info">
            {{ formatBreakpointType(breakpoint?.breakpoint_type) }}
          </Tag>
          <span class="workflow-id">
            Workflow: {{ breakpoint?.workflow_id }}
          </span>
        </div>
        <p class="info-text">
          This workflow has paused and requires your approval to continue.
        </p>
      </div>

      <!-- Options List -->
      <div v-if="breakpoint?.options && breakpoint.options.length > 0" class="options-section">
        <h4 class="section-title">Select a capability to proceed:</h4>

        <div class="options-list">
          <div
            v-for="(option, index) in breakpoint.options"
            :key="index"
            class="option-card"
            :class="{ 'selected': selectedOptionIndex === index }"
            @click="selectedOptionIndex = index"
          >
            <div class="option-header">
              <RadioButton
                v-model="selectedOptionIndex"
                :inputId="`option-${index}`"
                :value="index"
              />
              <label :for="`option-${index}`" class="option-label">
                <strong>Option {{ index + 1 }}</strong>
              </label>
            </div>

            <div class="option-details">
              <div class="detail-item">
                <span class="detail-label">Provider</span>
                <span class="detail-value">{{ option.provider_id }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">Capability</span>
                <span class="detail-value">{{ option.capability_id }}</span>
              </div>
            </div>

            <div class="option-metrics">
              <div class="metric-item">
                <span class="metric-label">Match Score</span>
                <Tag severity="success">{{ Math.round(option.match_score * 100) }}%</Tag>
              </div>

              <div class="metric-item">
                <span class="metric-label">Trust Score</span>
                <Tag :severity="getTrustSeverity(option.trust_score)">
                  {{ Math.round(option.trust_score) }}
                </Tag>
              </div>

              <div class="metric-item">
                <span class="metric-label">Price</span>
                <span class="price-value">${{ option.price.toFixed(2) }}</span>
              </div>
            </div>

            <div v-if="option.details" class="option-additional">
              <span class="additional-label">Additional Details:</span>
              <pre class="additional-details">{{ JSON.stringify(option.details, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- No Options -->
      <div v-else class="no-options">
        <p>No capability options available</p>
      </div>

      <!-- Approval Notes -->
      <div class="notes-section">
        <label for="approval-notes">Approval Notes (Optional)</label>
        <Textarea
          id="approval-notes"
          v-model="approvalNotes"
          placeholder="Add any notes or comments about this approval..."
          rows="3"
        />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <Button
          label="Reject"
          severity="secondary"
          text
          @click="handleReject"
          :loading="isRejecting"
        />
        <Button
          label="Approve & Continue"
          icon="pi pi-check"
          @click="handleApprove"
          :loading="isApproving"
          :disabled="selectedOptionIndex === null"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import RadioButton from 'primevue/radiobutton'
import Textarea from 'primevue/textarea'
import { useMissionStore } from '@/stores/mission.store'
import type { Breakpoint } from '@/types/mission.types'

const props = defineProps<{
  isOpen: boolean
  breakpoint: Breakpoint | null
}>()

const emit = defineEmits<{
  close: []
  approved: []
  rejected: []
}>()

const missionStore = useMissionStore()

const selectedOptionIndex = ref<number | null>(null)
const approvalNotes = ref('')
const isApproving = ref(false)
const isRejecting = ref(false)

// Reset selection when breakpoint changes
watch(() => props.breakpoint, () => {
  selectedOptionIndex.value = null
  approvalNotes.value = ''
})

function formatBreakpointType(type?: string): string {
  if (!type) return 'Unknown'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

function getTrustSeverity(score: number): string {
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  return 'danger'
}

async function handleApprove() {
  if (selectedOptionIndex.value === null || !props.breakpoint) return

  isApproving.value = true

  try {
    await missionStore.approveBreakpoint(
      props.breakpoint.breakpoint_id,
      selectedOptionIndex.value
    )

    emit('approved')
    handleClose()
  } catch (error) {
    console.error('Failed to approve breakpoint:', error)
    // TODO: Show error toast
  } finally {
    isApproving.value = false
  }
}

async function handleReject() {
  if (!props.breakpoint) return

  isRejecting.value = true

  try {
    await missionStore.rejectBreakpoint(props.breakpoint.breakpoint_id)

    emit('rejected')
    handleClose()
  } catch (error) {
    console.error('Failed to reject breakpoint:', error)
    // TODO: Show error toast
  } finally {
    isRejecting.value = false
  }
}

function handleClose() {
  selectedOptionIndex.value = null
  approvalNotes.value = ''
  emit('close')
}
</script>

<style scoped>
.breakpoint-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.info-banner {
  padding: 1rem;
  background-color: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 6px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.workflow-id {
  font-size: 0.875rem;
  color: #64748b;
}

.info-text {
  margin: 0;
  font-size: 0.875rem;
  color: #475569;
}

.options-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-card {
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-card:hover {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.option-card.selected {
  border-color: #3b82f6;
  background-color: #eff6ff;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.option-label {
  cursor: pointer;
  font-size: 1rem;
}

.option-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.75rem;
  color: #64748b;
}

.detail-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
}

.option-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.75rem;
  color: #64748b;
}

.price-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: #1e293b;
}

.option-additional {
  margin-top: 1rem;
}

.additional-label {
  font-size: 0.75rem;
  color: #64748b;
  display: block;
  margin-bottom: 0.5rem;
}

.additional-details {
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  background-color: #f1f5f9;
  padding: 0.5rem;
  border-radius: 4px;
  margin: 0;
  overflow-x: auto;
}

.no-options {
  padding: 3rem 1rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 8px;
  color: #64748b;
}

.notes-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.notes-section label {
  font-weight: 600;
  color: #334155;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}
</style>
