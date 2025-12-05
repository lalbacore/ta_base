<template>
  <c-modal :is-open="isOpen" @close="handleClose" size="xl">
    <c-modal-overlay />
    <c-modal-content>
      <c-modal-header>
        <c-heading size="md">Breakpoint Approval Required</c-heading>
      </c-modal-header>
      <c-modal-close-button />

      <c-modal-body>
        <c-v-stack spacing="4" align="stretch">
          <!-- Breakpoint Info -->
          <c-box
            p="4"
            bg="blue.50"
            border-radius="md"
            border="1px"
            border-color="blue.200"
          >
            <c-h-stack spacing="2" mb="2">
              <c-badge color-scheme="blue">
                {{ formatBreakpointType(breakpoint?.breakpoint_type) }}
              </c-badge>
              <c-text font-size="sm" color="gray.600">
                Workflow: {{ breakpoint?.workflow_id }}
              </c-text>
            </c-h-stack>
            <c-text font-size="sm">
              This workflow has paused and requires your approval to continue.
            </c-text>
          </c-box>

          <!-- Options List -->
          <c-box v-if="breakpoint?.options && breakpoint.options.length > 0">
            <c-heading size="sm" mb="3">
              Select a capability to proceed:
            </c-heading>

            <c-radio-group v-model="selectedOptionIndex">
              <c-v-stack spacing="3" align="stretch">
                <c-box
                  v-for="(option, index) in breakpoint.options"
                  :key="index"
                  p="4"
                  border="2px"
                  :border-color="selectedOptionIndex === index ? 'blue.500' : 'gray.200'"
                  border-radius="md"
                  cursor="pointer"
                  transition="all 0.2s"
                  _hover="{ borderColor: 'blue.300', bg: 'blue.50' }"
                  @click="selectedOptionIndex = index"
                >
                  <c-radio :value="index" mb="3">
                    <c-text font-weight="bold">
                      Option {{ index + 1 }}
                    </c-text>
                  </c-radio>

                  <c-simple-grid columns="2" spacing="3" mb="3">
                    <c-box>
                      <c-text font-size="xs" color="gray.500">Provider</c-text>
                      <c-text font-size="sm" font-weight="medium">
                        {{ option.provider_id }}
                      </c-text>
                    </c-box>

                    <c-box>
                      <c-text font-size="xs" color="gray.500">Capability</c-text>
                      <c-text font-size="sm" font-weight="medium">
                        {{ option.capability_id }}
                      </c-text>
                    </c-box>
                  </c-simple-grid>

                  <c-simple-grid columns="3" spacing="3">
                    <c-box>
                      <c-text font-size="xs" color="gray.500">Match Score</c-text>
                      <c-badge color-scheme="green">
                        {{ Math.round(option.match_score * 100) }}%
                      </c-badge>
                    </c-box>

                    <c-box>
                      <c-text font-size="xs" color="gray.500">Trust Score</c-text>
                      <c-badge :color-scheme="getTrustColorScheme(option.trust_score)">
                        {{ Math.round(option.trust_score) }}
                      </c-badge>
                    </c-box>

                    <c-box>
                      <c-text font-size="xs" color="gray.500">Price</c-text>
                      <c-text font-size="sm" font-weight="bold">
                        ${{ option.price.toFixed(2) }}
                      </c-text>
                    </c-box>
                  </c-simple-grid>

                  <!-- Details (collapsed by default) -->
                  <c-box v-if="option.details" mt="3">
                    <c-text font-size="xs" color="gray.500" mb="1">
                      Additional Details:
                    </c-text>
                    <c-code font-size="xs" display="block" p="2" bg="gray.100" border-radius="sm">
                      {{ JSON.stringify(option.details, null, 2) }}
                    </c-code>
                  </c-box>
                </c-box>
              </c-v-stack>
            </c-radio-group>
          </c-box>

          <!-- No Options -->
          <c-box
            v-else
            p="6"
            text-align="center"
            border="2px dashed"
            border-color="gray.300"
            border-radius="md"
          >
            <c-text color="gray.500">
              No capability options available
            </c-text>
          </c-box>

          <!-- Approval Reason (optional) -->
          <c-form-control>
            <c-form-label>Approval Notes (Optional)</c-form-label>
            <c-textarea
              v-model="approvalNotes"
              placeholder="Add any notes or comments about this approval..."
              rows="3"
            />
          </c-form-control>
        </c-v-stack>
      </c-modal-body>

      <c-modal-footer>
        <c-h-stack spacing="3">
          <c-button
            variant="ghost"
            @click="handleReject"
            :is-loading="isRejecting"
          >
            Reject
          </c-button>
          <c-button
            color-scheme="blue"
            @click="handleApprove"
            :is-loading="isApproving"
            :is-disabled="selectedOptionIndex === null"
          >
            Approve & Continue
          </c-button>
        </c-h-stack>
      </c-modal-footer>
    </c-modal-content>
  </c-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  CModal,
  CModalOverlay,
  CModalContent,
  CModalHeader,
  CModalBody,
  CModalFooter,
  CModalCloseButton,
  CBox,
  CHStack,
  CVStack,
  CHeading,
  CText,
  CBadge,
  CButton,
  CRadioGroup,
  CRadio,
  CSimpleGrid,
  CFormControl,
  CFormLabel,
  CTextarea,
  CCode
} from '@chakra-ui/vue-next'
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

function getTrustColorScheme(score: number): string {
  if (score >= 80) return 'green'
  if (score >= 60) return 'yellow'
  return 'red'
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
