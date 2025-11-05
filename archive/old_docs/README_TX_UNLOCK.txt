================================================================================
TK11.DAT TX UNLOCK - README
================================================================================

QUICK START GUIDE

This directory contains a complete reverse engineering analysis of the TK11.dat
radio configuration file, including TX (transmit) lock mechanism identification
and unlock tools.

================================================================================
WHAT'S IN THIS PACKAGE
================================================================================

DOCUMENTATION FILES:
--------------------
1. README_TX_UNLOCK.txt (this file)
   - Quick start guide
   - File index
   - Usage instructions

2. ANALYSIS_SUMMARY.txt
   - Executive summary of findings
   - Key discoveries
   - Verification results

3. TX_UNLOCK_REPORT.md
   - Complete technical documentation
   - Detailed field descriptions
   - Channel record layout
   - Safety warnings

4. QUICK_REFERENCE.txt
   - Fast lookup guide
   - Visual diagrams
   - Common procedures
   - Offset calculator

DATA FILES:
-----------
1. TK11.dat (ORIGINAL - DO NOT MODIFY)
   - Original configuration file
   - Keep as backup
   - Size: 880,640 bytes

2. TK11_TX_UNLOCKED.dat (MODIFIED)
   - TX-unlocked version
   - 40 channels unlocked
   - Ready to use (test first!)
   - Size: 880,640 bytes

ANALYSIS SCRIPTS:
-----------------
1. analyze_tk11.py
   - Initial file analysis
   - Pattern detection
   - String extraction
   - Frequency scanning

2. detailed_channel_analysis.py
   - Complete channel parser
   - TX flag analyzer
   - Automatic unlock patcher
   - Creates TK11_TX_UNLOCKED.dat

3. refined_analysis.py
   - Field-by-field breakdown
   - First N records viewer
   - Detailed structure analysis

4. verify_unlock.py
   - Compare original vs unlocked
   - Verify all changes
   - Show before/after hex dumps

================================================================================
QUICK START - 3 STEPS
================================================================================

STEP 1: UNDERSTAND WHAT WAS FOUND
----------------------------------
   Read: ANALYSIS_SUMMARY.txt

   KEY FINDING:
   - TX lock is controlled by Byte 22 in each 64-byte channel record
   - 0xFF = TX enabled
   - 0x00 = TX disabled
   - 40 channels were locked (now unlocked)

STEP 2: VERIFY THE UNLOCKED FILE
---------------------------------
   Run: python verify_unlock.py

   Expected output:
   - 40 bytes changed
   - 40 channels modified
   - All changes at byte 22
   - File integrity: GOOD

STEP 3: USE THE UNLOCKED FILE
------------------------------
   1. Backup original TK11.dat
   2. Load TK11_TX_UNLOCKED.dat into programming software
   3. Upload to radio
   4. Test with DUMMY LOAD first
   5. Only transmit on legal frequencies

================================================================================
DETAILED USAGE
================================================================================

TO RE-CREATE THE UNLOCKED FILE:
--------------------------------
   python detailed_channel_analysis.py

   This will:
   - Scan all 13,760 channel records
   - Find channels with valid frequencies
   - Set Byte 22 = 0xFF for all active channels
   - Output: TK11_TX_UNLOCKED.dat

TO VERIFY MODIFICATIONS:
-------------------------
   python verify_unlock.py

   Shows:
   - Which channels were modified
   - Exact byte changes (before/after)
   - Frequency of each modified channel
   - Visual hex dump comparison

TO ANALYZE ORIGINAL FILE:
--------------------------
   python analyze_tk11.py
   python refined_analysis.py

   Shows:
   - Complete file structure
   - All channel details
   - Hex dumps
   - Pattern analysis

================================================================================
FILE FORMAT QUICK REFERENCE
================================================================================

RECORD SIZE: 64 bytes per channel
TOTAL RECORDS: 13,760 channels
FILE SIZE: 880,640 bytes

CHANNEL OFFSET CALCULATION:
   Offset = Channel_Number × 64
   Example: Channel 1044 = 1044 × 64 = 66,816 = 0x10500

TX PERMIT BYTE:
   Location: Byte 22 (offset +0x16 from record start)
   Values: 0xFF = enabled, 0x00 = disabled

FREQUENCY FORMAT:
   Location: Bytes 0-3
   Format: 32-bit little-endian integer in Hertz
   Example: 0x0029C944 = 2,738,500 Hz = 2.7385 MHz

CHANNEL NAME:
   Location: Bytes 24-39 (16 bytes)
   Format: ASCII, null-padded
   Max: 15 characters + null terminator

================================================================================
LOCKED CHANNELS IDENTIFIED
================================================================================

Total: 40 channels with TX disabled

Frequency Ranges:
- 58-108 MHz (FM broadcast band) - ILLEGAL TO TRANSMIT
- ~1850 MHz (cellular/restricted) - ILLEGAL TO TRANSMIT

Sample Channels:
   Channel 1044: 58.0000 MHz  (FM broadcast)
   Channel 1046: 76.0000 MHz  (FM broadcast)
   Channel 1048: 100.0000 MHz (FM broadcast)
   Channel 1088: 67.2404 MHz
   Channels 1408-1470: 1851.8762 MHz (cellular)
   Channel 1604: 76.0000 MHz  (FM broadcast)

All have been unlocked in TK11_TX_UNLOCKED.dat

================================================================================
SAFETY AND LEGAL WARNINGS
================================================================================

CRITICAL - READ BEFORE USING:

1. LEGAL COMPLIANCE
   - Unlocking TX does NOT make transmission legal
   - FM broadcast (88-108 MHz): ILLEGAL in most countries
   - Cellular bands: ILLEGAL, severe penalties
   - Only transmit on authorized frequencies

2. TESTING REQUIREMENTS
   - ALWAYS test with dummy load first
   - NEVER test on antenna initially
   - Verify frequency accuracy
   - Monitor with second radio/spectrum analyzer

3. AUTHORIZATION
   - Amateur radio: Need valid license
   - Business/commercial: Need FCC license or equivalent
   - Public service: Need proper authorization
   - Broadcast frequencies: NEVER TRANSMIT

4. PENALTIES FOR ILLEGAL TRANSMISSION
   - Heavy fines ($10,000+ in USA)
   - Criminal prosecution possible
   - Equipment confiscation
   - Loss of radio licenses

5. WARRANTY
   - Modification may void warranty
   - Use at your own risk
   - No guarantee of functionality

YOU ARE RESPONSIBLE for legal compliance and proper operation!

================================================================================
TECHNICAL DETAILS
================================================================================

Discovery Method:
- Binary pattern analysis
- Record structure identification (64-byte records)
- Statistical comparison of locked vs unlocked channels
- Byte-by-byte flag analysis

Verification:
- 40 channels identified with TX disabled
- All set to byte value 0x00 or restricted (0x08, 0xBF)
- Modified to 0xFF in unlocked version
- File integrity verified (size unchanged, targeted modifications only)

Confidence Level: HIGH
- Clear pattern identified
- Consistent across all locked channels
- Logical frequency ranges (regulatory compliance)
- Successful modification and verification

================================================================================
TROUBLESHOOTING
================================================================================

PROBLEM: Script won't run
SOLUTION: Install Python 3, ensure TK11.dat is in same directory

PROBLEM: "File not found" error
SOLUTION: Check file path in script, verify TK11.dat exists

PROBLEM: Radio won't accept modified file
SOLUTION: Verify file size (must be 880,640 bytes), try re-creating

PROBLEM: TX still doesn't work
SOLUTION:
   - Radio may have hardware lock
   - Check radio settings/menus
   - Verify frequency is not out of radio's TX range
   - Some radios need additional software settings

PROBLEM: Programming software errors
SOLUTION:
   - Try loading original first, then modified
   - Update programming software
   - Check cable connection
   - Radio may reject modified config

================================================================================
FOR MORE INFORMATION
================================================================================

Complete Technical Documentation:
   TX_UNLOCK_REPORT.md - Full analysis report with field descriptions

Quick Reference:
   QUICK_REFERENCE.txt - Diagrams and procedures

Analysis Summary:
   ANALYSIS_SUMMARY.txt - Executive summary and findings

Python Scripts:
   All include detailed comments explaining the analysis

================================================================================
REVISION HISTORY
================================================================================

2024-XX-XX: Initial reverse engineering analysis
   - File format identified (64-byte records)
   - TX lock mechanism discovered (Byte 22)
   - 40 locked channels found and unlocked
   - Complete documentation created

================================================================================
CREDITS AND DISCLAIMER
================================================================================

Analysis Type: Binary reverse engineering
Tools Used: Python 3, binary analysis techniques
Radio Model: TK11 (inferred from filename)

DISCLAIMER:
This analysis is provided for educational and authorized use only.
The author is not responsible for:
- Illegal use of unlocked radio capabilities
- Damage to equipment from modifications
- Regulatory violations or penalties
- Loss of warranty or radio functionality

Always ensure you have proper authorization before transmitting on any
frequency. Comply with all local, national, and international regulations.

================================================================================
CONTACT AND SUPPORT
================================================================================

For questions about the analysis methodology, refer to the technical
documentation included in this package.

For radio-specific questions, consult:
- Radio manufacturer documentation
- Amateur radio communities (if applicable)
- Licensed radio technicians
- Regulatory authorities (FCC, etc.)

Remember: This tool unlocks the software TX lock, but does not grant
legal permission to transmit on restricted frequencies.

================================================================================
END OF README
================================================================================

Ready to use? Follow the QUICK START guide above.
Questions? Read the ANALYSIS_SUMMARY.txt and TX_UNLOCK_REPORT.md
Safety first? Read the WARNINGS section carefully!

Good luck and operate responsibly!

================================================================================
