#!/usr/bin/env python3
"""
TK11 Firmware Analysis Tool
Reverse engineering script to identify hidden transmission modes
"""

import os
import re
import struct
from collections import defaultdict

class FirmwareAnalyzer:
    def __init__(self, firmware_path):
        self.firmware_path = firmware_path
        with open(firmware_path, 'rb') as f:
            self.data = f.read()
        self.size = len(self.data)

    def extract_strings(self, min_length=4):
        """Extract ASCII strings from binary"""
        pattern = rb'[\x20-\x7E]{%d,}' % min_length
        strings = []
        for match in re.finditer(pattern, self.data):
            offset = match.start()
            string = match.group().decode('ascii', errors='ignore')
            strings.append((offset, string))
        return strings

    def search_modulation_keywords(self):
        """Search for modulation-related strings"""
        keywords = [
            b'USB', b'usb', b'LSB', b'lsb',
            b'CW', b'cw', b'FM', b'fm', b'AM', b'am',
            b'WFM', b'NFM', b'SSB', b'ssb',
            b'modulation', b'MODULATION',
            b'mode', b'MODE', b'Mode',
            b'transmit', b'TRANSMIT', b'Transmit',
            b'receive', b'RECEIVE', b'Receive',
            b'TX', b'tx', b'Tx',
            b'RX', b'rx', b'Rx',
            b'disable', b'DISABLE', b'lock', b'LOCK',
            b'enable', b'ENABLE', b'unlock', b'UNLOCK'
        ]

        results = defaultdict(list)
        for keyword in keywords:
            offset = 0
            while True:
                pos = self.data.find(keyword, offset)
                if pos == -1:
                    break
                # Get context (32 bytes before and after)
                start = max(0, pos - 32)
                end = min(len(self.data), pos + len(keyword) + 32)
                context = self.data[start:end]
                results[keyword.decode('ascii', errors='ignore')].append({
                    'offset': pos,
                    'hex_offset': f'0x{pos:08X}',
                    'context': context.hex()
                })
                offset = pos + 1

        return results

    def find_byte_patterns(self):
        """Look for common mode control patterns"""
        patterns = {
            'Mode flags (5 bits)': rb'[\x00-\x1F]',  # 5-bit mode selector
            'TX enable flag': rb'\x00\x01|\x01\x00',
            'Mode array': None  # Will search for arrays
        }

        # Look for mode configuration structures
        mode_structures = []

        # Pattern: consecutive mode definitions (FM=0, AM=1, USB=2, LSB=3, CW=4)
        for i in range(len(self.data) - 20):
            chunk = self.data[i:i+20]
            # Look for sequential or structured patterns
            if len(set(chunk[::2])) >= 4 and len(set(chunk[::2])) <= 6:
                mode_structures.append((i, chunk.hex()))

        return mode_structures[:50]  # Return first 50 candidates

    def analyze_header(self):
        """Analyze firmware header"""
        header = self.data[:256]

        analysis = {
            'magic_bytes': header[:16].hex(),
            'possible_version': None,
            'possible_arch': 'Unknown',
            'header_hex': header.hex()
        }

        # Look for version string in header
        version_pattern = rb'[0-9]\.[0-9]{2}\.[0-9]{2}'
        match = re.search(version_pattern, header)
        if match:
            analysis['possible_version'] = match.group().decode('ascii')

        return analysis

    def find_frequency_ranges(self):
        """Look for frequency range definitions"""
        # Common frequency representations in firmware:
        # - BCD encoded (e.g., 144.000 MHz as 0x144000)
        # - Integer kHz (e.g., 144000 for 144 MHz)
        # - Integer Hz

        freq_ranges = []

        # Look for common amateur radio frequencies in different formats
        test_freqs = [
            (144000, 'VHF 144 MHz'),
            (146000, 'VHF 146 MHz'),
            (430000, 'UHF 430 MHz'),
            (440000, 'UHF 440 MHz'),
            (28000, 'HF 28 MHz'),
        ]

        for freq, desc in test_freqs:
            # Try little-endian 32-bit
            freq_bytes = struct.pack('<I', freq)
            pos = self.data.find(freq_bytes)
            if pos != -1:
                freq_ranges.append({
                    'description': desc,
                    'offset': f'0x{pos:08X}',
                    'format': 'LE32',
                    'value': freq
                })

        return freq_ranges

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("=" * 80)
        print("TK11 FIRMWARE REVERSE ENGINEERING REPORT")
        print("=" * 80)
        print(f"\nFile: {self.firmware_path}")
        print(f"Size: {self.size} bytes ({self.size/1024:.2f} KB)")

        # Header analysis
        print("\n" + "=" * 80)
        print("1. FIRMWARE HEADER ANALYSIS")
        print("=" * 80)
        header = self.analyze_header()
        print(f"Magic Bytes: {header['magic_bytes'][:32]}...")
        if header['possible_version']:
            print(f"Version String: {header['possible_version']}")

        # String extraction
        print("\n" + "=" * 80)
        print("2. ASCII STRING EXTRACTION")
        print("=" * 80)
        strings = self.extract_strings(min_length=5)
        print(f"Total strings found: {len(strings)}")
        print("\nSample strings (first 30):")
        for offset, string in strings[:30]:
            print(f"  0x{offset:08X}: {string[:60]}")

        # Modulation keywords
        print("\n" + "=" * 80)
        print("3. MODULATION KEYWORD SEARCH")
        print("=" * 80)
        keywords = self.search_modulation_keywords()

        critical_keywords = ['USB', 'LSB', 'CW', 'SSB']
        print("\n*** CRITICAL FINDINGS - SSB/CW MODE DETECTION ***")
        for kw in critical_keywords:
            if kw in keywords or kw.lower() in keywords or kw.upper() in keywords:
                key = kw if kw in keywords else (kw.lower() if kw.lower() in keywords else kw.upper())
                if key in keywords:
                    print(f"\n[FOUND] '{key}' - {len(keywords[key])} occurrences:")
                    for entry in keywords[key][:5]:  # Show first 5
                        print(f"  Offset: {entry['hex_offset']}")
                        print(f"  Context: {entry['context'][:80]}...")

        print("\n*** ALL MODULATION-RELATED KEYWORDS ***")
        for keyword, occurrences in sorted(keywords.items()):
            if occurrences:
                print(f"\n'{keyword}': {len(occurrences)} occurrence(s)")
                for entry in occurrences[:3]:  # Show first 3 of each
                    print(f"  @ {entry['hex_offset']}")

        # Frequency ranges
        print("\n" + "=" * 80)
        print("4. FREQUENCY RANGE ANALYSIS")
        print("=" * 80)
        freq_ranges = self.find_frequency_ranges()
        if freq_ranges:
            print("Frequency references found:")
            for fr in freq_ranges:
                print(f"  {fr['description']}: {fr['offset']} ({fr['format']})")
        else:
            print("No standard frequency patterns detected")

        # Mode patterns
        print("\n" + "=" * 80)
        print("5. MODE CONTROL PATTERN ANALYSIS")
        print("=" * 80)
        patterns = self.find_byte_patterns()
        print(f"Potential mode configuration structures found: {len(patterns)}")
        print("\nFirst 10 candidates:")
        for i, (offset, hex_data) in enumerate(patterns[:10]):
            print(f"  {i+1}. Offset 0x{offset:08X}: {hex_data}")

        # Save detailed results
        self.save_detailed_results(strings, keywords, freq_ranges, patterns)

    def save_detailed_results(self, strings, keywords, freq_ranges, patterns):
        """Save detailed results to files"""

        # Save all strings
        with open('E:\\AI\\tk11\\firmware_strings_full.txt', 'w') as f:
            f.write("TK11 FIRMWARE - ALL ASCII STRINGS\n")
            f.write("=" * 80 + "\n\n")
            for offset, string in strings:
                f.write(f"0x{offset:08X}: {string}\n")

        # Save keyword results
        with open('E:\\AI\\tk11\\firmware_keywords.txt', 'w') as f:
            f.write("TK11 FIRMWARE - MODULATION KEYWORD ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            for keyword, occurrences in sorted(keywords.items()):
                f.write(f"\n{'='*60}\n")
                f.write(f"KEYWORD: '{keyword}' ({len(occurrences)} occurrences)\n")
                f.write(f"{'='*60}\n")
                for entry in occurrences:
                    f.write(f"\nOffset: {entry['hex_offset']}\n")
                    f.write(f"Context (hex): {entry['context']}\n")
                    # Try to decode context
                    try:
                        context_bytes = bytes.fromhex(entry['context'])
                        ascii_context = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context_bytes)
                        f.write(f"Context (ASCII): {ascii_context}\n")
                    except:
                        pass

        # Save hex dump of interesting regions
        with open('E:\\AI\\tk11\\firmware_mode_patterns.txt', 'w') as f:
            f.write("TK11 FIRMWARE - POTENTIAL MODE CONTROL PATTERNS\n")
            f.write("=" * 80 + "\n\n")
            for i, (offset, hex_data) in enumerate(patterns):
                f.write(f"\nPattern {i+1} @ 0x{offset:08X}:\n")
                f.write(f"Hex: {hex_data}\n")
                # Decode as ASCII
                try:
                    raw_bytes = bytes.fromhex(hex_data)
                    ascii_rep = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw_bytes)
                    f.write(f"ASCII: {ascii_rep}\n")
                except:
                    pass

        print("\n" + "=" * 80)
        print("DETAILED RESULTS SAVED TO:")
        print("  - E:\\AI\\tk11\\firmware_strings_full.txt")
        print("  - E:\\AI\\tk11\\firmware_keywords.txt")
        print("  - E:\\AI\\tk11\\firmware_mode_patterns.txt")
        print("=" * 80)


if __name__ == '__main__':
    analyzer = FirmwareAnalyzer('E:\\AI\\tk11\\TK11_v5.00.09_ENG.bin')
    analyzer.generate_report()
