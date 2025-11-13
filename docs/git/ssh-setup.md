# SSH Key Setup for GitHub

This guide walks you through setting up SSH authentication with GitHub from within the dev container.

## Prerequisites

- Access to the dev container terminal
- A GitHub account
- Administrative access to your GitHub account settings

## Step 1: Generate SSH Key Pair

From within the dev container terminal, generate a new SSH key pair:

```bash
ssh-keygen -t ed25519 -C "github-key-$(date +%Y%m%d)" -f ~/.ssh/id_ed25519 -N ""
```

This command:
- Uses the Ed25519 algorithm (recommended by GitHub)
- Creates a comment with the current date
- Saves the key to the default location (`~/.ssh/id_ed25519`)
- Uses an empty passphrase for convenience in dev containers

## Step 2: Display Your Public Key

Get your public key to add to GitHub:

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output (it should look like):
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBOsDG/Jp/c4Xc+/dVGN1GiIimRmo56s83GiRFq/Ti0k github-key-20251113
```

## Step 3: Add SSH Key to GitHub

1. Go to [GitHub.com](https://github.com) and sign in
2. Click your profile picture in the top right corner
3. Select **Settings** from the dropdown menu
4. In the left sidebar, click **SSH and GPG keys**
5. Click the **New SSH key** button
6. Fill in the form:
   - **Title**: Give your key a descriptive name (e.g., "Dev Container Key", "Omega Project Key")
   - **Key**: Paste your public key from Step 2
7. Click **Add SSH key**
8. You may be prompted to enter your GitHub password to confirm

## Step 4: Test SSH Connection

Verify that your SSH key is working:

```bash
ssh -T git@github.com
```

You should see a message like:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## Security Notes

- **Private Key Security**: The private key (`~/.ssh/id_ed25519`) should never be shared or copied outside the dev container
- **Key Rotation**: Consider regenerating SSH keys periodically for security
- **Multiple Keys**: You can add multiple SSH keys to your GitHub account for different environments

## Troubleshooting

### Permission Denied (publickey)
If you get a permission denied error:
1. Verify your public key was added correctly to GitHub
2. Check that the SSH agent is running: `eval "$(ssh-agent -s)"`
3. Add your key to the agent: `ssh-add ~/.ssh/id_ed25519`

### Key Already Exists
If you already have an SSH key and want to use it:
1. Check existing keys: `ls -la ~/.ssh/`
2. Use your existing key instead of generating a new one
3. Make sure to use the correct public key file (usually ends with `.pub`)

## Next Steps

Once SSH is configured, you can:
- Clone repositories using SSH URLs (`git@github.com:username/repo.git`)
- Push and pull without entering credentials
- Use Git operations seamlessly within the dev container