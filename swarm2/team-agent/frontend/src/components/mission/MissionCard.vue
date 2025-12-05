<template>
  <c-box
    p="6"
    bg="white"
    border="1px"
    border-color="gray.200"
    border-radius="lg"
    box-shadow="sm"
    cursor="pointer"
    transition="all 0.2s"
    _hover="{ boxShadow: 'md', borderColor: 'blue.300' }"
    @click="handleClick"
  >
    <c-flex justify="space-between" align="start" mb="3">
      <c-box flex="1">
        <c-h-stack spacing="3" mb="2">
          <c-heading size="md">{{ mission.mission_id }}</c-heading>
          <c-badge :color-scheme="statusColorScheme">
            {{ workflow?.status || 'pending' }}
          </c-badge>
        </c-h-stack>
        <c-text color="gray.600" font-size="sm">
          Created {{ formatDate(workflow?.created_at) }}
        </c-text>
      </c-box>

      <c-icon-button
        aria-label="More options"
        icon="ellipsis-v"
        variant="ghost"
        size="sm"
        @click.stop="handleOptionsClick"
      />
    </c-flex>

    <c-text mb="4" no-of-lines="2">
      {{ mission.description }}
    </c-text>

    <c-v-stack spacing="3" align="stretch" mb="4">
      <!-- Progress Bar -->
      <c-box v-if="workflow">
        <c-flex justify="space-between" mb="1">
          <c-text font-size="sm" font-weight="medium">
            Progress
          </c-text>
          <c-text font-size="sm" color="gray.600">
            {{ workflow.progress }}%
          </c-text>
        </c-flex>
        <c-progress
          :value="workflow.progress"
          :color-scheme="progressColorScheme"
          size="sm"
          border-radius="full"
        />
      </c-box>

      <!-- Current Stage -->
      <c-box v-if="workflow?.current_stage">
        <c-text font-size="sm" color="gray.500" mb="1">
          Current Stage
        </c-text>
        <c-badge variant="outline" color-scheme="blue">
          {{ formatStageName(workflow.current_stage) }}
        </c-badge>
      </c-box>
    </c-v-stack>

    <!-- Mission Stats -->
    <c-simple-grid columns="3" spacing="3">
      <c-box>
        <c-text font-size="xs" color="gray.500" mb="1">
          Capabilities
        </c-text>
        <c-text font-weight="bold" font-size="sm">
          {{ mission.required_capabilities.length }}
        </c-text>
      </c-box>

      <c-box>
        <c-text font-size="xs" color="gray.500" mb="1">
          Min Trust
        </c-text>
        <c-text font-weight="bold" font-size="sm">
          {{ mission.min_trust_score }}
        </c-text>
      </c-box>

      <c-box>
        <c-text font-size="xs" color="gray.500" mb="1">
          Breakpoints
        </c-text>
        <c-text font-weight="bold" font-size="sm">
          {{ mission.breakpoints.length }}
        </c-text>
      </c-box>
    </c-simple-grid>
  </c-box>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  CBox,
  CFlex,
  CHStack,
  CVStack,
  CHeading,
  CText,
  CBadge,
  CIconButton,
  CProgress,
  CSimpleGrid
} from '@chakra-ui/vue-next'
import type { MissionSpec, WorkflowStatus } from '@/types/mission.types'

const props = defineProps<{
  mission: MissionSpec
  workflow?: WorkflowStatus
}>()

const router = useRouter()

const statusColorScheme = computed(() => {
  switch (props.workflow?.status) {
    case 'running':
      return 'blue'
    case 'completed':
      return 'green'
    case 'failed':
      return 'red'
    case 'paused':
      return 'orange'
    default:
      return 'gray'
  }
})

const progressColorScheme = computed(() => {
  const progress = props.workflow?.progress || 0
  if (progress === 100) return 'green'
  if (progress >= 50) return 'blue'
  return 'gray'
})

function formatDate(dateString?: string): string {
  if (!dateString) return 'Unknown'

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`

  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}d ago`

  return date.toLocaleDateString()
}

function formatStageName(stage: string): string {
  return stage
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function handleClick() {
  router.push(`/missions/${props.mission.mission_id}`)
}

function handleOptionsClick() {
  // TODO: Show options menu
  console.log('Options clicked for', props.mission.mission_id)
}
</script>
