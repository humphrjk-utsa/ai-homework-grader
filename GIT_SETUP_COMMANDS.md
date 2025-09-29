# Git Setup Commands for New Repository

## 🔧 Handling the Remote Issue

The error "remote upstream already exists" means you're in an existing git repository. Here's how to properly set up your new repository:

## 📋 Option 1: Create Fresh Repository (Recommended)

### Step 1: Navigate to homework_grader directory
```bash
cd homework_grader
```

### Step 2: Check if it's already a git repository
```bash
ls -la  # Look for .git directory
```

### Step 3: If .git exists, remove it to start fresh
```bash
rm -rf .git  # On Windows: rmdir /s .git
```

### Step 4: Initialize new repository
```bash
git init
git add .
git commit -m "Initial commit: AI-powered homework grader"
```

### Step 5: Add your new repository as origin
```bash
# Replace YOUR_USERNAME and YOUR_REPO_NAME with actual values
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 📋 Option 2: Work with Existing Remotes

If you want to keep the existing git history:

### Check current remotes
```bash
git remote -v
```

### Remove existing upstream if needed
```bash
git remote remove upstream
```

### Add your new repository
```bash
git remote add upstream https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

### Or rename origin to upstream
```bash
git remote rename origin upstream
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO.git
```

## 📋 Option 3: Copy Files to New Directory (Cleanest)

### Step 1: Create new directory outside current repo
```bash
cd ..
mkdir ai-homework-grader
cd ai-homework-grader
```

### Step 2: Copy homework_grader contents
```bash
# Copy all files from homework_grader to current directory
cp -r ../Data-Management-Assignment-1-Intro-to-R/homework_grader/* .
```

### Step 3: Initialize fresh git repository
```bash
git init
git add .
git commit -m "Initial commit: AI-powered homework grader with comprehensive feedback

Features:
- Two-model AI grading system (Qwen 3.0 + Gemma 3.0)
- Comprehensive feedback with 6 detailed sections
- Professional PDF reports with R code examples
- Modern Streamlit web interface
- AI training and correction system
- Cross-platform support (Windows/Mac)
- Clean, modular architecture"

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## 🎯 Recommended Approach

**I recommend Option 3** (copy to new directory) because:
- ✅ Clean git history starting from your homework grader
- ✅ No conflicts with existing remotes
- ✅ Clear separation from original repository
- ✅ Professional commit history for new repo

## 📝 Sample Commands for Windows

If you're on Windows and git commands aren't working in PowerShell:

### Using Git Bash (recommended)
1. Open Git Bash (comes with Git for Windows)
2. Navigate to your directory
3. Run the git commands above

### Using Command Prompt
```cmd
cd homework_grader
git init
git add .
git commit -m "Initial commit: AI-powered homework grader"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Using GitHub Desktop
1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose homework_grader folder
4. Create repository on GitHub.com
5. Publish repository from GitHub Desktop

## 🚀 After Repository Creation

Once your repository is created:

### Add repository topics/tags
- ai
- education
- grading
- streamlit
- python
- machine-learning
- automation

### Update README with correct repository URL
Replace placeholder URLs in README.md with your actual repository URL.

### Create first release
```bash
git tag -a v1.0.0 -m "First release: Complete AI homework grader"
git push origin v1.0.0
```

## 🎉 Success!

Your homework grader will be a standalone, professional repository ready for:
- ⭐ GitHub stars and forks
- 🤝 Community contributions
- 📦 Package distribution
- 🚀 Production deployment
- 📚 Educational use

The repository contains everything needed for a complete, professional AI grading system! 🎓