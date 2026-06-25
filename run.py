# run.py
import os
import sys
import subprocess

def check_and_install_dependencies():
    required_packages = ["fastapi", "uvicorn", "pillow", "numpy", "python-multipart"]
    installed_packages = []
    
    print("=" * 60)
    print("   MYNTRA FOR BHARAT - WARDROBE PLANNER STARTUP WIZARD   ")
    print("=" * 60)
    print("Checking dependencies...")
    
    # Check what packages are available
    for pkg in required_packages:
        try:
            if pkg == "pillow":
                import PIL
            elif pkg == "python-multipart":
                import multipart
            else:
                __import__(pkg)
            print(f"  [OK] {pkg} is installed.")
        except ImportError:
            print(f"  [..] {pkg} is missing, preparing to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                print(f"  [OK] {pkg} successfully installed!")
            except Exception as e:
                print(f"  [X] Failed to install {pkg} automatically. Error: {e}")
                print(f"      Please run: pip install {pkg}")
                sys.exit(1)

    print("All dependencies are satisfied!")
    print("-" * 60)

def main():
    check_and_install_dependencies()
    
    # Change directory to backend to run uvicorn correctly
    project_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_dir, "backend")
    os.chdir(backend_dir)
    sys.path.insert(0, backend_dir)
    
    print("Starting FastAPI Uvicorn Server at http://127.0.0.1:8000 ...")
    print("Press Ctrl+C to stop the server.")
    print("=" * 60)
    
    try:
        # Run uvicorn server
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        # Alternative fallback using subprocess
        try:
            subprocess.run(["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"])
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutdown complete.")
