# LockIn - Productivity & Deep Work System

LockIn is a comprehensive, secure, cross-platform productivity application designed to maximize focus (Deep Work) by combating digital distractions. It combines OS-level process monitoring with an advanced server-side gamification engine.

By transforming solitary work into a social, competitive experience, LockIn creates accountability. Users can track their focused time, block distracting applications, compete in real-time rooms, and climb global leaderboards.

---

## 🚀 Core Features

- **OS-Level Focus Tracking:** Actively monitors the foreground window to detect whether the user is on a productive application or a distraction.
- **Social Competitions:** Create private or public focus rooms. Compete with friends to see who can maintain the highest focus score over a defined period.
- **Advanced Gamification:** An algorithmic Stats Engine calculates a "Focus Score" based on productive time vs. distraction penalties. Users unlock achievements and build streaks.
- **Secure Architecture:** Built from the ground up with cybersecurity in mind, featuring end-to-end TLS encryption and hardened database interactions.

---

## 🏗 System Architecture

LockIn employs a robust **Client-Server Architecture**. 

```mermaid
graph TD
    subgraph Client [LockIn Desktop Client (PyQt5)]
        UI[UI Layer: PyQt5 Views & Tabs]
        SM[Session Manager]
        AM[App Monitor & Scanner]
        NC[Network Client]
        
        UI <--> SM
        SM <--> AM
        UI <--> NC
        SM <--> NC
    end

    subgraph Transport [Network Layer]
        TLS[Secure TLS/SSL TCP Socket]
        JSON[4-Byte Length-Prefixed JSON]
    end

    subgraph Server [LockIn Backend Server (Python)]
        SS[Multi-threaded Socket Server]
        SE[Stats Engine]
        DB[(SQLite Database)]
        
        SS <--> SE
        SS <--> DB
    end

    NC <==>|Encrypted TCP| TLS
    TLS <==> JSON
    JSON <==> SS
```

### 1. The Client (Frontend & OS Monitor)
The client is a desktop application that acts as both the user interface and the local telemetry agent.

* **UI Layer (`src/client/ui/`)**: Built using PyQt5. Features a responsive, modern design with a master-detail sidebar layout. It contains specialized tabs for Competitions, Leaderboards, Focus Sessions, and Settings.
* **App Monitor (`src/client/logic/app_monitor.py`)**: Uses OS-level APIs (`psutil`, `pygetwindow`) to track the currently active foreground window every second. It calculates the raw "focus time" vs. "distractions".
* **Network Client (`src/client/logic/network_client.py`)**: Responsible for packing telemetry data into JSON payloads and transmitting them over a secure socket connection.

### 2. The Communication Protocol
Instead of standard HTTP, LockIn utilizes a **custom TCP Socket Protocol** optimized for low-latency state synchronization.
* **Framing:** Every payload is prefixed with a 4-byte structural header indicating the exact byte-length of the incoming JSON message. This prevents TCP stream fragmentation issues.
* **Encryption:** The entire TCP stream is wrapped in an SSL/TLS context, ensuring that no plaintext telemetry or credentials traverse the network.

### 3. The Server (Backend & Data Layer)
The server acts as the authoritative source of truth, validating client telemetry and updating global state.

* **Socket Server (`src/server/socket_server.py`)**: A multi-threaded daemon. Every incoming client connection is dispatched to an isolated worker thread, ensuring the server can handle high concurrency without blocking.
* **Stats Engine (`src/server/logic/stats_engine.py`)**: The brain of the gamification system. It receives raw telemetry (total time, focus time, distraction count) and applies a weighted algorithm (70% focus ratio, 30% distraction penalty) to generate a normalized Focus Score (0-100). It also computes daily streaks.
* **Database Manager (`src/server/database/db_manager.py`)**: Manages the SQLite relational database. It handles complex operations like recalculating competition ranks, updating leaderboard states, and conditionally granting achievements based on historical performance.

---

## 🔒 Security & Cyber Implementations

As a project with a strong cybersecurity focus, LockIn implements several critical defense mechanisms:

1. **Transport Layer Security (TLS):** All client-server communication is encrypted using the `ssl` module, preventing Packet Sniffing and Man-in-the-Middle (MitM) attacks.
2. **SQL Injection (SQLi) Prevention:** The database layer strictly utilizes parameterized queries (`?` placeholders) for all CRUD operations. No raw user input is ever concatenated into SQL strings.
3. **Password Cryptography:** Passwords are never stored in plaintext. They are hashed using the `SHA-256` algorithm (`hashlib`) before being committed to the database.
4. **Data Validation:** The server does not trust client state blindly. The `StatsEngine` recalculates final scores server-side to prevent client-side manipulation of leaderboards.

---

## 🛠 Installation & Setup

LockIn has been stripped of unnecessary virtual environments to provide a seamless, global installation process.

### Prerequisites
* Python 3.8+ installed and added to your system `PATH`.

### Quick Start (Windows)
1. Clone or extract the project directory.
2. Run the provided setup script to install dependencies:
   ```cmd
   install.bat
   ```
   *(This will automatically upgrade pip and install PyQt5, psutil, Pillow, and cryptography).*

### Running the System
You must start the server before launching the client.

**1. Start the Server:**
Open a terminal in the root directory and run:
```cmd
python src/server/socket_server.py
```
*You should see `[INFO] LockIn SECURE TCP server v2 listening on 0.0.0.0:65432`.*

**2. Start the Client:**
Open a separate terminal in the root directory and run:
```cmd
python src/client/main.py
```

---

## 💻 Tech Stack
* **Language:** Python 3
* **GUI Framework:** PyQt5
* **Networking:** Native Python Sockets (`socket`), `ssl`, `json`, `struct`
* **OS Interfacing:** `psutil`, `pygetwindow`
* **Database:** SQLite3
* **Image Processing:** `Pillow` (for dynamic UI asset handling)