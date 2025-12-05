import axios, { AxiosInstance, AxiosError } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5174/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login or refresh token
      console.error('Unauthorized request')
    }

    if (error.response?.status === 429) {
      // Rate limiting - retry after delay
      console.warn('Rate limited - please try again later')
    }

    // Retry logic for network errors
    if (!error.response && error.config) {
      const retryCount = (error.config as any).__retryCount || 0
      if (retryCount < 3) {
        (error.config as any).__retryCount = retryCount + 1
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retryCount)))
        return apiClient.request(error.config)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
