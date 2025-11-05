#!/usr/bin/env python3
"""
Find TX validation mask in TK11 firmware
This script searches for the 0x03 byte that controls which modes can transmit
"""

import struct
from pathlib import Path

def find_tx_mask_candidates(firmware_path):
    """Find all occurrences of 0x03 byte and analyze context"""

    with open(firmware_path, 'rb') as f:
        data = f.read()

    print("="*80)
    print("TX VALIDATION MASK FINDER")
    print("="*80)
    print(f"\nFirmware: {firmware_path}")
    print(f"Size: {len(data):,} bytes ({len(data)/1024:.1f} KB)")

    # Search for 0x03 byte
    print("\n--- SEARCHING FOR TX MASK (0x03) ---")

    candidates = []
    offset = 0

    while True:
        offset = data.find(b'\x03', offset)
        if offset == -1:
            break

        candidates.append(offset)
        offset += 1

    print(f"\nFound {len(candidates)} occurrences of 0x03 byte")

    # Analyze context around each occurrence
    print("\n--- ANALYZING CANDIDATES ---")
    print("Looking for patterns that suggest TX validation code...\n")

    # Patterns to look for:
    # 1. Near "TX" string
    # 2. Near mode validation code (0x00, 0x01, 0x02, 0x03, 0x04)
    # 3. In executable code section (not data)
    # 4. Pattern: mask byte followed by conditional logic

    high_confidence = []
    medium_confidence = []

    for offset in candidates:
        # Get context (32 bytes before and after)
        start = max(0, offset - 32)
        end = min(len(data), offset + 32)
        context = data[start:end]

        score = 0
        reasons = []

        # Check for nearby "TX" string
        search_range_start = max(0, offset - 1000)
        search_range_end = min(len(data), offset + 1000)
        search_range = data[search_range_start:search_range_end]

        if b'TX' in search_range:
            score += 10
            reasons.append("Near 'TX' string")

        # Check for mode bytes nearby (0x00, 0x01, 0x02, 0x04)
        if offset + 1 < len(data):
            next_byte = data[offset + 1]
            if next_byte in [0x00, 0x01, 0x02, 0x04, 0xFF]:
                score += 5
                reasons.append(f"Followed by mode-like byte (0x{next_byte:02X})")

        if offset - 1 >= 0:
            prev_byte = data[offset - 1]
            if prev_byte in [0x00, 0x01, 0x02, 0x04, 0xFF]:
                score += 5
                reasons.append(f"Preceded by mode-like byte (0x{prev_byte:02X})")

        # Check if in likely code section (not in padding or data)
        # Code sections usually have varied bytes, not repetitive patterns
        if offset >= 16 and offset + 16 < len(data):
            sample = data[offset-16:offset+16]
            unique_bytes = len(set(sample))
            if unique_bytes > 16:  # High variety = likely code
                score += 3
                reasons.append("High byte variety (code-like)")

        # Check for 0x1F byte nearby (RX mask from analysis)
        if b'\x1f' in context:
            score += 8
            reasons.append("Near 0x1F (RX mask)")

        # Look for bitwise operation patterns (AND/OR/XOR instructions)
        # Common ARM/x86 opcodes for bitwise ops
        if offset + 4 < len(data):
            next_4 = data[offset:offset+4]
            # Check for common bit test patterns
            if any(b in next_4 for b in [b'\x01', b'\x02', b'\x04', b'\x08']):
                score += 4
                reasons.append("Near bit pattern")

        candidate_info = {
            'offset': offset,
            'score': score,
            'reasons': reasons,
            'context': context,
            'context_start': start
        }

        if score >= 15:
            high_confidence.append(candidate_info)
        elif score >= 5:
            medium_confidence.append(candidate_info)

    # Sort by score
    high_confidence.sort(key=lambda x: x['score'], reverse=True)
    medium_confidence.sort(key=lambda x: x['score'], reverse=True)

    print(f"High confidence candidates: {len(high_confidence)}")
    print(f"Medium confidence candidates: {len(medium_confidence)}")

    # Display top candidates
    print("\n" + "="*80)
    print("TOP CANDIDATES (Score >= 15)")
    print("="*80)

    for i, cand in enumerate(high_confidence[:10], 1):
        print(f"\n[{i}] Offset: 0x{cand['offset']:08X} (Score: {cand['score']})")
        print(f"    Reasons: {', '.join(cand['reasons'])}")
        print(f"    Context (±32 bytes):")

        # Hex dump
        ctx = cand['context']
        ctx_start = cand['context_start']

        for j in range(0, len(ctx), 16):
            line = ctx[j:j+16]
            hex_str = ' '.join(f'{b:02x}' for b in line)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)

            # Highlight the target byte
            offset_in_line = cand['offset'] - ctx_start - j
            if 0 <= offset_in_line < len(line):
                hex_parts = hex_str.split(' ')
                hex_parts[offset_in_line] = f'[{hex_parts[offset_in_line]}]'
                hex_str = ' '.join(hex_parts)

            print(f"    {ctx_start + j:08X}: {hex_str:<48} {ascii_str}")

    if medium_confidence and len(high_confidence) < 5:
        print("\n" + "="*80)
        print("MEDIUM CONFIDENCE CANDIDATES (Score 5-14)")
        print("="*80)

        for i, cand in enumerate(medium_confidence[:5], 1):
            print(f"\n[{i}] Offset: 0x{cand['offset']:08X} (Score: {cand['score']})")
            print(f"    Reasons: {', '.join(cand['reasons'])}")

    # Look specifically at offset 0x0000054A mentioned in analysis
    target_offset = 0x0000054A
    if target_offset < len(data):
        print("\n" + "="*80)
        print(f"CHECKING OFFSET 0x{target_offset:08X} (from Agent #3 analysis)")
        print("="*80)

        value = data[target_offset]
        print(f"Value at 0x{target_offset:08X}: 0x{value:02X}")

        if value == 0x03:
            print("*** THIS IS THE TX MASK! ***")
        else:
            print(f"Note: Expected 0x03, found 0x{value:02X}")

        # Show context
        ctx_start = max(0, target_offset - 32)
        ctx_end = min(len(data), target_offset + 32)
        ctx = data[ctx_start:ctx_end]

        print("\nContext:")
        for j in range(0, len(ctx), 16):
            line = ctx[j:j+16]
            hex_str = ' '.join(f'{b:02x}' for b in line)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in line)

            offset_in_line = target_offset - ctx_start - j
            if 0 <= offset_in_line < len(line):
                hex_parts = hex_str.split(' ')
                hex_parts[offset_in_line] = f'[{hex_parts[offset_in_line]}]'
                hex_str = ' '.join(hex_parts)

            print(f"  {ctx_start + j:08X}: {hex_str:<48} {ascii_str}")

    return high_confidence, medium_confidence

def main():
    firmware_path = Path(r"E:\AI\tk11\TK11_v5.00.09_ENG.bin")

    if not firmware_path.exists():
        print(f"ERROR: Firmware file not found: {firmware_path}")
        return

    high, medium = find_tx_mask_candidates(firmware_path)

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    if high:
        print(f"\nMost likely TX mask location: 0x{high[0]['offset']:08X}")
        print(f"Confidence score: {high[0]['score']}")
        print(f"Reasons: {', '.join(high[0]['reasons'])}")
    else:
        print("\nNo high-confidence candidates found.")
        print("Manual analysis required.")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
1. Review the top candidates above
2. Choose the most likely offset (highest score)
3. Use firmware patcher script to modify that offset
4. Test patched firmware in radio

WARNING: Patching the wrong offset can brick your radio!
Always keep backup of original firmware.
""")

if __name__ == "__main__":
    main()
