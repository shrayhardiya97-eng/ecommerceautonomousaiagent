import sys
import uvicorn
from app.config import settings

def main():
    if "--cli" in sys.argv:
        import asyncio
        from cli import run_cli
        asyncio.run(run_cli())
    else:
        print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        print("🌐 Open http://localhost:8000 in your browser to interact with the Autonomous Shopping Agent")
        print("💡 Pass '--cli' flag to run the interactive Rich terminal interface")
        uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
