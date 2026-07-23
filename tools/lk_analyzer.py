#!/usr/bin/env python3
"""
MediaTek LK Dump Deep Analyzer Tool
Scans any MTK lk.img dump file, extracts partition headers, checks security policies,
discovers registered fastboot commands, and tests exploit compatibility.
Usage:
    python lk_analyzer.py <path_to_lk.img>
"""

import sys
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PARENT_DIR, "injector"))

try:
    from liblk.image import LkImage
except ImportError:
    LkImage = None

def analyze_lk(image_path):
    if not os.path.exists(image_path):
        print(f"[!] File not found: {image_path}")
        sys.exit(1)

    print("==========================================================")
    print("   MEDIATEK LK DUMP DEEP ANALYZER TOOL")
    print(f"   Target Image: {image_path}")
    print(f"   Image Size: {os.path.getsize(image_path):,} bytes")
    print("==========================================================")

    with open(image_path, "rb") as f:
        data = f.read()

    magic = data[:4]
    magic_hex = hex(int.from_bytes(magic, "little")) if len(magic) >= 4 else "N/A"
    print(f"\n[1] HEADER CHECK:")
    print(f"    First 4 Bytes: {magic} (Hex: {magic_hex})")
    if magic_hex == "0x58881688":
        print("    [+] Valid MediaTek LK GFH Container Magic Identified!")
    else:
        print("    [!] Warning: Magic byte does not match standard 0x58881688 MTK header.")

    if LkImage:
        try:
            image = LkImage(image_path)
            print(f"\n[2] PARTITIONS IN CONTAINER ({len(image.partitions)} found):")
            for name, part in image.partitions.items():
                addr = getattr(part, 'lk_address', None) or part.header.memory_address
                print(f"    - Sub-partition '{name}': Memory Base={hex(addr)}, Size={part.header.size:,} bytes, Certs={len(part.certs)}")
        except Exception as e:
            print(f"    [!] Error parsing container partitions: {e}")

    print("\n[3] SECURITY POLICIES & EXPLOIT PATTERNS:")
    patterns = {
        'sec_get_vfy_policy (Unpatched)': bytes.fromhex('200200b4fd7bbea9'),
        'sec_get_vfy_policy (Generic)': bytes.fromhex('000100b4fd7bbfa9'),
        'sec_get_vfy_policy (Patched)': bytes.fromhex('00008052c0035fd6'),
        'spoof_lock_state': bytes.fromhex('f3031f2aaf000017200200b4fd7bbea9f30b00f9fd030091'),
        'spoof_sboot_state': bytes.fromhex('fd7bbea9f30b00f9fd030091f30300aa20008052'),
        'dont_relock_seccfg': bytes.fromhex('fd7bbea9f30b00f9fd030091f303002a28008052'),
    }

    for name, pat in patterns.items():
        count = data.count(pat)
        print(f"    - {name:32s}: {count} match(es)")

    print("\n[4] REGISTERED FASTBOOT & OEM COMMANDS DISCOVERED:")
    fastboot_cmds = re.findall(rb'[a-zA-Z0-9_\-:]*(?:fastboot|oem|flashing|reboot|getvar|download|flash|erase)[a-zA-Z0-9_\-:]*', data)
    unique_cmds = sorted(list(set(cmd.decode('latin1', 'ignore') for cmd in fastboot_cmds if 3 < len(cmd) < 50)))
    print(f"    Found {len(unique_cmds)} fastboot/oem strings. Top entries:")
    for cmd in unique_cmds[:25]:
        print(f"      * {cmd}")
    if len(unique_cmds) > 25:
        print(f"      ... and {len(unique_cmds)-25} additional commands")

    print("\n==========================================================")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PARENT_DIR, "bin", "x6871.bin")
    analyze_lk(target)
