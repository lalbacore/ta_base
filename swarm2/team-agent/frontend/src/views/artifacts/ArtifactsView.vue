<template>
  <c-box p="8">
    <c-heading mb="6">Artifacts & Manifests</c-heading>

    <c-box
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        No artifacts available
      </c-text>
      <c-text color="gray.400">
        View workflow manifests and verify signatures
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
</script>
