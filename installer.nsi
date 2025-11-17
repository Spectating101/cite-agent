; Cite Agent Windows Installer
; NSIS (Nullsoft Scriptable Install System) Script
; Creates a professional Windows installer with:
; - Desktop shortcut
; - Start menu entry
; - PATH configuration
; - Uninstaller

!define PRODUCT_NAME "Cite Agent"
!define PRODUCT_VERSION "1.4.8"
!define PRODUCT_PUBLISHER "Cite Agent Team"
!define PRODUCT_WEB_SITE "https://github.com/Spectating101/cite-agent"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\cite-agent.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Modern UI
!include "MUI2.nsh"
!include "EnvVarUpdate.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "${NSISDIR}\Contrib\Graphics\Wizard\win.bmp"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page (if LICENSE file exists)
!insertmacro MUI_PAGE_LICENSE "LICENSE"
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\cite-agent.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Launch Cite Agent now"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.md"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "View README"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Installer info
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "CiteAgentSetup-${PRODUCT_VERSION}.exe"
InstallDir "$PROGRAMFILES\Cite Agent"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer

  ; Copy all files from PyInstaller dist folder
  File /r "dist\cite-agent\*.*"

  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Cite Agent"
  CreateShortCut "$SMPROGRAMS\Cite Agent\Cite Agent.lnk" "$INSTDIR\cite-agent.exe" "" "$INSTDIR\cite-agent.exe" 0
  CreateShortCut "$SMPROGRAMS\Cite Agent\Uninstall.lnk" "$INSTDIR\uninst.exe"

  ; Desktop shortcut
  CreateShortCut "$DESKTOP\Cite Agent.lnk" "$INSTDIR\cite-agent.exe" "" "$INSTDIR\cite-agent.exe" 0

  ; Add to PATH for command-line access
  ${EnvVarUpdate} $0 "PATH" "A" "HKLM" "$INSTDIR"

  ; Refresh environment for current session
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\cite-agent.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\cite-agent.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

Section Uninstall
  ; Remove from PATH
  ${un.EnvVarUpdate} $0 "PATH" "R" "HKLM" "$INSTDIR"

  ; Remove shortcuts
  Delete "$DESKTOP\Cite Agent.lnk"
  RMDir /r "$SMPROGRAMS\Cite Agent"

  ; Remove installation directory
  RMDir /r "$INSTDIR"

  ; Clean up registry
  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; Refresh environment
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment" /TIMEOUT=5000

  SetAutoClose true
SectionEnd
