# DMR Hotspot Monitor für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Diese Integration ermöglicht es, DMR Last Heard Daten von einem MMDVM/Pi-Star Hotspot in Home Assistant anzuzeigen.

## Features

- ✅ Automatische Erkennung der DMR API
- ✅ Live-Updates der Last Heard Liste
- ✅ Sensoren für: Rufzeichen, Talkgroup, Quelle (RF/Net), Zeit, Dauer, Paketverlust, Modus
- ✅ Konfigurierbar über die UI
- ✅ Mehrere Hotspots gleichzeitig möglich
- ✅ Einstellbares Aktualisierungsintervall

## Installation

### Via HACS (empfohlen)

1. HACS öffnen
2. Auf die drei Punkte oben rechts klicken
3. "Benutzerdefinierte Repositories" wählen
4. Repository-URL einfügen: `https://github.com/do1tl/dmr_hotspot`
5. Kategorie: "Integration"
6. "Hinzufügen" klicken
7. Nach "DMR Hotspot Monitor" suchen und installieren
8. Home Assistant neu starten

### Manuelle Installation

1. Kopiere den `custom_components/dmr_hotspot` Ordner in dein `custom_components` Verzeichnis
2. Home Assistant neu starten

## Konfiguration

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen**
3. Suche nach "DMR Hotspot"
4. Gib die IP-Adresse deines Hotspots ein (z.B. `192.168.2.10`)
5. Optional: Name und Aktualisierungsintervall anpassen
6. Fertig! Die Sensoren werden automatisch angelegt

## API-Anforderungen

Die Integration benötigt einen API-Endpoint der ein JSON-Array zurückgibt:

```json
[
  {
    "time_utc": "2025-11-22 22:15:35",
    "mode": "DMR Slot 2",
    "callsign": "DO1TL",
    "name": "",
    "callsign_suffix": "",
    "target": "TG 262",
    "src": "RF",
    "duration": "2.3",
    "loss": "0%"
  }
]
```

Typischerweise verfügbar unter: `http://IP_ADRESSE/api/`

## Sensoren

Die Integration erstellt folgende Sensoren:

- **Rufzeichen** - Das zuletzt gehörte Rufzeichen
- **Talkgroup** - Die verwendete Talkgroup
- **Quelle** - RF (Funk) oder Net (Netzwerk)
- **Zeit** - Zeitpunkt der letzten Aktivität
- **Dauer** - Dauer der Übertragung in Sekunden
- **Paketverlust** - Prozentuale Paketverlustrate
- **Modus** - DMR Slot (1 oder 2)

## Support

Bei Problemen oder Feature-Wünschen öffne bitte ein Issue auf GitHub.

## Lizenz

MIT License - siehe LICENSE Datei

73! 📻
