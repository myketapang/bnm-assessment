# 🚀 COMPLETE GITHUB + NETLIFY DEPLOYMENT GUIDE
## From Zero to Production in 15 Minutes

---

## STEP 1: PREPARE YOUR GITHUB REPOSITORY (5 minutes)

### 1.1 Create GitHub Repository

```bash
# Create new directory
mkdir bnm-assessment
cd bnm-assessment

# Initialize Git
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 1.2 Create File Structure

```bash
# Create all directories
mkdir -p .github/workflows
mkdir -p src/{models,analysis,data,visualization}
mkdir -p web/{css,js,api,assets}
mkdir -p tests
mkdir -p data/{raw,processed,external}
mkdir -p outputs/{reports,figures,dashboards}
mkdir -p docs
mkdir -p config
mkdir -p scripts
mkdir -p logs

# Create .gitkeep files
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch outputs/.gitkeep
touch logs/.gitkeep
```

### 1.3 Add All Files (Copy-Paste)

Create each file below in your repository:

```bash
# Example - Create README.md
cat > README.md << 'EOF'
# BNM Data Scientist Assessment

Production-grade analysis suite for...
[copy content from section 2 below]
EOF
```

**REPEAT FOR EACH FILE:**
- README.md
- requirements.txt
- setup.py
- .gitignore
- netlify.toml
- package.json
- src/config.py
- src/utils.py
- src/__init__.py
- web/index.html
- web/css/style.css
- web/js/main.js
- .github/workflows/tests.yml
- .github/workflows/deploy.yml
- docs/DEPLOYMENT.md

### 1.4 Add Files and Commit

```bash
git add .
git commit -m "Initial commit: Production-ready BNM assessment suite"
```

---

## STEP 2: PUSH TO GITHUB (2 minutes)

### 2.1 Create Repository on GitHub.com

1. Go to https://github.com/new
2. Repository name: `bnm-assessment`
3. Description: "Production-grade data science assessment suite"
4. Select: Public (for Netlify deployment)
5. Click "Create repository"

### 2.2 Connect Local to Remote

```bash
# Add remote (copy the URL from GitHub)
git remote add origin https://github.com/YOUR_USERNAME/bnm-assessment.git

# Rename branch to main (if on master)
git branch -M main

# Push to GitHub
git push -u origin main
```

### 2.3 Verify

Go to https://github.com/YOUR_USERNAME/bnm-assessment and confirm files appear

---

## STEP 3: SETUP GITHUB SECRETS (3 minutes)

### 3.1 Generate Netlify Token

1. Go to https://app.netlify.com/account/applications/personal-access-tokens
2. Click "New access token"
3. Name: "GitHub Deploy"
4. Copy the token

### 3.2 Create GitHub Secrets

1. Go to https://github.com/YOUR_USERNAME/bnm-assessment/settings/secrets/actions
2. Click "New repository secret"

**Add these secrets:**

```
Name: NETLIFY_AUTH_TOKEN
Value: [paste token from 3.1]

Name: NETLIFY_SITE_ID
Value: [you'll get this after Netlify deployment]
```

---

## STEP 4: CONNECT TO NETLIFY (3 minutes)

### 4.1 Create Netlify Account

1. Go to https://netlify.com
2. Sign up with GitHub (recommended for easiest setup)

### 4.2 Create New Site

1. Dashboard → "Add new site"
2. Select "Import an existing project"
3. Choose GitHub
4. Select your `bnm-assessment` repository
5. Click "Deploy site"

### 4.3 Get Site ID

1. Go to Site Settings → General
2. Copy "Site ID" (looks like: `abc12def-gh45-ijkl-mn67-opqrs90tuvwx`)
3. Add to GitHub secret `NETLIFY_SITE_ID`

---

## STEP 5: CONFIGURE NETLIFY BUILD (2 minutes)

### 5.1 Build Settings

In Netlify Site Settings:

```
Build command: npm run build
Publish directory: web
Functions directory: web/api
```

### 5.2 Environment Variables

In Netlify Site Settings → Build & deploy → Environment:

```
PYTHON_VERSION = 3.9
NODE_VERSION = 16
ENVIRONMENT = production
LOG_LEVEL = INFO
```

---

## STEP 6: DEPLOY! (Automated)

### 6.1 Push Code to GitHub

```bash
# Make a change (or just re-commit)
git add .
git commit -m "Update: Configure Netlify deployment"
git push origin main
```

### 6.2 Watch Deployments

**GitHub Actions:**
1. Go to your repo → Actions tab
2. See build status
3. Should show ✅ Passed

**Netlify:**
1. Go to https://app.netlify.com
2. Click your site
3. See deployment progress
4. Live site: `https://your-site.netlify.app`

---

## STEP 7: VERIFY DEPLOYMENT (1 minute)

### 7.1 Check Site

Open: https://your-site.netlify.app

You should see:
- ✅ Navigation bar
- ✅ 5 analysis cards
- ✅ Fully responsive design
- ✅ All links working

### 7.2 Check Build Status

**GitHub:** Actions tab should show green ✅  
**Netlify:** Deployments tab should show "Published"

---

## STEP 8: CUSTOM DOMAIN (Optional, 2 minutes)

### 8.1 Add Custom Domain

In Netlify → Site Settings → Domain management:

1. Click "Add custom domain"
2. Enter your domain (e.g., `bnm-assessment.com`)
3. Follow DNS configuration instructions
4. Wait for DNS propagation (5-30 minutes)

### 8.2 Update DNS

At your domain registrar:

```
CNAME record:
Host: www
Points to: your-site.netlify.app
```

---

## CONTINUOUS DEPLOYMENT

### How It Works

```
You push code to GitHub
        ↓
GitHub Actions runs tests
        ↓
If tests pass, auto-deploy to Netlify
        ↓
Site updates at https://your-site.netlify.app
```

### Monitor Deployments

**GitHub Actions:** https://github.com/YOUR_USERNAME/bnm-assessment/actions  
**Netlify Deploy Log:** https://app.netlify.com/sites/YOUR_SITE/deploys

---

## TROUBLESHOOTING

### Build Fails on Netlify

```bash
# Check locally first
npm install
npm run build

# Review logs at: Netlify → Deploys → View log
```

### Site Not Updated

- Wait 30 seconds after push
- Hard refresh (Ctrl+Shift+R)
- Check Netlify deploy status
- Check GitHub Actions status

### 404 Errors

- Ensure file paths are correct
- Check netlify.toml configuration
- Verify publish directory is `web`

### Environment Variables Not Working

- Netlify → Build & deploy → Environment
- Redeploy after adding variables
- Use `process.env.VARIABLE_NAME` in code

---

## POST-DEPLOYMENT CHECKLIST

- [ ] Site loads without errors
- [ ] All pages accessible
- [ ] Dashboard displays correctly
- [ ] Mobile responsive
- [ ] GitHub Actions passing
- [ ] Netlify deploy successful
- [ ] Domain configured (if custom)
- [ ] SSL/TLS enabled (automatic)
- [ ] Analytics enabled (optional)

---

## MONITORING & MAINTENANCE

### Daily

- Monitor GitHub Actions for failed tests
- Check Netlify analytics for traffic

### Weekly

- Review error logs
- Update dependencies (npm/pip)
- Test new features

### Monthly

- Security scan
- Performance audit
- Backup important data

---

## ROLLBACK DEPLOYMENT

If something breaks:

```bash
# GitHub
git revert HEAD
git push origin main

# Or Netlify
Go to Deploys → Click previous version → "Publish deploy"
```

---

## ANALYTICS & MONITORING

### Google Analytics (Optional)

```html
<!-- Add to web/index.html <head> -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Sentry Error Tracking (Optional)

```bash
npm install @sentry/browser
```

---

## SECURITY BEST PRACTICES

### GitHub

- ✅ Enable 2FA on GitHub account
- ✅ Use SSH keys (not HTTPS with passwords)
- ✅ Review secrets regularly
- ✅ Limit repository collaborators

### Netlify

- ✅ Use OAuth2 (GitHub auth)
- ✅ Enable netlify.toml for consistency
- ✅ Regular security audits
- ✅ Monitor API access

### Code

- ✅ Run security scan: `npm audit`
- ✅ Keep dependencies updated
- ✅ Never commit secrets (use .env)
- ✅ Use environment variables for sensitive data

---

## PERFORMANCE OPTIMIZATION

### Web Optimization

```html
<!-- Compress images -->
<!-- Use modern formats (webp) -->
<!-- Minify CSS/JS -->
<!-- Enable gzip on Netlify (automatic) -->
```

### Database (if applicable)

```
- Use connection pooling
- Enable query caching
- Index frequently searched columns
```

### CDN

Netlify automatically uses:
- Global edge servers
- Automatic minification
- Cache busting

---

## QUICK REFERENCE

### Useful URLs

```
GitHub Repo: https://github.com/YOUR_USERNAME/bnm-assessment
Live Site: https://your-site.netlify.app
GitHub Actions: https://github.com/YOUR_USERNAME/bnm-assessment/actions
Netlify Dashboard: https://app.netlify.com
```

### Common Commands

```bash
# Development
npm start
npm run dev
python -m pytest

# Deployment
git push origin main
netlify deploy --prod

# Troubleshooting
netlify logs
npm audit
pip freeze
```

---

## 🎉 YOU'RE LIVE!

Your site is now:
- ✅ Deployed on Netlify
- ✅ Auto-updating from GitHub
- ✅ Tested automatically
- ✅ Production-ready
- ✅ Globally distributed

**Next Steps:**
1. Share the link: `https://your-site.netlify.app`
2. Monitor analytics
3. Gather feedback
4. Iterate and improve

---

## SUPPORT

- GitHub Issues: Report bugs
- Netlify Support: https://netlify.com/support
- Email: hocc@bnm.gov.my

**Happy deploying! 🚀**
