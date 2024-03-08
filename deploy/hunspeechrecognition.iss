[Setup]
AppName=HunSpeechRecognition
AppVersion=1.0
DefaultDirName={pf}\HunSpeechRecognition
OutputDir=.
OutputBaseFilename=HunSpeechRecognitionInstall
PrivilegesRequired=admin
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\hunspeechrecognition.exe
SetupIconFile=..\images\icon.ico

[Files]
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\hunspeechrecognition\hunspeechrecognition.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "environment\*"; DestDir: "{userappdata}\HunSpeechRecognition\environment"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "ffmpeg-master-latest-win64-gpl\*"; DestDir: "{app}\ffmpeg-master-latest-win64-gpl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\hunspeechrecognition\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Ensures the YourApplicationName folder is created inside the AppData\Roaming directory
Name: "{userappdata}\HunSpeechRecognition"
Name: "{userappdata}\HunSpeechRecognition\log"
Name: "{userappdata}\HunSpeechRecognition\whisper_models"

[Code]

[Icons]
Name: "{commondesktop}\HunSpeechRecognition"; Filename: "{app}\hunspeechrecognition.exe"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "HUNSPEECH_PATH"; ValueData: "{app}"; Flags: preservestringtype
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "HUNSPEECH_APPDATA"; ValueData: "{userappdata}\HunSpeechRecognition"; Flags: preservestringtype
