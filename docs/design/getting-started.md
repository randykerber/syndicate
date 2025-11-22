# Getting Started with Syndicate

## Prerequisites

- Python 3.12+ with uv package manager
- Node.js 18+ with npm
- Git
- IntelliJ IDEA Ultimate (recommended)

## Environment Setup

1. **Clone and navigate to the project:**
   ```bash
   cd ~/gh/randykerber/syndicate
   ```

2. **Set up environment variables:**
   ```bash
   cp config/shared/.env.example config/shared/.env
   # Edit config/shared/.env with your API keys
   ```

3. **Install Python dependencies:**
   ```bash
   cd python
   uv sync --extra dev
   ```

4. **Install JavaScript dependencies:**
   ```bash
   cd js
   npm install
   ```

## Verification

### Test Python Environment
```bash
cd python
uv run python -m pytest tests/ -v
```

### Test JavaScript Environment  
```bash
cd js
npm test
```

## Development Workflow

1. **Python agents:** Work in `python/src/syndicate/`
2. **JavaScript tools:** Work in `js/src/`
3. **Shared config:** Edit `config/shared/` files
4. **Documentation:** Update `docs/` as needed

## IDE Setup

Open the root `syndicate/` directory in IntelliJ IDEA Ultimate for unified multi-language development.

## Next Steps

- Read `docs/architecture/` for system design
- Explore `docs/workflows/` for usage patterns  
- Check `docs/python/` and `docs/js/` for language-specific guides