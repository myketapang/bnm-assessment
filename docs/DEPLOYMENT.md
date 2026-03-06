```markdown
# Deployment Guide

## GitHub

1. Create repo at https://github.com/new
2. Name: bnm-assessment
3. Push code:

```bash
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/bnm-assessment.git
git branch -M main
git push -u origin main
```

## Netlify

1. https://netlify.com
2. "New site from Git"
3. Select repository
4. Build command: `npm run build`
5. Publish: `web`
6. Deploy

## GitHub Secrets

Add to repo Settings → Secrets:

```
NETLIFY_AUTH_TOKEN=<your-token>
NETLIFY_SITE_ID=<your-site-id>
```

## Deploy

```bash
git push origin main
```

Auto-deploys via GitHub Actions to Netlify.

## Monitor

- GitHub: Actions tab
- Netlify: Deployments
- Live: https://your-site.netlify.app
```

---

## STEP 4: CREATE EMPTY DIRECTORY MARKER FILES (30 seconds)

These files allow Git to track empty directories.

### Windows:

```batch
type nul > data\raw\.gitkeep
type nul > data\processed\.gitkeep
type nul > outputs\.gitkeep
type nul > logs\.gitkeep
```

### Mac/Linux:

```bash
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch outputs/.gitkeep
touch logs/.gitkeep
```

## STEP 5: VERIFY STRUCTURE (1 minute)

In terminal, check your files exist:

### Windows:
```batch
dir /s | findstr /C:"gitignore" /C:"README" /C:"requirements"
```

### Mac/Linux:
```bash
find . -type f -name "*.py" -o -name "*.json" -o -name "*.toml" | head -20
```