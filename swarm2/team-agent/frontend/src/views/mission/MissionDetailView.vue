<template>
  <c-box p="8">
    <c-heading mb="6">Mission Details</c-heading>

    <c-text color="gray.600">
      Mission ID: {{ route.params.id }}
    </c-text>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CText } from '@chakra-ui/vue-next'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>
