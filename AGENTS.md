# Mediatool - Django Video/Audio Downloader

## Project Overview
A Django MVP that downloads videos/audio from multiple platforms using **yt-dlp**, processes them with **ffmpeg**, manages async tasks via **Celery**, and provides real-time updates through **Django Channels WebSockets**.

**Current State:** MVP with mixed concerns; business logic scattered across views and utility modules.

## Tech Stack
- **Django** - Web framework
- **Celery** - Async task queue
- **Django Channels** - WebSocket support
- **yt-dlp** - Video downloading
- **ffmpeg** - Media processing
- **Redis** - Celery broker (assumed)

## Project Structure

```
jobs/                    # Django app - Job management & API
├── models.py           # Job model (download requests)
├── views.py            # API endpoints (NEEDS REFACTOR)
├── serializer.py       # DRF serializers
├── task.py             # Celery tasks (NEEDS REFACTOR)
└── urls.py

videodownloader/         # Business logic layer (NEEDS REFACTOR)
├── videodownload.py    # yt-dlp integration
├── chooseresolution.py # Format selection logic
├── geturl.py           # URL parsing
├── playlistinfo.py     # Playlist handling
├── login.py            # Authentication
└── websocket/
    ├── consumers.py    # WebSocket handlers
    └── routing.py      # WebSocket routing
```

## Current Pain Points

1. **Mixed Concerns** - Business logic in views, tasks, and utility modules
2. **Hard to Test** - Direct yt-dlp/ffmpeg calls scattered everywhere
3. **No Abstraction** - WebSocket updates tightly coupled to tasks
4. **Difficult to Extend** - Adding new platforms or formats requires modifying multiple files
5. **Error Handling** - Inconsistent error management across layers

## Refactoring Roadmap

### Phase 1: Service Layer Pattern
Extract business logic from views/tasks into dedicated service classes:

```
videodownloader/
├── services/
│   ├── download_service.py    # Orchestrates downloads
│   ├── format_service.py      # Format selection strategy
│   ├── extractor_service.py   # URL extraction
│   └── processor_service.py   # ffmpeg processing
```

**Benefit:** Testable, reusable, decoupled from views/tasks.

### Phase 2: Strategy Pattern
Support multiple downloaders (YouTube, generic HTTP, playlists):

```
videodownloader/
├── strategies/
│   ├── base_strategy.py       # Abstract base
│   ├── youtube_strategy.py    # YouTube-specific
│   ├── playlist_strategy.py   # Playlist logic
│   └── generic_strategy.py    # Fallback for other sites
```

### Phase 3: Observer/Pub-Sub Pattern
Replace direct WebSocket calls with event-driven architecture:

```
videodownloader/
├── events/
│   ├── download_events.py    # Event definitions
│   └── event_handler.py      # Dispatch to WebSocket
```

### Phase 4: Repository Pattern
Abstract data access:

```
jobs/
├── repositories/
│   └── job_repository.py     # Job queries & updates
```

## Next Steps

1. **Review current `views.py`** - Identify API endpoints
2. **Review `task.py`** - Understand Celery flow
3. **Review `videodownload.py`** - Map business logic
4. **Create Service Layer** - Extract core download logic
5. **Implement Strategy Pattern** - Support multiple platforms
6. **Add Event System** - Replace tight WebSocket coupling

## Commands

```bash
# Run Celery worker
celery -A videotools worker -l info

# Run local dev with Channels
python manage.py runserver

# Run tests (after adding them)
python manage.py test
```

## Resources
- [Django Channels Documentation](https://channels.readthedocs.io/)
- [Celery Best Practices](https://docs.celeryproject.io/en/stable/)
- [Design Patterns in Python](https://refactoring.guru/design-patterns/python)