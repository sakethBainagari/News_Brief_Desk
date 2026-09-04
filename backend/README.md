# Backend

## Setup

```bash
cd backend
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy environment file:
```bash
cp ../.env.example .env
```

Run:
```bash
python app.py
```

Health check:
`GET http://localhost:5000/api/health`
