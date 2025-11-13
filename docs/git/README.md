# Git Documentation

This section contains comprehensive guides for Git and GitHub setup within the development container environment.

## Quick Start

For new users, follow these guides in order:

1. **[SSH Key Setup](./ssh-setup.md)** - Configure SSH authentication with GitHub
2. **[Repository Setup](./repository-setup.md)** - Connect local repository to GitHub

## What's Included

### SSH Key Setup (`ssh-setup.md`)
Complete guide for generating SSH keys within the dev container and configuring them with GitHub for secure, passwordless authentication.

**Key Topics:**
- Generating Ed25519 SSH key pairs
- Adding public keys to GitHub
- Testing SSH connections
- Security best practices
- Troubleshooting common issues

### Repository Setup (`repository-setup.md`)
Step-by-step instructions for initializing Git repositories and connecting them to GitHub.

**Key Topics:**
- Git repository initialization
- Remote origin configuration
- Staging and committing files
- Pushing to GitHub
- Branch management
- Common workflows

## Prerequisites

- Development container environment
- GitHub account with appropriate permissions
- Basic familiarity with terminal/command line

## Security Considerations

- SSH private keys remain within the dev container and should never be shared
- Public keys can be safely added to multiple GitHub accounts or services
- Consider key rotation for enhanced security
- Use descriptive names for SSH keys to track their usage

## Additional Resources

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Git Official Documentation](https://git-scm.com/doc)
- [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)

## Support

If you encounter issues not covered in these guides:
1. Check the troubleshooting sections in each guide
2. Verify your development environment setup
3. Consult the official GitHub and Git documentation
4. Consider regenerating SSH keys if authentication issues persist