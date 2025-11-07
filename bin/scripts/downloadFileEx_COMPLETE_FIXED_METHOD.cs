// =============================================================================
// COMPLETE FIXED downloadFileEx() METHOD - COPY/PASTE INTO dnSpy
// =============================================================================
//
// This is the complete method with encryption fix applied.
// You can copy this entire method and paste it into dnSpy.
//
// HOW TO USE:
// 1. Open TK11.exe in dnSpy
// 2. Navigate to: K7 -> wfm_progress -> downloadFileEx(byte[] allBuffer)
// 3. Right-click -> "Edit Method (C#)..."
// 4. SELECT ALL and DELETE the existing method body
// 5. COPY and PASTE this entire method below
// 6. Click "Compile"
// 7. File -> Save Module -> Save as TK11_ENCRYPTION_FIXED.exe
//
// =============================================================================

private bool downloadFileEx(byte[] allBuffer)
{
	int num = 1024;
	int i = 0;
	int num2 = 0;
	uint seqNo = 0U;
	bool flag = false;
	try
	{
		num = 256;
		seqNo = this.generateSeqNo();
		int num3 = allBuffer.Length / num;
		num2 = ((allBuffer.Length % num == 0) ? num3 : (num3 + 1));
		byte[] array = new byte[num2 * num];
		Array.Copy(allBuffer, array, allBuffer.Length);
		this.progressBar1.Maximum = num2;

		bool flag2 = false;
		bool bypassedHandshake = false;  // ⭐ ADDED: Track bypass state
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
			bypassedHandshake = true;  // ⭐ ADDED: Mark as bypassed
			MessageBox.Show("Bootloader bypass aktív!", "Level 3");
		}

		Thread.Sleep(500);

		byte[] array2 = new byte[16];
		byte[] array3 = new byte[16];
		for (int j = 0; j < 16; j++)
		{
			array2[j] = Util.updatakey[wfm_progress.seed, j];
			array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
		}

		// ⭐ FIXED: Only modify IV if handshake succeeded
		if (!bypassedHandshake)
		{
			for (i = 0; i < array3.Length; i++)
			{
				byte[] array5 = array3;
				int num4 = i;
				int num5 = num4;
				array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
			}
		}
		// If bypassed, use IV as-is (from updatakey table without XOR)

		array = Util.AESEncrypt(array, array2, array3);
		wfm_progress.addr = 0;

		for (i = 0; i < num2; i++)
		{
			byte[] array4 = new byte[num];
			Array.Copy(array, wfm_progress.addr, array4, 0, num);
			wfm_progress.addr += num;
			flag = protocol_struct.packetFileEx(array4, i, num2, num, seqNo);
			this.backgroundWorker1.ReportProgress(i);
			if (!flag)
			{
				break;
			}
		}
	}
	catch (Exception)
	{
		flag = false;
	}
	return flag;
}

// =============================================================================
// CHANGES MADE:
// =============================================================================
//
// Line ~19: Added "bool bypassedHandshake = false;"
// Line ~37: Added "bypassedHandshake = true;" when bypassing
// Line ~53: Wrapped XOR loop in "if (!bypassedHandshake) { ... }"
//
// That's it! Only 3 lines changed.
//
// =============================================================================
// WHAT THIS FIXES:
// =============================================================================
//
// BEFORE:
// - Bootloader handshake fails
// - Bypass sets flag2 = true (continues)
// - XOR tries to use uninitialized UpdataConnRsp.u8RandCode
// - Wrong encryption keys used
// - Bootloader can't decrypt firmware
// - Result: "Write Fail" ❌
//
// AFTER:
// - Bootloader handshake fails
// - Bypass sets flag2 = true AND bypassedHandshake = true
// - XOR is SKIPPED (uses base IV from updatakey table)
// - Correct predictable encryption keys used
// - Bootloader CAN decrypt firmware
// - Result: "Write Success" ✅ (if firmware format is correct)
//
// =============================================================================
