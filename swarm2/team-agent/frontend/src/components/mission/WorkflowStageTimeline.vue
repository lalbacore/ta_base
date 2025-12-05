<template>
  <c-box>
    <c-heading size="md" mb="4">Workflow Progress</c-heading>

    <c-v-stack spacing="0" align="stretch">
      <c-box
        v-for="(stage, index) in stages"
        :key="stage.stage_name"
        position="relative"
      >
        <!-- Timeline Line -->
        <c-box
          v-if="index < stages.length - 1"
          position="absolute"
          left="19px"
          top="40px"
          bottom="-40px"
          w="2px"
          :bg="getLineColor(stage, stages[index + 1])"
        />

        <!-- Stage Item -->
        <c-flex align="start" py="4">
          <!-- Status Icon -->
          <c-box
            position="relative"
            z-index="1"
            flex-shrink="0"
            mr="4"
          >
            <c-circle
              size="40px"
              :bg="getStatusColor(stage.status)"
              color="white"
              display="flex"
              align-items="center"
              justify-content="center"
              box-shadow="0 0 0 4px white"
            >
              <c-text v-if="stage.status === 'completed'" font-size="xl">
                ✓
              </c-text>
              <c-text v-else-if="stage.status === 'failed'" font-size="xl">
                ✗
              </c-text>
              <c-spinner
                v-else-if="stage.status === 'running'"
                size="sm"
                color="white"
              />
              <c-text v-else font-size="xl">
                ○
              </c-text>
            </c-circle>
          </c-box>

          <!-- Stage Content -->
          <c-box flex="1">
            <c-h-stack spacing="3" mb="2">
              <c-heading size="sm">
                {{ formatStageName(stage.stage_name) }}
              </c-heading>
              <c-badge :color-scheme="getStatusColorScheme(stage.status)">
                {{ stage.status }}
              </c-badge>
            </c-h-stack>

            <c-text font-size="sm" color="gray.600" mb="2">
              {{ getStageDescription(stage.stage_name) }}
            </c-text>

            <!-- Timestamps -->
            <c-h-stack spacing="4" font-size="xs" color="gray.500">
              <c-text v-if="stage.started_at">
                Started: {{ formatTimestamp(stage.started_at) }}
              </c-text>
              <c-text v-if="stage.completed_at">
                Completed: {{ formatTimestamp(stage.completed_at) }}
              </c-text>
              <c-text v-if="stage.started_at && stage.completed_at">
                Duration: {{ calculateDuration(stage.started_at, stage.completed_at) }}
              </c-text>
            </c-h-stack>

            <!-- Stage Output (if available) -->
            <c-box
              v-if="stage.output && stage.status === 'completed'"
              mt="3"
              p="3"
              bg="gray.50"
              border-radius="md"
              border="1px"
              border-color="gray.200"
            >
              <c-text font-size="sm" font-weight="medium" mb="2">
                Output
              </c-text>
              <c-code font-size="xs" display="block" white-space="pre-wrap">
                {{ JSON.stringify(stage.output, null, 2) }}
              </c-code>
            </c-box>
          </c-box>
        </c-flex>
      </c-box>
    </c-v-stack>

    <!-- Empty State -->
    <c-box
      v-if="stages.length === 0"
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="md"
    >
      <c-text color="gray.500">
        No workflow stages yet
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import {
  CBox,
  CFlex,
  CHStack,
  CVStack,
  CHeading,
  CText,
  CBadge,
  CCircle,
  CSpinner,
  CCode
} from '@chakra-ui/vue-next'
import type { WorkflowStage } from '@/types/mission.types'

defineProps<{
  stages: WorkflowStage[]
}>()

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function getStageDescription(stage: string): string {
  const descriptions: Record<string, string> = {
    'architect': 'Designing system architecture and component structure',
    'builder': 'Implementing the designed solution',
    'critic': 'Reviewing code quality and security',
    'governance': 'Validating compliance and policy adherence',
    'recorder': 'Recording workflow results and generating manifest',
    'initializing': 'Setting up workflow environment',
    'capability_selection': 'Selecting capabilities for execution'
  }
  return descriptions[stage] || 'Processing stage...'
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'completed':
      return 'green.500'
    case 'running':
      return 'blue.500'
    case 'failed':
      return 'red.500'
    default:
      return 'gray.300'
  }
}

function getStatusColorScheme(status: string): string {
  switch (status) {
    case 'completed':
      return 'green'
    case 'running':
      return 'blue'
    case 'failed':
      return 'red'
    default:
      return 'gray'
  }
}

function getLineColor(currentStage: WorkflowStage, nextStage: WorkflowStage): string {
  if (currentStage.status === 'completed') {
    if (nextStage.status === 'pending') {
      return 'gray.300'
    }
    return 'green.500'
  }
  return 'gray.300'
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

function calculateDuration(start: string, end: string): string {
  const startDate = new Date(start)
  const endDate = new Date(end)
  const durationMs = endDate.getTime() - startDate.getTime()

  const seconds = Math.floor(durationMs / 1000)
  if (seconds < 60) return `${seconds}s`

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes < 60) return `${minutes}m ${remainingSeconds}s`

  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m`
}
</script>
