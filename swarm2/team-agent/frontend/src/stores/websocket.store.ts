import { defineStore } from 'pinia'
import { ref } from 'vue'

interface WebSocketConnection {
  socket: WebSocket | null
  connected: boolean
  reconnectAttempts: number
}

type MessageCallback = (data: any) => void

export const useWebSocketStore = defineStore('websocket', () => {
  // State
  const connections = ref<Map<string, WebSocketConnection>>(new Map())
  const subscriptions = ref<Map<string, Set<MessageCallback>>>(new Map())
  const connected = ref(false)

  // Actions
  function connect(channel: string, url: string): void {
    if (connections.value.has(channel)) {
      console.warn(`Already connected to channel: ${channel}`)
      return
    }

    const socket = new WebSocket(url)

    socket.onopen = () => {
      console.log(`WebSocket connected: ${channel}`)
      connections.value.set(channel, {
        socket,
        connected: true,
        reconnectAttempts: 0
      })
      connected.value = true
    }

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      const callbacks = subscriptions.value.get(channel)
      if (callbacks) {
        callbacks.forEach(callback => callback(data))
      }
    }

    socket.onerror = (error) => {
      console.error(`WebSocket error on ${channel}:`, error)
    }

    socket.onclose = () => {
      console.log(`WebSocket closed: ${channel}`)
      const connection = connections.value.get(channel)
      if (connection) {
        connection.connected = false
        connections.value.set(channel, connection)
      }
      reconnect(channel, url)
    }
  }

  function disconnect(channel: string): void {
    const connection = connections.value.get(channel)
    if (connection?.socket) {
      connection.socket.close()
      connections.value.delete(channel)
    }
  }

  function subscribe(channel: string, callback: MessageCallback): void {
    if (!subscriptions.value.has(channel)) {
      subscriptions.value.set(channel, new Set())
    }
    subscriptions.value.get(channel)?.add(callback)
  }

  function unsubscribe(channel: string, callback: MessageCallback): void {
    const callbacks = subscriptions.value.get(channel)
    if (callbacks) {
      callbacks.delete(callback)
      if (callbacks.size === 0) {
        subscriptions.value.delete(channel)
      }
    }
  }

  function reconnect(channel: string, url: string): void {
    const connection = connections.value.get(channel)
    if (connection && connection.reconnectAttempts < 5) {
      setTimeout(() => {
        console.log(`Attempting to reconnect: ${channel}`)
        connection.reconnectAttempts++
        connect(channel, url)
      }, 5000)
    }
  }

  function send(channel: string, message: any): void {
    const connection = connections.value.get(channel)
    if (connection?.socket && connection.connected) {
      connection.socket.send(JSON.stringify(message))
    } else {
      console.error(`Cannot send message - not connected to ${channel}`)
    }
  }

  return {
    connections,
    subscriptions,
    connected,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    reconnect,
    send
  }
})
