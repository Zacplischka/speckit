#!/usr/bin/env python3
"""
Launch script for the Task Manager Streamlit application.
Provides an easy way to start the application with proper configuration.
"""

import sys
import subprocess
import os
from pathlib import Path


def main():
    """Launch the Streamlit Task Manager application."""

    # Get the project root directory
    project_root = Path(__file__).parent

    # Change to project root directory
    os.chdir(project_root)

    # Add project root to Python path for imports
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root) + ':' + env.get('PYTHONPATH', '')

    # Path to the Streamlit application
    app_path = "src/ui/streamlit_app.py"

    # Check if the app file exists
    if not Path(app_path).exists():
        print(f"Error: Application file {app_path} not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)

    # Streamlit configuration
    streamlit_args = [
        "streamlit", "run", app_path,
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.serverAddress", "localhost",
        "--browser.gatherUsageStats", "false",
        "--logger.level", "warning"
    ]

    print("🚀 Starting Task Manager...")
    print("📍 Application will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print("-" * 50)

    try:
        # Launch Streamlit with updated environment
        subprocess.run(streamlit_args, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except FileNotFoundError:
        print("Error: Streamlit not installed!")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()