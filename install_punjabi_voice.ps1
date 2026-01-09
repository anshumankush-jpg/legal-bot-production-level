# PowerShell Script to Install Punjabi Language Pack
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Punjabi Language Pack Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click on PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running as Administrator... OK" -ForegroundColor Green
Write-Host ""

# Function to check Windows version
function Get-WindowsVersion {
    $version = [System.Environment]::OSVersion.Version
    return $version
}

# Function to install language pack
function Install-PunjabiLanguage {
    Write-Host "Installing Punjabi Language Pack..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        # For Windows 10/11
        $windowsVersion = Get-WindowsVersion
        
        if ($windowsVersion.Major -ge 10) {
            Write-Host "Detected Windows 10/11" -ForegroundColor Green
            Write-Host ""
            
            # Install Punjabi language
            Write-Host "Step 1: Installing Punjabi (India) language..." -ForegroundColor Yellow
            
            # Using Windows Language Settings
            $languageTag = "pa-IN"
            
            # Check if already installed
            $installedLanguages = Get-WinUserLanguageList
            $punjabiInstalled = $installedLanguages | Where-Object { $_.LanguageTag -eq $languageTag }
            
            if ($punjabiInstalled) {
                Write-Host "Punjabi language is already installed!" -ForegroundColor Green
            } else {
                Write-Host "Adding Punjabi language..." -ForegroundColor Yellow
                
                # Add Punjabi to language list
                $languageList = Get-WinUserLanguageList
                $languageList.Add($languageTag)
                Set-WinUserLanguageList $languageList -Force
                
                Write-Host "Punjabi language added successfully!" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "Step 2: Installing Speech Components..." -ForegroundColor Yellow
            
            # Install speech components
            try {
                # Download and install speech pack
                $capability = "Language.TextToSpeech~~~pa-IN~0.0.1.0"
                
                Write-Host "Installing Text-to-Speech for Punjabi..." -ForegroundColor Yellow
                Add-WindowsCapability -Online -Name $capability -ErrorAction SilentlyContinue
                
                Write-Host "Speech components installed!" -ForegroundColor Green
            } catch {
                Write-Host "Note: Speech components may need to be installed manually" -ForegroundColor Yellow
            }
            
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  Installation Complete!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next Steps:" -ForegroundColor Cyan
            Write-Host "1. Restart your computer" -ForegroundColor Yellow
            Write-Host "2. Open Windows Settings > Time & Language > Language" -ForegroundColor Yellow
            Write-Host "3. Click on Punjabi > Options" -ForegroundColor Yellow
            Write-Host "4. Download Speech pack if not already downloaded" -ForegroundColor Yellow
            Write-Host "5. Restart your browser" -ForegroundColor Yellow
            Write-Host "6. Test Punjabi voice in the demo page" -ForegroundColor Yellow
            Write-Host ""
            
        } else {
            Write-Host "ERROR: Windows version not supported" -ForegroundColor Red
            Write-Host "This script requires Windows 10 or later" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "ERROR: Installation failed" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install manually using Windows Settings" -ForegroundColor Yellow
        Show-ManualInstructions
    }
}

# Function to show manual installation instructions
function Show-ManualInstructions {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Manual Installation Instructions" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Method 1: Windows Settings (Recommended)" -ForegroundColor Yellow
    Write-Host "1. Press Win + I to open Settings" -ForegroundColor White
    Write-Host "2. Go to Time & Language > Language" -ForegroundColor White
    Write-Host "3. Click 'Add a language'" -ForegroundColor White
    Write-Host "4. Search for 'Punjabi' or 'pa'" -ForegroundColor White
    Write-Host "5. Select 'Punjabi (India)' or 'ਪੰਜਾਬੀ (ਭਾਰਤ)'" -ForegroundColor White
    Write-Host "6. Click 'Install'" -ForegroundColor White
    Write-Host "7. Wait for installation to complete" -ForegroundColor White
    Write-Host "8. Click on Punjabi > Options" -ForegroundColor White
    Write-Host "9. Under Speech, click 'Download'" -ForegroundColor White
    Write-Host "10. Restart your computer" -ForegroundColor White
    Write-Host ""
    Write-Host "Method 2: PowerShell Command" -ForegroundColor Yellow
    Write-Host "Run this command in PowerShell (as Admin):" -ForegroundColor White
    Write-Host '$list = Get-WinUserLanguageList; $list.Add("pa-IN"); Set-WinUserLanguageList $list -Force' -ForegroundColor Cyan
    Write-Host ""
}

# Function to verify installation
function Test-PunjabiInstallation {
    Write-Host ""
    Write-Host "Checking Punjabi installation..." -ForegroundColor Cyan
    Write-Host ""
    
    $languageTag = "pa-IN"
    $installedLanguages = Get-WinUserLanguageList
    $punjabiInstalled = $installedLanguages | Where-Object { $_.LanguageTag -eq $languageTag }
    
    if ($punjabiInstalled) {
        Write-Host "✓ Punjabi language is installed" -ForegroundColor Green
        return $true
    } else {
        Write-Host "✗ Punjabi language is NOT installed" -ForegroundColor Red
        return $false
    }
}

# Main execution
Write-Host "This script will install Punjabi language pack on your system" -ForegroundColor White
Write-Host ""

# Check current installation
$isInstalled = Test-PunjabiInstallation

if ($isInstalled) {
    Write-Host ""
    $response = Read-Host "Punjabi is already installed. Do you want to reinstall? (y/n)"
    if ($response -ne 'y') {
        Write-Host "Installation cancelled" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To test Punjabi voice, open the demo page:" -ForegroundColor Cyan
        Write-Host "legal-bot\tests\voice_settings_demo.html" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 0
    }
}

Write-Host ""
$confirm = Read-Host "Do you want to proceed with installation? (y/n)"

if ($confirm -eq 'y') {
    Install-PunjabiLanguage
    
    Write-Host ""
    Write-Host "Installation process completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: You must restart your computer for changes to take effect!" -ForegroundColor Yellow
    Write-Host ""
    
    $restart = Read-Host "Do you want to restart now? (y/n)"
    if ($restart -eq 'y') {
        Write-Host "Restarting computer in 10 seconds..." -ForegroundColor Yellow
        Write-Host "Press Ctrl+C to cancel" -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        Restart-Computer -Force
    } else {
        Write-Host ""
        Write-Host "Please restart your computer manually" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "Installation cancelled" -ForegroundColor Yellow
    Show-ManualInstructions
}

Write-Host ""
Read-Host "Press Enter to exit"
