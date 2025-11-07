// ALTERNATIVE APPROACH: Write 0x17 during channel DOWNLOAD operation
// This hooks into an operation we KNOW works (user confirmed channels can be downloaded)
//
// Find the function that downloads channels TO the radio
// This is likely in wfm_progress class, probably called something like:
// - DownloadChannels()
// - WriteChannelsToRadio()
// - UpdateRadio()
// - or similar
//
// Look for a function that:
// 1. Opens COM port
// 2. Sends channel data to radio
// 3. Closes COM port
//
// Then add this code AT THE END of that function (after channels written successfully):

// ========================================
// ADD THIS AT THE END OF CHANNEL DOWNLOAD
// ========================================

if (main.gEngineerMode)  // Only execute if Engineering mode enabled
{
    try
    {
        MessageBox.Show(
            "Engineering Mode Active!\n\n" +
            "Will now write 0x17 to address 0x314D\n" +
            "to enable USB TX mode.",
            "Test Write"
        );

        // COM port should already be open from channel download
        // But check to be safe
        if (!ComPort.Instance.IsOpen())
        {
            if (!ComPort.Instance.Open())
            {
                MessageBox.Show("COM port not open! Skipping test write.");
                return;  // or continue with rest of function
            }
        }

        // Write 0x17 to config memory address 0x314D
        byte[] testValue = new byte[] { 0x17 };
        bool success = protocol_struct.Write(0x314D, testValue, 1);

        if (success)
        {
            MessageBox.Show(
                "✅ TEST WRITE SUCCESSFUL!\n\n" +
                "Wrote 0x17 to config address 0x314D\n\n" +
                "Now test USB TX on K38 channel:\n" +
                "1. Turn on radio\n" +
                "2. Select K38 USB channel (27.385 MHz)\n" +
                "3. Press PTT button\n" +
                "4. Check if 'DISABLE' still appears\n\n" +
                "If still disabled, firmware reads from flash, not config.",
                "Write Success"
            );
        }
        else
        {
            MessageBox.Show(
                "⚠️ WRITE FAILED!\n\n" +
                "protocol_struct.Write() returned false\n" +
                "Radio may have rejected the write.",
                "Write Failed"
            );
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show(
            $"Exception during test write:\n\n{ex.Message}",
            "Error"
        );
    }
}

// ========================================
// EXAMPLE: If channel download function looks like this:
// ========================================

/*
private void DownloadToRadio()
{
    // ... existing code to download channels ...

    // Send channel data
    for (int i = 0; i < channels.Length; i++)
    {
        protocol_struct.WriteChannelData(i, channels[i]);
    }

    MessageBox.Show("Channel download complete!");

    // ⭐ ADD THE TEST WRITE CODE HERE ⭐
    if (main.gEngineerMode)
    {
        // ... test write code from above ...
    }

    // Close port and cleanup
    ComPort.Instance.Close();
}
*/

// ========================================
// HOW TO FIND THE RIGHT FUNCTION
// ========================================

/*
1. Look for the button you click to download channels to radio
2. Right-click the button in dnSpy
3. Select "Analyze"
4. Find "Used by" to see what handles the click event
5. Follow to the function that actually writes to radio
6. Add the test write code at the end

OR

1. Search for "protocol_struct.Write" in the codebase
2. See what functions call it
3. Find one that writes channel data
4. Add test write at the end of that function
*/

// ========================================
// ALTERNATIVE: Write during UPLOAD (read from radio)
// ========================================

/*
If you can't find download function, try adding to upload function:

private void UploadFromRadio()
{
    // ... existing code to read channels ...

    MessageBox.Show("Channel upload complete!");

    // ⭐ ADD TEST WRITE HERE ⭐
    if (main.gEngineerMode)
    {
        // COM port already open from upload
        byte[] testValue = new byte[] { 0x17 };
        bool success = protocol_struct.Write(0x314D, testValue, 1);

        if (success)
        {
            MessageBox.Show("Test write successful during upload!");
        }
    }

    ComPort.Instance.Close();
}
*/

// ========================================
// WHY THIS APPROACH WORKS
// ========================================

/*
ADVANTAGES:
✅ COM port guaranteed to be open (channel operation just used it)
✅ Radio guaranteed to be connected (channel operation just worked)
✅ User already knows how to trigger this (load/download channels)
✅ Timing is perfect - right after successful communication

DISADVANTAGES:
⚠️ Only runs when user downloads/uploads channels
⚠️ May run multiple times if user does multiple operations
⚠️ Need to find the right function to modify

SOLUTION TO DISADVANTAGES:
Add a flag to run only once:

public static bool testWriteCompleted = false;

if (main.gEngineerMode && !testWriteCompleted)
{
    // ... do test write ...
    testWriteCompleted = true;  // Only run once
}
*/
