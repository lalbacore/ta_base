<template>
  
    <div class="create-mission">
      <h1 class="page-title">Create New Mission</h1>
      <p class="page-subtitle">
        Define your mission parameters and requirements
      </p>

      <div class="form-container">
        <MissionCreateForm />
      </div>
    </div>
  
</template>

<script setup lang="ts">
import MissionCreateForm from '@/components/mission/MissionCreateForm.vue'
</script>

<style scoped>
.create-mission {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.page-subtitle {
  color: #64748b;
  margin-bottom: 2rem;
}

.form-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
