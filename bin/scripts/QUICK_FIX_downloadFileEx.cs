// =============================================================================
// TK11.exe CRITICAL FIX - downloadFileEx() Encryption Issue
// =============================================================================
//
// ⚠️  THIS FIX IS REQUIRED FOR SUCCESSFUL FIRMWARE FLASHING!
//
// PROBLEM: When bootloader handshake is bypassed, encryption uses
//          uninitialized keys, causing bootloader to reject firmware.
//
// SOLUTION: Skip IV modification when bypassing, use base keys instead.
//
// =============================================================================
// INSTRUCTIONS FOR dnSpy:
// =============================================================================
//
// 1. Open TK11.exe in dnSpy
// 2. Navigate to: K7 -> wfm_progress -> downloadFileEx(byte[] allBuffer)
// 3. Right-click -> "Edit Method (C#)..."
// 4. Make TWO changes (see below)
// 5. Click "Compile"
// 6. File -> Save Module -> Save as TK11_ENCRYPTION_FIXED.exe
//
// =============================================================================

// CHANGE #1: Add bypass tracking variable
// ----------------------------------------------------------------------------
// FIND (around line 18-30):

bool flag2 = false;
wfm_progress.seed = new Random().Next(0, 16);

for (i = 0; i < 5; i++)
{
    try
    {
        flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
    }
    catch (Exception)
    {
        flag2 = false;
    }
    if (protocol_struct.boot_version == "4.00.03" || flag2)
    {
        break;
    }
}

if (!flag2)
{
    flag2 = true;
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}

// REPLACE WITH:

bool flag2 = false;
bool bypassedHandshake = false;  // ⭐ ADD THIS LINE
wfm_progress.seed = new Random().Next(0, 16);

for (i = 0; i < 5; i++)
{
    try
    {
        flag2 = protocol_struct.SendUpdataConnectReq(protocol_struct.boot_version, wfm_progress.seed);
    }
    catch (Exception)
    {
        flag2 = false;
    }
    if (protocol_struct.boot_version == "4.00.03" || flag2)
    {
        break;
    }
}

if (!flag2)
{
    flag2 = true;
    bypassedHandshake = true;  // ⭐ ADD THIS LINE
    MessageBox.Show("Bootloader bypass aktív!", "Level 3");
}

// =============================================================================

// CHANGE #2: Skip IV modification when bypassing
// ----------------------------------------------------------------------------
// FIND (around line 40-50):

for (i = 0; i < array3.Length; i++)
{
    byte[] array5 = array3;
    int num4 = i;
    int num5 = num4;
    array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
}

array = Util.AESEncrypt(array, array2, array3);

// REPLACE WITH:

if (!bypassedHandshake)  // ⭐ ADD THIS CONDITION
{
    for (i = 0; i < array3.Length; i++)
    {
        byte[] array5 = array3;
        int num4 = i;
        int num5 = num4;
        array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
    }
}

array = Util.AESEncrypt(array, array2, array3);

// =============================================================================
// SUMMARY OF CHANGES:
// =============================================================================
//
// 1. Added: bool bypassedHandshake = false;
// 2. Set it to true when bypassing: bypassedHandshake = true;
// 3. Wrapped XOR loop in condition: if (!bypassedHandshake) { ... }
//
// That's it! Only 3 lines added/changed.
//
// =============================================================================
// WHY THIS WORKS:
// =============================================================================
//
// Normal operation:
// - Handshake succeeds → bypassedHandshake = false
// - XOR loop runs → IV modified with bootloader random code
// - Firmware encrypted with negotiated keys
// - Bootloader can decrypt ✅
//
// Bypass operation:
// - Handshake fails → bypassedHandshake = true
// - XOR loop SKIPPED → IV uses base keys from updatakey table
// - Firmware encrypted with predictable keys
// - Bootloader can decrypt ✅
//
// =============================================================================
// TESTING:
// =============================================================================
//
// After applying this fix:
//
// 1. Copy TK11_ENCRYPTION_FIXED.exe to TK11.exe
// 2. Open TK11.exe
// 3. Load any firmware variant (e.g., v1_simple_crc16xmodem.bin)
// 4. Connect radio and click "Write"
// 5. You should see "Bootloader bypass aktív!" message
// 6. Expected: "Write Success" instead of "Write Fail"
// 7. If success: Radio restarts and firmware is flashed! 🎉
//
// =============================================================================
