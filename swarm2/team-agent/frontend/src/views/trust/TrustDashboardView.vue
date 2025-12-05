<template>
  <c-box p="8">
    <c-heading mb="6">Trust Scoring Dashboard</c-heading>

    <c-box
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        No agent trust data available
      </c-text>
      <c-text color="gray.400">
        Trust scores will appear here once agents start executing workflows
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
</script>
