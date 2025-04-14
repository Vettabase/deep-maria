#!/usr/bin/env python3
"""
Setup script for Docker Compose environment.
This script ensures Docker is installed, .env file exists,
and runs the Docker Compose configuration.

Usage:
  setup.py [options]

Options:
  --clean         Remove all containers, networks and volumes without removing .env
  --force-clean   Remove all containers, networks, volumes and delete .env file
"""

import os
import sys
import subprocess
import shutil
import pathlib
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../python_libs')))
from messages import Severity, show_message


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
            show_message(Severity.INFO, "Docker is installed")
            return True
            
        show_message(Severity.FATAL, "Docker is not installed")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        return False
        
    except Exception as e:
        show_message(Severity.FATAL, f"Error checking Docker: {e}")
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
            show_message(Severity.INFO, "Docker Compose (V2) is available")
            return True, ["docker", "compose"]
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
            show_message(Severity.INFO, "Docker Compose (V1) is available")
            return True, ["docker-compose"]
    except Exception:
        pass
        
    show_message(Severity.FATAL, "Docker Compose is not available")
    print("Please install Docker Compose: https://docs.docker.com/compose/install/")
    return False, None


def clean_environment(compose_cmd, remove_env=False):
    """Clean up Docker environment by removing containers, networks, and volumes."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    try:
        show_message(Severity.WARN, "Cleaning up Docker environment...")
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "down", "--remove-orphans", "-v"],
            check=False
        )
        
        if result.returncode == 0:
            show_message(Severity.INFO, "Docker environment cleaned successfully")
        else:
            show_message(Severity.WARN, f"Docker environment cleanup exited with code: {result.returncode}")
        
        # Remove .env file if force-clean option is used
        if remove_env:
            env_file = script_dir / ".env"
            if env_file.exists():
                env_file.unlink()
                show_message(Severity.INFO, ".env file removed")
    
    except Exception as e:
        show_message(Severity.WARN, f"Error during cleanup: {e}")


def ensure_env_file():
    """Make sure .env file exists, create from .env.example if not."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    env_file = script_dir / ".env"
    env_example = script_dir / ".env.example"

    if env_file.exists():
        show_message(Severity.INFO, ".env file exists")
        return True
    
    if not env_example.exists():
        show_message(Severity.FATAL, "Neither .env nor .env.example file found")
        return False
    
    try:
        # Copy .env.example to .env
        shutil.copy2(env_example, env_file)
        show_message(Severity.INFO, "Created .env file from .env.example")
        show_message(Severity.WARN, "You may want to edit .env file to customize settings")
        return True
    except Exception as e:
        show_message(Severity.FATAL, f"Error creating .env file: {e}")
        return False


def run_docker_compose(compose_cmd):
    """Run the Docker Compose file."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    try:
        # Run docker-compose up with detached mode
        show_message(Severity.COOL, "Starting Docker containers...")
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "up", "-d"],
            check=False
        )
        
        if result.returncode == 0:
            show_message(Severity.INFO, "Docker containers started successfully")
            return True
        else:
            show_message(Severity.FATAL, f"Failed to start Docker containers (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        show_message(Severity.FATAL, f"Error running Docker Compose: {e}")
        return False


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Setup Docker environment for deep-maria")
    parser.add_argument("--clean", action="store_true", 
                        help="Remove all containers, networks and volumes without removing .env")
    parser.add_argument("--force-clean", action="store_true", 
                        help="Remove all containers, networks, volumes and delete .env file")
    return parser.parse_args()


def main():
    """Main function to run the setup process."""
    args = parse_arguments()
    
    # Check for Docker first
    if not check_docker():
        sys.exit(1)
    
    # Check for Docker Compose (needed because older Docker versions don't include Compose)
    compose_available, compose_cmd = check_docker_compose()
    if not compose_available:
        sys.exit(1)
    
    # Handle clean and force-clean options
    if args.clean or args.force_clean:
        clean_environment(compose_cmd, remove_env=args.force_clean)
    
    # For normal setup or after force-clean, ensure .env exists
    if not ensure_env_file():
        sys.exit(1)
    
    # Start the Docker environment
    if not run_docker_compose(compose_cmd):
        sys.exit(1)
    
    show_message(Severity.INFO, "Setup completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
