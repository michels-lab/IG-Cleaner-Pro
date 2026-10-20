; Insta Cleaner Pro Developer Edition — independently installed diagnostic + opt-in real action QA twin.
; Same full executable and UI; --developer is mandatory on every entry point.
; Different AppId/installation directory avoids replacing the public app.
#ifndef MyAppVersion
 #error MyAppVersion is required.
#endif
#ifndef PayloadDir
 #error PayloadDir is required.
#endif

[Setup]
AppId={{A8B19C6D-6C31-45B4-92DF-4B4DB20CB7DA}
AppName=Insta Cleaner Pro Developer Edition
AppVerName=Insta Cleaner Pro Developer Edition v{#MyAppVersion}
AppVersion={#MyAppVersion}
AppPublisher=Michel's Lab
AppPublisherURL=https://github.com/michels-lab
AppSupportURL=https://github.com/michels-lab/IG-Cleaner-Pro/issues
AppUpdatesURL=https://github.com/michels-lab/IG-Cleaner-Pro/releases
VersionInfoCompany=Michel's Lab
VersionInfoProductName=Insta Cleaner Pro Developer Edition
VersionInfoDescription=Local robot audit, notes and explicitly consented real action tests
DefaultDirName={localappdata}\Programs\Michel's Lab\Insta Cleaner Pro Developer
DefaultGroupName=Insta Cleaner Pro Developer
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=..\..\LICENSE.txt
SetupIconFile=..\..\desktop\assets\ig-cleaner-pro\official-app-icon.ico
UninstallDisplayIcon={app}\InstaCleanerPro.exe
OutputDir=..\..\artifacts
OutputBaseFilename=IG-Cleaner-Pro-Windows-Developer-Setup-v{#MyAppVersion}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
SetupLogging=yes
CloseApplications=yes
RestartApplications=no
Uninstallable=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "{#PayloadDir}\InstaCleanerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\BUILD-INFO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\EXECUTABLE-SHA256.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\chrome-extension\*"; DestDir: "{app}\chrome-extension"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{userprograms}\Insta Cleaner Pro Developer\Insta Cleaner Pro - Developer Edition"; Filename: "{app}\InstaCleanerPro.exe"; Parameters: "--developer"; IconFilename: "{app}\InstaCleanerPro.exe"

[Run]
Filename: "{app}\InstaCleanerPro.exe"; Parameters: "--developer"; Description: "Launch read-only Developer Edition"; Flags: nowait postinstall skipifsilent
