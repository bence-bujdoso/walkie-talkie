// TK11.exe Patcher - downloadFileEx() Method Patch (LEVEL 3)
// =============================================================
//
// ⚠️  ONLY USE THIS IF LEVEL 1 & 2 BYPASS DIDN'T WORK! ⚠️
//
// This patches the bootloader handshake check to force success
// even if the bootloader rejects the firmware format.
//
// INSTRUCTIONS:
// 1. Open TK11_PATCHED.exe (the one you already patched) in dnSpy
// 2. Navigate to: K7 -> wfm_progress -> downloadFileEx(byte[] allBuffer)
// 3. Right-click -> "Edit Method (C#)..."
// 4. Find this code (around line 20-30):
//
//    if (!flag2)
//    {
//        return false;
//    }
//
// 5. CHANGE IT TO:
//
//    if (!flag2)
//    {
//        flag2 = true;  // ⭐ BYPASS: Force success
//        System.Windows.Forms.MessageBox.Show(
//            "Bootloader handshake bypassed",
//            "TK11 Level 3 Bypass",
//            System.Windows.Forms.MessageBoxButtons.OK,
//            System.Windows.Forms.MessageBoxIcon.Information
//        );
//    }
//
// 6. Click "Compile"
// 7. File -> Save Module -> Save as TK11_PATCHED_LEVEL3.exe
//
// =============================================================
//
// ALTERNATIVE: Comment out the return statement:
//
//    if (!flag2)
//    {
//        // return false;  // ⭐ BYPASSED
//    }
//
// =============================================================
