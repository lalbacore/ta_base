<template>
  <router-link :to="to" custom v-slot="{ navigate, isActive }">
    <Button
      @click="navigate"
      :severity="isActive ? 'primary' : 'secondary'"
      :text="!isActive"
      class="nav-link"
      :class="{ 'active': isActive }"
    >
      <span class="nav-icon">{{ icon }}</span>
      <slot />
    </Button>
  </router-link>
</template>

<script setup lang="ts">
import Button from 'primevue/button'

defineProps<{
  to: string
  icon: string
}>()
</script>

<style scoped>
.nav-link {
  width: 100%;
  justify-content: flex-start;
  margin-bottom: 0.25rem;
}

.nav-icon {
  margin-right: 0.5rem;
}

.nav-link.active {
  background-color: var(--primary-color);
  color: white;
}
</style>
