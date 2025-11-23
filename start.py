#!/usr/bin/env python3
"""
RAG System Startup Script
==========================
This script starts both backend and frontend services automatically.

Usage:
    python start.py

Or make it executable:
    chmod +x start.py
    ./start.py
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}→ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

# Global variables to track processes
backend_process = None
frontend_process = None

def cleanup(signum=None, frame=None):
    """Clean up processes on exit"""
    print_header("Shutting Down Services")
    
    global backend_process, frontend_process
    
    if backend_process:
        print_info("Stopping backend...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            print_success("Backend stopped")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print_warning("Backend force killed")
    
    if frontend_process:
        print_info("Stopping frontend...")
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
            print_success("Frontend stopped")
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            print_warning("Frontend force killed")
    
    # Kill any remaining processes on ports 8000 and 3000
    try:
        subprocess.run(
            "lsof -ti:8000,3000 | xargs kill -9 2>/dev/null",
            shell=True,
            stderr=subprocess.DEVNULL
        )
    except:
        pass
    
    print_success("All services stopped")
    print(f"\n{Colors.OKBLUE}Thank you for using the RAG system!{Colors.ENDC}\n")
    sys.exit(0)

def check_port(port):
    """Check if a port is in use"""
    result = subprocess.run(
        f"lsof -ti:{port}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.returncode == 0

def kill_port(port):
    """Kill process using a specific port"""
    subprocess.run(
        f"lsof -ti:{port} | xargs kill -9 2>/dev/null",
        shell=True,
        stderr=subprocess.DEVNULL
    )

def check_requirements():
    """Check if all requirements are met"""
    print_header("Checking Requirements")
    
    # Check if we're in the right directory
    project_dir = Path(__file__).parent.absolute()
    os.chdir(project_dir)
    print_success(f"Working directory: {project_dir}")
    
    # Check for virtual environment
    venv_path = project_dir / "venv"
    if not venv_path.exists():
        print_error("Virtual environment not found!")
        print_info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment found")
    
    # Check for .env file
    env_file = project_dir / ".env"
    if not env_file.exists():
        print_error(".env file not found!")
        print_info("Please create .env file with your GOOGLE_API_KEY")
        sys.exit(1)
    else:
        print_success(".env file found")
    
    # Check for required files
    required_files = [
        "app/main.py",
        "frontend/index.html",
        "chunks.jsonl",
        "chroma_db"
    ]
    
    for file in required_files:
        file_path = project_dir / file
        if file_path.exists():
            print_success(f"Found: {file}")
        else:
            print_error(f"Missing: {file}")
            sys.exit(1)
    
    return project_dir

def load_env_file(project_dir):
    """Load environment variables from .env file"""
    env_file = project_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip().strip('"').strip("'")
        print_success("Environment variables loaded")
    else:
        print_warning("No .env file found")

def start_backend(project_dir):
    """Start the backend service"""
    print_header("Starting Backend Service")
    
    # Check if port 8000 is in use
    if check_port(8000):
        print_warning("Port 8000 is already in use")
        print_info("Killing existing process...")
        kill_port(8000)
        time.sleep(2)
    
    # Get Python executable from venv
    if sys.platform == "win32":
        python_exe = project_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_exe = project_dir / "venv" / "bin" / "python"
    
    # Start backend
    print_info("Starting FastAPI backend...")
    
    backend_env = os.environ.copy()
    
    global backend_process
    backend_process = subprocess.Popen(
        [str(python_exe), "app/main.py"],
        cwd=project_dir,
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for backend to start
    print_info("Waiting for backend to initialize...")
    max_wait = 30
    for i in range(max_wait):
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:8000/"],
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                print_success("Backend is running on http://localhost:8000")
                return True
        except:
            pass
        
        # Check if process died
        if backend_process.poll() is not None:
            print_error("Backend failed to start!")
            stdout, stderr = backend_process.communicate()
            if stderr:
                print_error(f"Error: {stderr}")
            return False
        
        time.sleep(1)
        if i % 5 == 0:
            print_info(f"Still waiting... ({i}/{max_wait}s)")
    
    print_error("Backend failed to start within timeout")
    return False

def start_frontend(project_dir):
    """Start the frontend service"""
    print_header("Starting Frontend Service")
    
    # Check if port 3000 is in use
    if check_port(3000):
        print_warning("Port 3000 is already in use")
        print_info("Killing existing process...")
        kill_port(3000)
        time.sleep(2)
    
    # Start frontend
    print_info("Starting frontend server...")
    
    frontend_dir = project_dir / "frontend"
    
    global frontend_process
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for frontend to start
    print_info("Waiting for frontend to initialize...")
    time.sleep(3)
    
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:3000/"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print_success("Frontend is running on http://localhost:3000")
            return True
    except:
        pass
    
    print_error("Frontend failed to start!")
    return False

def open_browser():
    """Open browser to the frontend"""
    print_header("Opening Browser")
    
    url = "http://localhost:3000"
    print_info(f"Opening {url}...")
    
    try:
        webbrowser.open(url)
        print_success("Browser opened")
    except:
        print_warning("Could not open browser automatically")
        print_info(f"Please open {url} manually")

def print_status():
    """Print system status"""
    print_header("System Status")
    
    print(f"{Colors.OKGREEN}{Colors.BOLD}All Services Running!{Colors.ENDC}\n")
    
    print(f"{Colors.OKCYAN}Backend API:{Colors.ENDC}")
    print(f"  → http://localhost:8000")
    print(f"  → API Docs: http://localhost:8000/docs\n")
    
    print(f"{Colors.OKCYAN}Frontend UI:{Colors.ENDC}")
    print(f"  → http://localhost:3000\n")
    
    print(f"{Colors.WARNING}To stop the services:{Colors.ENDC}")
    print(f"  → Press Ctrl+C in this terminal\n")
    
    print(f"{Colors.OKBLUE}Try asking:{Colors.ENDC}")
    print(f"  • Who is Brutus?")
    print(f"  • What does the Soothsayer say to Caesar?")
    print(f"  • Why does Brutus kill Caesar?")
    print(f"  • What happens at Caesar's funeral?\n")

def main():
    """Main function"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    print_header("RAG System Startup")
    print(f"{Colors.OKBLUE}Starting Julius Caesar RAG System...{Colors.ENDC}\n")
    
    try:
        # Check requirements
        project_dir = check_requirements()
        
        # Load environment variables
        load_env_file(project_dir)
        
        # Start backend
        if not start_backend(project_dir):
            print_error("Failed to start backend. Exiting...")
            cleanup()
            sys.exit(1)
        
        # Start frontend
        if not start_frontend(project_dir):
            print_error("Failed to start frontend. Exiting...")
            cleanup()
            sys.exit(1)
        
        # Open browser
        open_browser()
        
        # Print status
        print_status()
        
        # Keep running
        print(f"{Colors.OKGREEN}System is running. Press Ctrl+C to stop.{Colors.ENDC}\n")
        
        # Monitor processes
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print_error("Backend process died!")
                cleanup()
                sys.exit(1)
            
            if frontend_process and frontend_process.poll() is not None:
                print_error("Frontend process died!")
                cleanup()
                sys.exit(1)
    
    except KeyboardInterrupt:
        cleanup()
    except Exception as e:
        print_error(f"Error: {e}")
        cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()

