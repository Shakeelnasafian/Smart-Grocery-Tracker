# 🛒 Smart Grocery Tracker

A full-stack grocery management web application built with **FastAPI** (Python) and **Vue 3**. Designed to help individuals track grocery inventory, monitor expiry dates, manage budgets, and reduce food waste.

[![CI/CD](https://github.com/Shakeelnasafian/Smart-Grocery-Tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/Shakeelnasafian/Smart-Grocery-Tracker/actions)

---

## Features

### Core
- **JWT Authentication** — Secure register, login, logout with token blacklisting and expiry
- **Grocery Inventory** — Add, edit, delete, and mark items as consumed
- **Search & Filter** — Real-time search by name, filter by category, show expiring items
- **Pagination** — Handles large inventories cleanly

### Analytics
- **Dashboard** — Total items, spending, waste rate, inventory health
- **Category Breakdown** — Visual breakdown of spending per category
- **Monthly Spending** — 6-month spending trend chart

### Budget Tracker
- Set monthly grocery budgets
- Auto-tracks spending from item prices
- Visual progress bar with over-budget alerts

### Shopping List
- Add items manually or auto-generate from expired/consumed inventory
- Mark items as purchased
- Persistent across sessions

### Expiry Alerts
- Configurable email alerts for items expiring within N days
- Background scheduler runs daily at 08:00
- Real-time expiry warnings on the dashboard

### Food Database Integration
- Search **Open Food Facts** (free, no API key needed) to auto-fill item details
- Barcode lookup endpoint for future mobile integration

### Recipe Suggestions
- Suggests recipes based on your current inventory via **Spoonacular API**
- Works without API key (returns mock suggestions for demo)

### Export
- **CSV export** of your full grocery list

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2 |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Database | SQLite (dev) / PostgreSQL (prod-ready via env var) |
| Migrations | Alembic |
| Scheduler | APScheduler |
| Rate Limiting | SlowAPI |
| HTTP Client | httpx (async) |
| Frontend | Vue 3, Vite, Pinia, Vue Router 4 |
| Styling | Tailwind CSS |
| Testing | Pytest, FastAPI TestClient |
| DevOps | Docker, Docker Compose, GitHub Actions CI/CD |
| Code Quality | flake8, Black, pre-commit hooks |

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

```bash
git clone https://github.com/Shakeelnasafian/Smart-Grocery-Tracker.git
cd Smart-Grocery-Tracker

# Copy and configure environment
cp backend/.env.example backend/.env

# Start everything
docker compose up --build
```

Visit: http://localhost (frontend) | http://localhost:8000/docs (API docs)

---

### Option 2: Manual Setup

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # Edit .env with your settings
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env           # Set VITE_API_URL if needed
npm run dev
```

Visit: http://localhost:5173

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key (change in prod!) | dev key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifespan | `60` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./grocery.db` |
| `SMTP_HOST` | Email server host | `smtp.gmail.com` |
| `SMTP_USER` | Email username | — |
| `SMTP_PASSWORD` | Email password/app-password | — |
| `SPOONACULAR_API_KEY` | Recipe API key (optional) | — |

---

## API Documentation

Interactive docs available at **`http://localhost:8000/docs`** (Swagger UI) when the backend is running.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Create account |
| `POST` | `/token` | Login |
| `POST` | `/logout` | Logout + revoke token |
| `GET` | `/me` | Current user info |
| `GET/POST` | `/grocery/` | List / create grocery items (search, filter, paginate) |
| `PUT/DELETE` | `/grocery/{id}` | Update / delete item |
| `GET` | `/grocery/export/csv` | Download CSV |
| `GET` | `/analytics/` | Full analytics summary |
| `GET/POST` | `/budget/` | List / create monthly budgets |
| `GET/POST` | `/shopping/` | Shopping list |
| `POST` | `/shopping/generate` | Auto-generate from inventory |
| `GET` | `/alerts/expiring` | Items expiring within N days |
| `GET` | `/food/search` | Search Open Food Facts |
| `GET` | `/food/barcode/{code}` | Lookup by barcode |
| `GET` | `/recipes/suggestions` | Recipe suggestions from inventory |

---

## Running Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

---

## Database Migrations (Alembic)

```bash
cd backend

# Run existing migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "description"
```

---

## Project Structure

```
Smart-Grocery-Tracker/
├── backend/
│   ├── app/
│   │   ├── config.py          # Settings from .env
│   │   ├── database.py        # SQLAlchemy engine & session
│   │   ├── models.py          # ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── crud.py            # Database operations
│   │   ├── scheduler.py       # APScheduler expiry alert jobs
│   │   ├── main.py            # FastAPI app, middleware, lifespan
│   │   └── routers/
│   │       ├── auth.py        # Auth endpoints
│   │       ├── grocery.py     # Grocery CRUD + CSV export
│   │       ├── analytics.py   # Analytics summary
│   │       ├── budget.py      # Budget management
│   │       ├── shopping.py    # Shopping list
│   │       ├── alerts.py      # Expiry alerts & settings
│   │       ├── food_api.py    # Open Food Facts integration
│   │       └── recipes.py     # Spoonacular recipe suggestions
│   ├── alembic/               # DB migrations
│   ├── tests/                 # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue  # Main view with search/filter/edit
│   │   │   ├── Analytics.vue  # Charts & spending breakdown
│   │   │   ├── Budget.vue     # Monthly budget tracker
│   │   │   └── Shopping.vue   # Shopping list
│   │   ├── store/auth.js      # Pinia auth store
│   │   └── router/index.js    # Routes with auth guards
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .github/workflows/ci.yml   # GitHub Actions CI/CD
└── .pre-commit-config.yaml
```

---

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Install pre-commit hooks: `pre-commit install`
4. Make changes, run tests: `pytest tests/ -v`
5. Open a Pull Request

---

## License

MIT — free to use for personal and commercial projects.
