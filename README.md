# CI/CD Pipeline with GitHub Actions

A production-grade CI/CD pipeline that takes a containerized Python API through seven automated stages — from code linting all the way to pushing a scanned, tested image to a container registry. Built entirely on GitHub Actions, no external CI server needed.

![Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Multi--Stage-0db7ed?logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776ab?logo=python&logoColor=white)
![Security](https://img.shields.io/badge/Security-Trivy-1904DA?logo=aqua&logoColor=white)

---

## What This Does

Every push to `main` triggers a seven-stage pipeline that mirrors how real engineering teams ship software:

```
Code Push
  │
  ├─► Lint (Flake8 + Pylint)
  │
  ├─► Unit Tests (Pytest + Coverage)
  │
  ├─► Dockerfile Lint (Hadolint)
  │
  ├─► Build (Multi-stage Docker image)
  │
  ├─► Security Scan (Trivy — checks for CVEs)
  │
  ├─► Integration Test (spin up container, hit endpoints)
  │
  └─► Push to GitHub Container Registry (only on main)
```

Each stage has to pass before the next one runs. If Trivy finds a critical vulnerability, the pipeline stops. If a unit test fails, nothing gets built. This is how you keep bad code out of production.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Repository                      │
│                                                          │
│   app.py ── Dockerfile ── tests/ ── .github/workflows/   │
└──────────────┬───────────────────────────────────────────┘
               │ git push / PR
               ▼
┌──────────────────────────────────────────────────────────┐
│                  GitHub Actions Runner                     │
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────────┐             │
│  │  LINT   │  │  TEST   │  │ DOCKERFILE   │             │
│  │ Flake8  │─►│ Pytest  │  │    LINT      │             │
│  │ Pylint  │  │ Coverage│  │  Hadolint    │             │
│  └─────────┘  └────┬────┘  └──────┬───────┘             │
│                     │              │                      │
│                     ▼              ▼                      │
│              ┌─────────────────────────┐                 │
│              │     BUILD IMAGE         │                 │
│              │  Multi-stage Dockerfile │                 │
│              └───────────┬─────────────┘                 │
│                          │                               │
│               ┌──────────┴──────────┐                    │
│               ▼                     ▼                    │
│     ┌──────────────┐    ┌────────────────┐               │
│     │ SECURITY     │    │ INTEGRATION    │               │
│     │ SCAN (Trivy) │    │ TEST           │               │
│     │ CVE Check    │    │ HTTP Endpoints │               │
│     └──────┬───────┘    └───────┬────────┘               │
│            │                    │                         │
│            └────────┬───────────┘                         │
│                     ▼                                    │
│           ┌───────────────────┐                          │
│           │  PUSH TO GHCR    │ (main branch only)        │
│           │  Tagged + Latest  │                          │
│           └───────────────────┘                          │
└──────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages Explained

### 1. Code Quality (Lint)
Runs **Flake8** for style violations and **Pylint** for code analysis. The pipeline fails if code quality drops below a 7.0 score — keeps things clean without being unreasonable.

### 2. Unit Tests
Runs the full test suite with **Pytest** and generates a coverage report. Tests check every endpoint for correct status codes, JSON structure, and response values.

### 3. Dockerfile Lint
**Hadolint** checks the Dockerfile against best practices — things like running as non-root, avoiding unnecessary packages, and proper layer ordering. Catches issues before they become security problems.

### 4. Build
Creates the Docker image using a **multi-stage build**. The first stage installs dependencies, the second stage copies only what's needed into a slim production image. Result: smaller image, smaller attack surface.

### 5. Security Scan
**Trivy** scans the built image for known vulnerabilities (CVEs). If it finds anything rated CRITICAL or HIGH, the pipeline stops. No exceptions.

### 6. Integration Test
Spins up the actual container, waits for it to boot, then hits the real HTTP endpoints. Validates that the health check returns 200 and the API response has the expected structure. This catches issues that unit tests miss — port binding, environment variables, container startup.

### 7. Push to Registry
Only runs on the `main` branch. Tags the image with both the commit SHA and `latest`, then pushes to GitHub Container Registry. Every deploy is traceable back to a specific commit.

---

## Project Structure

```
cicd-pipeline/
├── .github/
│   └── workflows/
│       └── pipeline.yml        # The full CI/CD workflow
├── tests/
│   └── test_app.py             # Unit tests (5 test cases)
├── app.py                      # Flask API (3 endpoints)
├── Dockerfile                  # Multi-stage production build
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```

---

## The Application

A simple Flask API with three endpoints. The point isn't the app — it's the pipeline around it. But even the app follows good practices:

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Returns service info, version, and health status |
| `GET /health` | Dedicated health check (used by Docker HEALTHCHECK) |
| `GET /api/info` | Returns metadata about the service |

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Srj0210/cicd-pipeline.git
cd cicd-pipeline

# Run with Docker
docker build -t cicd-demo .
docker run -p 5000:5000 cicd-demo

# Test it
curl http://localhost:5000/health

# Run tests
pip install -r requirements.txt
pytest tests/ -v
```

---

## Key Decisions

**Why multi-stage Docker builds?**
The builder stage pulls in all the tooling needed to install dependencies. The production stage only copies the installed packages. The final image is ~150MB instead of ~900MB, and it doesn't include pip, gcc, or anything an attacker could use.

**Why Trivy over Snyk or Grype?**
Trivy is open-source, fast, and doesn't need an API key. It scans both OS packages and application dependencies in a single pass. For a pipeline that runs on every push, speed matters.

**Why integration tests in the pipeline?**
Unit tests mock everything. Integration tests prove the container actually boots, binds to the right port, and responds to HTTP requests. I've seen plenty of apps that pass unit tests but fail in a container because of a missing environment variable.

**Why non-root user in Docker?**
If someone compromises the application, they get `appuser` permissions instead of `root`. It's a two-line change in the Dockerfile that makes a real difference.

---

## Technologies

- **Python 3.11** + Flask — lightweight API
- **Docker** — multi-stage builds with health checks
- **GitHub Actions** — 7-stage CI/CD pipeline
- **Pytest** — unit testing with coverage
- **Trivy** — container vulnerability scanning
- **Hadolint** — Dockerfile best practice linting
- **Flake8 + Pylint** — code quality enforcement
- **GitHub Container Registry** — image storage

---

## Author

**Suraj Maitra** — Cloud & DevOps Engineer
- GitHub: [Srj0210](https://github.com/Srj0210)
- LinkedIn: [suraj-maitra](https://linkedin.com/in/suraj-maitra-066934161)
