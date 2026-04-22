# Workplace Relations Data Pipeline

A scalable, production-grade data pipeline for extracting and transforming legal decisions from the Irish Workplace Relations website.

## 🚀 Overview

This solution implements a two-stage ETL pipeline:
1.  **Ingestion (Landing Zone)**: Uses **Scrapy** to asynchronously crawl and download raw documents (PDF, DOC, HTML) and metadata.
2.  **Transformation (Processed Zone)**: Uses **BeautifulSoup** to clean HTML content, removing boilerplate (nav, footer) and retaining only relevant legal text.

The entire lifecycle is orchestrated via **Dagster**, providing software-defined assets, partitioning, and deep observability.

---

## 🛠 Setup & Run

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.9+

### 2. Infrastructure
Start the database (MongoDB) and object storage (MinIO):
```bash
docker-compose up -d
```

### 3. Setup Environment
Install dependencies and prepare the virtual environment:
```bash
make setup
```

### 4. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
*(Note: .env.example is provided for configuration reference but is untracked by Git for security).*

### 5. Launch the Orchestrator
Start the Dagster development server:
```bash
make dev
```
Open http://localhost:3000 to access the Dagster UI. From here, you can materialize assets for specific partitions (Body + Month).

---

## 🧪 Development Tools

### Testing
Run the unit tests for utility functions and transformation logic:
```bash
make test
```

### Linting & Formatting
Check for code quality and formatting issues:
```bash
make lint
make format
```

---

## 📋 Requirements Mapping

| Requirement | Implementation |
| :--- | :--- |
| **Scrapy Framework** | `src/workplace_relations/spiders/` |
| **Partitioning (Body/Date)** | `src/orchestrator/partitions.py` |
| **Deduplication (SHA-256)** | `src/workplace_relations/pipelines.py` |
| **HTML Cleaning** | `src/pipeline/services/html_cleaner.py` |
| **JSON Logging (#10)** | `src/orchestrator/assets/landing_zone.py` |
| **Architecture Doc** | `ARCHITECTURE.md` (root) |

---

## 🏛 Architecture
For detailed information on design decisions, partitioning strategy, and scaling, see [**ARCHITECTURE.md**](./ARCHITECTURE.md).
