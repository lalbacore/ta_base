<template>
  <c-box p="8">
    <c-flex justify="space-between" align="center" mb="6">
      <c-heading>Missions</c-heading>
      <c-button color-scheme="blue" @click="navigateToCreate">
        Create Mission
      </c-button>
    </c-flex>

    <c-box
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        No missions yet
      </c-text>
      <c-text color="gray.400">
        Click "Create Mission" to start your first workflow
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CFlex, CHeading, CButton, CText } from '@chakra-ui/vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToCreate = () => {
  router.push('/missions/create')
}
</script>
