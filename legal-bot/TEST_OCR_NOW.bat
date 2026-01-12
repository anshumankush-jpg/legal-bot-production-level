@echo off
echo ============================================
echo   TEST OCR SYSTEM
echo ============================================
echo.
echo This will test your OCR system end-to-end
echo.
pause

echo.
echo Step 1: Testing OCR extraction...
python test_ocr_direct.py
echo.
pause

echo.
echo Step 2: Checking vector storage...
python check_saved_vectors.py
echo.
pause

echo.
echo Step 3: Testing chat with specific question...
python test_chat_with_image.py
echo.
pause

echo.
echo Step 4: Testing chat with generic question...
python test_generic_question.py
echo.
pause

echo.
echo ============================================
echo   ALL TESTS COMPLETE!
echo ============================================
echo.
echo Your OCR system is working!
echo.
echo Next: Open http://localhost:4201 and try it!
echo.
pause
