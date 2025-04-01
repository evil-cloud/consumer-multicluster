from   fastapi import FastAPI
import logging
import json
from   datetime import datetime, timezone
from   prometheus_fastapi_instrumentator import Instrumentator
import os
import googlecloudprofiler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("service-b")

CLUSTER_NAME = os.environ.get("CLUSTER_NAME", "unknown-cluster")
SERVICE_VERSION = os.environ.get("SERVICE_VERSION", "v1")
POD_NAME = os.environ.get("POD_NAME", "unknown-pod")

def log_json(level, component, message, status_code=None):
    log_entry = {
        "level": level,
        "time": datetime.now(timezone.utc).isoformat(),
        "component": component,
        "message": message
    }
    if status_code is not None:
        log_entry["status_code"] = status_code
    print(json.dumps(log_entry))

app = FastAPI()
Instrumentator().instrument(app).expose(app)

try:
    googlecloudprofiler.start(
        service="servicio-b",
        service_version="v1",
        verbose=2  
    )
    
except (ValueError, NotImplementedError) as exc:
    log_json("warning", "profiler", f"Error initializing Cloud Profiler: {exc}")

@app.get("/")
async def hello():
    log_json("info", "service-b", f"Respondiendo desde Servicio B en el cluster '{CLUSTER_NAME}' (pod: {POD_NAME}).", 200)
    return {"message": f"¡Hola desde el Servicio B en {CLUSTER_NAME}, ver: {SERVICE_VERSION}!"}

@app.get("/health")
async def health_check():
    log_json("info", "service-b", f"Health check llamado desde el cluster '{CLUSTER_NAME}' (pod: {POD_NAME}).", 200)
    return {"status": "ok", "service": "B", "cluster": CLUSTER_NAME, "version": SERVICE_VERSION, "pod": POD_NAME}