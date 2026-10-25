"""AI Provider abstraction for AskSpace AI.

Supports:
1. DemoAIProvider: Offline academic demo mode with high-value answers for MCA students & developers.
2. GeminiAIProvider: Google Gemini API integration.
3. OpenAIAIProvider: OpenAI API integration.
"""

import json
import logging
import os
import re
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AIProviderError(Exception):
    """Base exception for AI provider operations."""
    pass


class AIConfigurationError(AIProviderError):
    """Raised when an AI provider is missing required credentials or config."""
    pass


class AIServiceUnavailableError(AIProviderError):
    """Raised when the remote AI service fails, times out, or hits rate limits."""
    pass


class BaseAIProvider(ABC):
    """Abstract interface for AI chat generation."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Active model name."""
        pass

    @property
    def is_demo(self) -> bool:
        """Whether this provider runs in demo mode."""
        return False

    @abstractmethod
    def generate_reply(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        category: str = 'General'
    ) -> Dict[str, Any]:
        """Generate response given conversation history."""
        pass


class DemoAIProvider(BaseAIProvider):
    """Offline, deterministic demo provider for student & developer workflows."""

    KNOWLEDGE_BASE = {
        'binary_search': {
            'keywords': ['binary search', 'search algorithm', 'divide and conquer'],
            'title': 'Binary Search Algorithm (O(log n))',
            'content': (
                "### Binary Search Algorithm\n\n"
                "**Binary Search** is an efficient divide-and-conquer algorithm for finding an element in a **sorted** array.\n\n"
                "#### Key Characteristics:\n"
                "- **Time Complexity**: $\\mathcal{O}(\\log n)$ in the worst and average cases; $\\mathcal{O}(1)$ best case.\n"
                "- **Space Complexity**: $\\mathcal{O}(1)$ iterative; $\\mathcal{O}(\\log n)$ recursive due to call stack.\n"
                "- **Prerequisite**: The sequence must be sorted in monotonic order.\n\n"
                "#### Python Implementation:\n"
                "```python\n"
                "def binary_search(arr: list[int], target: int) -> int:\n"
                "    \"\"\"Return the index of target in sorted arr, or -1 if not found.\"\"\"\n"
                "    left, right = 0, len(arr) - 1\n"
                "    \n"
                "    while left <= right:\n"
                "        # Avoid integer overflow in other languages: left + (right - left) // 2\n"
                "        mid = (left + right) // 2\n"
                "        \n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            left = mid + 1\n"
                "        else:\n"
                "            right = mid - 1\n"
                "            \n"
                "    return -1\n"
                "\n"
                "# Test case\n"
                "numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]\n"
                "print(binary_search(numbers, 23))  # Output: 5\n"
                "```\n\n"
                "#### Common Edge Cases:\n"
                "1. Array is empty (`len(arr) == 0`).\n"
                "2. Target is smaller than the first item or larger than the last item.\n"
                "3. Array contains duplicate values (use `bisect_left` or `bisect_right` in Python for boundary matches)."
            )
        },
        'flask_architecture': {
            'keywords': ['flask', 'architecture', 'application factory', 'blueprint', 'flask structure'],
            'title': 'Scalable Flask Application Architecture',
            'content': (
                "### Production-Grade Flask Application Architecture\n\n"
                "For serious projects such as an MCA final-year application or production microservices, use the **Application Factory Pattern** coupled with **Blueprints**.\n\n"
                "#### Recommended Directory Layout:\n"
                "```text\n"
                "askspace-ai/\n"
                "├── app/\n"
                "│   ├── __init__.py       # Factory: create_app()\n"
                "│   ├── config.py         # Config classes (Dev, Test, Prod)\n"
                "│   ├── extensions.py     # db = SQLAlchemy(), migrate, etc.\n"
                "│   ├── models/           # SQLAlchemy models\n"
                "│   ├── routes/           # Blueprints for features/APIs\n"
                "│   ├── services/         # Business logic & AI abstractions\n"
                "│   ├── static/           # CSS, JS, brand assets\n"
                "│   └── templates/        # Jinja2 layouts\n"
                "├── tests/                # Automated pytest suite\n"
                "├── instance/             # Local database & secret configs\n"
                "├── run.py                # Server entrypoint\n"
                "└── requirements.txt\n"
                "```\n\n"
                "#### Application Factory Example (`app/__init__.py`):\n"
                "```python\n"
                "from flask import Flask\n"
                "from app.config import Config\n"
                "from app.extensions import db\n"
                "\n"
                "def create_app(config_class=Config) -> Flask:\n"
                "    app = Flask(__name__)\n"
                "    app.config.from_object(config_class)\n"
                "    \n"
                "    # Initialize extensions\n"
                "    db.init_app(app)\n"
                "    \n"
                "    # Register Blueprints\n"
                "    from app.routes.chat import chat_bp\n"
                "    from app.routes.pages import pages_bp\n"
                "    app.register_blueprint(chat_bp, url_prefix='/api')\n"
                "    app.register_blueprint(pages_bp)\n"
                "    \n"
                "    return app\n"
                "```\n\n"
                "#### Advantages:\n"
                "- **Testability**: Easily instantiate isolated app instances with in-memory SQLite in `pytest`.\n"
                "- **Separation of Concerns**: Business logic resides in `services/`, not route handlers.\n"
                "- **Zero Circular Imports**: Extensions are defined in `extensions.py` without an app instance."
            )
        },
        'acid_properties': {
            'keywords': ['acid', 'database', 'transaction', 'dbms', 'atomicity', 'consistency', 'isolation', 'durability'],
            'title': 'ACID Properties in Database Management Systems',
            'content': (
                "### ACID Properties in Relational Databases\n\n"
                "**ACID** is an acronym representing the four fundamental properties that guarantee reliable database transactions:\n\n"
                "| Property | Meaning | How RDBMS Implements It |\n"
                "| :--- | :--- | :--- |\n"
                "| **Atomicity** | \"All or nothing\". The transaction executes completely or is completely rolled back. | Write-Ahead Logging (WAL) and Undo logs. |\n"
                "| **Consistency** | The database transitions from one valid state to another, preserving all schemas, constraints, and cascades. | Foreign keys, CHECK constraints, and unique indexes. |\n"
                "| **Isolation** | Concurrent transactions execute without interfering with one another. | Multi-Version Concurrency Control (MVCC) and Two-Phase Locking (2PL). |\n"
                "| **Durability** | Once committed, changes survive power outages or system crashes. | Non-volatile transaction logs (Redo log) flushed to disk. |\n\n"
                "#### SQL Transaction Example:\n"
                "```sql\n"
                "BEGIN TRANSACTION;\n"
                "\n"
                "UPDATE accounts \n"
                "SET balance = balance - 500 \n"
                "WHERE account_id = 'A101' AND balance >= 500;\n"
                "\n"
                "UPDATE accounts \n"
                "SET balance = balance + 500 \n"
                "WHERE account_id = 'B202';\n"
                "\n"
                "COMMIT; -- If either update fails, call ROLLBACK instead.\n"
                "```\n\n"
                "#### Isolation Levels (from lowest to highest):\n"
                "1. **Read Uncommitted** (permits dirty reads)\n"
                "2. **Read Committed** (default in PostgreSQL/Oracle; prevents dirty reads)\n"
                "3. **Repeatable Read** (default in MySQL InnoDB; prevents non-repeatable reads)\n"
                "4. **Serializable** (strictest isolation; prevents phantom reads)"
            )
        },
        'rest_api_design': {
            'keywords': ['rest', 'api design', 'restful', 'http methods', 'status codes', 'endpoint'],
            'title': 'RESTful API Design Best Practices',
            'content': (
                "### Principles of Professional RESTful API Design\n\n"
                "A clean REST API is predictable, resource-oriented, and adheres to standard HTTP semantics.\n\n"
                "#### 1. Resource Nouns over Action Verbs\n"
                "- **Good**: `GET /api/conversations`, `POST /api/conversations`, `DELETE /api/conversations/42`\n"
                "- **Bad**: `/api/getConversations`, `/api/createNewConversation`, `/api/deleteConversation`\n\n"
                "#### 2. HTTP Method Semantics\n"
                "- `GET`: Safe & idempotent. Retrieve data without side effects.\n"
                "- `POST`: Non-idempotent. Create a new child resource.\n"
                "- `PUT`: Idempotent. Replace entire resource.\n"
                "- `PATCH`: Idempotent/Non-idempotent. Partially update resource fields.\n"
                "- `DELETE`: Idempotent. Remove the resource.\n\n"
                "#### 3. Standard HTTP Status Codes\n"
                "- `200 OK`: Successful retrieval or synchronous update.\n"
                "- `201 Created`: Resource created successfully (`Location` header optional).\n"
                "- `204 No Content`: Successful deletion without response body.\n"
                "- `400 Bad Request`: Malformed JSON or failed validation.\n"
                "- `401 Unauthorized`: Authentication missing or invalid.\n"
                "- `403 Forbidden`: Authenticated user lacks permission.\n"
                "- `404 Not Found`: Resource ID does not exist.\n"
                "- `422 Unprocessable Entity`: Semantic validation failed.\n"
                "- `500 Internal Server Error`: Unexpected backend failure.\n\n"
                "#### 4. Predictable JSON Response Envelope:\n"
                "```json\n"
                "{\n"
                "  \"success\": true,\n"
                "  \"data\": {\n"
                "    \"id\": 1,\n"
                "    \"title\": \"Flask Architecture\",\n"
                "    \"category\": \"Coding\"\n"
                "  },\n"
                "  \"error\": null\n"
                "}\n"
                "```"
            )
        },
        'interview_prep': {
            'keywords': ['interview', 'mca', 'career', 'resume', 'internship', 'portfolio', 'coding interview', 'hire'],
            'title': 'MCA Technical Interview & Internship Preparation Guide',
            'content': (
                "### MCA Technical Interview & Internship Strategy\n\n"
                "To stand out for software development engineer (SDE) internships and campus placements:\n\n"
                "#### 1. Core Academic Subjects (Non-Negotiable)\n"
                "- **Data Structures & Algorithms**: Arrays, Hash Maps, Linked Lists, Trees (BST, Traversals), Heaps, and Dynamic Programming fundamentals.\n"
                "- **DBMS**: SQL queries (JOINs, GROUP BY, HAVING, Subqueries), Indexing (B-Trees), Normalization (1NF through BCNF), and ACID transactions.\n"
                "- **Operating Systems**: Process vs Thread, Process Scheduling algorithms, Deadlocks (Four Conditions & Banker's Algorithm), Virtual Memory and Paging.\n"
                "- **Computer Networks**: TCP vs UDP, TCP 3-Way Handshake, HTTP/HTTPS handshake (TLS), DNS resolution workflow.\n\n"
                "#### 2. Portfolio Project Excellence (Like AskSpace AI)\n"
                "Recruiters look for candidates who understand engineering depth rather than just tutorials:\n"
                "- **Explain Trade-offs**: Why SQLite for local single-user vs PostgreSQL for horizontal scale? Why Flask application factory instead of a single file?\n"
                "- **Clean Architecture**: Show separation of concerns (Routes -> Services -> Models).\n"
                "- **Automated Testing**: Highlight high test coverage with `pytest`.\n"
                "- **Security**: Mention CSRF protection, input sanitization, and parameterized queries.\n\n"
                "#### 3. Behavioral / STAR Method\n"
                "Format behavioral answers using **S**ituation, **T**ask, **A**ction, **R**esult to showcase problem solving and ownership under pressure."
            )
        },
        'operating_systems': {
            'keywords': ['process', 'thread', 'deadlock', 'virtual memory', 'paging', 'os', 'operating system'],
            'title': 'Core Operating System Concepts for Engineers',
            'content': (
                "### Core Operating System Fundamentals\n\n"
                "#### 1. Process vs. Thread\n"
                "- **Process**: An executing instance of a program with its own dedicated virtual address space, file descriptors, and security context. Inter-Process Communication (IPC) requires pipes, sockets, or shared memory.\n"
                "- **Thread**: The smallest unit of execution scheduled by the OS within a process. Threads share the same address space, heap, and code segment, but maintain their own registers and stack.\n\n"
                "#### 2. The Four Necessary Conditions for Deadlock (Coffman Conditions)\n"
                "A deadlock occurs if and only if all four conditions hold simultaneously:\n"
                "1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode.\n"
                "2. **Hold and Wait**: A process holds at least one resource while waiting to acquire additional resources.\n"
                "3. **No Preemption**: Resources cannot be forcibly confiscated from a process holding them.\n"
                "4. **Circular Wait**: A closed chain of processes exists where each process waits for a resource held by the next process.\n\n"
                "#### 3. Virtual Memory & Demand Paging\n"
                "- Maps physical RAM and swap storage into a contiguous address space per process.\n"
                "- Uses **Page Tables** and **Translation Lookaside Buffers (TLB)** for high-speed hardware address translation.\n"
                "- **Page Fault**: Occurs when an address references a page not currently resident in physical RAM, prompting the OS to fetch it from disk."
            )
        },
        'computer_networks': {
            'keywords': ['network', 'networks', 'tcp', 'udp', 'osi', 'handshake', 'osi model', 'protocol'],
            'title': 'Computer Networks & TCP/IP Architecture',
            'content': (
                "### Computer Networks & Transport Layer Fundamentals\n\n"
                "#### 1. The OSI 7-Layer Reference Model\n"
                "| Layer # | Name | Primary Function | Standard Protocol / Unit |\n"
                "| :--- | :--- | :--- | :--- |\n"
                "| 7 | **Application** | Network service interfaces for user software | HTTP/HTTPS, DNS, SSH, SMTP |\n"
                "| 6 | **Presentation** | Data encryption, serialization, and compression | TLS/SSL, JSON, JPEG |\n"
                "| 5 | **Session** | Dialogue control and session checkpointing | NetBIOS, RPC, Sockets |\n"
                "| 4 | **Transport** | End-to-end delivery and reliability | TCP (Segments), UDP (Datagrams) |\n"
                "| 3 | **Network** | Logical addressing and shortest path routing | IPv4, IPv6, ICMP, OSPF, BGP |\n"
                "| 2 | **Data Link** | Physical frame delivery and MAC addressing | Ethernet (Frames), 802.11 Wi-Fi |\n"
                "| 1 | **Physical** | Transmission of unstructured raw bitstreams | Copper, Fiber Optics, Radio |\n\n"
                "#### 2. TCP 3-Way Handshake (Connection Establishment)\n"
                "1. **Client -> Server (`SYN`)**: Client sends a SYN packet with initial sequence number $ISN_c$.\n"
                "2. **Server -> Client (`SYN-ACK`)**: Server allocates buffers, acknowledges $ACK = ISN_c + 1$, and sends its $ISN_s$.\n"
                "3. **Client -> Server (`ACK`)**: Client acknowledges $ACK = ISN_s + 1$. Connection state transitions to `ESTABLISHED`.\n\n"
                "#### 3. TCP vs. UDP Comparison\n"
                "- **TCP**: Connection-oriented, guaranteed in-order delivery, flow control (Sliding Window), congestion control.\n"
                "- **UDP**: Connectionless, best-effort lightweight datagrams, zero handshake latency. Used in VoIP, DNS, and real-time multiplayer gaming."
            )
        },
        'sorting_algorithms': {
            'keywords': ['sorting', 'quicksort', 'mergesort', 'time complexity', 'sort algorithm'],
            'title': 'Sorting Algorithms: QuickSort vs. MergeSort',
            'content': (
                "### Comparison of Efficient Sorting Algorithms\n\n"
                "#### QuickSort vs. MergeSort Comparison:\n"
                "| Metric | QuickSort | MergeSort |\n"
                "| :--- | :--- | :--- |\n"
                "| **Best Case Time** | $\\mathcal{O}(n \\log n)$ | $\\mathcal{O}(n \\log n)$ |\n"
                "| **Average Case Time** | $\\mathcal{O}(n \\log n)$ | $\\mathcal{O}(n \\log n)$ |\n"
                "| **Worst Case Time** | $\\mathcal{O}(n^2)$ (sorted array with naive pivot) | $\\mathcal{O}(n \\log n)$ guaranteed |\n"
                "| **Auxiliary Space** | $\\mathcal{O}(\\log n)$ call stack (in-place) | $\\mathcal{O}(n)$ auxiliary array |\n"
                "| **Stability** | Not Stable (in standard partition) | **Stable** (preserves equal key order) |\n\n"
                "#### Clean Python QuickSort Implementation:\n"
                "```python\n"
                "def quicksort(arr: list[int]) -> list[int]:\n"
                "    \"\"\"Divide-and-conquer sorting with median-of-three or pivot partitioning.\"\"\"\n"
                "    if len(arr) <= 1:\n"
                "        return arr\n"
                "    \n"
                "    pivot = arr[len(arr) // 2]\n"
                "    left = [x for x in arr if x < pivot]\n"
                "    middle = [x for x in arr if x == pivot]\n"
                "    right = [x for x in arr if x > pivot]\n"
                "    \n"
                "    return quicksort(left) + middle + quicksort(right)\n"
                "\n"
                "# Verification\n"
                "nums = [38, 27, 43, 3, 9, 82, 10]\n"
                "print(quicksort(nums))  # [3, 9, 10, 27, 38, 43, 82]\n"
                "```"
            )
        },
        'oop_design_patterns': {
            'keywords': ['design pattern', 'design patterns', 'singleton', 'factory pattern', 'observer', 'oop', 'solid'],
            'title': 'Software Design Patterns & SOLID Principles',
            'content': (
                "### Essential Object-Oriented Design Patterns\n\n"
                "Design patterns are reusable solutions to commonly occurring software architecture problems.\n\n"
                "#### 1. The SOLID Principles\n"
                "- **S (Single Responsibility)**: A class should have one, and only one, reason to change.\n"
                "- **O (Open/Closed)**: Software entities should be open for extension, but closed for modification.\n"
                "- **L (Liskov Substitution)**: Subtypes must be substitutable for their base types without altering correctness.\n"
                "- **I (Interface Segregation)**: Clients should not be forced to depend on interfaces they do not use.\n"
                "- **D (Dependency Inversion)**: Depend on abstractions rather than concrete implementations.\n\n"
                "#### 2. Factory Pattern Example (Python):\n"
                "```python\n"
                "from abc import ABC, abstractmethod\n"
                "\n"
                "class NotificationService(ABC):\n"
                "    @abstractmethod\n"
                "    def send(self, recipient: str, message: str) -> None:\n"
                "        pass\n"
                "\n"
                "class EmailService(NotificationService):\n"
                "    def send(self, recipient: str, message: str) -> None:\n"
                "        print(f\"Sending Email to {recipient}: {message}\")\n"
                "\n"
                "class SMSService(NotificationService):\n"
                "    def send(self, recipient: str, message: str) -> None:\n"
                "        print(f\"Sending SMS to {recipient}: {message}\")\n"
                "\n"
                "class NotificationFactory:\n"
                "    @staticmethod\n"
                "    def create(channel: str) -> NotificationService:\n"
                "        if channel.lower() == 'email':\n"
                "            return EmailService()\n"
                "        elif channel.lower() == 'sms':\n"
                "            return SMSService()\n"
                "        raise ValueError(f\"Unsupported channel: {channel}\")\n"
                "```"
            )
        },
        'git_version_control': {
            'keywords': ['git', 'version control', 'git branching', 'rebase', 'merge conflict'],
            'title': 'Professional Git Branching and Workflow',
            'content': (
                "### Professional Git Workflows for Developers\n\n"
                "#### 1. Merge vs. Rebase\n"
                "- **`git merge`**: Creates a 3-way merge commit combining branches. Preserves complete, non-linear historical fidelity of branches.\n"
                "- **`git rebase`**: Replays local commits on top of the target base branch. Produces a clean, linear commit history without merge bubbles.\n\n"
                "#### 2. Essential Commands Checklist:\n"
                "```bash\n"
                "# Create and switch to a feature branch\n"
                "git switch -c feature/askspace-chat\n"
                "\n"
                "# Stage and commit changes cleanly\n"
                "git add app/ services/\n"
                "git commit -m \"feat: implement conversation cascade deletion\"\n"
                "\n"
                "# Keep feature branch updated with upstream main\n"
                "git fetch origin\n"
                "git rebase origin/main\n"
                "\n"
                "# Inspect git commit history in graph format\n"
                "git log --oneline --graph --decorate --all\n"
                "```"
            )
        }
    }

    @property
    def provider_name(self) -> str:
        return 'demo'

    @property
    def model_name(self) -> str:
        return 'AskSpace Curated Knowledge Engine'

    @property
    def is_demo(self) -> bool:
        return True

    def generate_reply(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        category: str = 'General'
    ) -> Dict[str, Any]:
        """Generate response by matching curated knowledge base or giving honest explanation."""
        if not messages:
            return {
                'content': "Hello! I am your AskSpace AI assistant. What would you like to explore today?",
                'provider': self.provider_name,
                'model': self.model_name,
                'is_demo': True
            }

        last_user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content', '').lower().strip()
                break

        # Check for matching topic in curated knowledge base
        matched_topic = None
        for key, topic_data in self.KNOWLEDGE_BASE.items():
            for kw in topic_data['keywords']:
                if re.search(r'\b' + re.escape(kw) + r'\b', last_user_message):
                    matched_topic = topic_data
                    break
            if matched_topic:
                break

        if matched_topic:
            content = (
                f"{matched_topic['content']}\n\n"
                "> [!NOTE]\n"
                "> **AskSpace Demo Mode**: This response is provided from the built-in curated academic engine. "
                "To connect live generative AI (Google Gemini or OpenAI), configure `GEMINI_API_KEY` or `OPENAI_API_KEY` in your `.env` file."
            )
        else:
            # Honest explanation for unmapped queries in demo mode
            snippet = last_user_message[:60] if len(last_user_message) > 60 else last_user_message
            content = (
                f"### AskSpace AI — Demo Mode Response\n\n"
                f"You asked: *\"{snippet}\"*\n\n"
                "AskSpace AI is currently running in **Demo Mode** without an active external API key. "
                "In this mode, AskSpace AI provides verified, structured answers for core computer science, software engineering, and MCA curriculum topics.\n\n"
                "#### Try exploring these built-in subjects:\n"
                "- **Algorithms**: Ask about *\"Binary Search\"*, *\"Sorting algorithms\"*, or *\"Time Complexity\"*.\n"
                "- **Web Architecture**: Ask about *\"Flask Architecture\"*, *\"REST API Design\"*, or *\"Application Factory\"*.\n"
                "- **Databases**: Ask about *\"ACID properties\"*, *\"SQL Transactions\"*, or *\"Database Normalization\"*.\n"
                "- **Operating Systems**: Ask about *\"Process vs Thread\"*, *\"Deadlocks\"*, or *\"Virtual Memory\"*.\n"
                "- **Career & Placements**: Ask about *\"MCA Technical Interview preparation\"* or *\"Resume advice\"*.\n\n"
                "#### Want Live Generative AI?\n"
                "Add your API key to `.env`:\n"
                "```bash\n"
                "# In your .env file:\n"
                "AI_PROVIDER=gemini\n"
                "GEMINI_API_KEY=your_gemini_api_key_here\n"
                "```\n"
                "Then restart the application to enjoy live, open-ended responses on any topic!"
            )

        return {
            'content': content,
            'provider': self.provider_name,
            'model': self.model_name,
            'is_demo': True,
            'notice': 'AI-generated content can be inaccurate. Please verify important technical information.'
        }


class GeminiAIProvider(BaseAIProvider):
    """Google Gemini AI integration."""

    def __init__(self, api_key: str, model_name: str = 'gemini-3.5-flash'):
        if not api_key:
            raise AIConfigurationError("GEMINI_API_KEY environment variable is required for Gemini provider.")
        self.api_key = api_key
        self._model = model_name or 'gemini-3.5-flash'

    @property
    def provider_name(self) -> str:
        return 'gemini'

    @property
    def model_name(self) -> str:
        return self._model

    def generate_reply(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        category: str = 'General'
    ) -> Dict[str, Any]:
        """Invoke Gemini generateContent REST endpoint with robust timeout and error handling."""
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent?key={self.api_key}"

        # Build contents structure
        contents = []
        for msg in messages:
            role = 'user' if msg.get('role') == 'user' else 'model'
            contents.append({
                'role': role,
                'parts': [{'text': msg.get('content', '')}]
            })

        payload = {
            'contents': contents,
            'generationConfig': {
                'temperature': 0.7,
                'maxOutputTokens': 2048,
            }
        }
        if system_prompt:
            payload['systemInstruction'] = {
                'parts': [{'text': system_prompt}]
            }

        headers = {'Content-Type': 'application/json'}
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(endpoint, data=req_data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)

                candidates = res_json.get('candidates', [])
                if not candidates:
                    raise AIServiceUnavailableError("Gemini returned an empty response candidate list.")

                candidate = candidates[0]
                parts = candidate.get('content', {}).get('parts', [])
                reply_text = "".join(part.get('text', '') for part in parts)

                return {
                    'content': reply_text,
                    'provider': self.provider_name,
                    'model': self.model_name,
                    'is_demo': False,
                    'notice': 'AI-generated content can be inaccurate. Please verify important technical information.'
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            logger.error(f"Gemini HTTP Error {e.code}: {err_msg}")
            if e.code == 400:
                raise AIServiceUnavailableError(f"Invalid request to Gemini: {e.reason}")
            elif e.code in (401, 403):
                raise AIConfigurationError("Gemini API key is invalid or unauthorized.")
            elif e.code == 429:
                raise AIServiceUnavailableError("Gemini rate limit exceeded. Please wait a moment and try again.")
            else:
                raise AIServiceUnavailableError(f"Gemini API returned HTTP status {e.code}.")
        except urllib.error.URLError as e:
            logger.error(f"Gemini Network Error: {e.reason}")
            raise AIServiceUnavailableError("Could not connect to Gemini service. Check network connectivity.")
        except Exception as e:
            logger.exception("Unexpected error communicating with Gemini")
            raise AIServiceUnavailableError(f"Error communicating with Gemini: {str(e)}")


class OpenAIAIProvider(BaseAIProvider):
    """OpenAI API integration."""

    def __init__(self, api_key: str, model_name: str = 'gpt-4o-mini'):
        if not api_key:
            raise AIConfigurationError("OPENAI_API_KEY environment variable is required for OpenAI provider.")
        self.api_key = api_key
        self._model = model_name or 'gpt-4o-mini'

    @property
    def provider_name(self) -> str:
        return 'openai'

    @property
    def model_name(self) -> str:
        return self._model

    def generate_reply(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        category: str = 'General'
    ) -> Dict[str, Any]:
        """Invoke OpenAI Chat Completions REST endpoint."""
        endpoint = "https://api.openai.com/v1/chat/completions"

        formatted_messages = []
        if system_prompt:
            formatted_messages.append({'role': 'system', 'content': system_prompt})
        for msg in messages:
            formatted_messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })

        payload = {
            'model': self._model,
            'messages': formatted_messages,
            'temperature': 0.7,
            'max_tokens': 2048,
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.api_key}"
        }
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(endpoint, data=req_data, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)

                choices = res_json.get('choices', [])
                if not choices:
                    raise AIServiceUnavailableError("OpenAI returned no completion choices.")

                reply_text = choices[0].get('message', {}).get('content', '')

                return {
                    'content': reply_text,
                    'provider': self.provider_name,
                    'model': self.model_name,
                    'is_demo': False,
                    'notice': 'AI-generated content can be inaccurate. Please verify important technical information.'
                }
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode('utf-8', errors='ignore')
            logger.error(f"OpenAI HTTP Error {e.code}: {err_msg}")
            if e.code in (401, 403):
                raise AIConfigurationError("OpenAI API key is invalid or unauthorized.")
            elif e.code == 429:
                raise AIServiceUnavailableError("OpenAI rate limit or quota exceeded.")
            else:
                raise AIServiceUnavailableError(f"OpenAI API error HTTP {e.code}.")
        except urllib.error.URLError as e:
            logger.error(f"OpenAI Network Error: {e.reason}")
            raise AIServiceUnavailableError("Could not connect to OpenAI service. Check network connectivity.")
        except Exception as e:
            logger.exception("Unexpected error communicating with OpenAI")
            raise AIServiceUnavailableError(f"Error communicating with OpenAI: {str(e)}")


def get_ai_provider(provider_type: Optional[str] = None) -> BaseAIProvider:
    """Factory to obtain configured AI provider with graceful demo fallback."""
    provider = (provider_type or os.environ.get('AI_PROVIDER', 'demo')).lower()

    if provider == 'gemini':
        api_key = os.environ.get('GEMINI_API_KEY', '').strip()
        model = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash').strip()
        if api_key:
            return GeminiAIProvider(api_key=api_key, model_name=model)
        logger.warning("GEMINI_API_KEY not configured. Falling back to DemoAIProvider.")
        return DemoAIProvider()

    elif provider == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY', '').strip()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini').strip()
        if api_key:
            return OpenAIAIProvider(api_key=api_key, model_name=model)
        logger.warning("OPENAI_API_KEY not configured. Falling back to DemoAIProvider.")
        return DemoAIProvider()

    return DemoAIProvider()
