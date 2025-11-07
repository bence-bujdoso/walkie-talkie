// TK11 Memory Scanner - Find TX Mode Mask in Configuration
// ============================================================
//
// This script uses protocol_struct.Read() to scan configuration memory
// looking for the TX mode mask value (0x03).
//
// HOW TO USE IN dnSpy:
// 1. Open TK11.exe in dnSpy
// 2. Create a new C# script or modify an existing method
// 3. Paste this code
// 4. Run it (or call it from a button click event)
//
// ============================================================

using System;
using System.Windows.Forms;
using K7;

public class MemoryScanner
{
    public static void ScanForTXMask()
    {
        MessageBox.Show("Starting memory scan...");

        // Scan from address 0 to 200000 in configuration memory
        // Looking for value 0x03 (original TX mode mask)

        for (int address = 0; address < 200000; address += 512)
        {
            try
            {
                // Read 512 bytes at this address
                byte[] data = protocol_struct.Read(address, 512);

                if (data != null)
                {
                    // Search for 0x03 in the data
                    for (int i = 0; i < data.Length; i++)
                    {
                        if (data[i] == 0x03)
                        {
                            // Found it! Check surrounding bytes
                            string context = "";
                            int start = Math.Max(0, i - 4);
                            int end = Math.Min(data.Length - 1, i + 4);

                            for (int j = start; j <= end; j++)
                            {
                                if (j == i)
                                    context += $"[{data[j]:X2}] ";
                                else
                                    context += $"{data[j]:X2} ";
                            }

                            MessageBox.Show(
                                $"Found 0x03 at:\n" +
                                $"Address: 0x{(address + i):X} ({address + i})\n" +
                                $"Context: {context}\n\n" +
                                $"Try patching this location!",
                                "TX Mask Found?"
                            );
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                // Skip errors, continue scanning
            }
        }

        MessageBox.Show("Scan complete!");
    }

    public static void PatchAddress(int address, byte newValue)
    {
        try
        {
            // Read current value
            byte[] current = protocol_struct.Read(address, 1);

            if (current != null && current.Length > 0)
            {
                MessageBox.Show($"Current value at 0x{address:X}: 0x{current[0]:X2}");

                // Write new value
                byte[] newData = new byte[] { newValue };
                bool success = protocol_struct.Write(address, newData, 1);

                if (success)
                {
                    MessageBox.Show($"Successfully wrote 0x{newValue:X2} to address 0x{address:X}!");
                }
                else
                {
                    MessageBox.Show("Write failed!");
                }
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error: {ex.Message}");
        }
    }
}

// ============================================================
// USAGE EXAMPLES:
// ============================================================

// To scan for TX mask:
// MemoryScanner.ScanForTXMask();

// To patch a specific address (example):
// MemoryScanner.PatchAddress(0x314D, 0x17);

// Or try different addresses if scan finds them:
// MemoryScanner.PatchAddress(12621, 0x17);  // 0x314D in decimal

// ============================================================
