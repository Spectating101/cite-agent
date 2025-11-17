/**
 * EnvVarUpdate.nsh
 * NSIS Environment Variable Update Plugin
 * Standard helper for adding/removing paths from PATH environment variable
 */

!ifndef ENVVARUPDATE_FUNCTION
!define ENVVARUPDATE_FUNCTION

!include "WinMessages.nsh"
!include "LogicLib.nsh"

!define EnvVarUpdate '!insertmacro EnvVarUpdateCall'
!define un.EnvVarUpdate '!insertmacro EnvVarUpdateCall'

!macro EnvVarUpdateCall _OUT_VARNAME _IN_VARNAME _ACTION _REGLOC _VALUE
  Push "${_VALUE}"
  Push "${_REGLOC}"
  Push "${_ACTION}"
  Push "${_IN_VARNAME}"
  Call ${__MACRO__}EnvVarUpdate
  Pop ${_OUT_VARNAME}
!macroend

!macro EnvVarUpdate UN
Function ${UN}EnvVarUpdate

  Push $0
  Push $1
  Push $2
  Push $3
  Push $4
  Push $5
  Push $6
  Push $7
  Push $8
  Push $9
  Push $R0

  Exch 4
  Pop $0  ; InVar (PATH)
  Exch 4
  Pop $1  ; Action (A=add, R=remove, P=prepend)
  Exch 4
  Pop $2  ; RegLoc (HKLM or HKCU)
  Exch 4
  Pop $3  ; PathValue

  ; Determine registry key
  ${If} $2 == "HKLM"
    StrCpy $4 "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    ReadRegStr $5 HKLM $4 $0
  ${Else}
    StrCpy $4 "Environment"
    ReadRegStr $5 HKCU $4 $0
  ${EndIf}

  ; Perform action
  ${If} $1 == "A"
    ; Append to PATH
    ${If} $5 == ""
      StrCpy $6 $3
    ${Else}
      ; Check if already in path
      ${StrContains} $7 $3 $5
      ${If} $7 != ""
        ; Already exists, don't add
        StrCpy $6 $5
      ${Else}
        StrCpy $6 "$5;$3"
      ${EndIf}
    ${EndIf}
  ${ElseIf} $1 == "P"
    ; Prepend to PATH
    ${If} $5 == ""
      StrCpy $6 $3
    ${Else}
      StrCpy $6 "$3;$5"
    ${EndIf}
  ${ElseIf} $1 == "R"
    ; Remove from PATH
    StrCpy $6 $5
    ${StrRep} $6 $6 ";$3;" ";"
    ${StrRep} $6 $6 ";$3" ""
    ${StrRep} $6 $6 "$3;" ""
    ${StrRep} $6 $6 "$3" ""
  ${EndIf}

  ; Write back to registry
  ${If} $2 == "HKLM"
    WriteRegExpandStr HKLM $4 $0 $6
  ${Else}
    WriteRegExpandStr HKCU $4 $0 $6
  ${EndIf}

  ; Return result
  StrCpy $R0 $6

  Pop $9
  Pop $8
  Pop $7
  Pop $6
  Pop $5
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0

  Exch $R0

FunctionEnd
!macroend

; Install both standard and uninstaller versions
!insertmacro EnvVarUpdate ""
!insertmacro EnvVarUpdate "un."

; Helper function: StrContains
!macro StrContainsCall _OUTPUT _SEARCH _STRING
  Push "${_STRING}"
  Push "${_SEARCH}"
  Call StrContains
  Pop ${_OUTPUT}
!macroend
!define StrContains '!insertmacro StrContainsCall'

Function StrContains
  Exch $1 ; search string
  Exch
  Exch $2 ; string to search in
  Push $3
  Push $4
  Push $5

  StrLen $3 $1
  StrLen $4 $2
  ${If} $4 < $3
    StrCpy $5 ""
    Goto done
  ${EndIf}

  IntOp $4 $4 - $3
  StrCpy $5 0

  loop:
    ${If} $5 > $4
      StrCpy $5 ""
      Goto done
    ${EndIf}
    StrCpy $0 $2 $3 $5
    ${If} $0 == $1
      StrCpy $5 $0
      Goto done
    ${EndIf}
    IntOp $5 $5 + 1
    Goto loop

  done:
    Pop $4
    Pop $3
    Exch $5
    Exch
    Pop $2
    Pop $1
FunctionEnd

; Helper function: StrRep
!macro StrRepCall _OUTPUT _SOURCE _SEARCH _REPLACE
  Push "${_SOURCE}"
  Push "${_SEARCH}"
  Push "${_REPLACE}"
  Call StrRep
  Pop ${_OUTPUT}
!macroend
!define StrRep '!insertmacro StrRepCall'

Function StrRep
  Exch $3 ; replace
  Exch
  Exch $2 ; search
  Exch 2
  Exch $1 ; source
  Push $4
  Push $5
  Push $6
  Push $7

  StrCpy $4 ""
  StrCpy $5 0
  StrLen $6 $2

  loop:
    StrCpy $7 $1 $6 $5
    ${If} $7 == ""
      Goto done
    ${EndIf}
    ${If} $7 == $2
      StrCpy $4 "$4$3"
      IntOp $5 $5 + $6
    ${Else}
      StrCpy $7 $1 1 $5
      StrCpy $4 "$4$7"
      IntOp $5 $5 + 1
    ${EndIf}
    Goto loop

  done:
    StrCpy $1 $4
    Pop $7
    Pop $6
    Pop $5
    Pop $4
    Pop $3
    Pop $2
    Exch $1
FunctionEnd

!endif
