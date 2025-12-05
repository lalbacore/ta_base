import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ChakraUIVuePlugin, { chakra } from '@chakra-ui/vue-next'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ChakraUIVuePlugin)

app.mount('#app')
