; Instalador de Emulador de Control (Inno Setup 6).
;
; No se compila a mano: lo hace  .venv\Scripts\python empaquetar.py --instalador
; Instala la app y, si faltan, los drivers ViGEmBus (mando virtual) y HidHide
; (ocultar el DS4). Los drivers se dejan al desinstalar: otros programas
; pueden estar usándolos.

#define Nombre "Emulador de Control"
#define Exe "EmuladorDeControl.exe"
#ifndef Version
  #define Version "1.0.0"
#endif

[Setup]
AppId={{E4A7FF26-2F29-485A-BD31-39EADBB1592B}
AppName={#Nombre}
AppVersion={#Version}
AppPublisher=Julian
DefaultDirName={autopf}\EmuladorDeControl
DefaultGroupName={#Nombre}
DisableProgramGroupPage=yes
; Instalar drivers requiere administrador
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=EmuladorDeControl_Setup
SetupIconFile=..\build\icono.ico
UninstallDisplayIcon={app}\{#Exe}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Si la app está abierta (p. ej. al actualizar), ofrece cerrarla
CloseApplications=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "escritorio"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"
Name: "inicio"; Description: "Abrir el emulador al iniciar Windows"; GroupDescription: "Arranque:"; Flags: unchecked

[Files]
Source: "..\dist\EmuladorDeControl\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "licencias\*"; DestDir: "{app}\licencias"; Flags: ignoreversion
; dontcopy: no se instalan; el código los extrae a una carpeta temporal si hacen falta
Source: "redist\ViGEmBus_Setup.exe"; Flags: dontcopy
Source: "redist\HidHide_Setup.exe"; Flags: dontcopy

[Icons]
Name: "{group}\{#Nombre}"; Filename: "{app}\{#Exe}"
Name: "{group}\Desinstalar {#Nombre}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#Nombre}"; Filename: "{app}\{#Exe}"; Tasks: escritorio
Name: "{commonstartup}\{#Nombre}"; Filename: "{app}\{#Exe}"; Tasks: inicio

[Run]
Filename: "{app}\{#Exe}"; Description: "Abrir {#Nombre}"; Flags: nowait postinstall skipifsilent; Check: not HayQueReiniciar

[UninstallRun]
; Si se desinstala con la ocultación activa, el DS4 quedaría oculto para
; todo. Se apaga y se borra de la lista blanca el .exe que ya no existirá.
Filename: "{commonpf}\Nefarius Software Solutions\HidHide\x64\HidHideCLI.exe"; Parameters: "--cloak-off --app-unreg ""{app}\{#Exe}"""; Flags: runhidden skipifdoesntexist; RunOnceId: "ApagarHidHide"

[Code]
var
  Reiniciar: Boolean;

function DriverInstalado(Servicio: String): Boolean;
begin
  Result := RegKeyExists(HKLM, 'SYSTEM\CurrentControlSet\Services\' + Servicio);
end;

function HayQueReiniciar: Boolean;
begin
  Result := Reiniciar;
end;

{ Inno pregunta esto al final: si devuelve True, ofrece reiniciar }
function NeedRestart: Boolean;
begin
  Result := Reiniciar;
end;

procedure InstalarDriver(Servicio, Instalador, Texto: String);
var
  Codigo: Integer;
begin
  if DriverInstalado(Servicio) then
    exit;
  WizardForm.StatusLabel.Caption := Texto;
  ExtractTemporaryFile(Instalador);
  if not Exec(ExpandConstant('{tmp}\' + Instalador), '/exenoui /qn /norestart', '',
              SW_HIDE, ewWaitUntilTerminated, Codigo) then
    Codigo := -1;
  { 0 = bien; 3010 = bien, pero hay que reiniciar }
  if Codigo = 3010 then
    Reiniciar := True
  else if Codigo <> 0 then
    MsgBox(Texto + #13#10#13#10 + 'Ha fallado (código ' + IntToStr(Codigo) + '). ' +
           'Puedes instalarlo a mano más tarde desde su página de GitHub.', mbError, MB_OK);
end;

procedure CurStepChanged(Paso: TSetupStep);
var
  HidHideNuevo: Boolean;
begin
  if Paso = ssPostInstall then
  begin
    HidHideNuevo := not DriverInstalado('HidHide');
    InstalarDriver('ViGEmBus', 'ViGEmBus_Setup.exe', 'Instalando ViGEmBus (mando de Xbox 360 virtual)...');
    InstalarDriver('HidHide', 'HidHide_Setup.exe', 'Instalando HidHide (ocultar el DS4 a los juegos)...');
    { El filtro de HidHide solo se engancha al mando tras reiniciar o reconectarlo }
    if HidHideNuevo and DriverInstalado('HidHide') then
      Reiniciar := True;
  end;
end;
