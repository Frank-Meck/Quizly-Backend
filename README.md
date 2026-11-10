# Quizly Backend

Django REST API für **Quizly** – eine Anwendung, mit der Benutzer aus YouTube-Videos automatisch interaktive Multiple-Choice-Quizze erstellen können.

Das Backend verwaltet Benutzerkonten, Authentifizierung, Quizze und Fragen. Die Quizgenerierung basiert auf der Transkription von Videoinhalten und der anschließenden Verarbeitung durch ein KI-Modell.

**Projektstatus:** In Entwicklung. Die zentralen Funktionen für Benutzerverwaltung, Authentifizierung und Quizverwaltung sind implementiert und automatisiert getestet. Die Verarbeitung von YouTube-Videos und die Anbindung externer KI-Dienste benötigen die entsprechenden Systemvoraussetzungen und Zugangsdaten.

## Inhaltsverzeichnis

- [Features](#features)
- [Technologien](#technologien)
- [Projektstruktur](#projektstruktur)
- [Architektur und Datenbankmodell](#architektur-und-datenbankmodell)
- [API-Dokumentation](#api-dokumentation)
- [Installation und Einrichtung](#installation-und-einrichtung)
- [Umgebungsvariablen](#umgebungsvariablen)
- [Tests](#tests)
- [Sicherheit](#sicherheit)
- [Fehlerbehandlung](#fehlerbehandlung)
- [Entwicklungsworkflow](#entwicklungsworkflow)
- [Git-Commit-Konventionen](#git-commit-konventionen)

## Features

Das Backend bietet folgende Funktionen:

- Registrierung und Anmeldung von Benutzern
- Authentifizierung mit Access- und Refresh-Tokens über HTTP-Cookies
- Abmeldung mit Invalidierung des Refresh-Tokens
- Erneuerung abgelaufener Access-Tokens
- Erstellung von Quizzen anhand einer YouTube-URL
- Verarbeitung von YouTube-Videos und Transkripten
- Transkription von Audio mit OpenAI Whisper
- Generierung von Quizfragen mit der Google Gemini API
- Erstellung von Multiple-Choice-Fragen mit jeweils vier Antwortoptionen
- Auflisten, Abrufen, Aktualisieren und Löschen eigener Quizze
- Automatisierte Tests mit Django und pytest

## Technologien

| Technologie | Verwendung |
|---|---|
| Python | Programmiersprache |
| Django | Backend-Framework |
| Django REST Framework | REST API |
| djangorestframework-simplejwt | JWT-Unterstützung |
| django-cors-headers | CORS-Konfiguration |
| SQLite | Lokale Entwicklungs- und Testdatenbank |
| yt-dlp | Abruf von YouTube-Inhalten |
| FFmpeg | Verarbeitung und Konvertierung von Audio |
| OpenAI Whisper | Transkription von Audio in Text |
| Google Gemini API | Generierung von Quizfragen |
| google-genai | Python-SDK für Gemini |
| python-dotenv | Laden von Umgebungsvariablen |
| pytest | Testframework |
| pytest-django | Django-Integration für pytest |

## Projektstruktur

Die folgende Darstellung zeigt die aktuelle Struktur des Backends. Automatisch erzeugte Dateien und Verzeichnisse wie `__pycache__`, `.pytest_cache` und die virtuelle Umgebung sind nicht aufgeführt.

```text
backend/
├── core/
│   ├── settings.py
│   ├── test_settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── users/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_functions.py
│   │   ├── test_login.py
│   │   ├── test_logout.py
│   │   ├── test_register.py
│   │   └── test_token_refresh.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── functions.py
│   ├── models.py
│   ├── serializers.py
│   └── views.py
├── quizzes/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_create_quiz.py
│   │   ├── test_delete_quiz.py
│   │   ├── test_functions_gemini.py
│   │   ├── test_functions_transcripts.py
│   │   ├── test_functions_validation.py
│   │   ├── test_functions_whisper.py
│   │   ├── test_get_quiz.py
│   │   ├── test_list_quizzes.py
│   │   ├── test_models.py
│   │   └── test_update_quiz.py
│   ├── admin.py
│   ├── apps.py
│   ├── functions.py
│   ├── models.py
│   ├── serializers.py
│   └── views.py
├── docs/
├── manage.py
├── pytest.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Die API-Routen werden zentral in `core/urls.py` definiert. Die Verarbeitung der Quizgenerierung befindet sich derzeit in `quizzes/functions.py`.

## Architektur und Datenbankmodell

Das Datenmodell besteht aus drei zentralen Entitäten: `User`, `Quiz` und `Question`.

### User

Das Projekt verwendet das eingebaute Django-User-Modell.

Wichtige Felder:

- `id` – Primärschlüssel
- `username` – eindeutiger Benutzername
- `email` – E-Mail-Adresse
- `password` – von Django gehashter Passwortwert
- `is_active` – Status des Benutzerkontos
- `is_staff` – Berechtigung für den Django-Administrationsbereich
- `date_joined` – Registrierungszeitpunkt
- `last_login` – letzter Anmeldezeitpunkt

Passwörter werden niemals im Klartext gespeichert.

### Quiz

Ein Quiz gehört zu genau einem Benutzer. Ein Benutzer kann mehrere Quizze besitzen.

| Feld | Beschreibung |
|---|---|
| `id` | Primärschlüssel |
| `user_id` | Fremdschlüssel zum Besitzer |
| `title` | Titel des Quiz |
| `description` | Beschreibung |
| `video_url` | YouTube-URL |
| `created_at` | Erstellungszeitpunkt |
| `updated_at` | Zeitpunkt der letzten Änderung |

### Question

Eine Frage gehört zu genau einem Quiz. Ein Quiz kann mehrere Fragen enthalten.

| Feld | Beschreibung |
|---|---|
| `id` | Primärschlüssel |
| `quiz_id` | Fremdschlüssel zum Quiz |
| `question_title` | Fragetext |
| `question_options` | Antwortoptionen, gespeichert als JSON-Array |
| `answer` | Richtige Antwort |
| `created_at` | Erstellungszeitpunkt |
| `updated_at` | Zeitpunkt der letzten Änderung |

Jede generierte Frage soll genau vier unterschiedliche Antwortoptionen besitzen. Die richtige Antwort muss einer dieser Optionen entsprechen.

### Beziehungen

- `User 1:n Quiz`
- `Quiz 1:n Question`

Beim Löschen eines Quiz werden die zugehörigen Fragen ebenfalls gelöscht. Die Löschstrategie für Benutzer und deren Quizze wird über die Django-Modellbeziehungen festgelegt.

## API-Dokumentation

**Basis-URL der lokalen Entwicklung:**

`http://127.0.0.1:8000`

Die API verwendet JSON für Request- und Response-Bodies, sofern nicht anders angegeben.

### Übersicht der Endpunkte

| Methode | Endpunkt | Beschreibung | Authentifizierung |
|---|---|---|---|
| POST | `/api/register/` | Benutzer registrieren | Nein |
| POST | `/api/login/` | Benutzer anmelden | Nein |
| POST | `/api/logout/` | Benutzer abmelden | Ja |
| POST | `/api/token/refresh/` | Access-Token erneuern | Refresh-Cookie |
| POST | `/api/quizzes/` | Quiz erstellen | Ja |
| GET | `/api/quizzes/` | Eigene Quizze auflisten | Ja |
| GET | `/api/quizzes/{id}/` | Einzelnes Quiz abrufen | Ja |
| PATCH | `/api/quizzes/{id}/` | Quiz aktualisieren | Ja |
| DELETE | `/api/quizzes/{id}/` | Quiz löschen | Ja |

### Authentifizierung

#### 1. Benutzer registrieren

`POST /api/register/`

Registriert einen neuen Benutzer. Eine Authentifizierung ist nicht erforderlich.

Request:

```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_password",
  "email": "your_email@example.com"
}
```

Erfolgreiche Antwort: `201 Created`

```json
{
  "detail": "User created successfully!"
}
```

Mögliche Fehler:

- `400 Bad Request` – ungültige Eingaben, bereits verwendeter Benutzername oder nicht übereinstimmende Passwörter.

#### 2. Benutzer anmelden

`POST /api/login/`

Meldet einen Benutzer mit Benutzername und Passwort an.

Request:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Erfolgreiche Antwort: `200 OK`

```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

Bei erfolgreicher Anmeldung setzt der Server folgende Cookies:

- `access_token` – für authentifizierte API-Anfragen
- `refresh_token` – zum Erneuern des Access-Tokens

Die Cookies werden mit geeigneten Sicherheitsoptionen konfiguriert. Dazu gehören insbesondere `HttpOnly`, eine passende `SameSite`-Einstellung und `Secure` für HTTPS-Umgebungen.

Mögliche Fehler:

- `400 Bad Request` – fehlende oder ungültige Eingabedaten
- `401 Unauthorized` – falsche Zugangsdaten

#### 3. Benutzer abmelden

`POST /api/logout/`

Beendet eine authentifizierte Sitzung, löscht die Token-Cookies und invalidiert das Refresh-Token.

Request:

```json
{}
```

Erfolgreiche Antwort: `200 OK`

```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

Mögliche Fehler:

- `401 Unauthorized` – keine gültige Authentifizierung oder kein verwendbares Refresh-Token.

#### 4. Access-Token erneuern

`POST /api/token/refresh/`

Erneuert das Access-Token anhand eines gültigen `refresh_token`-Cookies.

Request-Body:

```json
{}
```

Das Refresh-Token wird aus dem Cookie gelesen.

Erfolgreiche Antwort: `200 OK`

```json
{
  "detail": "Token refreshed"
}
```

Der Server setzt ein neues `access_token`-Cookie.

Mögliche Fehler:

- `401 Unauthorized` – fehlendes, ungültiges oder abgelaufenes Refresh-Token.

### Quiz-Verwaltung

Alle Quiz-Endpunkte erfordern eine gültige Authentifizierung. Benutzer dürfen ausschließlich auf ihre eigenen Quizze zugreifen.

#### 5. Quiz erstellen

`POST /api/quizzes/`

Erstellt aus einem YouTube-Video automatisch ein Quiz.

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

Verarbeitungsablauf:

1. Die URL validieren und die YouTube-Video-ID extrahieren.
2. Die URL in ein einheitliches Format normalisieren.
3. Die verfügbaren Video- beziehungsweise Audiodaten abrufen.
4. Das Audio bei Bedarf mit FFmpeg verarbeiten.
5. Den gesprochenen Inhalt mit Whisper transkribieren.
6. Das Transkript an Gemini übergeben.
7. Multiple-Choice-Fragen mit jeweils vier Antwortoptionen generieren.
8. Die KI-Antwort parsen und validieren.
9. Das Quiz und die Fragen in der Datenbank speichern.
10. Temporäre Dateien nach der Verarbeitung entfernen.

Erfolgreiche Antwort: `201 Created`

```json
{
  "id": 1,
  "title": "Einführung in das Thema",
  "description": "Ein kurzer Überblick über die wichtigsten Inhalte des Videos.",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-01-15T10:00:00Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Welche Aussage trifft auf das Thema zu?",
      "question_options": [
        "Antwort A",
        "Antwort B",
        "Antwort C",
        "Antwort D"
      ],
      "answer": "Antwort B",
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

Das Beispiel zeigt die Struktur der Antwort. Die tatsächliche Anzahl der Fragen richtet sich nach der implementierten Generierung. IDs und Zeitstempel werden vom Backend erzeugt.

Mögliche Fehler:

- `400 Bad Request` – ungültige oder nicht unterstützte URL
- `401 Unauthorized` – fehlende oder ungültige Authentifizierung
- `502 Bad Gateway` – Fehler bei einem externen Dienst, sofern dieser Status für den jeweiligen Fehler vorgesehen ist
- `503 Service Unavailable` – vorübergehend nicht verfügbarer Verarbeitungsdienst

#### 6. Eigene Quizze auflisten

`GET /api/quizzes/`

Gibt die Quizze des angemeldeten Benutzers zurück. Quizze anderer Benutzer dürfen nicht enthalten sein.

Erfolgreiche Antwort: `200 OK`

```json
[
  {
    "id": 1,
    "title": "Einführung in das Thema",
    "description": "Ein kurzer Überblick über das Video.",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": []
  }
]
```

#### 7. Einzelnes Quiz abrufen

`GET /api/quizzes/{id}/`

Liefert ein einzelnes Quiz einschließlich seiner Fragen.

Erfolgreiche Antwort: `200 OK`

Die Antwort verwendet dieselbe Objektstruktur wie beim Erstellen eines Quiz.

Mögliche Fehler:

- `401 Unauthorized` – nicht authentifiziert
- `404 Not Found` – Quiz existiert nicht oder gehört einem anderen Benutzer

Der Zugriff auf fremde Quizze wird bewusst nicht offengelegt.

#### 8. Quiz aktualisieren

`PATCH /api/quizzes/{id}/`

Aktualisiert unterstützte Felder eines eigenen Quiz. Die Aktualisierung erfolgt teilweise; nicht angegebene Felder bleiben unverändert.

Request-Beispiel:

```json
{
  "title": "Aktualisierter Quiztitel",
  "description": "Eine aktualisierte Beschreibung."
}
```

Erfolgreiche Antwort: `200 OK`

Die Antwort enthält das aktualisierte Quizobjekt.

Mögliche Fehler:

- `400 Bad Request` – ungültige oder nicht unterstützte Felder
- `401 Unauthorized` – nicht authentifiziert
- `404 Not Found` – Quiz nicht vorhanden oder nicht zugänglich

#### 9. Quiz löschen

`DELETE /api/quizzes/{id}/`

Löscht ein eigenes Quiz einschließlich der zugehörigen Fragen.

Erfolgreiche Antwort: `204 No Content`

Bei Erfolg wird kein Response-Body zurückgegeben.

Mögliche Fehler:

- `401 Unauthorized` – nicht authentifiziert
- `404 Not Found` – Quiz nicht vorhanden oder nicht zugänglich

## Installation und Einrichtung

### Voraussetzungen

Für die lokale Entwicklung werden benötigt:

- Python 3.13 oder eine mit den Abhängigkeiten kompatible Python-Version
- Git
- pip
- FFmpeg
- Ein Gemini-API-Schlüssel für die Quizgenerierung

Whisper benötigt zusätzliche Abhängigkeiten, insbesondere PyTorch. Beim ersten Einsatz eines Whisper-Modells kann ein zusätzlicher Modelldownload erforderlich sein.

### 1. Repository klonen

```powershell
git clone https://github.com/Frank-Meck/Quizly-Backend.git
cd Quizly-Backend
```

### 2. Virtuelle Umgebung erstellen

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Falls PowerShell die Aktivierung des virtuellen Environments blockiert, kann die Ausführungsrichtlinie für den aktuellen Benutzer angepasst werden:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Anschließend kann die virtuelle Umgebung erneut aktiviert werden:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Abhängigkeiten installieren

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. FFmpeg überprüfen

```powershell
ffmpeg -version
```

FFmpeg muss über die Kommandozeile erreichbar sein. Es wird für die Audioverarbeitung benötigt.

### 5. Umgebungsvariablen konfigurieren

Erstelle anhand von `.env.example` eine lokale `.env`-Datei:

```powershell
Copy-Item .env.example .env
```

Öffne anschließend die `.env`-Datei und trage deine persönlichen Werte ein.

Beispiel:

```dotenv
SECRET_KEY=your_generated_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
GEMINI_API_KEY=your_actual_gemini_api_key
```

Einen Django-Secret-Key kannst du beispielsweise mit folgendem Befehl erzeugen:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Kopiere den erzeugten Wert in die `.env`-Datei.

**Wichtig:**

- `SECRET_KEY` ist verpflichtend. Ohne diesen Wert startet Django nicht.
- `GEMINI_API_KEY` wird für die Anbindung der Gemini API benötigt.
- `DEBUG=True` ist ausschließlich für die lokale Entwicklung vorgesehen.
- `ALLOWED_HOSTS` enthält die erlaubten Hostnamen, getrennt durch Kommata.
- Die `.env`-Datei enthält persönliche Zugangsdaten und darf nicht in Git eingecheckt werden.
- Die `.env.example`-Datei dient als Vorlage und enthält keine echten Geheimnisse.

### 6. Datenbank vorbereiten

```powershell
python manage.py migrate
```

### 7. Entwicklungsserver starten

```powershell
python manage.py runserver
```

Die lokale Anwendung ist anschließend unter folgender Adresse erreichbar:

`http://127.0.0.1:8000/`

### 8. Optional: Administrationskonto erstellen

```powershell
python manage.py createsuperuser
```

Dieser Schritt ist optional und setzt die entsprechende Django-Admin-Konfiguration voraus.

## Umgebungsvariablen

Die Anwendung lädt die Konfiguration aus der `.env`-Datei im Backend-Hauptverzeichnis.

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `SECRET_KEY` | Django-Sicherheitsschlüssel | Generierter Schlüssel |
| `DEBUG` | Aktiviert den Debug-Modus | `True` oder `False` |
| `ALLOWED_HOSTS` | Erlaubte Hostnamen | `127.0.0.1,localhost` |
| `GEMINI_API_KEY` | API-Schlüssel für Gemini | Persönlicher API-Key |

Die tatsächlichen Werte werden lokal in der `.env`-Datei hinterlegt und nicht versioniert.

## Tests

Das Projekt verwendet pytest und pytest-django. Die Testkonfiguration befindet sich in `pytest.ini`. Für Tests wird `core.test_settings` verwendet.

Die Testeinstellungen nutzen eine In-Memory-SQLite-Datenbank und einen schnellen Passwort-Hasher.

### Alle Tests ausführen

```powershell
python -m pytest
```

Alternativ können die Tests direkt über Django gestartet werden:

```powershell
python manage.py test --settings=core.test_settings
```

### Einzelnen Test ausführen

```powershell
python -m pytest users/tests/test_register.py
```

### Testprinzipien

- API-Endpunkte mit automatisierten Tests überprüfen.
- Erfolgsfälle und ungültige Eingaben testen.
- Authentifizierung und Berechtigungen überprüfen.
- Sicherstellen, dass Benutzer nicht auf fremde Quizze zugreifen können.
- Datenbankänderungen und Löschverhalten testen.
- Externe Aufrufe an YouTube, Whisper und Gemini in automatisierten Tests mocken.
- Tests reproduzierbar und unabhängig von echten API-Schlüsseln halten.

Integrationstests mit echten externen Diensten benötigen eine gesonderte Konfiguration und entsprechende Zugangsdaten.

## Sicherheit

Bei der Implementierung werden insbesondere folgende Punkte berücksichtigt:

- Passwörter ausschließlich über die Django-Authentifizierungsfunktionen verarbeiten.
- API-Schlüssel und andere Geheimnisse über Umgebungsvariablen bereitstellen.
- `.env` und lokale Datenbankdateien nicht versionieren.
- Authentifizierungs- und Berechtigungsprüfungen für geschützte Endpunkte durchführen.
- Zugriffe auf Quizze auf den angemeldeten Besitzer beschränken.
- Cookie-Optionen passend zur Entwicklungs- und Produktionsumgebung konfigurieren.
- Für produktive Umgebungen HTTPS verwenden.
- CORS auf tatsächlich benötigte Frontend-Ursprünge begrenzen.
- YouTube-URLs serverseitig validieren.
- Externe Dienstfehler behandeln, ohne Geheimnisse oder interne Details offenzulegen.
- Temporäre Audio- und Transkriptionsdateien nach Abschluss der Verarbeitung entfernen.
- Eingaben und KI-generierte Inhalte vor dem Speichern validieren.

## Fehlerbehandlung

Die Anwendung behandelt Fehler aus den einzelnen Verarbeitungsschritten kontrolliert.

Dazu gehören insbesondere:

- Ungültige oder nicht unterstützte YouTube-URLs
- Nicht verfügbare oder nicht abrufbare Videos
- Fehler beim Audio-Download
- Fehler bei der Transkription
- Zeitüberschreitungen und Fehler der Gemini API
- Ungültige oder unvollständige KI-Ausgaben
- Fehlende oder ungültige Authentifizierung
- Nicht vorhandene Ressourcen oder fehlende Berechtigungen

KI-generierte Antworten werden validiert. Es wird nicht vorausgesetzt, dass das Modell immer korrektes JSON mit der erwarteten Anzahl von Fragen und Antwortoptionen zurückgibt.

## Entwicklungsworkflow

Das Backend wird schrittweise testgetrieben entwickelt (TDD):

1. Anforderungen und erwartetes Verhalten festlegen.
2. Tests für das gewünschte Verhalten schreiben.
3. Tests ausführen und erwartete Fehler überprüfen.
4. Die Funktion implementieren.
5. Tests erneut ausführen und Fehler beheben.
6. Änderungen prüfen und mit einer passenden Commit-Nachricht sichern.

Die API-Dokumentation wird aktualisiert, wenn sich die verbindliche API-Spezifikation ändert.

## Git-Commit-Konventionen

Commit-Nachrichten folgen dem Schema:

`type: short description`

| Typ | Verwendung |
|---|---|
| `feat` | Neue Funktionalität |
| `fix` | Fehlerbehebung |
| `docs` | Dokumentation |
| `style` | Reine Formatierung |
| `refactor` | Code-Umstrukturierung |
| `perf` | Performance-Optimierung |
| `test` | Tests |
| `chore` | Wartung und Konfiguration |
| `build` | Build-System und Abhängigkeiten |
| `ci` | CI/CD-Pipelines |
| `revert` | Frühere Änderungen zurücknehmen |

Beispiele:

```text
feat: add user registration endpoint
feat: generate quizzes from YouTube videos
test: add registration endpoint tests
fix: validate login credentials
docs: update API documentation
build: add video and AI processing dependencies
chore: update gitignore
```

## Lizenz und Nutzung

Die Lizenz und Nutzungsbedingungen des Projekts sind entsprechend den Vorgaben des Projektinhabers festzulegen.

Vor einer öffentlichen Veröffentlichung sollten außerdem die Nutzungsbedingungen der eingebundenen externen Dienste und die Rechte an verarbeiteten Videoinhalten berücksichtigt werden.
