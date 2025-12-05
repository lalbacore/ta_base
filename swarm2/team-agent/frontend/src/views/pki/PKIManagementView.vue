<template>
  <c-box p="8">
    <c-heading mb="6">PKI Management</c-heading>

    <c-box
      p="8"
      text-align="center"
      border="2px dashed"
      border-color="gray.300"
      border-radius="lg"
    >
      <c-text font-size="xl" color="gray.500" mb="2">
        Certificate Management
      </c-text>
      <c-text color="gray.400">
        View and manage certificates for Root, Government, Execution, and Logging domains
      </c-text>
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
</script>
