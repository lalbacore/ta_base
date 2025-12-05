<template>
  <c-box p="8">
    <c-heading mb="6">Dashboard</c-heading>

    <c-simple-grid columns="3" spacing="6" mb="8">
      <StatCard
        title="Active Missions"
        value="0"
        icon="🎯"
        color-scheme="blue"
      />
      <StatCard
        title="Average Trust Score"
        value="0"
        icon="🔒"
        color-scheme="green"
      />
      <StatCard
        title="Certificates Expiring"
        value="0"
        icon="⚠️"
        color-scheme="orange"
      />
    </c-simple-grid>

    <c-text color="gray.500">
      Welcome to Team Agent Platform - Multi-Agent Orchestration System
    </c-text>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CHeading, CSimpleGrid, CText } from '@chakra-ui/vue-next'
import StatCard from '@/components/dashboard/StatCard.vue'
</script>
