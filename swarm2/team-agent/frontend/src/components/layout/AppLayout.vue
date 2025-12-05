<template>
  <c-box h="100vh" display="flex" flex-direction="column">
    <!-- Header -->
    <c-box
      as="header"
      bg="gray.800"
      color="white"
      px="6"
      py="4"
      box-shadow="sm"
      display="flex"
      align-items="center"
      justify-content="space-between"
    >
      <c-heading size="md">Team Agent Platform</c-heading>
      <c-flex align="center" gap="4">
        <c-text font-size="sm">Multi-Agent Orchestration</c-text>
      </c-flex>
    </c-box>

    <!-- Main Container -->
    <c-flex flex="1" overflow="hidden">
      <!-- Sidebar -->
      <c-box
        as="nav"
        w="250px"
        bg="gray.50"
        border-right="1px"
        border-color="gray.200"
        overflow-y="auto"
        p="4"
      >
        <c-v-stack spacing="2" align="stretch">
          <NavLink to="/" icon="📊">Dashboard</NavLink>
          <NavLink to="/missions" icon="🎯">Missions</NavLink>
          <NavLink to="/trust" icon="🔒">Trust Scoring</NavLink>
          <NavLink to="/pki" icon="🔐">PKI Management</NavLink>
          <NavLink to="/registry" icon="📋">Registry</NavLink>
          <NavLink to="/governance" icon="⚖️">Governance</NavLink>
          <NavLink to="/artifacts" icon="📦">Artifacts</NavLink>
          <NavLink to="/logs" icon="📝">Logs</NavLink>
        </c-v-stack>
      </c-box>

      <!-- Content Area -->
      <c-box flex="1" overflow-y="auto" bg="white">
        <router-view />
      </c-box>
    </c-flex>
  </c-box>
</template>

<script setup lang="ts">
import { CBox, CFlex, CHeading, CText, CVStack } from '@chakra-ui/vue-next'
import NavLink from './NavLink.vue'
</script>
