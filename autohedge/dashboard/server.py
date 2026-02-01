"""
Dashboard server startup
"""

import uvicorn
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from routes import app


def main():
    host = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    port = int(os.getenv("DASHBOARD_PORT", "8000"))

    print("=" * 60)
    print("🏦 AutoHedge Dashboard")
    print("=" * 60)
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   URL:  http://localhost:{port}")
    print("=" * 60)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
