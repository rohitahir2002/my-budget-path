import sys
import uvicorn

# Ensure utf-8 encoding on Windows console
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(">> Starting BudgetPath Pro FastAPI Server...")
    print(">> API Documentation: http://localhost:8000/docs")
    print(">> Health Check:     http://localhost:8000/api/health")
    print("=" * 60)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
