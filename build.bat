@echo off
echo AI Photo Editor Build Script
echo ============================

echo.
echo Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Cleanup completed.

echo.
echo Building AI Photo Editor executable...
pyinstaller ai-editor.spec

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo You can find your executable in the 'dist' folder.

echo.
echo Testing executable...
if exist "dist\AI-Photo-Editor.exe" (
    echo Executable found: dist\AI-Photo-Editor.exe
    for %%A in ("dist\AI-Photo-Editor.exe") do echo File size: %%~zA bytes
) else if exist "dist\AI-Photo-Editor\AI-Photo-Editor.exe" (
    echo Executable found: dist\AI-Photo-Editor\AI-Photo-Editor.exe
    for %%A in ("dist\AI-Photo-Editor\AI-Photo-Editor.exe") do echo File size: %%~zA bytes
) else (
    echo Warning: Executable not found!
)

echo.
echo Build process completed!
pause
