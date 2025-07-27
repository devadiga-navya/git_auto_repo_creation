# GitHub Repository Creator for Hackathon Teams

A simple and reliable Python script to create GitHub repositories for hackathon teams and add team leaders as collaborators.

## 🚀 Quick Start

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure Environment**
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env with your settings
# GITHUB_TOKEN=your_github_token
# GITHUB_ORG_NAME=your-organization-name
# TEMPLATE_REPO_NAME=your-template-repo
```

### 3. **Prepare Team Data**
Create `teams_data.xlsx` with this structure:
| team_name | leader_email |
|-----------|--------------|
| Team Alpha | devadiga-navya |
| Team Beta | another-user |

### 4. **Run the Script**
```bash
python simple_repo_creator.py
```

## 📁 Repository Structure

```
git_auto_repo_creation/
├── simple_repo_creator.py    # Main script (recommended)
├── quick_setup.py           # Alternative with org membership
├── add_users_manually.py    # Manual user addition tool
├── get_github_usernames.py  # Username helper tool
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── env_example.txt         # Environment variables template
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── teams_data.xlsx         # Your team data (not in repo)
```

## 🛠️ Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `simple_repo_creator.py` | **Main script** - Creates repos and adds users | **Recommended for most cases** |
| `quick_setup.py` | Alternative with organization membership | If you need org membership too |
| `add_users_manually.py` | Manual user addition | For troubleshooting |
| `get_github_usernames.py` | Username helper | To create username templates |

## ⚙️ Configuration

### Environment Variables (.env file)
```env
# Required
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_ORG_NAME=your-organization-name
TEMPLATE_REPO_NAME=your-template-repo

# Optional
REPO_PREFIX=hackathon-
REPO_VISIBILITY=private
DEFAULT_PERMISSION=push
SCRIPT_GIT_USER_NAME=Hackathon Organizer
SCRIPT_GIT_USER_EMAIL=organizer@hackathon.com
```

### Excel File Format
- **team_name**: Team name (used for repository naming)
- **leader_email**: GitHub username of team leader

## 🎯 What the Script Does

1. **Creates repositories** from template (or empty if template fails)
2. **Adds team leaders** as repository collaborators with push permissions
3. **Handles errors gracefully** and provides clear feedback
4. **Uses custom Git user** to avoid showing your name in commits

## 🔧 Troubleshooting

### Common Issues

1. **"Template repository not found"**
   - Ensure your template repository exists and is named correctly
   - Check the `TEMPLATE_REPO_NAME` in your `.env` file

2. **"User not found"**
   - Use GitHub usernames instead of emails
   - Verify the username exists on GitHub

3. **"Permission denied"**
   - Check your GitHub token has organization permissions
   - Ensure you have admin access to the organization

### Debug Steps
```bash
# Test your setup
python get_github_usernames.py

# Run the main script
python simple_repo_creator.py

# Manual addition if needed
python add_users_manually.py
```

## 🔒 Security Notes

- Never commit your `.env` file
- Use environment variables for sensitive data
- Regularly rotate your GitHub token
- Grant minimum required permissions

## 📝 Output

The script provides:
- **Console output**: Real-time progress and status
- **Log file**: Detailed logs saved to `simple_repo_creator.log`
- **Repository creation**: New repositories created from template
- **User invitations**: Team leaders added as collaborators

## 🎉 Success Example

```
✅ Simple repository creation completed successfully!
🎉 Repositories created and users added!
📝 Note: Users were not added to the organization (use manual invitation if needed)
```

## 📄 License

This project is open source and available under the MIT License.