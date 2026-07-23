#!/usr/bin/env python3
"""
Fenrir Fastboot Flashing Helper for Windows & Linux
Automatically detects connected device, queries fastboot slot info, and flashes lk.patched image.
Usage:
    python flash.py [image_path]
"""

import sys
import os
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_fastboot():
    fb = shutil.which("fastboot")
    if fb:
        return fb
    # Check common Android SDK locations on Windows
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    candidate = os.path.join(local_app_data, "Android", "Sdk", "platform-tools", "fastboot.exe")
    if os.path.exists(candidate):
        return candidate
    return None

def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRIPT_DIR, "lk.patched")

    if not os.path.exists(image_path):
        print(f"[!] Error: Image file to flash not found at: {image_path}")
        print("    Run 'python build.py X6871' first to generate lk.patched.")
        sys.exit(1)

    fastboot_bin = find_fastboot()
    if not fastboot_bin:
        print("[!] Error: 'fastboot' command not found in PATH or Android SDK.")
        print("    Please install Android Platform-Tools or add fastboot.exe to your PATH.")
        sys.exit(1)

    print("==================================================")
    print("  Fenrir Automated Fastboot Flashing Utility")
    print(f"  Target Image: {image_path}")
    print("==================================================")

    print("[*] Waiting for device in Fastboot mode...")
    try:
        proc = subprocess.run([fastboot_bin, "devices"], capture_output=True, text=True, timeout=10)
        output = proc.stdout.strip()
        if not output:
            print("[!] No devices found in fastboot mode. Connect phone in fastboot mode (Vol Down + Power).")
            sys.exit(1)
        print(f"[+] Connected device:\n{output}\n")
    except Exception as e:
        print(f"[!] Error querying fastboot devices: {e}")
        sys.exit(1)

    print("[*] Flashing patched bootloader image to 'lk' partition...")
    try:
        # Check current slot (A/B)
        slot_proc = subprocess.run([fastboot_bin, "getvar", "current-slot"], capture_output=True, text=True)
        slot = "a"
        if "current-slot: b" in slot_proc.stderr.lower() or "current-slot: b" in slot_proc.stdout.lower():
            slot = "b"
        
        print(f"[*] Detected active slot: {slot}")
        
        # Flash to active slot and lk partition
        res1 = subprocess.run([fastboot_bin, "flash", f"lk_{slot}", image_path])
        if res1.returncode == 0:
            print(f"[+] Successfully flashed lk_{slot}!")
        else:
            print("[*] Trying generic 'lk' partition target...")
            res2 = subprocess.run([fastboot_bin, "flash", "lk", image_path])
            if res2.returncode == 0:
                print("[+] Successfully flashed lk!")
            else:
                print("[!] Flashing failed. Verify unlock state and connection.")
                sys.exit(1)

    except Exception as e:
        print(f"[!] Error during flashing: {e}")
        sys.exit(1)

    print("\n[+] All steps completed! Rebooting device...")
    subprocess.run([fastboot_bin, "reboot"])

if __name__ == '__main__':
    main()
