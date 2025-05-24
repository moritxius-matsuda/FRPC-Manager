# FRPC Dienst-Einrichtung

Dieses Dokument erklärt, wie der FRPC-Dienst manuell eingerichtet werden kann, falls die automatische Einrichtung fehlschlägt.

## Automatische Einrichtung

Normalerweise wird der FRPC-Dienst automatisch während des Installationsprozesses eingerichtet. Dies geschieht in zwei Schritten:

1. Während der Installation wird die Dienstkonfiguration erstellt
2. Wenn du die Weboberfläche zum ersten Mal besuchst und die Einrichtung abschließt, wird der Dienst gestartet

## Manuelle Einrichtung

Falls der FRPC-Dienst nicht korrekt eingerichtet wurde, kannst du das beiliegende Skript verwenden:

```bash
sudo bash setup_frpc_service.sh
```

Dieses Skript wird:
1. Die Dienstkonfiguration erstellen
2. Den Dienst aktivieren und starten
3. Den Status des Dienstes anzeigen

## Überprüfen des Dienststatus

Du kannst den Status des FRPC-Dienstes jederzeit überprüfen mit:

```bash
systemctl status frpc.service
```

## Dienst manuell starten/stoppen

```bash
# Dienst starten
sudo systemctl start frpc.service

# Dienst stoppen
sudo systemctl stop frpc.service

# Dienst neu starten
sudo systemctl restart frpc.service
```

## Logs anzeigen

Um die Logs des FRPC-Dienstes anzuzeigen:

```bash
journalctl -u frpc.service
```

Für Echtzeit-Logs:

```bash
journalctl -u frpc.service -f
```

## Fehlerbehebung

Wenn der Dienst nicht startet, überprüfe:

1. Ob die Konfigurationsdatei existiert:
   ```bash
   ls -la /etc/frpc/frpc.toml
   ```

2. Ob die FRPC-Binärdatei existiert:
   ```bash
   ls -la /usr/local/bin/frpc
   ```
   
   Falls die Binärdatei nicht existiert, führe das Download-Skript aus:
   ```bash
   sudo bash download_frpc.sh
   ```

3. Ob die Dienstkonfiguration korrekt ist:
   ```bash
   cat /etc/systemd/system/frpc.service
   ```

Falls einer dieser Schritte fehlschlägt, führe die entsprechenden Setup-Skripte erneut aus oder kontaktiere den Support.