/*
 * TK11.exe Patch Instructions
 *
 * This file contains the C# code to patch TK11.exe using dnSpy
 * to bypass firmware validation.
 *
 * INSTRUCTIONS:
 * 1. Backup original TK11.exe first!
 * 2. Open TK11.exe in dnSpy
 * 3. Navigate to: TK11 → K7 → wfm_progress
 * 4. Find method: Updata()
 * 5. Right-click → Edit Method (C#)...
 * 6. Replace ENTIRE method with code below
 * 7. Click "Compile"
 * 8. File → Save Module
 * 9. Save as TK11_PATCHED.exe
 */

// =============================================================================
// LEVEL 2 BYPASS - Direct Firmware Loading (RECOMMENDED)
// =============================================================================
// This completely bypasses firmware validation and loads any file directly.
// Use this version for maximum compatibility with patched firmware.
// =============================================================================

public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // ⭐ BYPASS: Load firmware directly without validation
        try
        {
            array = System.IO.File.ReadAllBytes(path);
            wfm_progress.file_ver = "direct";
            MessageBox.Show("Firmware loaded (validation bypassed)");
        }
        catch (Exception ex)
        {
            MessageBox.Show("Error reading file: " + ex.Message);
            array = null;
        }

        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            MessageBox.Show("Could not read firmware file");
        }
    }
}

// =============================================================================
// ALTERNATIVE: LEVEL 1 BYPASS - Conservative (Try Original First)
// =============================================================================
// Uncomment below if you prefer a more conservative approach that tries
// the original validation first, then falls back to direct loading.
// =============================================================================

/*
public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;
        try
        {
            array = this.PareUpdataFile(path);
            wfm_progress.file_ver = "new";
        }
        catch (Exception ex)
        {
            array = null;
            wfm_progress.file_ver = "old";
        }
        if (array == null)
        {
            try
            {
                array = this.PareUpdataFile1(path);
            }
            catch (Exception ex)
            {
                array = null;
            }
        }
        // ⭐ BYPASS: If validation failed, load directly
        if (array == null)
        {
            try
            {
                array = System.IO.File.ReadAllBytes(path);
                wfm_progress.file_ver = "bypass";
            }
            catch (Exception ex2)
            {
                array = null;
            }
        }
        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            MessageBox.Show(this.GetLang("文件版本错误"));
        }
    }
}
*/

// =============================================================================
// VERIFICATION
// =============================================================================
// After patching:
// 1. TK11_PATCHED.exe should be ~373 KB (original is ~382 KB)
// 2. Open TK11_PATCHED.exe
// 3. Try to load: patched_firmware_final\TK11_PATCHED_v3_minimal.bin
// 4. You should see "Firmware loaded (validation bypassed)" message
// 5. NO "File version is Wrong" (文件版本错误) error!
//
// If you still get the error, make sure you're running TK11_PATCHED.exe
// and not the original TK11.exe!
// =============================================================================

// =============================================================================
// TROUBLESHOOTING
// =============================================================================
//
// "Compilation failed"
//   → Check syntax: all { } match, all ; present
//   → Try copying code again carefully
//   → Use LEVEL 1 bypass (simpler code)
//
// "Still getting File version is Wrong"
//   → Make sure you saved the module in dnSpy
//   → Make sure you're running TK11_PATCHED.exe
//   → Check file size: patched should be ~373 KB
//
// "Write fail immediately"
//   → This is a different issue (bootloader rejecting firmware format)
//   → Try different firmware variants (v1, v2, v3, v4)
//   → Consider LEVEL 3 bypass (see COMPLETE_TK11_BYPASS.md)
//
// =============================================================================