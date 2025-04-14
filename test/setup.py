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
    COOL     = 1
    INFO     = 2
    WARN     = 3
    FATAL    = 4

def show_message(severity, message):
    marker = {
        severity.COOL:     "🚀",
        severity.INFO:     "✅",
        severity.WARN:     "⚠️",
        severity.FATAL:    "❌"
    }
    print(f"{marker[severity]} {message}")

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
            show_message(severity.INFO, "Docker is installed")
            return True
            
        show_message(severity.FATAL, "Docker is not installed")
        show_message(severity.INFO, "Please install Docker: https://docs.docker.com/get-docker/")
        return False
        
    except Exception as e:
        show_message(severity.FATAL, f"Error checking Docker: {e}")
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
            show_message(severity.INFO, "Docker Compose (V2) is available")
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
            show_message(severity.INFO, "Docker Compose (V1) is available")
            return True
    except Exception:
        pass
        
    show_message(severity.FATAL, "Docker Compose is not available")
    show_message(severity.INFO, "Please install Docker Compose: https://docs.docker.com/compose/install/")
    return False


def ensure_env_file():
    """Make sure .env file exists, create from .env.example if not."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    env_file = script_dir / ".env"
    env_example = script_dir / ".env.example"

    if env_file.exists():
        show_message(severity.INFO, ".env file exists")
        return True
    
    if not env_example.exists():
        show_message(severity.FATAL, "Neither .env nor .env.example file found")
        return False
    
    try:
        # Copy .env.example to .env
        shutil.copy2(env_example, env_file)
        show_message(severity.INFO, "Created .env file from .env.example")
        show_message(severity.WARN, "You may want to edit .env file to customize settings")
        return True
    except Exception as e:
        show_message(severity.FATAL, f"Error creating .env file: {e}")
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
        show_message(severity.COOL, "Starting Docker containers...")
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "up", "-d"],
            check=False
        )
        
        if result.returncode == 0:
            show_message(severity.INFO, "Docker containers started successfully")
            return True
        else:
            show_message(severity.FATAL, f"Failed to start Docker containers (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        show_message(severity.FATAL, f"Error running Docker Compose: {e}")
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
        
    show_message(severity.INFO, "Setup completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
