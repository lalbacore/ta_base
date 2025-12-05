<template>
  
    <div class="pki-management">
      <h1 class="page-title">PKI Management</h1>

      <Message severity="info" :closable="false">
        <div class="info-content">
          <h3>Public Key Infrastructure</h3>
          <p>Manage certificates for Root CA, Government, Execution, and Logging domains. Monitor certificate lifecycles, handle renewals, and track revocations.</p>
        </div>
      </Message>

      <div class="placeholder-content">
        <i class="pi pi-lock placeholder-icon"></i>
        <h3>Certificate Management</h3>
        <p>View and manage certificates for Root, Government, Execution, and Logging domains</p>
      </div>
    </div>
  
</template>

<script setup lang="ts">
import Message from 'primevue/message'
</script>

<style scoped>
.pki-management {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: #1e293b;
}

.info-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.info-content p {
  margin: 0;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  margin-top: 2rem;
}

.placeholder-icon {
  font-size: 4rem;
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.placeholder-content h3 {
  font-size: 1.25rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.placeholder-content p {
  color: #94a3b8;
}
</style>
