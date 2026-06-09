# Bluestock Nifty 100 Financial Intelligence Platform (B100)

This repository contains the complete implementation of the **Bluestock Nifty 100 Financial Intelligence Platform (B100)**. The platform extracts raw corporate financial reports, loads them into a structured PostgreSQL Star Schema, executes ML health scoring and anomaly detection, and exposes a user-facing dashboard alongside a secure Channel Partner API.

---

## 🛠️ Tech Stack & Key Components
1. **Core Database**: PostgreSQL (Star Schema with 3 dimensions and 6 facts)
2. **Data Pipeline**: Python, pandas, and SQLAlchemy
3. **ML Analytics Engine**: Pure Python/NumPy calculations for health scoring, anomaly detection, clustering, peer group similarity, and time-series forecasting.
4. **Backend Web App**: Django 4.2 & Django REST Framework (DRF)
5. **Caching & Broker**: Redis & Celery asynchronous task queues
6. **Frontend Display**: Responsive server-rendered HTML templates with Tailwind CSS CDN and Chart.js AJAX graphs.

---

## 📂 Project Directory Structure

```
├── data/
│   ├── raw/                 # Raw corporate finance Excel worksheets (.xlsx)
│   ├── clean/               # Extracted CSV datasets & ML output files
│   ├── schema_notes.md      # Detailed database schema metadata documentation
│   └── power_bi_dax.md      # Ready-to-copy DAX formulas for Power BI
├── etl/
│   ├── 01_extract.py        # Extracts raw Excel data to CSV
│   ├── 02_clean.py          # Data sanitation & initial ratio calculations
│   ├── schema.sql           # Database schema DDL statements
│   └── 03_load_to_warehouse.py # Loader initializing Postgres tables & loading data
├── notebooks/
│   ├── 01_eda.ipynb         # Interactive exploratory data analysis notebook
│   ├── 02_health_scoring.ipynb # Computes composite health scores (0-100)
│   ├── 03_anomaly_detection.ipynb # Z-score and Isolation Forest logic
│   ├── 04_sector_clustering.ipynb # K-Means sector groupings with PCA
│   ├── 05_peer_comparison.ipynb # Cosine similarity peer mapping
│   └── 06_trend_forecasting.ipynb # 1-year revenue forecasts using regression
├── bluestock/               # Django core settings, Celery setup, and URL configurations
├── companies/               # Django app managing financials model and charts views
├── ml_engine/               # Django app exposing Celery task runner & ML DB models
├── api_management/          # Django app handling HMAC signature auth, throttles, and webhooks
├── dashboard/               # Django views rendering HTML template pages
├── templates/               # Responsive HTML templates with AJAX charts
└── tests/                   # Pytest test suite for HMAC auth and endpoints
```

---

## 🚀 Setup & Execution Instructions

### 1. Prerequisites
Ensure you have Python (version 3.10+) installed. Install Postgres and Redis locally, then run:
```bash
pip install -r requirements.txt
```
*(If dependencies are not yet in a file, you can install the critical ones manually: `pip install django djangorestframework drf-spectacular django-redis celery[redis] django-cors-headers bcrypt python-decouple pandas numpy sqlalchemy psycopg2-binary`)*

### 2. Configure Environment variables
Create a `.env` file in the root folder (already created default is provided):
```ini
DATABASE_URL=postgresql://postgres:password@localhost:5432/b100
REDIS_URL=redis://127.0.0.1:6379/1
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Run the ETL Pipeline
1. Run extraction:
   ```bash
   python etl/01_extract.py
   ```
2. Clean data & calculate derived ratios:
   ```bash
   python etl/02_clean.py
   ```
3. Load to local Postgres instance:
   ```bash
   python etl/03_load_to_warehouse.py
   ```

### 4. Execute the ML calculations
Recalculate and generate ML outputs:
```bash
python -c "import os; os.system('python scratch/run_ml_calculations.py')"
```
*(This will generate ML outputs using pure-Python/NumPy scripts to avoid binary/DLL security policy blocks on Windows host runtimes).*

### 5. Launch Django Web server
Run migrations and launch:
```bash
python manage.py migrate
python manage.py runserver
```
Navigate to:
- Frontend Dashboard: `http://127.0.0.1:8000/`
- Interactive OpenAPI Swagger Docs: `http://127.0.0.1:8000/api/v1/schema/swagger-ui/`

### 6. Start Celery Async Workers & Beat Scheduler
```bash
# Start Celery Worker
celery -A bluestock worker -l info

# Start Celery Beat Scheduler
celery -A bluestock beat -l info
```

### 7. Run Django Test Suite
```bash
python manage.py test tests
```

---

## 🔒 Security & Channel Partner API Reference

Authentication is performed via custom **HMAC-SHA256 Signatures**.
Clients must include these headers on all requests to `/api/partner/v1/...`:
- `X-API-Key-ID`: Channel key ID identifier.
- `X-Timestamp`: Unix timestamp of the request.
- `X-Nonce`: Random cryptographic salt string.
- `X-Signature`: Hex digest of `HMAC-SHA256(Timestamp + Nonce, SecretKey)`.

### Registering a New Partner Key
```bash
curl -X POST http://127.0.0.1:8000/api/partner/v1/keys/ \
  -H "Content-Type: application/json" \
  -d '{"partner_name": "Acme Ventures", "tier": "PRO"}'
```
*Saves secret key encrypted using master key in database. Secret key is returned only once.*
