<template>
  <c-box p="8">
    <c-heading mb="6">Governance & Policy Management</c-heading>

    <c-box
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        Policy Configuration
      </c-text>
      <c-text color="gray.400">
        Configure governance policies and view decision history
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
</script>
