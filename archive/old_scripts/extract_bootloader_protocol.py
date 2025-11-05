#!/usr/bin/env python3
"""
Extract TK11 Bootloader Protocol Details
Analyzes TK11.exe to extract the complete packet structure and validation mechanism
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import clr
    clr.AddReference("System.Reflection")
    from System.Reflection import Assembly, BindingFlags
    from System import Type, Byte
except:
    print("ERROR: pythonnet (clr) not available")
    print("Run: pip install pythonnet")
    sys.exit(1)

def analyze_protocol_struct(assembly):
    """Extract protocol_struct class details"""

    print("="*80)
    print("PROTOCOL_STRUCT CLASS ANALYSIS")
    print("="*80)

    # Find protocol_struct class
    protocol_struct_type = None
    for t in assembly.GetTypes():
        if 'protocol_struct' in t.FullName:
            protocol_struct_type = t
            break

    if not protocol_struct_type:
        print("ERROR: protocol_struct class not found!")
        return

    print(f"\n[+] Found: {protocol_struct_type.FullName}\n")

    # Get all fields (constants)
    fields = protocol_struct_type.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance)

    print("\n" + "-"*80)
    print("FIELDS AND CONSTANTS")
    print("-"*80)

    for field in fields:
        print(f"\n{field.Name}")
        print(f"  Type: {field.FieldType}")
        print(f"  Static: {field.IsStatic}, Literal: {field.IsLiteral}")

        # Try to get value if it's a constant
        if field.IsStatic and field.IsLiteral:
            try:
                value = field.GetRawConstantValue()
                print(f"  VALUE: {value} (0x{value:X} if applicable)")
            except:
                pass
        elif field.IsStatic:
            try:
                value = field.GetValue(None)
                if value is not None:
                    print(f"  VALUE: {value}")
            except:
                pass

    # Get all methods
    methods = protocol_struct_type.GetMethods(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance)

    print("\n" + "-"*80)
    print("METHODS")
    print("-"*80)

    for method in methods:
        if method.Name.startswith('get_') or method.Name.startswith('set_') or method.Name.startswith('.'):
            continue  # Skip property accessors and constructors

        print(f"\n{method.Name}()")
        print(f"  Returns: {method.ReturnType}")

        params = method.GetParameters()
        if len(params) > 0:
            print("  Parameters:")
            for p in params:
                print(f"    - {p.ParameterType} {p.Name}")

    # Look for nested types (like MSG_* structures)
    nested_types = protocol_struct_type.GetNestedTypes(BindingFlags.Public | BindingFlags.NonPublic)

    if len(nested_types) > 0:
        print("\n" + "-"*80)
        print("NESTED MESSAGE STRUCTURES")
        print("-"*80)

        for nested in nested_types:
            print(f"\n{nested.Name}")

            # Get fields of this structure
            struct_fields = nested.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)

            total_size = 0
            for sf in struct_fields:
                size_str = ""

                # Try to estimate field size
                if sf.FieldType.Name == "Byte":
                    size_str = "[1 byte]"
                    total_size += 1
                elif sf.FieldType.Name == "UInt16" or sf.FieldType.Name == "Int16":
                    size_str = "[2 bytes]"
                    total_size += 2
                elif sf.FieldType.Name == "UInt32" or sf.FieldType.Name == "Int32":
                    size_str = "[4 bytes]"
                    total_size += 4
                elif sf.FieldType.Name == "Byte[]":
                    size_str = "[array]"

                print(f"  + {sf.Name}: {sf.FieldType.Name} {size_str}")

            if total_size > 0:
                print(f"  TOTAL SIZE (approx): {total_size} bytes (0x{total_size:X})")

def main():
    print("="*80)
    print("TK11 BOOTLOADER PROTOCOL EXTRACTION")
    print("="*80)
    print()

    exe_path = Path("E:/AI/tk11/TK11.exe")

    if not exe_path.exists():
        print(f"ERROR: {exe_path} not found!")
        return 1

    print(f"[*] Loading assembly: {exe_path}")

    try:
        assembly = Assembly.LoadFrom(str(exe_path))
        print("[+] Assembly loaded successfully\n")
    except Exception as e:
        print(f"ERROR: Failed to load assembly: {e}")
        return 1

    # Analyze protocol_struct class
    analyze_protocol_struct(assembly)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
