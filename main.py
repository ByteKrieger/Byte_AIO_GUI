import sys, ctypes, os
import PySimpleGUI as sg
import subprocess

# Überprüfe, ob das Skript als Administrator ausgeführt wird.
if not ctypes.windll.shell32.IsUserAnAdmin():
    answer = sg.popup_yes_no(
        "Warnung: Das Programm wird nicht als Administrator ausgeführt.\n"
        "Einige Funktionen erfordern Administratorrechte.\n\n"
        "Möchten Sie das Programm jetzt als Administrator neu starten?"
    )
    if answer == "Yes":
        # Neustart mit Administratorrechten
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)
    else:
        sg.popup("Das Programm läuft jetzt ohne Administratorrechte.\nEinige Befehle könnten fehlschlagen.", title="Warnung")

sg.theme('NeonYellow1')

# Speichere das aktuelle Arbeitsverzeichnis (wird z. B. für FRST64 genutzt)
working_dir = os.getcwd()

# Farben
ORANGE = '#FFA500'
DARK_ORANGE = '#FF8C00'

# Kategorien mit den entsprechenden Befehlen
command_groups = {
    "Bereinigung": {
        "Mülleimer leeren": {
            "command": "rd /s /q C:\\$Recycle.Bin",
            "is_powershell": False,
            "requires_admin": True
        },
        "Datenträgerbereinigung inkl. Systemdaten starten": {
            "command": "cleanmgr /sagerun:1",
            "is_powershell": False,
            "requires_admin": True
        }
    },
    "Checks": {
        "Speicherbelegung anzeigen": {
            "command": (
                "Get-WmiObject Win32_LogicalDisk | ForEach-Object { "
                "if ($_.Size -gt 0) { $device = $_.DeviceID.Trim(); "
                "$freeGB = [math]::Round($_.FreeSpace/1GB,0); "
                "$sizeGB = [math]::Round($_.Size/1GB,0); "
                "$usedGB = $sizeGB - $freeGB; "
                "$usedPercent = [math]::Round(($usedGB / $sizeGB * 100),0); "
                "Write-Output ('{0} = {1}% {2}/{3} GB' -f $device, $usedPercent, $usedGB, $sizeGB) } "
                "else { $device = $_.DeviceID.Trim(); "
                "Write-Output ('{0} = NaN% 0/0 GB' -f $device) } }"
            ),
            "is_powershell": True,
            "requires_admin": False
        },
        "Exchange HealthCheck": {
            "command": (
                "if (Test-Path \"$env:TEMP\\ExchangeHealthCheck.ps1\") { Remove-Item \"$env:TEMP\\ExchangeHealthCheck.ps1\" -Force }; "
                "Invoke-WebRequest -Uri \"https://github.com/microsoft/CSS-Exchange/releases/latest/download/HealthChecker.ps1\" -OutFile \"$env:TEMP\\ExchangeHealthCheck.ps1\"; "
                "& \"$env:TEMP\\ExchangeHealthCheck.ps1\""
            ),
            "is_powershell": True,
            "requires_admin": True
        },
        "FRST64 herunterladen und ausführen": {
            "command": (
                f"if (Test-Path \"{working_dir}\\FRST64.exe\") {{ Remove-Item \"{working_dir}\\FRST64.exe\" -Force }}; "
                f"Invoke-WebRequest -Uri \"https://bytekrieger.de/FRST64.exe\" -OutFile \"{working_dir}\\FRST64.exe\"; "
                f"& \"{working_dir}\\FRST64.exe\""
            ),
            "is_powershell": True,
            "requires_admin": True
        },
        "Programme abfragen": {
            "command": (
                "Get-ItemProperty HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | "
                "Sort Displayname | Select-Object DisplayName, DisplayVersion, InstallDate, Publisher"
            ),
            "is_powershell": True,
            "requires_admin": False
        }
    },
    "DISM&Update": {
        "Schnellcheck Komponenten-Speicher": {
            "command": "dism /Online /Cleanup-Image /CheckHealth",
            "is_powershell": False,
            "requires_admin": True
        },
        "Vollständiger Check Komponenten-Speicher": {
            "command": "dism /Online /Cleanup-Image /ScanHealth",
            "is_powershell": False,
            "requires_admin": True
        },
        "Analyse Komponenten-Speicher": {
            "command": "dism /Online /Cleanup-Image /AnalyzeComponentStore",
            "is_powershell": False,
            "requires_admin": True
        },
        "Bereinigen Komponenten-Speicher": {
            "command": "dism /Online /Cleanup-Image /StartComponentCleanup",
            "is_powershell": False,
            "requires_admin": True
        },
        "Reparatur via Windows Update": {
            "command": "dism /Online /Cleanup-Image /RestoreHealth",
            "is_powershell": False,
            "requires_admin": True
        },
        "Reparatur via WIM": {
            "command": "",  # Wird im Event-Loop speziell behandelt
            "is_powershell": False,
            "requires_admin": True
        }
    },
    "Reparaturen": {
        "SFC /scannow": {
            "command": "sfc /scannow",
            "is_powershell": False,
            "requires_admin": True
        },
        "Checkdisk": {
            "command": "chkdsk C:",
            "is_powershell": False,
            "requires_admin": True
        },
        "Printer Spooler reparieren": {
            "command": "net stop spooler && net start spooler",
            "is_powershell": False,
            "requires_admin": True
        },
        "Explorer Neustarten": {
            "command": "taskkill /f /im explorer.exe & start explorer.exe",
            "is_powershell": False,
            "requires_admin": False
        }
    },
    "weitere": {
        "Caffeine herunterladen und ausführen": {
            "command": (
                "if (Test-Path \"$env:TEMP\\caffeine64.exe\") { Remove-Item \"$env:TEMP\\caffeine64.exe\" -Force }; "
                "Invoke-WebRequest -Uri \"https://bytekrieger.de/caffeine64.exe\" -OutFile \"$env:TEMP\\caffeine64.exe\"; "
                "& \"$env:TEMP\\caffeine64.exe\""
            ),
            "is_powershell": True,
            "requires_admin": False
        }
    }
}

# Funktion zum Erstellen von Buttons für jede Registerkarte.
def create_buttons(command_group, group_name):
    rows = []
    if not command_group:
        rows.append([sg.Text("Keine Befehle definiert")])
    else:
        for command_name, command_info in command_group.items():
            key = command_name
            if command_info.get("requires_admin"):
                button_text = command_name + " *"
                btn = sg.Button(button_text, auto_size_button=True, button_color=('red', 'black'), key=key)
            else:
                btn = sg.Button(command_name, auto_size_button=True, button_color=(ORANGE, 'black'), key=key)
            if group_name == "DISM&Update" and command_name == "Bereinigen Komponenten-Speicher":
                row = [btn, sg.Checkbox("Mit Superseeded (ResetBase)", key="-SUPERSEDED-")]
            elif group_name == "Reparaturen" and command_name == "Checkdisk":
                row = [btn, sg.Checkbox("Full (/r)", key="-CHKDSK_FULL-"), sg.Checkbox("Force (/f)", key="-CHKDSK_FORCE-")]
            else:
                row = [btn]
            rows.append(row)
    return rows

tabs = []
for group_name, command_group in command_groups.items():
    tab_layout = create_buttons(command_group, group_name)
    tabs.append(sg.Tab(group_name, tab_layout))

admin_exists = any(
    command_info.get("requires_admin", False)
    for group in command_groups.values()
    for command_info in group.values()
)
admin_note = sg.Text("* benötigt Administratorrechte", text_color="red", justification="left", expand_x=True) if admin_exists else sg.Text("")

layout = [
    [sg.TabGroup([[tab] for tab in tabs])],
    [sg.Checkbox('Protokollierung aktivieren', default=False, key='-LOG-')],
    [admin_note, sg.Exit()]
]

window = sg.Window("PowerShell/CMD GUI", layout, element_justification='center', finalize=True)
hover_bg = "#C1E1C1"

for group_name, command_group in command_groups.items():
    for command_name, command_info in command_group.items():
        key = command_name
        orig_color = ('red', 'black') if command_info.get("requires_admin") else (ORANGE, 'black')
        try:
            btn_element = window[key]
            btn_element.Widget.bind(
                "<Enter>",
                lambda e, key=key, orig=orig_color: window[key].update(button_color=(orig[0], hover_bg))
            )
            btn_element.Widget.bind(
                "<Leave>",
                lambda e, key=key, orig=orig_color: window[key].update(button_color=(orig[0], orig[1]))
            )
        except Exception as ex:
            print(f"Fehler beim Binden des Hover-Events für {key}: {ex}")

def run_command(command, text, is_powershell=True, log_enabled=False):
    try:
        if log_enabled:
            log_filename = f"{text}_output.txt"
            if is_powershell:
                full_cmd = (
                    f'start "" powershell -NoExit -Command "{command} | Tee-Object -FilePath \'{log_filename}\' | ForEach-Object {{ if ($_ -is [string]) {{ $_.TrimEnd() }} else {{ $_ }} }} | Out-Host; '
                    f'Read-Host -Prompt \'Press Enter to exit\'; exit"'
                )
            else:
                full_cmd = (
                    f'start "" cmd /c "{command} > \"{log_filename}\" 2>&1 & type \"{log_filename}\" & pause & exit"'
                )
        else:
            if is_powershell:
                full_cmd = (
                    f'start "" powershell -NoExit -Command "{command} | Out-String | ForEach-Object {{ if ($_ -is [string]) {{ $_.TrimEnd() }} else {{ $_ }} }} | Out-Host; '
                    f'Read-Host -Prompt \'Press Enter to exit\'; exit"'
                )
            else:
                full_cmd = f'start "" cmd /c "{command} & pause & exit"'
        subprocess.Popen(full_cmd, shell=True)
    except Exception as e:
        sg.popup(f"Fehler beim Ausführen des Befehls: {e}", title="Fehler")

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == "Reparatur via WIM":
        wim_path = sg.popup_get_file("Wählen Sie eine WIM-Datei", file_types=(("WIM files", "*.wim"),))
        if wim_path:
            index = sg.popup_get_text("Bitte geben Sie den Index der WIM-Version ein (z.B. 1,2,3...):", "Index Eingabe")
            if index and index.isdigit():
                cmd = f'dism /Online /Cleanup-Image /RestoreHealth /Source:wim:"{wim_path}":{index} /LimitAccess'
                run_command(cmd, event, False, values['-LOG-'])
            else:
                sg.popup("Ungültiger Index!", title="Fehler")
        continue

    for group_name, command_group in command_groups.items():
        if event in command_group:
            command_data = command_group[event]
            cmd = command_data["command"]
            if event == "Bereinigen Komponenten-Speicher":
                if values.get("-SUPERSEDED-"):
                    cmd += " /ResetBase"
            if event == "Checkdisk":
                if values.get("-CHKDSK_FULL-"):
                    cmd += " /r"
                if values.get("-CHKDSK_FORCE-"):
                    cmd += " /f"
            run_command(cmd, event, command_data["is_powershell"], values['-LOG-'])

window.close()
