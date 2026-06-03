# EventLens AI

### AI-Powered Event Photo Retrieval Platform (v2.0)

EventLens AI is a modern cloud-based event photography platform that enables photographers, agencies, and event organizers to automatically organize and deliver photos to attendees using facial recognition. 

Attendees can scan a custom event QR code and upload a selfie to find all of their photos in under 2 seconds.

---

## Technical Architecture

The codebase is split into two primary components:
1. **FastAPI Backend (`/backend`)**: Handles database schema migrations, JWT security/RBAC, S3 pre-signed upload URL generation, pgvector cosine search, and triggers the background face extraction job.
2. **Streamlit Frontend (`/frontend`)**: Provides clean dashboards for organizers (uploading files, viewing analytics) and an interface for guests (uploading a selfie and downloading matched photo streams).

```
                      +-----------------------------+
                      |      Streamlit Frontend     |
                      +--------------+--------------+
                                     |
                                     | (HTTP Requests)
                                     v
                      +--------------+--------------+
                      |       FastAPI Backend       |
                      +-------+--------------+------+
                              |              |
           (Queue upload job) |              | (pgvector search)
                              v              v
      +-----------------------+---+      +---+---------------------+
      |           Redis           |      |  PostgreSQL + pgvector  |
      +-----------------------+---+      +---+---------------------+
                              |              ^
            (Fetch job batch) |              | (Save face embeddings)
                              v              |
      +-----------------------+---+          |
      |       Celery Worker       +----------+
      | (RetinaFace + ArcFace)    |
      +-----------------------+---+
                              |
                              | (Original Image Preservation)
                              v
                      +-------+-------------+
                      |  MinIO / AWS S3     |
                      +---------------------+
```

---

## File Structure

```text
e:/Projects/eventSNAP1/
├── docker-compose.yml       # Docker orchestrator for all databases, queues, and services
├── .env.example             # Template for all environment variables
├── README.md                # System documentation
├── backend/                 # Backend FastAPI directory
│   ├── Dockerfile
│   ├── requirements.txt     # Backend framework dependencies
│   ├── requirements-ai.txt  # TensorFlow, Scikit-Learn, and InsightFace libraries
│   └── app/
│       ├── main.py          # FastAPI application entrypoint and startup events
│       ├── api/
│       │   └── routes/      # Routers for auth, events, photos, search, and analytics
│       ├── core/            # Configuration management, JWT security, and S3 manager
│       ├── db/              # Session factory and declarative base
│       ├── models/          # Users, Events, Photos, Faces, and Person clusters
│       ├── schemas/         # Pydantic data schemas
│       └── services/        # AI pipelines, HDBSCAN clustering, and pgvector queries
└── frontend/                # Frontend Streamlit directory
    ├── Dockerfile
    ├── requirements.txt     # Frontend dependencies
    ├── app.py               # Main page layout and URL param router
    ├── components/          # Views for Auth, Dashboard, Event List, and Guest portal
    └── utils/               # API communications wrapper
```

---

## Key Features

1. **Upload Pipeline (Queue-based)**: Photographers request pre-signed PUT URLs from the backend and upload directly to storage, avoiding memory bottlenecks on the API layer. A Celery worker processes photos in 128-image batches:
   - **RetinaFace**: Bounding box extraction and eye landmark detection.
   - **Face Alignment**: Affine transformation based on eye coordinates.
   - **Quality Filter**: Blur detection via Laplacian variance and face size boundaries to exclude tiny background faces.
   - **ArcFace**: Generates a 512-D unit-normalized face embedding.
2. **Background Clustering**: An asynchronous clustering task grouping face embeddings within the *same* event using **HDBSCAN** (with a **DBSCAN** fallback). This builds a `person_id` mapping.
3. **Event Isolation Engine**: Strict multi-tenant data isolation. All search operations and database queries require and filter on `event_id` to guarantee zero cross-event face leakage.
4. **Vector Search Engine**: Guests upload a selfie to perform a **pgvector** cosine search. The engine identifies matching faces, expands them to find all photos in their associated person cluster, and returns the unified gallery in under 2 seconds.

---

## Quick Start Setup

### Prerequisites
Make sure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

### Setup Steps
1. **Copy the Environment Variables Template**:
   ```bash
   cp .env.example .env
   ```
2. **Spin up the Services via Docker Compose**:
   ```bash
   docker-compose up --build
   ```
3. **Access the Portals**:
   - Streamlit Frontend: `http://localhost:8501`
   - FastAPI Interactive Swagger Docs: `http://localhost:8000/docs`
   - MinIO Object Storage Console: `http://localhost:9001`
