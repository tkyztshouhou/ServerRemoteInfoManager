[Setup]
AppName=服务器运维管理工具
AppVersion=4.0.20260831
AppPublisher=LiuShan
DefaultDirName={autopf}\ServerRemoteInfoManager
DefaultGroupName=服务器运维管理工具
OutputBaseFilename=ServerRemoteInfoManager-4.0.20260831-Setup
Compression=lzma2/ultra64
SolidCompression=yes
OutputDir=dist
; 图标（用 img/app.ico）
SetupIconFile=img\app.ico
UninstallDisplayIcon={app}\ServerRemoteInfoManager.exe
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\ServerRemoteInfoManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\服务器运维管理工具"; Filename: "{app}\ServerRemoteInfoManager.exe"
Name: "{userdesktop}\服务器运维管理工具"; Filename: "{app}\ServerRemoteInfoManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式（当前用户）"; GroupDescription: "附加任务"

[Run]
Filename: "{app}\ServerRemoteInfoManager.exe"; Description: "立即运行"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{userdesktop}\服务器运维管理工具.lnk"
