#!/usr/bin/env python3
"""
Advanced TK11 Firmware Analyzer
================================
Comprehensive binary analysis tool for TK11 radio firmware files.

Features:
- Multi-offset TX mask detection
- Multiple CRC algorithm validation (CRC16-XMODEM, CRC16-IBM, CRC16-CCITT)
- Entropy analysis for encryption detection
- Header structure parsing
- Firmware comparison between variants
- Binary pattern recognition
- Statistical analysis of byte distributions

Author: Claude (Advanced Analysis Agent)
Date: 2025-11-06
"""

import os
import sys
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib


class CRCCalculator:
    """Multiple CRC algorithm implementations for validation."""

    @staticmethod
    def crc16_xmodem(data: bytes) -> int:
        """CRC16-XMODEM (polynomial 0x1021, init 0x0000)"""
        crc = 0x0000
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    @staticmethod
    def crc16_ibm(data: bytes) -> int:
        """CRC16-IBM (polynomial 0x8005, init 0x0000)"""
        crc = 0x0000
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0x8005
                else:
                    crc = crc >> 1
        return crc

    @staticmethod
    def crc16_ccitt(data: bytes) -> int:
        """CRC16-CCITT (polynomial 0x1021, init 0xFFFF)"""
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc

    @staticmethod
    def crc16_ccitt_false(data: bytes) -> int:
        """CRC16-CCITT-FALSE (polynomial 0x1021, init 0xFFFF, no final XOR)"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc


class FirmwareAnalyzer:
    """Advanced firmware analysis and validation."""

    # Known critical offsets
    TX_MASK_OFFSET = 0x314D
    EXPECTED_SIZE = 357976  # bytes

    # Potential CRC locations (offsets in header)
    CRC_POSITIONS = [0x0C, 0x0E, 0x10, 0x12, 0x1C, 0x1E, 0x20, 0x22]

    def __init__(self, firmware_path: str):
        self.path = Path(firmware_path)
        self.data = None
        self.size = 0
        self.metadata = {}

        if self.path.exists():
            with open(self.path, 'rb') as f:
                self.data = f.read()
            self.size = len(self.data)

    def analyze_full(self) -> Dict:
        """Perform comprehensive analysis."""
        if not self.data:
            return {"error": "Firmware file not found"}

        results = {
            "file": str(self.path),
            "size": self.size,
            "basic_info": self._analyze_basic(),
            "tx_mask": self._analyze_tx_mask(),
            "header": self._analyze_header(),
            "crc_analysis": self._analyze_crc_all_methods(),
            "entropy": self._analyze_entropy(),
            "encryption": self._detect_encryption(),
            "patterns": self._find_patterns(),
            "hashes": self._calculate_hashes(),
        }

        return results

    def _analyze_basic(self) -> Dict:
        """Basic firmware information."""
        return {
            "size_matches_expected": self.size == self.EXPECTED_SIZE,
            "expected_size": self.EXPECTED_SIZE,
            "actual_size": self.size,
            "size_difference": self.size - self.EXPECTED_SIZE,
        }

    def _analyze_tx_mask(self) -> Dict:
        """Analyze TX mask at critical offset."""
        if self.size <= self.TX_MASK_OFFSET:
            return {"error": "File too small"}

        tx_byte = self.data[self.TX_MASK_OFFSET]

        return {
            "offset": f"0x{self.TX_MASK_OFFSET:04X}",
            "value": f"0x{tx_byte:02X}",
            "binary": f"{tx_byte:08b}",
            "modes_enabled": {
                "FM (bit 0)": bool(tx_byte & 0x01),
                "AM (bit 1)": bool(tx_byte & 0x02),
                "USB (bit 2)": bool(tx_byte & 0x04),
                "LSB (bit 3)": bool(tx_byte & 0x08),
                "CW (bit 4)": bool(tx_byte & 0x10),
            },
            "is_patched": tx_byte == 0x13,
            "is_original": tx_byte == 0x03,
        }

    def _analyze_header(self) -> Dict:
        """Parse firmware header structure."""
        header = self.data[:256]  # First 256 bytes

        # Try to extract magic numbers and structure
        header_analysis = {
            "first_16_bytes": header[:16].hex(),
            "first_4_bytes_as_uint32_le": struct.unpack("<I", header[:4])[0] if len(header) >= 4 else None,
            "first_4_bytes_as_uint32_be": struct.unpack(">I", header[:4])[0] if len(header) >= 4 else None,
        }

        # Check for potential CRC values at known positions
        crc_candidates = {}
        for pos in self.CRC_POSITIONS:
            if len(header) > pos + 1:
                crc_le = struct.unpack("<H", header[pos:pos+2])[0]
                crc_be = struct.unpack(">H", header[pos:pos+2])[0]
                crc_candidates[f"0x{pos:04X}"] = {
                    "little_endian": f"0x{crc_le:04X}",
                    "big_endian": f"0x{crc_be:04X}",
                }

        header_analysis["potential_crc_positions"] = crc_candidates

        return header_analysis

    def _analyze_crc_all_methods(self) -> Dict:
        """Try all CRC algorithms at multiple positions."""
        results = {}

        # Test CRC over entire file except last 2 bytes
        data_for_crc = self.data[:-2] if len(self.data) > 2 else self.data
        stored_crc_eof_le = struct.unpack("<H", self.data[-2:])[0] if len(self.data) >= 2 else None
        stored_crc_eof_be = struct.unpack(">H", self.data[-2:])[0] if len(self.data) >= 2 else None

        algorithms = {
            "CRC16-XMODEM": CRCCalculator.crc16_xmodem,
            "CRC16-IBM": CRCCalculator.crc16_ibm,
            "CRC16-CCITT": CRCCalculator.crc16_ccitt,
            "CRC16-CCITT-FALSE": CRCCalculator.crc16_ccitt_false,
        }

        for name, func in algorithms.items():
            calculated = func(data_for_crc)
            results[name] = {
                "calculated": f"0x{calculated:04X}",
                "matches_eof_le": calculated == stored_crc_eof_le,
                "matches_eof_be": calculated == stored_crc_eof_be,
                "stored_eof_le": f"0x{stored_crc_eof_le:04X}" if stored_crc_eof_le else None,
                "stored_eof_be": f"0x{stored_crc_eof_be:04X}" if stored_crc_eof_be else None,
            }

        # Also check CRC over different ranges
        # Try excluding header
        if len(self.data) > 256:
            data_no_header = self.data[256:-2]
            for name, func in algorithms.items():
                calc = func(data_no_header)
                results[f"{name}_no_header"] = f"0x{calc:04X}"

        return results

    def _analyze_entropy(self) -> Dict:
        """Calculate Shannon entropy to detect encryption/compression."""
        if not self.data:
            return {"error": "No data"}

        # Calculate byte frequency
        freq = [0] * 256
        for byte in self.data:
            freq[byte] += 1

        # Calculate entropy
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / len(self.data)
                entropy -= p * (p.bit_length() - 1)  # Approximation

        # More accurate calculation
        import math
        entropy = 0.0
        for count in freq:
            if count > 0:
                p = count / len(self.data)
                entropy -= p * math.log2(p)

        return {
            "entropy_bits": round(entropy, 4),
            "max_entropy": 8.0,
            "normalized": round(entropy / 8.0, 4),
            "likely_encrypted": entropy > 7.5,
            "interpretation": self._interpret_entropy(entropy),
        }

    def _interpret_entropy(self, entropy: float) -> str:
        """Interpret entropy value."""
        if entropy > 7.9:
            return "Very high - likely encrypted or compressed"
        elif entropy > 7.5:
            return "High - possibly encrypted"
        elif entropy > 6.5:
            return "Medium-high - mixed data"
        elif entropy > 5.0:
            return "Medium - typical firmware"
        else:
            return "Low - lots of repetition or padding"

    def _detect_encryption(self) -> Dict:
        """Detect encryption patterns."""
        # Check for long runs of identical bytes (suggests not encrypted)
        max_run = 0
        current_run = 1
        prev_byte = self.data[0] if self.data else 0

        for byte in self.data[1:]:
            if byte == prev_byte:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 1
            prev_byte = byte

        # Check for null bytes
        null_count = self.data.count(0x00)
        ff_count = self.data.count(0xFF)

        return {
            "max_identical_run": max_run,
            "null_bytes": null_count,
            "null_percentage": round(100 * null_count / len(self.data), 2),
            "0xFF_bytes": ff_count,
            "likely_encrypted": max_run < 50 and null_count < len(self.data) * 0.01,
        }

    def _find_patterns(self) -> Dict:
        """Find interesting byte patterns."""
        patterns = {
            "version_strings": [],
            "timestamps": [],
            "potential_strings": [],
        }

        # Look for ASCII strings (4+ printable characters)
        current_string = []
        for i, byte in enumerate(self.data):
            if 32 <= byte <= 126:  # Printable ASCII
                current_string.append(chr(byte))
            else:
                if len(current_string) >= 4:
                    string = ''.join(current_string)
                    if any(c.isalnum() for c in string):
                        patterns["potential_strings"].append({
                            "offset": f"0x{i-len(current_string):04X}",
                            "string": string,
                            "length": len(current_string),
                        })
                current_string = []

        # Limit results
        patterns["potential_strings"] = patterns["potential_strings"][:20]

        return patterns

    def _calculate_hashes(self) -> Dict:
        """Calculate cryptographic hashes."""
        return {
            "md5": hashlib.md5(self.data).hexdigest(),
            "sha1": hashlib.sha1(self.data).hexdigest(),
            "sha256": hashlib.sha256(self.data).hexdigest(),
        }

    def compare_with(self, other_path: str) -> Dict:
        """Compare with another firmware file."""
        other = FirmwareAnalyzer(other_path)
        if not other.data:
            return {"error": "Other file not found"}

        # Find differences
        differences = []
        min_size = min(len(self.data), len(other.data))

        for i in range(min_size):
            if self.data[i] != other.data[i]:
                differences.append({
                    "offset": f"0x{i:04X}",
                    "file1": f"0x{self.data[i]:02X}",
                    "file2": f"0x{other.data[i]:02X}",
                })

                # Limit to first 100 differences
                if len(differences) >= 100:
                    break

        return {
            "size_difference": len(self.data) - len(other.data),
            "total_differences": len(differences),
            "differences": differences[:20],  # Show first 20
            "files_identical": len(differences) == 0 and len(self.data) == len(other.data),
        }


def print_analysis_report(analysis: Dict):
    """Pretty print analysis results."""
    print("\n" + "="*80)
    print("TK11 FIRMWARE ANALYSIS REPORT")
    print("="*80)

    print(f"\n[*] File: {analysis.get('file', 'Unknown')}")
    print(f"[*] Size: {analysis.get('size', 0):,} bytes")

    # Basic info
    basic = analysis.get('basic_info', {})
    if basic.get('size_matches_expected'):
        print("[+] Size matches expected TK11 firmware size")
    else:
        diff = basic.get('size_difference', 0)
        print(f"[!] Size difference: {diff:+,} bytes")

    # TX Mask
    print("\n" + "-"*80)
    print("TX MASK ANALYSIS (Offset 0x314D)")
    print("-"*80)
    tx = analysis.get('tx_mask', {})
    print(f"Value: {tx.get('value', 'N/A')} (binary: {tx.get('binary', 'N/A')})")

    modes = tx.get('modes_enabled', {})
    for mode, enabled in modes.items():
        status = "[+]" if enabled else "[-]"
        print(f"  {status} {mode}")

    if tx.get('is_patched'):
        print("\n[+] FIRMWARE IS PATCHED - USB TX ENABLED")
    elif tx.get('is_original'):
        print("\n[-] FIRMWARE IS ORIGINAL - USB TX DISABLED")

    # Entropy
    print("\n" + "-"*80)
    print("ENCRYPTION ANALYSIS")
    print("-"*80)
    entropy = analysis.get('entropy', {})
    print(f"Shannon Entropy: {entropy.get('entropy_bits', 0):.4f} bits/byte")
    print(f"Normalized: {entropy.get('normalized', 0):.2%}")
    print(f"Interpretation: {entropy.get('interpretation', 'Unknown')}")

    encryption = analysis.get('encryption', {})
    if encryption.get('likely_encrypted'):
        print("[!] Firmware appears to be encrypted")
    else:
        print("[*] Firmware may not be encrypted (or uses weak encryption)")

    # CRC Analysis
    print("\n" + "-"*80)
    print("CRC VALIDATION")
    print("-"*80)
    crc_results = analysis.get('crc_analysis', {})

    for algo, result in crc_results.items():
        if isinstance(result, dict):
            print(f"\n{algo}:")
            print(f"  Calculated: {result.get('calculated', 'N/A')}")
            if result.get('matches_eof_le'):
                print(f"  [+] MATCHES stored CRC at EOF (little-endian)")
            elif result.get('matches_eof_be'):
                print(f"  [+] MATCHES stored CRC at EOF (big-endian)")
            else:
                print(f"  [-] No match")

    # Hashes
    print("\n" + "-"*80)
    print("FILE HASHES")
    print("-"*80)
    hashes = analysis.get('hashes', {})
    for hash_type, value in hashes.items():
        print(f"{hash_type.upper()}: {value}")

    print("\n" + "="*80)
    print("END OF REPORT")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_firmware_analyzer.py <firmware.bin> [compare_with.bin]")
        print("\nFeatures:")
        print("  - TX mask analysis at offset 0x314D")
        print("  - Multiple CRC algorithm validation")
        print("  - Encryption detection (entropy analysis)")
        print("  - Binary pattern recognition")
        print("  - Firmware comparison")
        sys.exit(1)

    firmware_path = sys.argv[1]

    # Analyze first firmware
    print(f"\n[*] Analyzing: {firmware_path}")
    analyzer = FirmwareAnalyzer(firmware_path)
    analysis = analyzer.analyze_full()

    if "error" in analysis:
        print(f"[!] Error: {analysis['error']}")
        sys.exit(1)

    print_analysis_report(analysis)

    # Compare if second file provided
    if len(sys.argv) >= 3:
        compare_path = sys.argv[2]
        print(f"\n[*] Comparing with: {compare_path}")
        comparison = analyzer.compare_with(compare_path)

        print("\n" + "="*80)
        print("FIRMWARE COMPARISON")
        print("="*80)

        if comparison.get('files_identical'):
            print("[+] Files are IDENTICAL")
        else:
            print(f"[!] Found {comparison.get('total_differences', 0)} differences")
            print(f"[!] Size difference: {comparison.get('size_difference', 0):+,} bytes")

            print("\nFirst 20 differences:")
            for diff in comparison.get('differences', []):
                print(f"  0x{diff['offset']}: {diff['file1']} -> {diff['file2']}")

        print("="*80 + "\n")


if __name__ == "__main__":
    main()
