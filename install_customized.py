#!/usr/8/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    print("========================================================")
    print("      NPD Management - Automated Custom Installer       ")
    print("========================================================")
    print("This script automatically configures your custom R&D Sandbox")
    print("DocTypes to mirror your target environment precisely before deployment.\n")

def get_input(prompt, default=None, hidden=False):
    if default:
        p = f"{prompt} [{default}]: "
    else:
        p = f"{prompt}: "
        
    if hidden:
        import getpass
        val = getpass.getpass(p)
    else:
        val = input(p)
        
    return val.strip() or default

def main():
    print_banner()
    
    # 1. Ask for Target Site
    site_name = get_input("Enter your target Frappe site name", "site1.local")
    
    print("\n--- Installation Synchronization Mode ---")
    print("1) Automated Live Sync (Connects over REST API overlays to build exact dynamic layouts)")
    print("2) Offline CSV Template Import (Reads pre-sorted CSV files exported from 'Customize Form')")
    mode = get_input("Select synchronization mode", "1")
    
    if mode == "1":
        # 2. Check/Prompt for API Credentials
        env_file = Path(".env")
        url, api_key, api_secret = "", "", ""
        
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        v = v.strip('"').strip("'")
                        if k == "ERPNEXT_URL": url = v
                        elif k == "USER_API_KEY": api_key = v
                        elif k == "USER_API_SECRET": api_secret = v
                        
        print("\n--- Target API Synchronization Settings ---")
        url = get_input("ERPNext Instance URL", url or "http://localhost:8000")
        api_key = get_input("Administrator API Key", api_key)
        api_secret = get_input("Administrator API Secret", api_secret, hidden=True)
        
        # Save back securely
        with open(env_file, "w") as f:
            f.write(f'ERPNEXT_URL="{url}"\n')
            f.write(f'USER_API_KEY="{api_key}"\n')
            f.write(f'USER_API_SECRET="{api_secret}"\n')
            
        print("\n[1/3] Executing live DocType schema extraction from target server...")
        res = subprocess.run([sys.executable, "extract_doctypes.py"])
        if res.returncode != 0:
            print("\n[ERROR] Schema extraction failed. Please verify your API credentials and server URL connection.")
            sys.exit(1)
            
    else:
        # Option 2: CSV Offline Mode
        print("\n--- Offline CSV Synchronization ---")
        print("Please ensure your exported 'Customize Form' CSV files are available.")
        
        doctypes_map = {
            "Item": "NPD Item",
            "BOM": "NPD BOM"
        }
        
        import extract_doctypes
        for dt_orig, dt_new in doctypes_map.items():
            default_name = f"{dt_orig.lower()}_layout.csv"
            ans = get_input(f"Enter absolute path to your exported CSV layout for '{dt_new}' (or drop '{default_name}' into this directory and press Enter)", default_name)
            if ans and os.path.exists(ans):
                extract_doctypes.compile_from_csv(dt_orig, ans, dt_new)
            else:
                print(f"[NOTE] Valid layout CSV not found at '{ans}'. Retaining native package defaults for '{dt_new}'.")
                    
    print("\n[2/3] Finalizing local R&D schema topological sections and structures...")
    res = subprocess.run([sys.executable, "finalize_doctypes.py"])
    if res.returncode != 0:
        print("\n[ERROR] Finalizing DocTypes failed.")
        sys.exit(1)
        
    print(f"\n[3/3] Deploying module natively onto site '{site_name}'...")
    
    # Execute bench install command gracefully
    try:
        res = subprocess.run(["bench", "--site", site_name, "install-app", "npd_management"])
        if res.returncode == 0:
            print("\n========================================================")
            print("  SUCCESS! NPD Management module customized & installed!")
            print("========================================================")
        else:
            print(f"\n[WARNING] Native bench command returned non-zero code. If operating within custom Docker instances, run manually:")
            print(f"          docker compose exec erpnext bench --site {site_name} install-app npd_management")
    except FileNotFoundError:
        print(f"\n[NOTE] 'bench' executable not detected in active direct path. Please run installation inside your container/bench:")
        print(f"       bench --site {site_name} install-app npd_management")

if __name__ == "__main__":
    main()
