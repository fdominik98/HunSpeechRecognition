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
AlwaysRestart=yes
DiskSpanning=yes
ExtraDiskSpaceRequired=5242880

[Files]
Source: "images\*"; DestDir: "{app}\images"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\hunspeechrecognition\hunspeechrecognition.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\whisper_models\*"; DestDir: "{userappdata}\HunSpeechRecognition\whisper_models"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "environment\*"; DestDir: "{userappdata}\HunSpeechRecognition\environment"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "ffmpeg-master-latest-win64-gpl\*"; DestDir: "{app}\ffmpeg-master-latest-win64-gpl"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\hunspeechrecognition\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Ensures the YourApplicationName folder is created inside the AppData\Roaming directory
Name: "{userappdata}\HunSpeechRecognition"
Name: "{userappdata}\HunSpeechRecognition\log"
Name: "{userappdata}\HunSpeechRecognition\whisper_models"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  EnvVarName: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    EnvVarName := 'HUNSPEECH_PATH';
    RegDeleteValue(HKEY_CURRENT_USER, 'Environment', EnvVarName);
    RegDeleteValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', EnvVarName);
    EnvVarName := 'HUNSPEECH_APPDATA';
    RegDeleteValue(HKEY_CURRENT_USER, 'Environment', EnvVarName);
    RegDeleteValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', EnvVarName);
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\HunSpeechRecognition\*";
Type: filesandordirs; Name: "{app}\*";
Type: dirifempty; Name: "{userappdata}\HunSpeechRecognition";
Type: dirifempty; Name: "{app}";

[Icons]
Name: "{commondesktop}\HunSpeechRecognition"; Filename: "{app}\hunspeechrecognition.exe"

[Registry]
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "HUNSPEECH_PATH"; ValueData: "{app}"; Flags: preservestringtype
Root: HKLM; Subkey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: "HUNSPEECH_APPDATA"; ValueData: "{userappdata}\HunSpeechRecognition"; Flags: preservestringtype
