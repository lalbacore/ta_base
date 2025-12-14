<template>
  <div class="episode-detail">
    <div v-if="loading" class="loading">Loading episode...</div>

    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <router-link to="/episodes" class="back-link">← Back to Episodes</router-link>
    </div>

    <div v-else-if="episode" class="episode-container">
      <!-- Header -->
      <div class="header">
        <router-link to="/episodes" class="back-link">← Back to Episodes</router-link>
        <h1>{{ episode.episode_id }}</h1>
        <div class="header-meta">
          <span class="status-badge" :class="episode.status">{{ episode.status }}</span>
          <span class="mission-id">Mission: {{ episode.mission_id }}</span>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-grid">
        <div class="card">
          <div class="card-label">Effectiveness Score</div>
          <div class="card-value score" :class="getScoreClass(episode.effectiveness_score)">
            {{ episode.effectiveness_score }}%
          </div>
        </div>

        <div class="card">
          <div class="card-label">Total Tokens</div>
          <div class="card-value">{{ formatNumber(episode.tokens?.total || 0) }}</div>
          <div class="card-breakdown">
            Prompt: {{ formatNumber(episode.tokens?.prompt || 0) }} |
            Completion: {{ formatNumber(episode.tokens?.completion || 0) }}
          </div>
        </div>

        <div class="card">
          <div class="card-label">Steps Executed</div>
          <div class="card-value">{{ episode.steps_count || 0 }}</div>
        </div>

        <div class="card">
          <div class="card-label">Artifacts</div>
          <div class="card-value">{{ episode.artifacts?.length || 0 }}</div>
        </div>
      </div>

      <!-- Token Breakdown by Agent -->
      <div v-if="Object.keys(episode.tokens?.by_agent || {}).length > 0" class="section">
        <h2>Token Consumption by Agent</h2>
        <div class="agent-tokens">
          <div
            v-for="(tokens, agent) in episode.tokens.by_agent"
            :key="agent"
            class="agent-token-row"
          >
            <div class="agent-name">{{ agent }}</div>
            <div class="agent-tokens-value">{{ formatNumber(tokens) }} tokens</div>
            <div class="agent-percentage">
              {{ ((tokens / episode.tokens.total) * 100).toFixed(1) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Token Estimation (if available) -->
      <div v-if="episode.tokens?.estimated > 0" class="section">
        <h2>Token Estimation</h2>
        <div class="estimation-grid">
          <div class="estimation-item">
            <span class="label">Estimated:</span>
            <span class="value">{{ formatNumber(episode.tokens.estimated) }}</span>
          </div>
          <div class="estimation-item">
            <span class="label">Actual:</span>
            <span class="value">{{ formatNumber(episode.tokens.total) }}</span>
          </div>
          <div class="estimation-item">
            <span class="label">Variance:</span>
            <span class="value" :class="getVarianceClass(episode.tokens.variance)">
              {{ (episode.tokens.variance * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>

      <!-- Artifacts -->
      <div v-if="episode.artifacts && episode.artifacts.length > 0" class="section">
        <h2>Artifacts</h2>
        <div class="artifacts-list">
          <div v-for="(artifact, index) in episode.artifacts" :key="index" class="artifact-item">
            <div class="artifact-icon">📄</div>
            <div class="artifact-info">
              <div class="artifact-name">{{ artifact.name || `Artifact ${index + 1}` }}</div>
              <div class="artifact-meta">{{ artifact.type || 'Unknown type' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Timeline -->
      <div class="section">
        <h2>Timeline</h2>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-label">Created</div>
              <div class="timeline-time">{{ formatDateTime(episode.created_at) }}</div>
            </div>
          </div>
          <div v-if="episode.started_at" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-label">Started</div>
              <div class="timeline-time">{{ formatDateTime(episode.started_at) }}</div>
            </div>
          </div>
          <div v-if="episode.completed_at" class="timeline-item">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-label">Completed</div>
              <div class="timeline-time">{{ formatDateTime(episode.completed_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const episode = ref<any>(null)
const loading = ref(true)
const error = ref('')

const loadEpisode = async () => {
  try {
    loading.value = true
    const response = await axios.get(`/api/episodes/${route.params.id}`)
    episode.value = response.data
  } catch (err: any) {
    error.value = err.response?.data?.error || 'Failed to load episode'
  } finally {
    loading.value = false
  }
}

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleString()
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

const getVarianceClass = (variance: number) => {
  if (Math.abs(variance) < 0.1) return 'good'
  if (Math.abs(variance) < 0.3) return 'fair'
  return 'poor'
}

onMounted(() => {
  loadEpisode()
})
</script>

<style scoped>
.episode-detail {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loading, .error {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.back-link {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  display: inline-block;
}

.back-link:hover {
  text-decoration: underline;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0.5rem 0;
  font-family: monospace;
}

.header-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-top: 0.5rem;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.running {
  background: #dbeafe;
  color: #1e40af;
}

.status-badge.failed {
  background: #fee2e2;
  color: #991b1b;
}

.mission-id {
  color: #666;
  font-size: 0.9rem;
}

/* Overview Grid */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.card-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.card-value {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
}

.card-value.score.excellent {
  color: #10b981;
}

.card-value.score.good {
  color: #3b82f6;
}

.card-value.score.fair {
  color: #f59e0b;
}

.card-value.score.poor {
  color: #ef4444;
}

.card-breakdown {
  font-size: 0.75rem;
  color: #666;
  margin-top: 0.5rem;
}

/* Sections */
.section {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section h2 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
}

/* Agent Tokens */
.agent-tokens {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.agent-token-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  align-items: center;
}

.agent-name {
  font-weight: 500;
  text-transform: capitalize;
}

.agent-tokens-value {
  color: #666;
  font-size: 0.9rem;
}

.agent-percentage {
  color: #3b82f6;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Estimation */
.estimation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.estimation-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
}

.estimation-item .label {
  color: #666;
  font-size: 0.9rem;
}

.estimation-item .value {
  font-weight: 600;
}

.estimation-item .value.good {
  color: #10b981;
}

.estimation-item .value.fair {
  color: #f59e0b;
}

.estimation-item .value.poor {
  color: #ef4444;
}

/* Artifacts */
.artifacts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.artifact-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  align-items: center;
}

.artifact-icon {
  font-size: 1.5rem;
}

.artifact-name {
  font-weight: 500;
}

.artifact-meta {
  font-size: 0.85rem;
  color: #666;
}

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  margin-top: 0.25rem;
  flex-shrink: 0;
}

.timeline-label {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.timeline-time {
  font-size: 0.85rem;
  color: #666;
}
</style>
