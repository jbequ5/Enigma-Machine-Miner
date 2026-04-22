import argparse
import uvicorn
from fastapi import FastAPI
from operations.orchestrator import EMOperationsOrchestrator

app = FastAPI(title="SAGE EM Operations")
orchestrator = EMOperationsOrchestrator()

@app.post("/start_swarm")
async def start_swarm(max_instances: int = None):
    orchestrator.launch_swarm(max_instances)
    return {"status": "swarm started", "instances": max_instances or "auto"}

@app.get("/status")
async def status():
    return {"active_instances": len(orchestrator.active_instances)}

@app.post("/stop")
async def stop():
    # Graceful shutdown logic here
    return {"status": "stopping"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAGE EM Operations Orchestrator")
    parser.add_argument("--wizard", action="store_true", help="Run 0.9.10 wizard")
    parser.add_argument("--autonomous", action="store_true", help="Run headless")
    parser.add_argument("--config", default="operations_config.json", help="Path to config")
    parser.add_argument("--max-instances", type=int, default=None)
    args = parser.parse_args()

    if args.wizard:
        print("Launching 0.9.10 wizard (implement your existing wizard call here)")
        # subprocess.call(["streamlit", "run", "your_wizard.py"])
    elif args.autonomous:
        orchestrator.launch_swarm(args.max_instances)
        # Start monitoring in background
        import threading
        monitor_thread = threading.Thread(target=orchestrator.monitor_and_recover, daemon=True)
        monitor_thread.start()
        print("EM Operations running autonomously. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("Shutting down...")
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
