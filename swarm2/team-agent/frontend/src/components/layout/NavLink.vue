<template>
  <router-link :to="to" custom v-slot="{ navigate, isActive }">
    <c-button
      @click="navigate"
      w="full"
      justify-content="flex-start"
      :variant="isActive ? 'solid' : 'ghost'"
      :color-scheme="isActive ? 'blue' : 'gray'"
      left-icon="icon"
    >
      <c-text mr="2">{{ icon }}</c-text>
      <slot />
    </c-button>
  </router-link>
</template>

<script setup lang="ts">
import { CButton, CText } from '@chakra-ui/vue-next'

defineProps<{
  to: string
  icon: string
}>()
</script>
