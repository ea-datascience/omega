# Git Repository Setup

This guide explains how to set up and connect your local repository to GitHub.

## Prerequisites

- SSH key configured with GitHub (see [SSH Setup Guide](./ssh-setup.md))
- Git initialized in your project directory
- GitHub repository created

## Repository Configuration Steps

### Step 1: Initialize Git Repository

If not already done, initialize Git in your project:

```bash
git init
```

This creates a local Git repository with the default branch name (usually `master`).

### Step 2: Add Remote Origin

Connect your local repository to the GitHub repository:

```bash
git remote add origin git@github.com:username/repository-name.git
```

For this project (omega), the command was:
```bash
git remote add origin git@github.com:ea-datascience/omega.git
```

### Step 3: Stage Files

Add all files to the staging area:

```bash
git add .
```

This stages all files in the current directory and subdirectories for commit.

### Step 4: Create Initial Commit

Create your first commit:

```bash
git commit -m "Initial commit: Add devcontainer configuration"
```

Choose a descriptive commit message that explains what's included in this initial commit.

### Step 5: Push to GitHub

Push your local commits to GitHub and set up tracking:

```bash
git push -u origin master
```

The `-u` flag sets up tracking between your local `master` branch and the remote `origin/master` branch.

## Verification

After pushing, verify your setup:

1. **Check remote configuration**:
   ```bash
   git remote -v
   ```

2. **Check branch tracking**:
   ```bash
   git branch -vv
   ```

3. **Visit your GitHub repository** in a web browser to confirm files were uploaded

## Branch Management

### Using 'main' Instead of 'master'

If you prefer to use `main` as your default branch (GitHub's current standard):

```bash
# Rename the current branch
git branch -m master main

# Update the upstream branch
git push -u origin main

# Optionally, delete the old master branch on GitHub
git push origin --delete master
```

### Setting Default Branch for Future Repositories

Configure Git to use `main` as default for new repositories:

```bash
git config --global init.defaultBranch main
```

## Common Workflow

After initial setup, your typical workflow will be:

```bash
# Make changes to files
# Stage changes
git add .

# Commit changes
git commit -m "Descriptive commit message"

# Push to GitHub
git push
```

## Troubleshooting

### Authentication Issues
- Ensure SSH key is properly configured (see [SSH Setup Guide](./ssh-setup.md))
- Test SSH connection: `ssh -T git@github.com`

### Remote Already Exists
If you get "remote origin already exists":
```bash
# Remove existing remote
git remote remove origin

# Add the correct remote
git remote add origin git@github.com:username/repo.git
```

### Permission Denied
- Verify you have write access to the GitHub repository
- Check that you're using the correct SSH URL format
- Ensure your SSH key is added to your GitHub account

## Repository Information

- **Repository Name**: omega
- **Owner**: ea-datascience  
- **SSH URL**: `git@github.com:ea-datascience/omega.git`
- **HTTPS URL**: `https://github.com/ea-datascience/omega.git`