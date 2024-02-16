Unicode True

; Define basic installer properties
Name "HunSpeechRecognition"
OutFile "HunSpeechRecognitionInstall.exe"
InstallDir "$PROGRAMFILES\HunSpeechRecognition"
RequestExecutionLevel admin ; Request admin rights

; Pages to display
Page directory ; Let the user choose the install directory
Page instfiles ; Show the installation progress

; Section defines part of the installation
Section "Install"
    SetOutPath $INSTDIR ; Set the installation directory
    ; Copy your application's files
    File /r "..\images"
    File /r "..\dependencies"
    File /r "..\ffmpeg-master-latest-win64-gpl"
    File /r "dist\hunspeechrecognition\_internal"
    File "dist\hunspeechrecognition\hunspeechrecognition.exe"

    SetOutPath $INSTDIR\log

    CreateShortcut "$DESKTOP\HunSpeechRecognition.lnk" "$INSTDIR\hunspeechrecognition.exe"

    EnVar::SetHKLM
    EnVar::AddValue "HUNSPEECH_PATH" $INSTDIR
   
SectionEnd
