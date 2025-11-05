#!/usr/bin/env python3
"""
TK11.exe .NET Assembly Analysis
Automatically extracts firmware validation code and checksum algorithm
"""

import subprocess
import os
import re
import json
from pathlib import Path

def run_dnspy_console(exe_path, output_dir):
    """Use dnSpy console to decompile TK11.exe"""
    dnspy_console = Path("dnSpy/dnSpy.Console.exe")

    if not dnspy_console.exists():
        print("ERROR: dnSpy.Console.exe not found")
        print("Trying alternative method...")
        return False

    cmd = [
        str(dnspy_console),
        exe_path,
        "--output", output_dir
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running dnSpy console: {e}")
        return False

def analyze_with_ilspy(exe_path):
    """Try to analyze using ILSpy command line if available"""
    try:
        # Check if ilspycmd is available
        result = subprocess.run(["ilspycmd", "--version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # Decompile to single file
            output = subprocess.run(
                ["ilspycmd", "-p", "-o", "tk11_decompiled.cs", exe_path],
                capture_output=True, text=True, timeout=120
            )
            return output.returncode == 0
    except:
        pass
    return False

def extract_strings_from_exe(exe_path):
    """Extract all strings from the executable"""
    print("[*] Extracting strings from TK11.exe...")

    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        # Extract ASCII strings (min length 4)
        ascii_strings = re.findall(rb'[\x20-\x7E]{4,}', data)

        # Extract Unicode strings (UTF-16LE)
        unicode_strings = re.findall(rb'(?:[\x20-\x7E]\x00){4,}', data)

        strings = []
        strings.extend([s.decode('ascii', errors='ignore') for s in ascii_strings])
        strings.extend([s.decode('utf-16le', errors='ignore') for s in unicode_strings])

        return list(set(strings))  # Remove duplicates

    except Exception as e:
        print(f"Error extracting strings: {e}")
        return []

def find_validation_related_strings(strings):
    """Find strings related to firmware validation"""
    keywords = [
        'version', 'Version', 'VERSION',
        'check', 'Check', 'CHECK',
        'valid', 'Valid', 'VALID',
        'firmware', 'Firmware', 'FIRMWARE',
        'file', 'File', 'FILE',
        'crc', 'CRC', 'checksum', 'Checksum',
        'error', 'Error', 'ERROR',
        '文件版本错误', 'File version is Wrong',
        'update', 'Update', 'UPDATE',
        'flash', 'Flash', 'FLASH'
    ]

    related = []
    for s in strings:
        for keyword in keywords:
            if keyword in s:
                related.append(s)
                break

    return sorted(set(related))

def analyze_pe_structure(exe_path):
    """Analyze PE structure to find .NET metadata"""
    print("[*] Analyzing PE structure...")

    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        # Check for .NET signature
        if b'mscoree.dll' in data:
            print("[+] Confirmed: .NET assembly")

        # Find COM descriptor
        if b'v4.0.30319' in data or b'v2.0.50727' in data:
            version = data[data.find(b'v'):data.find(b'v')+20].decode('ascii', errors='ignore')
            print(f"[+] .NET Framework version: {version}")

        return True
    except Exception as e:
        print(f"Error analyzing PE: {e}")
        return False

def use_monodis(exe_path):
    """Try using monodis to disassemble if available"""
    try:
        result = subprocess.run(
            ["monodis", exe_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            output_file = "tk11_monodis.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f"[+] Disassembly saved to {output_file}")
            return True
    except:
        pass
    return False

def create_dnspy_automation_script():
    """Create a C# script that can be run in dnSpy to automate analysis"""

    script = '''// dnSpy Automation Script
// Paste this into dnSpy's Script tab and run
using System;
using System.Linq;
using dnSpy.Contracts.Scripting;

public class FindValidation {
    public void Execute(IScriptGlobals globals) {
        var asm = globals.LoadedAssemblies.FirstOrDefault();
        if (asm == null) {
            Console.WriteLine("No assembly loaded");
            return;
        }

        Console.WriteLine("Searching for validation methods...");

        foreach (var type in asm.GetTypes()) {
            foreach (var method in type.GetMethods()) {
                var body = method.Body;
                if (body != null) {
                    var il = body.ToString();
                    if (il.Contains("File version is Wrong") ||
                        il.Contains("文件版本错误")) {
                        Console.WriteLine($"Found in: {type.FullName}.{method.Name}");
                        Console.WriteLine($"Method: {method}");
                    }
                }
            }
        }
    }
}
'''

    with open("dnspy_automation_script.cs", 'w', encoding='utf-8') as f:
        f.write(script)

    print("[+] Created dnspy_automation_script.cs")
    return True

def manual_hex_search(exe_path):
    """Search for specific byte patterns that might indicate validation code"""
    print("[*] Searching for validation patterns in binary...")

    try:
        with open(exe_path, 'rb') as f:
            data = f.read()

        # Search for the error message
        error_msg_utf16 = "文件版本错误".encode('utf-16le')
        error_msg_ascii = b"File version is Wrong"

        positions = []

        offset = data.find(error_msg_utf16)
        if offset != -1:
            print(f"[+] Found UTF-16 error message at offset: 0x{offset:08X}")
            positions.append(('utf-16', offset))

        offset = data.find(error_msg_ascii)
        if offset != -1:
            print(f"[+] Found ASCII error message at offset: 0x{offset:08X}")
            positions.append(('ascii', offset))

        # Search for common validation patterns
        # CRC32 polynomial
        crc_patterns = [
            b'\xDB\x71\x0E\xED',  # CRC32 polynomial (little-endian)
            b'\xED\x0E\x71\xDB',  # CRC32 polynomial (big-endian)
        ]

        for i, pattern in enumerate(crc_patterns):
            offset = data.find(pattern)
            if offset != -1:
                print(f"[+] Found CRC pattern {i} at offset: 0x{offset:08X}")

        return positions

    except Exception as e:
        print(f"Error in hex search: {e}")
        return []

def generate_report(exe_path):
    """Generate comprehensive analysis report"""

    print("\n" + "="*80)
    print("TK11.exe .NET Assembly Analysis Report")
    print("="*80 + "\n")

    # 1. Extract strings
    strings = extract_strings_from_exe(exe_path)
    print(f"[*] Extracted {len(strings)} unique strings")

    # 2. Find validation-related strings
    validation_strings = find_validation_related_strings(strings)
    print(f"[*] Found {len(validation_strings)} validation-related strings:")
    for s in validation_strings[:20]:  # Show first 20
        print(f"    - {s}")
    if len(validation_strings) > 20:
        print(f"    ... and {len(validation_strings) - 20} more")

    # 3. Analyze PE structure
    analyze_pe_structure(exe_path)

    # 4. Hex search for error messages
    positions = manual_hex_search(exe_path)

    # 5. Try alternative tools
    print("\n[*] Attempting to use alternative decompilation tools...")
    if analyze_with_ilspy(exe_path):
        print("[+] ILSpy decompilation successful - check tk11_decompiled.cs")
    else:
        print("[-] ILSpy not available")

    if use_monodis(exe_path):
        print("[+] monodis disassembly successful - check tk11_monodis.txt")
    else:
        print("[-] monodis not available")

    # 6. Create automation script
    create_dnspy_automation_script()

    # 7. Save full report
    report = {
        'total_strings': len(strings),
        'validation_strings': validation_strings,
        'error_message_positions': positions,
        'all_strings': strings
    }

    with open('tk11_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n[+] Full report saved to: tk11_analysis_report.json")

    # 8. Next steps
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. MANUAL ANALYSIS WITH dnSpy:
   - Run: dnSpy/dnSpy.exe
   - Open: TK11.exe
   - Search for: "File version is Wrong" (Ctrl+Shift+K)
   - Analyze the method that contains this string
   - Look for validation/checksum calculation code

2. USE THE AUTOMATION SCRIPT:
   - Open dnSpy
   - Load TK11.exe
   - Go to Script tab
   - Load: dnspy_automation_script.cs
   - Run it to find validation methods automatically

3. ALTERNATIVE: Try ILSpy GUI
   - Download from: https://github.com/icsharpcode/ILSpy
   - Open TK11.exe
   - Search for the error message
   - Export the relevant class to C# code

4. ONCE YOU FIND THE VALIDATION CODE:
   - Take a screenshot or copy the full method
   - Share it and I can help you:
     a) Understand the checksum algorithm
     b) Implement it in Python
     c) Patch the firmware with correct checksums
     OR
     d) Patch TK11.exe to skip validation entirely
""")

    print("\n[*] Analysis complete!")

def main():
    exe_path = "TK11.exe"

    if not os.path.exists(exe_path):
        print(f"ERROR: {exe_path} not found!")
        return

    generate_report(exe_path)

if __name__ == "__main__":
    main()