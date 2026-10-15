; Insta Cleaner Pro · Michel's Lab · first-class Windows installer.
; The underlying PyInstaller executable remains an implementation detail.
; Pass /DMyAppVersion=120.47 and /DPayloadDir=<absolute staging path> to ISCC.
#ifndef MyAppVersion
 #error MyAppVersion must be passed from the governed release metadata.
#endif
#ifndef PayloadDir
 #error PayloadDir must be passed from the verified Windows staging directory.
#endif

[Setup]
AppId={{E4D8F690-4D44-4C9E-8E6B-BCDD2879F08C}
AppName=Insta Cleaner Pro
AppVerName=Insta Cleaner Pro v{#MyAppVersion}
AppVersion={#MyAppVersion}
AppPublisher=Michel's Lab
AppPublisherURL=https://github.com/michels-lab
AppSupportURL=https://github.com/michels-lab/IG-Cleaner-Pro/issues
AppUpdatesURL=https://github.com/michels-lab/IG-Cleaner-Pro/releases
AppContact=michelslab.dev@gmail.com
VersionInfoCompany=Michel's Lab
VersionInfoProductName=Insta Cleaner Pro
VersionInfoDescription=Insta Cleaner Pro — integrated Windows app and automation tools
DefaultDirName={localappdata}\Programs\Michel's Lab\Insta Cleaner Pro
DefaultGroupName=Insta Cleaner Pro
DisableProgramGroupPage=yes
UsePreviousAppDir=yes
PrivilegesRequired=lowest
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=..\..\LICENSE.txt
SetupIconFile=..\..\desktop\assets\ig-cleaner-pro\official-app-icon.ico
UninstallDisplayIcon={app}\InstaCleanerPro.exe
OutputDir=..\..\artifacts
OutputBaseFilename=IG-Cleaner-Pro-Windows-Setup-v{#MyAppVersion}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
SetupLogging=yes
CloseApplications=yes
RestartApplications=no
; Same AppId and directory on every version: upgrade in place.
; Browser sessions, imported lists and robot journals live outside {app}.
Uninstallable=yes
ChangesAssociations=no
ChangesEnvironment=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
english.DesktopShortcut=Create a desktop shortcut
spanish.DesktopShortcut=Crear un acceso directo en el escritorio
english.OptionalShortcuts=Optional shortcuts:
spanish.OptionalShortcuts=Accesos directos opcionales:
english.LaunchApp=Launch Insta Cleaner Pro
spanish.LaunchApp=Abrir Insta Cleaner Pro
english.PinTaskbarHelp=Show how to pin Insta Cleaner Pro to the taskbar
spanish.PinTaskbarHelp=Ver cómo anclar Insta Cleaner Pro a la barra de tareas

[Files]
Source: "{#PayloadDir}\InstaCleanerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\BUILD-INFO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\EXECUTABLE-SHA256.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PayloadDir}\chrome-extension\*"; DestDir: "{app}\chrome-extension"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "TaskbarPinning.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userprograms}\Insta Cleaner Pro"; Filename: "{app}\InstaCleanerPro.exe"; IconFilename: "{app}\InstaCleanerPro.exe"
Name: "{autodesktop}\Insta Cleaner Pro"; Filename: "{app}\InstaCleanerPro.exe"; IconFilename: "{app}\InstaCleanerPro.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:OptionalShortcuts}"; Flags: unchecked

[Run]
Filename: "{app}\InstaCleanerPro.exe"; Description: "{cm:LaunchApp}"; Flags: nowait postinstall skipifsilent
; Windows taskbar pinning is always a human choice, not a shell hack.
Filename: "{sys}\notepad.exe"; Parameters: """{app}\TaskbarPinning.txt"""; Description: "{cm:PinTaskbarHelp}"; Flags: nowait postinstall skipifsilent unchecked
