from swarms.team_agent.roles import Architect, Builder, Critic, Governance, Recorder

class BaseTeam:
    """
    BaseTeam orchestrates a team of specialized agents through a complete workflow.
    
    Workflow:
    Request → Architect → Builder → Critic → Governance → Recorder → Result
    """
    
    def __init__(self, workflow_id: str | None = None):
        """Initialize the team with all 5 agents."""
        self.architect = Architect()
        self.builder = Builder()
        self.critic = Critic()
        # If provided, propagate; otherwise Governance will default
        if workflow_id:
            self.governance = Governance(workflow_id=workflow_id)
        else:
            self.governance = Governance()
        self.recorder = Recorder()
        self.workflows = []
    
    def run(self, request):
        """Execute the team workflow."""
        workflow_id = f"workflow_{len(self.workflows) + 1}"
        
        try:
            # Store original request for the result
            original_request = request
            
            # Normalize request to dict
            if isinstance(request, str):
                request = {"intent": request}
            
            # Stage 1: Validate request
            if not request or not isinstance(request, dict):
                return self._failed_workflow(workflow_id, "Invalid request")
            
            intent = request.get("intent", "")
            if not intent or not isinstance(intent, str) or not intent.strip():
                return self._failed_workflow(workflow_id, "Invalid request")
            
            # Stage 2: Architect designs
            design = self.architect.act(intent)
            if design.get("status") != "designed":
                return self._failed_workflow(workflow_id, "Design phase failed")
            
            # Stage 3: Builder builds
            build = self.builder.act(design)
            if build.get("status") != "built":
                return self._failed_workflow(workflow_id, "Build phase failed")
            
            # Stage 4: Critic reviews
            review = self.critic.act({"design": design, "build": build})
            if review.get("status") != "reviewed":
                return self._failed_workflow(workflow_id, "Review phase failed")
            
            # Stage 5: Governance enforces
            governance = self.governance.act({"request": request, "review": review})
            if governance.get("status") != "enforced":
                return self._failed_workflow(workflow_id, "Governance enforcement failed")
            
            if not governance.get("allowed"):
                return self._rejected_workflow(workflow_id, "Governance rejected the request", governance)
            
            # Stage 6: Recorder logs and signs
            record_package = {
                "request": request,
                "design": design,
                "build": build,
                "review": review,
                "governance": governance
            }
            record = self.recorder.act(record_package)
            
            if record.get("status") != "recorded":
                return self._failed_workflow(workflow_id, "Recording phase failed")
            
            # Success
            result = {
                "status": "success",
                "workflow_id": workflow_id,
                "request": original_request,
                "result": record,
                "team_composite_score": record.get("composite_score", {}).get("overall", 0),
                "stages": {
                    "request": {"status": "complete", "data": request},
                    "architect": {"status": "complete", "data": design},
                    "builder": {"status": "complete", "data": build},
                    "critic": {"status": "complete", "data": review},
                    "governance": {"status": "complete", "data": governance},
                    "recorder": {"status": "complete", "data": record},
                },
            }
            self.workflows.append(result)
            return result
        except Exception as e:
            failed = self._failed_workflow(workflow_id, f"Workflow error: {str(e)}")
            self.workflows.append(failed)
            return failed

    def _failed_workflow(self, workflow_id, reason):
        """Create a failed workflow result."""
        return {
            "status": "failed",
            "workflow_id": workflow_id,
            "reason": reason,
            "result": None,
            "team_composite_score": 0.0,
        }

    def _rejected_workflow(self, workflow_id, reason, details):
        """Create a rejected workflow result."""
        return {
            "status": "rejected",
            "workflow_id": workflow_id,
            "reason": reason,
            "details": details,
            "result": None,
            "team_composite_score": details.get("composite_score", 0.0),
        }
    
    def get_agent_stats(self):
        """Get statistics on all agents."""
        return {
            "architect": {
                "designs_created": len(self.architect.designs),
                "capabilities": self.architect.capabilities
            },
            "builder": {
                "builds_created": len(self.builder.builds),
                "capabilities": self.builder.capabilities
            },
            "critic": {
                "reviews_conducted": len(self.critic.reviews),
                "capabilities": self.critic.capabilities
            },
            "governance": {
                "decisions_made": len(self.governance.decisions),
                "capabilities": self.governance.capabilities
            },
            "recorder": {
                "records_created": len(self.recorder.records),
                "capabilities": self.recorder.capabilities
            }
        }
    
    def get_workflow_history(self):
        """Get history of all workflows."""
        return {
            "total_workflows": len(self.workflows),
            "successful": len([w for w in self.workflows if w["status"] == "success"]),
            "rejected": len([w for w in self.workflows if w["status"] == "rejected"]),
            "failed": len([w for w in self.workflows if w["status"] == "failed"]),
            "workflows": self.workflows
        }