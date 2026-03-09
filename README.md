# image-gen-4-all
free image gen

## Documentation

- [HART-Morphosis docs](docs/index.md)
- [Enterprise-grade review & roadmap](docs/enterprise_roadmap.md)
- [API Reference](docs/api_reference.md)

## Quick Start

### CLI

```bash
pip install -r requirements.txt
python -m src.hart_morphosis.cli.main --prompt "face in galaxy" --zoom 4
```

### FastAPI Backend

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
# API docs at http://localhost:8000/docs
```

### Next.js UI

```bash
# In one terminal — start the backend
uvicorn api.main:app --port 8000 --reload

# In another terminal — start the UI
cd ui
npm install
npm run dev
# Open http://localhost:3000
```

### Legacy Streamlit UI

```bash
cd web_ui
streamlit run app.py
# Open http://localhost:8501
```

