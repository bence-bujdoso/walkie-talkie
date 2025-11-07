// DEBUG VERSION: toolStripButton4_Click with extensive logging
// Replace the existing method in TK11.exe with this version
// Each MessageBox will help identify where execution stops

private void toolStripButton4_Click(object sender, EventArgs e)
{
    login login = new login();
    main.password_mode = "eng_mode";
    login.ShowDialog();

    MessageBox.Show("DEBUG A: After login.ShowDialog()");

    if (main.gEngineerMode)
    {
        MessageBox.Show("DEBUG B: Inside gEngineerMode block");

        if (!main.IsHideParamTree)
        {
            main.IsHideParamTree = true;
            main.tn.Nodes.Add(this.GetLang("Hide_param"), this.GetLang("Hide_param"), 2, 2);
            MessageBox.Show("DEBUG C: Hide Param added");
        }
        else
        {
            MessageBox.Show("DEBUG C-ALT: Hide Param already exists");
        }

        MessageBox.Show("DEBUG D: About to start test write");

        try
        {
            MessageBox.Show("DEBUG E: Inside try block");

            // Check if ComPort.Instance exists
            if (ComPort.Instance == null)
            {
                MessageBox.Show("ERROR: ComPort.Instance is NULL!");
                return;
            }

            MessageBox.Show("DEBUG F: ComPort.Instance exists");

            // Try to open COM port
            bool portOpened = ComPort.Instance.Open();

            MessageBox.Show($"DEBUG G: ComPort.Open() returned: {portOpened}");

            if (portOpened)
            {
                MessageBox.Show("DEBUG H: COM port opened successfully");

                try
                {
                    // Prepare test value
                    byte[] testValue = new byte[] { 0x17 };

                    MessageBox.Show("DEBUG I: About to call Write()");

                    // Call Write function
                    bool success = protocol_struct.Write(0x314D, testValue, 1);

                    MessageBox.Show($"DEBUG J: Write() returned: {success}");

                    // Close COM port
                    ComPort.Instance.Close();

                    MessageBox.Show("DEBUG K: COM port closed");

                    if (success)
                    {
                        MessageBox.Show(
                            "✅ TEST WRITE COMPLETE!\n\n" +
                            "Wrote 0x17 to config address 0x314D\n\n" +
                            "Now test USB TX on K38 channel!\n" +
                            "If still shows DISABLE, we need to write to firmware flash instead.",
                            "Success"
                        );
                    }
                    else
                    {
                        MessageBox.Show(
                            "⚠️ WRITE FAILED\n\n" +
                            "protocol_struct.Write() returned false\n" +
                            "Radio may have rejected the write.",
                            "Write Failed"
                        );
                    }
                }
                catch (Exception writeEx)
                {
                    MessageBox.Show($"EXCEPTION during write: {writeEx.Message}\n\n{writeEx.StackTrace}");
                    ComPort.Instance.Close();
                }
            }
            else
            {
                MessageBox.Show(
                    "⚠️ COM PORT FAILED TO OPEN\n\n" +
                    "Possible reasons:\n" +
                    "- Radio not connected\n" +
                    "- Port already open\n" +
                    "- Wrong COM port selected\n\n" +
                    "Try connecting radio first, then click Eng Mode button.",
                    "COM Port Error"
                );
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"EXCEPTION in try block:\n\n" +
                $"Message: {ex.Message}\n\n" +
                $"Type: {ex.GetType().Name}\n\n" +
                $"StackTrace: {ex.StackTrace}",
                "Exception Caught"
            );
        }

        MessageBox.Show("DEBUG L: End of gEngineerMode block");
    }
    else
    {
        MessageBox.Show("DEBUG: gEngineerMode is FALSE - password may have failed");
    }

    MessageBox.Show("DEBUG M: End of toolStripButton4_Click");
}
