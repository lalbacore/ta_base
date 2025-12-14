import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { title: 'Dashboard' }
  },
  {
    path: '/missions',
    name: 'Missions',
    component: () => import('@/views/mission/MissionListView.vue'),
    meta: { title: 'Missions' }
  },
  {
    path: '/missions/create',
    name: 'MissionCreate',
    component: () => import('@/views/mission/MissionCreateView.vue'),
    meta: { title: 'Create Mission' }
  },
  {
    path: '/missions/:id',
    name: 'MissionDetail',
    component: () => import('@/views/mission/MissionDetailView.vue'),
    meta: { title: 'Mission Details' }
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/views/agents/AgentsView.vue'),
    meta: { title: 'Agent Manager' }
  },
  {
    path: '/pki',
    name: 'PKI',
    component: () => import('@/views/pki/PKIManagementView.vue'),
    meta: { title: 'PKI Management' }
  },
  {
    path: '/registry',
    name: 'Registry',
    component: () => import('@/views/registry/RegistryView.vue'),
    meta: { title: 'Capability Registry' }
  },
  {
    path: '/governance',
    name: 'Governance',
    component: () => import('@/views/governance/GovernanceView.vue'),
    meta: { title: 'Governance & Policy' }
  },
  {
    path: '/artifacts',
    name: 'Artifacts',
    component: () => import('@/views/artifacts/ArtifactsView.vue'),
    meta: { title: 'Artifacts & Manifests' }
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/logs/LogsView.vue'),
    meta: { title: 'Logs' }
  },
  {
    path: '/episodes',
    name: 'Episodes',
    component: () => import('@/views/episodes/EpisodeListView.vue'),
    meta: { title: 'Episodes' }
  },
  {
    path: '/episodes/:id',
    name: 'EpisodeDetail',
    component: () => import('@/views/episodes/EpisodeDetailView.vue'),
    meta: { title: 'Episode Details' }
  },
  {
    path: '/providers',
    name: 'Providers',
    component: () => import('@/views/providers/ProvidersView.vue'),
    meta: { title: 'Multi-Provider Infrastructure' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title} - Team Agent` || 'Team Agent'
  next()
})

export default router
