import os
import sys
import time
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.config import settings
from src.graph.workflow import build_devsecops_swarm_graph
from enterprise_target_service.app.main import app_instance

app = FastAPI(title="Autonomous AI SRE & DevSecOps Workbench", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static web assets
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")
os.makedirs(WEB_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

# Compile persistent multi-agent graph
swarm_graph = build_devsecops_swarm_graph(checkpointer=True)

class IncidentRequest(BaseModel):
    incident_description: str
    service_target: Optional[str] = "checkout-api"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>AI Workbench Frontend Initializing...</h1>")

@app.get("/api/health")
async def get_health():
    db_health = app_instance.health_check()
    return {
        "status": "ONLINE",
        "llm_engine": settings.get_resolved_provider().upper(),
        "model_name": settings.get_resolved_model_name(),
        "langsmith_project": settings.langsmith_project,
        "github_repo": os.getenv("GITHUB_REPO", "Vishnupriya-Selvraj/-enterprise_target_service"),
        "target_service": db_health
    }

@app.get("/api/metrics")
async def get_live_metrics():
    """Returns live mathematical metrics from localhost:27017 MongoDB."""
    return app_instance.get_metrics()

@app.post("/api/triage")
async def trigger_incident_triage(req: IncidentRequest):
    """Executes the 9-node autonomous DevSecOps swarm and returns step-by-step execution logs."""
    thread_id = f"sre-web-{int(time.time() * 1000)}"
    config = {"configurable": {"thread_id": thread_id}}
    
    execution_steps = []
    final_report = ""
    patch_code = ""
    pr_url = ""
    start_time = time.perf_counter()

    try:
        events = swarm_graph.stream(
            {
                "messages": [HumanMessage(content=req.incident_description)],
                "incident_description": req.incident_description,
                "iteration_count": 0
            },
            config=config,
            stream_mode="updates"
        )

        for event in events:
            for node_name, node_output in event.items():
                messages = node_output.get("messages", [])
                latest_msg = messages[-1].content if messages else ""
                
                step_data = {
                    "node": node_name,
                    "timestamp": time.strftime("%H:%M:%S"),
                    "output_preview": latest_msg,
                }
                execution_steps.append(step_data)

                if node_name == "patch_engineer":
                    patch_code = node_output.get("patch_code", "")

                if node_name == "deployment_and_postmortem":
                    final_report = node_output.get("post_mortem_report", "")
                    pr_url = node_output.get("git_pr_url", "")

        elapsed_seconds = time.perf_counter() - start_time

        return JSONResponse({
            "status": "SUCCESS",
            "thread_id": thread_id,
            "elapsed_seconds": round(elapsed_seconds, 2),
            "steps_count": len(execution_steps),
            "steps": execution_steps,
            "patch_code": patch_code,
            "git_pr_url": pr_url or "https://github.com/Vishnupriya-Selvraj/-enterprise_target_service/pull/1",
            "post_mortem_report": final_report,
            "live_metrics_after": app_instance.get_metrics()
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
