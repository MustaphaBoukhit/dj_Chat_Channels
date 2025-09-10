# Django Channels Chat — Realtime Group & Private Messaging

A small learning project that demonstrates how to build **real‑time chat** with **Django**, **Channels**, and **Daphne**. It supports:

- **Realtime group chat**: instantly broadcast messages to everyone in a room/group.
- **Private messages (1:1)**: send a message that only the target user can see.

> Built to explore WebSockets and Django’s ASGI stack with Channels.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Install & Run (Quickstart)](#install--run-quickstart)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Development Notes](#development-notes)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Features
- **Group rooms**: join a room and see messages broadcast instantly to all connected users.
- **Private messaging**: send a direct message to a specific user; only they can see it.
- **ASGI-native**: uses Django Channels over WebSockets, served by Daphne.

## Tech Stack
- **Backend**: Django, Django Channels (ASGI)
- **ASGI Server**: Daphne
- **Channel Layer**: In-memory (dev) or Redis (recommended for multi-process / production)

> You can start with the in‑memory channel layer for local development and switch to **Redis** when you need scale or multiple worker processes.

---

## Getting Started

### Prerequisites
- Python **3.10+**
- pip / venv
- (Optional but recommended) **Redis** for the channel layer

### Install & Run (Quickstart)
```bash
# 1) Clone
git clone https://github.com/MustaphaBoukhit/dj_Chat_Channels/.git
cd dj_Chat_Channels

# 2) Create & activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Apply migrations
python manage.py migrate

# 5) Install Redis, in my case I install Ubuntu on Windows as it needs a linux machine
(Optional) Run Redis with Docker (if using Redis channel layer)
docker run --name chat-redis -p 6379:6379 -d redis:7-alpine

# 6) Run the ASGI server with Daphne (recommended for WebSockets)
# Replace `config.asgi:application` with your actual ASGI path if different
python -m daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Now open http://localhost:8000
```

### Configuration
In `settings.py`, ensure Channels is installed and the ASGI entrypoint is set:

```python
INSTALLED_APPS = [
    # ...
    'channels',
    'chat',  # your app with Consumers
]

ASGI_APPLICATION = 'config.asgi.application'  # update to your project path
```

#### Channel Layers
For quick local dev you can use the in‑memory layer (single process only):

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
```

For multi‑process or production, use Redis:

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    }
}
```

Also ensure your `ASGI` routing is configured in something like `chat/routing.py` and included in your `config/asgi.py`.

---

## Usage
- Navigate to the home page, pick or create a **room**, and start chatting — messages should appear **instantly** for all connected users in that room.
- select a user from the list of online users to send a direct message to; only the target user should receive it.
- If you expose WebSocket endpoints, they might look like (adjust to your actual routes):
  - `ws/chat/<room_name>/`

> Exact URLs, payload formats, and UI controls depend on your implementation. Update this section with the final details as you build them.

---

## Project Structure
A typical layout (adjust to your repo):

```
.
├─ chat/
│  ├─ consumers.py        # ChatConsumer
│  ├─ routing.py          # websocket_urlpatterns
│  ├─ urls.py             # app URLs (optional)
│  ├─ templates/          # HTML templates
│  └─ static/             # JS for WebSocket client
├─ config/
│  ├─ asgi.py             # ASGI application
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py             # (still fine for HTTP, not used for websockets)
├─ manage.py
├─ requirements.txt
└─ README.md
```

---

## Development Notes
- **Daphne vs runserver**: Use **Daphne** (or Uvicorn) to properly test WebSockets. Django’s `runserver` is fine for quick dev but ASGI servers are closer to real deployments.
- **Auth**: For private messages, ensure you authenticate WebSocket connections (e.g., using session or token auth via AuthMiddlewareStack) and perform permission checks in your Consumers.
- **Scaling**: When scaling beyond a single process, switch to **Redis** for the channel layer and run multiple Daphne workers behind a reverse proxy (e.g., Nginx).

---

## Testing
Run the test suite (if present):

```bash
python manage.py test
```

Consider adding consumer tests with Channels’ testing utilities.

---

## Roadmap
- [ ] Message persistence (store chat history in DB)
- [ ] Typing indicators / presence
- [ ] Read receipts
- [ ] separate private message UI
- [ ] Message delivery status and retries
- [ ] Dockerfile / docker-compose for dev

---

## Contributing
Contributions are welcome! 
1. Fork the repository
2. Create your feature branch: `git checkout -b feature/awesome`
3. Commit your changes: `git commit -m "feat: add awesome feature"`
4. Push to the branch: `git push origin feature/awesome`
5. Open a Pull Request

---

## License
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements
- [Nik_Tomazic](https://testdriven.io/blog/django-channels/)
- [Django](https://www.djangoproject.com/)
- [Django Channels](https://channels.readthedocs.io/)
- [Daphne](https://github.com/django/daphne)

