```markdown
# Installation Guide

## Requirements

- Python 3.9+
- Node.js 14+
- Git

## Steps

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/bnm-assessment.git
cd bnm-assessment
```

### 2. Python Setup

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node Dependencies

```bash
npm install
```

### 5. Test

```bash
pytest tests/ -v
```

### 6. Build

```bash
npm run build
```

## Verify

```bash
python -c "import pandas; print(pandas.__version__)"
pytest --version
node --version
```

All should show version numbers.

## Troubleshooting

- **Virtual env not activating:** Try `pip install --upgrade pip`
- **Module not found:** Ensure venv is activated
- **Permission denied:** On Mac/Linux: `chmod +x venv/bin/activate`
```