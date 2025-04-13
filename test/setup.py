#!/usr/bin/env python3
"""
Setup script for Docker Compose environment.
This script ensures Docker is installed, .env file exists,
and runs the Docker Compose configuration.
"""

import os
import sys
import subprocess
import shutil
import pathlib
from enum import Enum

class severity(Enum):
    INFO     = 1
    WARN     = 2
    FATAL    = 3

def show_message(severity, message):
    marker = {
        severity.INFO:     "✅",
        severity.WARN:     "⚠️",
        severity.FATAL:    "❌"
    }
    print(f"{marker} {message}")

def check_docker():
    """Check if Docker is installed and available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Docker is installed")
            return True
            
        print("❌ Docker is not installed")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        return False
        
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False


def check_docker_compose():
    """Check if Docker Compose is available."""
    # First try Docker Compose V2 (part of Docker CLI as 'docker compose')
    try:
        result = subprocess.run(
            ["docker", "compose", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose (V2) is available")
            return True
    except Exception:
        pass
            
    # Try standalone Docker Compose (V1)
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Docker Compose (V1) is available")
            return True
    except Exception:
        pass
        
    print("❌ Docker Compose is not available")
    print("Please install Docker Compose: https://docs.docker.com/compose/install/")
    return False


def ensure_env_file():
    """Make sure .env file exists, create from .env.example if not."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    env_file = script_dir / ".env"
    env_example = script_dir / ".env.example"

    if env_file.exists():
        print("✅ .env file exists")
        return True
    
    if not env_example.exists():
        print("❌ Neither .env nor .env.example file found")
        return False
    
    try:
        # Copy .env.example to .env
        shutil.copy2(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  You may want to edit .env file to customize settings")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False


def run_docker_compose():
    """Run the Docker Compose file."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    # Determine which docker compose command to use
    compose_cmd = ["docker", "compose"]
    try:
        result = subprocess.run(
            compose_cmd + ["version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        if result.returncode != 0:
            compose_cmd = ["docker-compose"]
    except Exception:
        compose_cmd = ["docker-compose"]
    
    try:
        # Run docker-compose up with detached mode
        print("🚀 Starting Docker containers...")
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "up", "-d"],
            check=False
        )
        
        if result.returncode == 0:
            print("✅ Docker containers started successfully")
            return True
        else:
            print(f"❌ Failed to start Docker containers (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running Docker Compose: {e}")
        return False


def main():
    """Main function to run the setup process."""
    # Check for Docker first
    if not check_docker():
        sys.exit(1)
    
    # Check for Docker Compose (needed because older Docker versions don't include Compose)
    if not check_docker_compose():
        sys.exit(1)
        
    if not ensure_env_file():
        sys.exit(1)
        
    if not run_docker_compose():
        sys.exit(1)
        
    print("✅ Setup completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
