"""Script to start the system locally."""
import subprocess
import os
import time
import sys
from pathlib import Path

def start_system():
    """Start both backend and frontend servers."""
    
    print("\n" + "="*60)
    print("Graph-Based Query System - Local Startup")
    print("="*60 + "\n")
    
    # Find project root
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent
    frontend_dir = project_root / 'frontend'
    
    print(f"📁 Project structure:")
    print(f"  Backend: {backend_dir}")
    print(f"  Frontend: {frontend_dir}")
    
    # Check Python environment
    print(f"\n🐍 Python version: {sys.version.split()[0]}")
    
    # Check dependencies
    print(f"\n📦 Checking dependencies...")
    try:
        import flask
        print(f"  ✓ Flask {flask.__version__}")
    except ImportError:
        print(f"  ✗ Flask not installed")
        return False
    
    try:
        import networkx
        print(f"  ✓ NetworkX {networkx.__version__}")
    except ImportError:
        print(f"  ✗ NetworkX not installed")
        return False
    
    # Check .env file
    env_file = backend_dir / '.env'
    if not env_file.exists():
        print(f"\n⚠️  .env file not found!")
        print(f"Creating .env from .env.example...")
        env_example = backend_dir / '.env.example'
        if env_example.exists():
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print(f"✓ Created .env - please edit with your API key")
        else:
            print(f"✗ .env.example not found")
            return False
    
    print(f"\n🚀 Starting system...")
    print(f"  Backend will run on: http://localhost:5000")
    print(f"  Frontend will run on: http://localhost:8000")
    print(f"\nYou can access the application at: http://localhost:8000")
    print(f"Press Ctrl+C to stop.\n")
    
    # Start backend
    print(f"Starting backend...")
    backend_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=str(backend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    time.sleep(3)  # Give backend time to start
    
    # Start frontend (if possible)
    print(f"Starting frontend...")
    try:
        frontend_process = subprocess.Popen(
            [sys.executable, '-m', 'http.server', '8000', '--directory', str(frontend_dir)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        print(f"\n✓ Both servers started!")
    except Exception as e:
        print(f"✗ Could not start frontend: {e}")
        print(f"  You can manually start it with:")
        print(f"    cd {frontend_dir}")
        print(f"    python -m http.server 8000")
        frontend_process = None
    
    # Wait for processes
    try:
        backend_process.wait()
    except KeyboardInterrupt:
        print(f"\n\nShutting down...")
        backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print(f"✓ Servers stopped")
    
    return True

if __name__ == '__main__':
    success = start_system()
    sys.exit(0 if success else 1)
