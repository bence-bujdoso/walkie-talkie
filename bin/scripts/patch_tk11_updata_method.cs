// TK11.exe Patcher - Updata() Method Replacement
// ================================================
//
// INSTRUCTIONS:
// 1. Open TK11.exe in dnSpy
// 2. Navigate to: K7 -> wfm_progress -> Updata()
// 3. Right-click on Updata() -> "Edit Method (C#)..."
// 4. DELETE ALL CODE and replace with the code below
// 5. Click "Compile"
// 6. File -> Save Module -> Save as TK11_PATCHED.exe
//
// ================================================

public void Updata()
{
    string path = Iparse.getchart("path", "program");
    if (protocol_struct.GetUpdataReady())
    {
        byte[] array = null;

        // ⭐ BYPASS LEVEL 1: Try original validation first (conservative)
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

        // Try legacy format if new format failed
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

        // ⭐ BYPASS LEVEL 2: If validation failed, load directly
        if (array == null)
        {
            try
            {
                array = System.IO.File.ReadAllBytes(path);
                wfm_progress.file_ver = "bypass";
                System.Windows.Forms.MessageBox.Show(
                    "Firmware loaded (validation bypassed)\n" +
                    "Size: " + array.Length + " bytes\n" +
                    "Ready to flash!",
                    "TK11 Patched - Bypass Mode",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Information
                );
            }
            catch (Exception ex2)
            {
                System.Windows.Forms.MessageBox.Show(
                    "Error reading file: " + ex2.Message,
                    "TK11 Patched - Error",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Error
                );
                array = null;
            }
        }

        // Flash the firmware
        if (array != null)
        {
            if (this.downloadFileEx(array))
            {
                System.Windows.Forms.MessageBox.Show(this.GetLang("write_success"));
            }
            else
            {
                System.Windows.Forms.MessageBox.Show(this.GetLang("write_fail"));
            }
        }
        else
        {
            System.Windows.Forms.MessageBox.Show("Could not read firmware file");
        }
    }
}
