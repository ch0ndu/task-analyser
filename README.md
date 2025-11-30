# Smart Task Analyzer

A mini-application that intelligently analyzes, scores, and prioritizes tasks based on urgency, importance, effort, and dependencies.  
This project was built as part of the **Software Development Intern Technical Assessment**.

---

## 🚀 Features

### 🔧 Backend (Django)
- Custom priority scoring algorithm:
  - **Urgency** — near or past-due tasks get higher weight  
  - **Importance** — 1–10 priority scale  
  - **Effort** — lower effort tasks become “quick wins”  
  - **Dependencies** — tasks blocking others are prioritized  
- Detects:
  - Missing or invalid data  
  - Circular dependencies  
- Clean API architecture with separation of logic (`scoring.py`)
- REST Endpoints:
  - `POST /api/tasks/analyze/`
  - `GET /api/tasks/suggest/`

### 💻 Frontend (HTML/CSS/JS)
- Simple and clean interface  
- Add tasks one-by-one or paste bulk JSON  
- Analyze tasks using dropdown strategies:
  - **Fastest Wins**
  - **High Impact**
  - **Deadline Driven**
  - **Smart Balance (default)**  
- Displays:
  - Priority score  
  - Explanation  
  - Color-coded urgency level  
- Smooth API integration using `fetch()`

---

## 📁 Project Structure

task-analyzer/
├── backend/
│ ├── settings.py
│ ├── urls.py
├── tasks/
│ ├── models.py
│ ├── scoring.py
│ ├── views.py
│ ├── urls.py
├── frontend/
│ ├── index.html
│ ├── styles.css
│ └── script.js
├── manage.py
└── README.md

---

## 🧠 Priority Scoring Logic

The scoring algorithm combines:

### 1️⃣ Urgency (40%)
- Past due → highest score  
- Due soon → higher priority  
- Far in future → lower urgency  

### 2️⃣ Importance (30%)
- Directly taken from user scale (1–10)

### 3️⃣ Effort (20%)
- Small tasks get bonus  
- Larger tasks get penalty  
- Formula: `effort_score = 1 / (estimated_hours + 1)`

### 4️⃣ Dependencies (10%)
- Tasks blocking more tasks get extra points  
- Circular dependencies → rejected immediately

👉 Final score = weighted sum of above.

---

## 🧩 Sorting Strategy Modes

| Mode | Logic |
|------|-------|
| **Fastest Wins** | Low-effort tasks first |
| **High Impact** | Importance dominates |
| **Deadline Driven** | Urgency dominates |
| **Smart Balance** | Custom weighted algorithm |

---

## 🔌 API Endpoints

### POST /api/tasks/analyze/

Example Request:
```json
[
  {
    "title": "Fix login bug",
    "due_date": "2025-11-30",
    "estimated_hours": 3,
    "importance": 8,
    "dependencies": []
  }
]
```

Response:
- Sorted tasks with calculated score  
- Explanation for each task  

---

### GET /api/tasks/suggest/

Returns:
- Top 3 tasks  
- Why they were selected  

Example Response:
```json
[
  {
    "title": "Fix login bug",
    "score": 92,
    "reason": "High urgency and high importance"
  }
]
```

---

## ⚙️ Installation & Setup (MacOS)

```
git clone git@github.com:YOUR_USERNAME/task-analyzer.git
cd task-analyzer
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py migrate
```

### 5. Start server
```bash
python manage.py runserver
```

### 6. Open in browser
http://127.0.0.1:8000/

---

## 🧪 Running Tests

```bash
python manage.py test
```
