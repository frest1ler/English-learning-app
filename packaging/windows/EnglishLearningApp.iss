#define MyAppName "English Learning App"
#define MyAppVersion "0.4.0"

[Setup]
AppId={{F276939B-69FB-46C3-AE8E-27090AE39620}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\EnglishLearningApp
DefaultGroupName={#MyAppName}
OutputDir=..\..\dist
OutputBaseFilename=EnglishLearningApp-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\..\dist\EnglishLearningApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\EnglishLearningApp.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\EnglishLearningApp.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\EnglishLearningApp.exe"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
