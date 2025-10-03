#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    # Get Turso auth token from environment
    auth_token = os.getenv('TURSO_AUTH_TOKEN')
    if not auth_token:
        print("Error: TURSO_AUTH_TOKEN environment variable not set")
        sys.exit(1)
    
    # Authenticate with Turso
    run_command(f"turso auth token {auth_token}")
    
    # Apply database schemas
    print("Applying database schemas...")
    run_command("turso db shell bioband-praveencoder2007 < database/schemas/minimal_db.sql")
    run_command("turso db shell bioband-praveencoder2007 < database/schemas/chat_messages.sql")
    
    print("Database sync completed successfully!")

if __name__ == "__main__":
    main()