<template>
  <c-box
    p="6"
    bg="white"
    border-radius="lg"
    box-shadow="sm"
    border="1px"
    border-color="gray.200"
  >
    <c-flex align="center" justify="space-between" mb="4">
      <c-text font-size="2xl">{{ icon }}</c-text>
      <c-badge :color-scheme="colorScheme">{{ title }}</c-badge>
    </c-flex>
    <c-text font-size="3xl" font-weight="bold" :color="`${colorScheme}.600`">
      {{ value }}
    </c-text>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CFlex, CText, CBadge } from '@chakra-ui/vue-next'

defineProps<{
  title: string
  value: string | number
  icon: string
  colorScheme: string
}>()
</script>
