#!/usr/bin/env python3
"""
Test if the ORIGINAL unmodified firmware also triggers the error
If it does, the issue is not our patch but something else
"""

from pathlib import Path
import shutil

original = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")
test_dir = Path(r"E:\AI\tk11\test_firmware")

test_dir.mkdir(exist_ok=True)

# Create exact copy of original
test_copy = test_dir / "TK11_ORIGINAL_UNMODIFIED_TEST.bin"
shutil.copy2(original, test_copy)

print("="*80)
print("TESTING HYPOTHESIS")
print("="*80)
print("""
Created an EXACT copy of the original firmware:
  {test_copy}

HYPOTHESIS TO TEST:
  If TK11.exe rejects this unmodified original firmware with
  "File version is Wrong!" error, then the problem is NOT our patch.

  The issue might be:
  1. TK11.exe expects a specific FILE NAME pattern
  2. TK11.exe checks the file timestamp/attributes
  3. TK11.exe requires firmware to be in a specific directory
  4. The "program=" path in config.ini matters
  5. There's a version mismatch with the TK11.exe version itself

NEXT STEPS:
  1. Try loading: {test_copy}
  2. If it WORKS -> Our patch breaks validation
  3. If it FAILS -> Something else is wrong (not the patch)

""".format(test_copy=test_copy))

print("\nOriginal firmware info:")
with open(original, 'rb') as f:
    data = f.read()
    print(f"  Size: {len(data):,} bytes (0x{len(data):X})")
    print(f"  First 16 bytes: {data[:16].hex()}")
    print(f"  Last 16 bytes: {data[-16:].hex()}")

print("\nTest copy info:")
with open(test_copy, 'rb') as f:
    data = f.read()
    print(f"  Size: {len(data):,} bytes (0x{len(data):X})")
    print(f"  First 16 bytes: {data[:16].hex()}")
    print(f"  Last 16 bytes: {data[-16:].hex()}")

print("\n" + "="*80)
print("Files are identical - ready for testing")
print("="*80)
