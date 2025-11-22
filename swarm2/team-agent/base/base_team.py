from swarms.team_agent.roles import Architect, Builder, Critic, Governance, Recorder

class BaseTeam:
    """
    BaseTeam orchestrates a team of specialized agents through a complete workflow.
    
    Workflow:
    Request → Architect → Builder → Critic → Governance → Recorder → Result
    """
    
    def __init__(self):
        """Initialize the team with all 5 agents."""
        self.architect = Architect()
        self.builder = Builder()
        self.critic = Critic()
        self.governance = Governance()
        self.recorder = Recorder()
        self.workflows = []
    
    def run(self, request):
        """
        Execute the complete workflow for a given request.
        
        Args:
            request (str): The initial request/intent for the team
            
        Returns:
            dict: Complete workflow result with signature and audit trail
        """
        if not request or not isinstance(request, str):
            return {
                "status": "failed",
                "reason": "Invalid request",
                "workflow_id": f"workflow_{len(self.workflows) + 1}"
            }
        
        workflow_id = f"workflow_{len(self.workflows) + 1}"
        
        try:
            # Stage 1: Architect designs
            design = self.architect.act(request)
            if design.get("status") != "designed":
                return self._failed_workflow(workflow_id, "Architecture design failed")
            
            # Stage 2: Builder implements
            build = self.builder.act(design)
            if build.get("status") != "built":
                return self._failed_workflow(workflow_id, "Build implementation failed")
            
            # Stage 3: Critic reviews
            review = self.critic.act({"design": design, "build": build})
            if review.get("status") != "reviewed":
                return self._failed_workflow(workflow_id, "Review phase failed")
            
            if not review.get("passed"):
                return self._rejected_workflow(
                    workflow_id,
                    "Review did not pass",
                    review
                )
            
            # Stage 4: Governance enforces
            governance = self.governance.act({"request": request, "review": review})
            if governance.get("status") != "enforced":
                return self._failed_workflow(workflow_id, "Governance enforcement failed")
            
            if not governance.get("allowed"):
                return self._rejected_workflow(
                    workflow_id,
                    "Governance rejected the request",
                    governance
                )
            
            # Stage 5: Recorder logs and signs
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
                "request": request,
                "result": record,
                "stages": {
                    "architect": {"status": "complete", "design_id": design.get("design_id")},
                    "builder": {"status": "complete", "build_id": build.get("build_id")},
                    "critic": {"status": "complete", "review_id": review.get("review_id")},
                    "governance": {"status": "complete", "decision_id": governance.get("decision_id")},
                    "recorder": {"status": "complete", "record_id": record.get("record_id")}
                }
            }
            self.workflows.append(result)
            return result
            
        except Exception as e:
            return self._failed_workflow(workflow_id, f"Workflow error: {str(e)}")
    
    def _failed_workflow(self, workflow_id, reason):
        """Create a failed workflow result."""
        return {
            "status": "failed",
            "workflow_id": workflow_id,
            "reason": reason
        }
    
    def _rejected_workflow(self, workflow_id, reason, details):
        """Create a rejected workflow result."""
        return {
            "status": "rejected",
            "workflow_id": workflow_id,
            "reason": reason,
            "details": details
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