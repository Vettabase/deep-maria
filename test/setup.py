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
from messages import Messages, Severity

severity = Severity()
messages = Messages(severity)

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
            messages.show_message("Docker is installed", 'INFO')
            return True
            
        messages.show_message("Docker is not installed", 'FATAL')
        print("Please install Docker: https://docs.docker.com/get-docker/")
        return False
        
    except Exception as e:
        messages.show_message(f"Error checking Docker: {e}", 'FATAL')
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
            messages.show_message("Docker Compose (V2) is available", 'INFO')
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
            messages.show_message("Docker Compose (V1) is available", 'INFO')
            return True, ["docker-compose"]
    except Exception:
        pass
        
    messages.show_message("Docker Compose is not available", 'FATAL')
    print("Please install Docker Compose: https://docs.docker.com/compose/install/")
    return False, None


def clean_environment(compose_cmd, remove_env=False):
    """Clean up Docker environment by removing containers, networks, and volumes."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    try:
        messages.show_message("Cleaning up Docker environment...", 'WARN')
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "down", "--remove-orphans", "-v"],
            check=False
        )
        
        if result.returncode == 0:
            messages.show_message("Docker environment cleaned successfully", 'INFO')
        else:
            messages.show_message(f"Docker environment cleanup exited with code: {result.returncode}", 'WARN')
        
        # Remove .env file if force-clean option is used
        if remove_env:
            env_file = script_dir / ".env"
            if env_file.exists():
                env_file.unlink()
                messages.show_message(".env file removed", 'INFO')
    
    except Exception as e:
        messages.show_message(f"Error during cleanup: {e}", 'WARN')


def ensure_env_file():
    """Make sure .env file exists, create from .env.example if not."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    env_file = script_dir / ".env"
    env_example = script_dir / ".env.example"

    if env_file.exists():
        messages.show_message(".env file exists", 'INFO')
        return True
    
    if not env_example.exists():
        messages.show_message("Neither .env nor .env.example file found", 'FATAL')
        return False
    
    try:
        # Copy .env.example to .env
        shutil.copy2(env_example, env_file)
        messages.show_message("Created .env file from .env.example", 'INFO')
        messages.show_message("You may want to edit .env file to customize settings", 'WARN')
        return True
    except Exception as e:
        messages.show_message(f"Error creating .env file: {e}", 'FATAL')
        return False


def run_docker_compose(compose_cmd):
    """Run the Docker Compose file."""
    # Get the current script directory
    script_dir = pathlib.Path(__file__).parent.absolute()
    
    try:
        # Run docker-compose up with detached mode
        messages.show_message("Starting Docker containers...", 'COOL')
        result = subprocess.run(
            compose_cmd + ["-f", str(script_dir / "docker-compose.yml"), "up", "-d"],
            check=False
        )
        
        if result.returncode == 0:
            messages.show_message("Docker containers started successfully", 'INFO')
            return True
        else:
            messages.show_message(f"Failed to start Docker containers (exit code: {result.returncode})", 'FATAL')
            return False
            
    except Exception as e:
        messages.show_message(f"Error running Docker Compose: {e}", 'FATAL')
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
    
    messages.show_message("Setup completed successfully", 'INFO')
    sys.exit(0)


if __name__ == "__main__":
    main()
