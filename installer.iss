; P2P Chat Application - Inno Setup Script
; ==========================================
; This script creates a Windows installer
;
; Prerequisites:
; 1. Build the executable first: python build.py
; 2. Download Inno Setup: https://jrsoftware.org/isinfo.php
; 3. Open this file in Inno Setup and compile

#define MyAppName "P2P Chat"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Network Programming Project"
#define MyAppExeName "P2P_Chat.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=P2P_Chat_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[Code]
// Optional: Add firewall rules during installation
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Add firewall rule for TCP
    Exec('netsh', 'advfirewall firewall add rule name="P2P Chat TCP" dir=in action=allow protocol=tcp localport=5000', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    // Add firewall rule for UDP
    Exec('netsh', 'advfirewall firewall add rule name="P2P Chat UDP" dir=in action=allow protocol=udp localport=5001', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  ResultCode: Integer;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    // Remove firewall rules
    Exec('netsh', 'advfirewall firewall delete rule name="P2P Chat TCP"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec('netsh', 'advfirewall firewall delete rule name="P2P Chat UDP"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
