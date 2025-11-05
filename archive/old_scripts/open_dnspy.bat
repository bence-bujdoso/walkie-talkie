@echo off
REM Quick launcher for dnSpy with TK11.exe

echo ================================================================================
echo Opening dnSpy with TK11.exe
echo ================================================================================
echo.
echo Instructions:
echo 1. dnSpy will open with TK11.exe loaded
echo 2. Press Ctrl+Shift+K to search
echo 3. Search for: "File version is Wrong"
echo 4. Navigate to K7.wfm_firmware class
echo 5. Find the validation method
echo 6. Edit it to bypass validation
echo 7. Save as TK11_PATCHED_FINAL.exe
echo.
echo Full instructions in: FINAL_DNSPY_INSTRUCTIONS.md
echo.
pause

start dnSpy\dnSpy.exe TK11.exe

echo.
echo dnSpy launched!
echo Follow the instructions in FINAL_DNSPY_INSTRUCTIONS.md
echo.
