# 📱 SociaLink API

**SociaLink** is a modern, lightweight social media API built with **FastAPI**. It supports all essential features for social platforms — posting, liking, commenting, and user management — making it ideal for developers looking to build or extend social apps.

---

## 🚀 Features

- 🔐 **JWT Authentication** – Secure user login and registration
- 📝 **Post Management** – Create, edit, delete, and fetch posts
- 💬 **Comments & Likes** – Engage with posts in real time
- 👥 **User Profiles** – View and manage user-related data
- 📡 **Async-First** – High-performance non-blocking I/O
- ✅ **Test Coverage** – Fully tested with Pytest and HTTPX

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **Database:** SQLite / PostgreSQL (via SQLAlchemy and Databases)
- **Auth:** OAuth2 with JWT Tokens
- **Testing:** Pytest, HTTPX, pytest-anyio
- **ORM:** SQLAlchemy Core
- **Environment:** Pydantic, Uvicorn

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/socialink-api.git
   cd socialink-api

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

3. **Install requirements**
   ```bash
   pip install -r requirements.txt

4. **Run the app locally**
   ```bash
    uvicorn socialink.main:app --reload
5. **Run tests**
   ```
    pytest

## API Documentation

You can access the full API documentation via Postman here:

👉 [SociaLink Documentation](https://documenter.getpostman.com/view/41195518/2sB2j3BBjM)
