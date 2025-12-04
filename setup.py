"""
Setup script for Privacy-First Personal Agent.
Installs dependencies and initializes the system.
"""
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and print status."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} complete")
            return True
        else:
            print(f"✗ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main setup function."""
    print("="*60)
    print("🔒 Privacy-First Personal Agent - Setup")
    print("="*60)
    
    # Step 1: Install Python dependencies
    print("\n[1/5] Installing Python dependencies...")
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        print("\n⚠ Some dependencies failed to install. You may need to install them manually.")
    
    # Step 2: Download spaCy model
    print("\n[2/5] Downloading spaCy language model...")
    run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy model"
    )
    
    # Step 3: Initialize database
    print("\n[3/5] Initializing encrypted database...")
    try:
        from database import PrivacyDatabase
        db = PrivacyDatabase()
        db.connect()
        db.close()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
    
    # Step 4: Initialize encryption
    print("\n[4/5] Setting up encryption...")
    try:
        from encryption import get_encryption_manager
        em = get_encryption_manager()
        print("✓ Encryption initialized")
    except Exception as e:
        print(f"✗ Encryption setup failed: {e}")
    
    # Step 5: Check Ollama
    print("\n[5/5] Checking Ollama installation...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print(f"✓ Ollama is running with {len(models)} model(s)")
                print(f"  Models: {', '.join([m['name'] for m in models])}")
            else:
                print("✓ Ollama is running but no models found")
                print("  Run: ollama pull llama3.2:3b")
        else:
            print("⚠ Ollama is not responding")
    except:        print("⚠ Ollama is not installed or not running")
        print("\n  To install Ollama:")
        print("    Visit: https://ollama.ai")
        print("    After installation, run: ollama pull llama3.2:3b")
    
    # Final summary
    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    print("\nTo start the agent, run:")
    print(f"  {sys.executable} cli.py")
    print("\nFor more information, see README.md")
    print("\n🔒 Remember: All your data stays private on your device!")


if __name__ == "__main__":
    main()
