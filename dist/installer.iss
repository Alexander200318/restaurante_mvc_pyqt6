[Setup]
AppName=RestauranteApp
AppVersion=1.0
DefaultDirName={pf}\RestauranteApp
DefaultGroupName=RestauranteApp
OutputDir=output
OutputBaseFilename=instalador
Compression=lzma
SolidCompression=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "C:\Users\adria\OneDrive\Escritorio\TRABAJOS\restaurante_mvc_pyqt6\dist\main.exe"; DestDir: "{app}"
Source: "C:\Users\adria\OneDrive\Escritorio\TRABAJOS\restaurante_mvc_pyqt6\dist\restaurante.db"; DestDir: "{app}"

[Icons]
Name: "{group}\RestauranteApp"; Filename: "{app}\main.exe"
Name: "{commondesktop}\RestauranteApp"; Filename: "{app}\main.exe"

[Run]
Filename: "{app}\main.exe"; Description: "Abrir RestauranteApp"; Flags: nowait postinstall skipifsilent