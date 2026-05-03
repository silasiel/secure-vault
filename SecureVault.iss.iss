[Setup]
AppName=SecureVault
AppVersion=1.0
DefaultDirName={autopf}\SecureVault
DefaultGroupName=SecureVault
OutputDir=installer
OutputBaseFilename=SecureVault_Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=svicon.ico

[Files]
Source: "dist\SecureVault.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\encryptor.exe"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
Name: "{app}\vault"
Name: "{app}\logs"

[Icons]
Name: "{group}\SecureVault"; Filename: "{app}\SecureVault.exe"
Name: "{commondesktop}\SecureVault"; Filename: "{app}\SecureVault.exe"

[Run]
Filename: "{app}\SecureVault.exe"; Description: "Launch SecureVault"; Flags: nowait postinstall skipifsilent