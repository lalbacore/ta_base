<template>
  <c-box p="8">
    <c-heading mb="2">Create New Mission</c-heading>
    <c-text color="gray.600" mb="6">
      Define your mission parameters and requirements
    </c-text>

    <c-box max-w="4xl">
      <MissionCreateForm />
    </c-box>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
import MissionCreateForm from '@/components/mission/MissionCreateForm.vue'
</script>
