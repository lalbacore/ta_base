"""
Parallel Agent Executor - Run multiple agents/capabilities concurrently.
"""
import asyncio
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class ParallelExecutor:
    """Execute multiple agents or capabilities in parallel."""
    
    def __init__(self, max_workers: int = 4):
        """Initialize with thread pool size."""
        self.max_workers = max_workers
    
    def execute_parallel(
        self,
        tasks: List[Dict[str, Any]],
        executor_func: Callable
    ) -> List[Dict[str, Any]]:
        """
        Execute tasks in parallel using threads.
        
        Args:
            tasks: List of task dicts with 'name' and 'context' keys
            executor_func: Function to execute each task (e.g., agent.run)
        
        Returns:
            List of results in same order as tasks
        """
        results = [None] * len(tasks)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(executor_func, task['context']): idx
                for idx, task in enumerate(tasks)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results[idx] = {
                        'task': tasks[idx]['name'],
                        'result': future.result(),
                        'status': 'success',
                        'error': None
                    }
                except Exception as e:
                    results[idx] = {
                        'task': tasks[idx]['name'],
                        'result': None,
                        'status': 'failed',
                        'error': str(e)
                    }
        
        return results
    
    async def execute_async(
        self,
        tasks: List[Dict[str, Any]],
        async_executor_func: Callable
    ) -> List[Dict[str, Any]]:
        """
        Execute tasks asynchronously (for async agent functions).
        
        Args:
            tasks: List of task dicts
            async_executor_func: Async function to execute each task
        
        Returns:
            List of results
        """
        async def run_task(idx: int, task: Dict[str, Any]):
            try:
                result = await async_executor_func(task['context'])
                return {
                    'task': task['name'],
                    'result': result,
                    'status': 'success',
                    'error': None
                }
            except Exception as e:
                return {
                    'task': task['name'],
                    'result': None,
                    'status': 'failed',
                    'error': str(e)
                }
        
        results = await asyncio.gather(
            *[run_task(idx, task) for idx, task in enumerate(tasks)]
        )
        
        return list(results)


class ParallelCapabilityExecutor(ParallelExecutor):
    """Specialized executor for running multiple capabilities."""
    
    def execute_capabilities(
        self,
        mission: str,
        capabilities: List[Any],
        architecture: str = ""
    ) -> Dict[str, Any]:
        """
        Execute multiple capabilities for same mission in parallel.
        
        Args:
            mission: The mission string
            capabilities: List of capability instances
            architecture: Optional architecture context
        
        Returns:
            Dict with results from all capabilities
        """
        tasks = [
            {
                'name': cap.metadata.get('name', f'cap_{idx}'),
                'context': {
                    'mission': mission,
                    'architecture': architecture,
                    'input': mission
                }
            }
            for idx, cap in enumerate(capabilities)
        ]
        
        def execute_cap(context):
            # Find matching capability
            cap = next(
                c for c in capabilities
                if c.metadata.get('name') == context.get('_cap_name')
            )
            return cap.execute(context)
        
        # Add capability name to context
        for task, cap in zip(tasks, capabilities):
            task['context']['_cap_name'] = cap.metadata.get('name')
        
        results = self.execute_parallel(tasks, execute_cap)
        
        # Aggregate results
        return {
            'mission': mission,
            'capabilities_executed': len(capabilities),
            'results': results,
            'successful': sum(1 for r in results if r['status'] == 'success'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'artifacts': self._merge_artifacts(results)
        }
    
    def _merge_artifacts(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge artifacts from multiple capability results."""
        merged = {}
        
        for result in results:
            if result['status'] == 'success' and result['result']:
                artifacts = result['result'].get('artifacts', [])
                
                # Handle both list and dict formats
                if isinstance(artifacts, list):
                    for artifact in artifacts:
                        name = artifact.get('name', result['task'])
                        merged[f"{result['task']}_{name}"] = artifact
                elif isinstance(artifacts, dict):
                    for name, content in artifacts.items():
                        merged[f"{result['task']}_{name}"] = content
        
        return merged