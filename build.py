#!/usr/bin/env python3
"""
Fenrir Windows Native Builder
Allows 1-command building and patching of MediaTek bootloader images on Windows & Linux.
Usage:
    python build.py <device_codename> [bootloader_path]
Example:
    python build.py X6871
    python build.py X6871 C:\\path\\to\\custom_lk.img
"""

import sys
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INJECTOR_DIR = os.path.join(SCRIPT_DIR, "injector")
BIN_DIR = os.path.join(SCRIPT_DIR, "bin")

sys.path.insert(0, INJECTOR_DIR)

try:
    from devices import DEVICES
    from injector import BootloaderInjector
except ImportError as e:
    print(f"[!] Error importing injector modules: {e}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python build.py <device> [image_path]")
        print("\nSupported Devices:")
        for dev in DEVICES:
            print(f"  - {dev.name} ({dev.codename})")
        sys.exit(1)

    device_arg = sys.argv[1].lower()
    
    target_dev = None
    for dev in DEVICES:
        if dev.name.lower() == device_arg:
            target_dev = dev
            break
            
    if not target_dev:
        print(f"[!] Unknown device: '{sys.argv[1]}'")
        print(f"Available codenames: {', '.join(d.name for d in DEVICES)}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        image_path = sys.argv[2]
    else:
        image_path = os.path.join(BIN_DIR, f"{target_dev.name.lower()}.bin")

    if not os.path.exists(image_path):
        print(f"[!] Bootloader image not found at: {image_path}")
        sys.exit(1)

    output_path = os.path.join(SCRIPT_DIR, "lk.patched")

    print("==================================================")
    print(f"  Building Fenrir Exploit for {target_dev.codename} ({target_dev.name})")
    print(f"  Input Bootloader: {image_path}")
    print(f"  Output Bootloader: {output_path}")
    print("==================================================")

    class Args:
        pass
    args = Args()
    args.image = image_path
    args.payload_dir = os.path.join(SCRIPT_DIR, "payload", "build")
    args.config = None
    args.list_stages = False
    args.output = output_path

    res = target_dev.execute(args)
    if res == 0:
        print(f"\n[+] Build successful! Output saved to: {output_path}")
    else:
        print(f"\n[!] Build failed with exit code: {res}")
        sys.exit(res)

if __name__ == '__main__':
    main()
