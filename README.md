# AskSpace AI — Personal AI Chat Workspace

> **A minimalist, premium personal AI chat workspace engineered for MCA final-year students, computer science scholars, and software engineers.**

AskSpace AI provides an elegant, distraction-free environment to explore technical questions, analyze algorithms, write modular backend code, and curate verified insights into a personal searchable notebook.

---

## 🌟 Key Features

1. **Intelligent Technical Chatting & Audio Tools**:
   - Send questions via `Enter` or the interactive send button (`Shift + Enter` for multi-line code prompts).
   - **🎙️ Voice Dictation (Speech-to-Text)**: Speak technical questions directly into the browser microphone.
   - **🔊 Read Aloud (Text-to-Speech)**: Audio playback for assistant explanations with one click.
   - **⚡ Quick Action AI Toolbar**: Instant templates for `🐞 Debug Code`, `⏱️ Complexity Proof`, `🎓 Viva Q&A`, `🧪 Unit Tests`, and `💡 Real Analogy`.
   - **Interactive Prompt Cards**: Fast start for **DSA**, **Flask Architecture**, **DBMS ACID Properties**, and **MCA Interviews**.
   - Built-in Markdown parser with syntax-highlighted code blocks, language badges, and one-click code copy.

2. **Full Conversation Persistence & Study Export**:
   - Conversations are stored locally with SQLite and SQLAlchemy.
   - Intelligent auto-titling derived from the user's initial technical prompt.
   - Rename, search by keyword, categorize (Study, Coding, Career, General), and delete conversations with cascading cleanup.
   - **📥 Markdown Export**: Download complete chat sessions as formatted study guides (`.md`).

3. **Personal Searchable Notebook**:
   - Save high-value AI explanations, proofs, and code snippets directly from message cards.
   - **➕ Custom Study Notes**: Manually write and organize personal study notes alongside AI answers.
   - Search notes in real time by title or content, and filter by category.
   - **📖 Compiled Study Book Export**: Export all saved notes as a single compilation markdown booklet.
   - "Open Chat" link to navigate back to the original conversation source.

4. **Multi-Provider AI Abstraction with Transparent Demo Mode**:
   - **Live Google Gemini 3.5 Flash Integration**: Real-time generation powered by Google Gemini API.
   - **Demo Mode (Offline Fallback)**: Delivers instant, verified academic answers across Core CS topics (Operating Systems, DBMS, Networks, Algorithms, System Design) when offline.
   - Zero client-side API key exposure.

5. **Modern SaaS Visual Design**:
   - Deep charcoal dark mode (`#0c0d12`, `#12141a`, `#181b22`) with subtle indigo and violet accents (`#6366f1`, `#8b5cf6`).
   - Slate light mode toggle persisted locally and in SQLite database.
   - Accessible color contrast, visible focus rings, and responsive mobile drawer navigation.
   - **⚡ Keyboard Shortcuts Modal**: Hit `?` or `Ctrl+K` for instant command reference.

---

## 🏛 Architecture

AskSpace AI adopts the **Flask Application Factory Pattern** with clean separation of concerns:

```text
askspace-ai/
├── app/
│   ├── __init__.py          # Flask Application Factory (create_app)
│   ├── config.py            # Development and Test configuration
│   ├── extensions.py        # SQLAlchemy extension instance
│   ├── models/              # Relational models with integrity cascades
│   │   ├── __init__.py
│   │   ├── conversation.py  # Conversation entity
│   │   ├── message.py       # Chat Message entity (user/assistant)
│   │   ├── notebook.py      # Saved NotebookEntry entity
│   │   └── preference.py    # Key-value UserPreference entity
│   ├── routes/              # Modular Blueprints
│   │   ├── __init__.py
│   │   ├── pages.py         # Jinja2 template views (/, /notebook, /settings)
│   │   ├── chat.py          # /api/chat and /api/status endpoints
│   │   ├── conversations.py # /api/conversations CRUD endpoints
│   │   ├── notebook.py      # /api/notebook CRUD endpoints
│   │   └── settings.py      # /api/preferences endpoints
│   ├── services/            # Business & AI Logic
│   │   ├── __init__.py
│   │   ├── ai_provider.py   # AIProvider base, Demo, Gemini, and OpenAI
│   │   └── chat_service.py  # Title generation, history context, prompt styling
│   ├── static/              # Vanilla static assets (zero heavy CDN dependencies)
│   │   ├── css/style.css    # Responsive design tokens & styles
│   │   └── js/app.js        # Markdown parser, AJAX controller, state management
│   └── templates/           # Semantic HTML5 Jinja2 layouts
│       ├── base.html        # Shell, sidebar, modals, and toasts
│       ├── index.html       # Chat workspace & welcome cards
│       ├── notebook.html    # Saved answers grid & search
│       └── settings.html    # Theme switch, engine status, and metrics
├── instance/                # SQLite persistent database (askspace.db)
├── tests/                   # Automated pytest suite (31 tests)
│   ├── conftest.py          # In-memory test fixtures
│   ├── test_ai_provider.py  # Provider failure & fallback tests
│   ├── test_chat.py         # Chat turn, validation & autotitle tests
│   ├── test_conversations.py# Conversation CRUD tests
│   ├── test_notebook.py     # Notebook save, search & remove tests
│   ├── test_pages.py        # Page rendering & security header tests
│   └── test_settings.py     # Preferences persistence tests
├── .env.example             # Environment template
├── .gitignore               # Version control rules
├── requirements.txt         # Pinned Python dependencies
├── run.py                   # Application launch entry point
└── README.md                # Project documentation
```

---

## 💻 Technology Stack

- **Backend**: Python 3.11+, Flask 3.1, Flask-SQLAlchemy 3.1, Jinja2
- **Database**: SQLite 3 with cascading foreign keys
- **Frontend**: Semantic HTML5, Modern CSS3 with CSS Custom Properties, Vanilla JavaScript (ES6+)
- **Testing**: `pytest` 9.1 with in-memory SQLite isolation
- **Environment Management**: `python-dotenv`

---

## 📋 Prerequisites

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.11 or newer (Python 3.11.9 verified)
- **PowerShell** (on Windows) or Bash

---

## 🚀 Setup & Installation (Windows PowerShell)

### 1. Open PowerShell and Navigate to the Project

```powershell
Set-Location "C:\Users\admin\.gemini\antigravity\scratch\askspace-ai"
```

### 2. Create and Activate Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

*(If script execution is disabled on your system, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

To configure external AI providers, open `.env` and set:

```env
# AI Provider: 'demo' (offline academic mode), 'gemini', or 'openai'
AI_PROVIDER=demo

# Optional: Google Gemini API (Recommended for live AI)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash

# Optional: OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 5. Launch the Application

```powershell
python run.py
```

The application will start on:
👉 **`http://127.0.0.1:5000`**

Open your web browser and navigate to `http://127.0.0.1:5000` to interact with AskSpace AI.

---

## 🧪 Running Automated Tests

AskSpace AI includes an automated `pytest` test suite with **34 unit and integration tests** covering:
- Homepage and navigation security headers
- Conversation creation, retrieval, auto-titling, renaming, and deletion
- Chat message validation (empty prompts, oversized payloads, non-existent conversations)
- Offline Demo Mode behavior and curated answers
- Notebook saving, searching, and removal
- Conversation and notebook compilation Markdown export endpoints
- Theme preference persistence across application restarts
- AI provider failure handling and fallback mechanisms

Run the test suite with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -v
```

**Test Results**:
```text
============================= 34 passed in 10.69s =============================
```

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Main Chat Workspace page |
| `GET` | `/notebook` | Personal Notebook view |
| `GET` | `/settings` | Workspace Settings & Provider status |
| `GET` | `/api/status` | Current AI provider and metadata |
| `POST` | `/api/chat` | Send message, auto-title, persist turn, return reply |
| `GET` | `/api/conversations` | List conversations with category & search filter |
| `POST` | `/api/conversations` | Create new conversation |
| `GET` | `/api/conversations/<id>` | Retrieve conversation with full message history |
| `PATCH` | `/api/conversations/<id>` | Rename conversation title or change category |
| `DELETE` | `/api/conversations/<id>` | Delete conversation and cascade messages |
| `GET` | `/api/notebook` | List saved notes with search & category filter |
| `POST` | `/api/notebook` | Save response to personal notebook |
| `DELETE` | `/api/notebook/<id>` | Delete note from personal notebook |
| `GET` | `/api/preferences` | Retrieve user preferences & workspace stats |
| `PATCH` | `/api/preferences` | Update theme mode or assistant tone |

---

## 📸 Screenshots & UI Preview

### 1. Welcome Screen
*Minimalist hero greeting with quick-start technical prompt cards and category tabs.*
```text
[ Screenshot Placeholder: Welcome Screen (Dark Theme) ]
```

### 2. Active Chat Stream
*Syntax-highlighted Python code, mathematical notation, time complexity analysis, copy button, and save to notebook controls.*
```text
[ Screenshot Placeholder: Active Chat Conversation with Code Formatting ]
```

### 3. Personal Notebook
*Searchable grid of curated answers and study notes with original conversation back-links.*
```text
[ Screenshot Placeholder: Personal Notebook Grid View ]
```

### 4. Settings & Provider Status
*Theme toggle, AI provider switcher, tone customization, and persistence statistics.*
```text
[ Screenshot Placeholder: Workspace Settings Panel ]
```

---

## 🛡 Security & Academic Project Limitations

1. **Single-User Workspace**:
   - Designed for personal academic use and local portfolio demonstration.
   - For a production multi-tenant deployment, implement user registration, PBKDF2/bcrypt password hashing, session cookies, and row-level ownership checks (`user_id` foreign keys).
2. **Server-Side API Keys**:
   - API keys are strictly read from backend environment variables and are never transmitted to client JavaScript.
3. **Input Sanitization**:
   - All user input and model output rendered to the DOM is escaped against Cross-Site Scripting (XSS).
4. **Security Headers**:
   - Server enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `Referrer-Policy: strict-origin-when-cross-origin`.

---

## 🎓 Academic Portfolio Note
Engineered as an **MCA Final-Year Capstone Project & Software Internship Portfolio piece** demonstrating:
- Solid software engineering principles and architectural design patterns
- RESTful HTTP semantics and clean API design
- Full-stack responsiveness without heavy bloated frontend frameworks
- Automated testing practices and resilience against network failures
