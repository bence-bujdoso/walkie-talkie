// =============================================================================
// OPTION: Skip Encryption When Bypassing Bootloader
// =============================================================================
//
// USE THIS IF:
// - Encryption fix is applied
// - All 8 firmware variants tested
// - All still show "Write Fail"
//
// THEORY:
// When bootloader handshake is bypassed, the bootloader might expect
// UNENCRYPTED firmware instead of encrypted firmware.
//
// This modification skips AES encryption entirely when the bypass is active.
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
		bool bypassedHandshake = false;
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
			bypassedHandshake = true;
			MessageBox.Show("Bootloader bypass aktív! (No encryption)", "Level 3");
		}
		Thread.Sleep(500);

		// ⭐ NEW: Only encrypt if handshake succeeded
		if (!bypassedHandshake)
		{
			byte[] array2 = new byte[16];
			byte[] array3 = new byte[16];
			for (int j = 0; j < 16; j++)
			{
				array2[j] = Util.updatakey[wfm_progress.seed, j];
				array3[j] = Util.updatakey[wfm_progress.seed, j + 16];
			}
			for (i = 0; i < array3.Length; i++)
			{
				byte[] array5 = array3;
				int num4 = i;
				int num5 = num4;
				array5[num5] ^= protocol_struct.UpdataConnRsp.u8RandCode[i];
			}
			array = Util.AESEncrypt(array, array2, array3);
		}
		// If bypassed, skip encryption - send raw firmware

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
// CHANGES FROM CURRENT VERSION:
// =============================================================================
//
// 1. Changed message: "Bootloader bypass aktív! (No encryption)"
// 2. Moved ALL encryption code into: if (!bypassedHandshake) { ... }
// 3. This includes:
//    - Key array creation (array2, array3)
//    - Key initialization from updatakey
//    - XOR loop
//    - AES encryption call
//
// Result: When bypassing, firmware is sent UNENCRYPTED to bootloader
//
// =============================================================================
// WHY THIS MIGHT WORK:
// =============================================================================
//
// Theory 1: Encryption tied to handshake
// - Normal operation: Handshake succeeds → Keys negotiated → Encrypt
// - Bypass operation: No handshake → No key negotiation → No encryption
//
// Theory 2: Bootloader has two modes
// - Secure mode: Requires handshake and encryption
// - Recovery mode: Bypass handshake, accepts raw firmware
//
// Theory 3: Encryption keys still wrong
// - Even with our fix, base keys might not match bootloader expectations
// - Skipping encryption removes this variable entirely
//
// =============================================================================
// TESTING:
// =============================================================================
//
// After applying this modification:
//
// 1. Compile and save as TK11_NO_ENCRYPTION.exe
// 2. Test with minimal firmware first
// 3. If works: Test with other firmware variants
// 4. If fails: Need deeper bootloader protocol analysis
//
// Expected behavior:
// - "Bootloader bypass aktív! (No encryption)" message
// - Progress bar completes
// - Either "Write Success" or "Write Fail"
//
// If "Write Success": Radio restarts and firmware is flashed! 🎉
// If "Write Fail": Bootloader requires something else (format, headers, etc.)
//
// =============================================================================
