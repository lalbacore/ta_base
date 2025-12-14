<template>
  <div class="episodes-view">
    <div class="header">
      <h1>Episodes</h1>
      <p class="subtitle">AI workflow execution tracking with token consumption metrics</p>
    </div>

    <div v-if="loading" class="loading">Loading episodes...</div>

    <div v-else-if="episodes.length === 0" class="empty-state">
      <p>No episodes yet. Submit a mission to create your first episode!</p>
    </div>

    <div v-else class="episodes-container">
      <!-- Stats Summary -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Episodes</div>
          <div class="stat-value">{{ stats.total_episodes || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Completed</div>
          <div class="stat-value success">{{ stats.completed || 0 }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Tokens</div>
          <div class="stat-value">{{ formatNumber(stats.total_tokens_consumed || 0) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Avg Tokens/Episode</div>
          <div class="stat-value">{{ formatNumber(Math.round(stats.average_tokens_per_episode || 0)) }}</div>
        </div>
      </div>

      <!-- Episodes Table -->
      <div class="episodes-table">
        <div class="table-header">
          <div class="col-id">Episode ID</div>
          <div class="col-mission">Mission</div>
          <div class="col-status">Status</div>
          <div class="col-tokens">Tokens</div>
          <div class="col-score">Score</div>
          <div class="col-date">Created</div>
        </div>

        <router-link
          v-for="episode in episodes"
          :key="episode.episode_id"
          :to="`/episodes/${episode.episode_id}`"
          class="table-row"
        >
          <div class="col-id">
            <code>{{ episode.episode_id }}</code>
          </div>
          <div class="col-mission">
            {{ episode.mission_id }}
          </div>
          <div class="col-status">
            <span class="status-badge" :class="episode.status">
              {{ episode.status }}
            </span>
          </div>
          <div class="col-tokens">
            <div class="token-info">
              <div class="token-total">{{ formatNumber(episode.tokens?.total || 0) }}</div>
              <div class="token-breakdown">
                P: {{ formatNumber(episode.tokens?.prompt || 0) }} |
                C: {{ formatNumber(episode.tokens?.completion || 0) }}
              </div>
            </div>
          </div>
          <div class="col-score">
            <div class="score-badge" :class="getScoreClass(episode.effectiveness_score)">
              {{ episode.effectiveness_score }}%
            </div>
          </div>
          <div class="col-date">
            {{ formatDate(episode.created_at) }}
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const episodes = ref<any[]>([])
const stats = ref<any>({})
const loading = ref(true)

const loadEpisodes = async () => {
  try {
    loading.value = true
    const [episodesRes, statsRes] = await Promise.all([
      axios.get('/api/episodes'),
      axios.get('/api/episodes/stats')
    ])
    episodes.value = episodesRes.data.episodes || []
    stats.value = statsRes.data || {}
  } catch (error) {
    console.error('Failed to load episodes:', error)
  } finally {
    loading.value = false
  }
}

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'fair'
  return 'poor'
}

onMounted(() => {
  loadEpisodes()
})
</script>

<style scoped>
.episodes-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.header h1 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 0.95rem;
}

.loading, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
}

.stat-value.success {
  color: #10b981;
}

/* Episodes Table */
.episodes-table {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr 0.8fr 1.2fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
  font-size: 0.85rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr 0.8fr 1.2fr;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #f0f0f0;
  text-decoration: none;
  color: inherit;
  transition: background-color 0.2s;
}

.table-row:hover {
  background: #f9fafb;
}

.table-row:last-child {
  border-bottom: none;
}

.col-id code {
  font-size: 0.85rem;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  color: #4b5563;
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

.status-badge.created {
  background: #f3f4f6;
  color: #4b5563;
}

.token-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.token-total {
  font-weight: 600;
  color: #333;
}

.token-breakdown {
  font-size: 0.75rem;
  color: #666;
}

.score-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
}

.score-badge.excellent {
  background: #d1fae5;
  color: #065f46;
}

.score-badge.good {
  background: #dbeafe;
  color: #1e40af;
}

.score-badge.fair {
  background: #fef3c7;
  color: #92400e;
}

.score-badge.poor {
  background: #fee2e2;
  color: #991b1b;
}

.col-date {
  font-size: 0.85rem;
  color: #666;
}
</style>
