import { onMounted, onUnmounted } from 'vue'
import { useWebSocketStore } from '@/stores/websocket.store'
import { useMissionStore } from '@/stores/mission.store'

export function useWorkflowWebSocket(workflowId: string) {
  const wsStore = useWebSocketStore()
  const missionStore = useMissionStore()

  const wsUrl = `${import.meta.env.VITE_WS_BASE_URL}/workflow/${workflowId}`

  function handleWorkflowUpdate(data: any) {
    console.log('Workflow update received:', data)

    const { type, workflow_id, data: updateData } = data

    switch (type) {
      case 'stage_started':
        // Update workflow status
        const workflow = missionStore.workflows.get(workflow_id)
        if (workflow) {
          workflow.current_stage = updateData.stage_name
          workflow.updated_at = updateData.timestamp
        }
        break

      case 'stage_completed':
        // Mark stage as completed and update progress
        const wf = missionStore.workflows.get(workflow_id)
        if (wf) {
          const stage = wf.stages.find(s => s.stage_name === updateData.stage_name)
          if (stage) {
            stage.status = 'completed'
            stage.completed_at = updateData.timestamp
            stage.output = updateData.output
          }
          wf.progress = updateData.progress
          wf.updated_at = updateData.timestamp
        }
        break

      case 'stage_failed':
        // Mark stage as failed
        const wfFailed = missionStore.workflows.get(workflow_id)
        if (wfFailed) {
          const stage = wfFailed.stages.find(s => s.stage_name === updateData.stage_name)
          if (stage) {
            stage.status = 'failed'
            stage.completed_at = updateData.timestamp
          }
          wfFailed.status = 'failed'
          wfFailed.updated_at = updateData.timestamp
        }
        break

      case 'breakpoint_requested':
        // Add breakpoint to store
        missionStore.breakpoints.set(updateData.breakpoint_id, {
          breakpoint_id: updateData.breakpoint_id,
          workflow_id: workflow_id,
          breakpoint_type: updateData.breakpoint_type,
          options: updateData.options,
          status: 'pending',
          created_at: updateData.timestamp
        })
        break

      case 'workflow_completed':
        // Mark workflow as completed
        const wfComplete = missionStore.workflows.get(workflow_id)
        if (wfComplete) {
          wfComplete.status = 'completed'
          wfComplete.progress = 100
          wfComplete.updated_at = updateData.timestamp
        }
        break
    }
  }

  onMounted(() => {
    wsStore.connect(`workflow_${workflowId}`, wsUrl)
    wsStore.subscribe(`workflow_${workflowId}`, handleWorkflowUpdate)
  })

  onUnmounted(() => {
    wsStore.unsubscribe(`workflow_${workflowId}`, handleWorkflowUpdate)
    wsStore.disconnect(`workflow_${workflowId}`)
  })

  return {
    isConnected: wsStore.connected
  }
}
