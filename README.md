# GitHub Repository Creator for Hackathon Teams

This Python script automates the creation of GitHub repositories for hackathon teams using a template repository and adds team leaders to their respective repositories based on data from an Excel file.

## Features

- 🔗 Connects to GitHub organization using personal access token
- 📁 Creates repositories from a template repository
- 👥 Adds team leaders to their respective repositories
- 📊 Reads team data from Excel file
- 📝 Comprehensive logging and error handling
- ⚙️ Configurable settings via environment variables

## Prerequisites

1. **Python 3.7+** installed on your system
2. **GitHub Personal Access Token** with organization permissions
3. **Template repository** in your GitHub organization
4. **Excel file** with team data

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Setup

### 1. GitHub Token Setup

Create a GitHub Personal Access Token:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate a new token with the following permissions:
   - `repo` (Full control of private repositories)
   - `admin:org` (Full control of organizations and teams)
   - `user` (Update user profile)

### 2. Environment Configuration

Create a `.env` file in the project root with your configuration:

```bash
# Copy the example file
cp env_example.txt .env
```

Edit the `.env` file with your actual values:

```env
# GitHub Configuration
GITHUB_TOKEN=your_actual_github_token_here
GITHUB_ORG_NAME=your-organization-name
TEMPLATE_REPO_NAME=hackathon_template

# Excel Configuration
EXCEL_FILE_PATH=teams_data.xlsx
TEAM_NAME_COLUMN=team_name
LEADER_EMAIL_COLUMN=leader_email

# Repository Configuration
REPO_PREFIX=hackathon-
REPO_DESCRIPTION=Hackathon project repository
REPO_VISIBILITY=private

# User Permission Configuration
DEFAULT_PERMISSION=push
```

### 3. Prepare Team Data

Create an Excel file (`teams_data.xlsx`) with the following structure:

| team_name | leader_email |
|-----------|--------------|
| Team Alpha | alpha@example.com |
| Team Beta | beta@example.com |
| Team Gamma | gamma@example.com |

Or use the helper script to create a sample file:

```bash
python create_sample_excel.py
```

### 4. Template Repository

Ensure you have a template repository in your GitHub organization:
- Repository should be named as specified in `TEMPLATE_REPO_NAME`
- Repository should be marked as a template repository in GitHub settings

## Usage

### Basic Usage

Run the main script:

```bash
python github_repo_creator.py
```

### Create Sample Data

Generate a sample Excel file for testing:

```bash
python create_sample_excel.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | Required |
| `GITHUB_ORG_NAME` | GitHub organization name | Required |
| `TEMPLATE_REPO_NAME` | Template repository name | `hackathon_template` |
| `EXCEL_FILE_PATH` | Path to Excel file | `teams_data.xlsx` |
| `TEAM_NAME_COLUMN` | Excel column name for team names | `team_name` |
| `LEADER_EMAIL_COLUMN` | Excel column name for leader emails | `leader_email` |
| `REPO_PREFIX` | Prefix for created repositories | `hackathon-` |
| `REPO_DESCRIPTION` | Description for created repositories | `Hackathon project repository` |
| `REPO_VISIBILITY` | Repository visibility (`private`/`public`) | `private` |
| `DEFAULT_PERMISSION` | Permission level for added users | `push` |

### Permission Levels

- `pull`: Can pull (read) but not push (write)
- `push`: Can pull and push (read and write)
- `admin`: Can pull, push and administer the repository
- `maintain`: Can manage the repository without access to sensitive or destructive actions
- `triage`: Can manage issues and pull requests without write access

## Output

The script provides:

- **Console output**: Real-time progress and status messages
- **Log file**: Detailed logs saved to `github_repo_creator.log`
- **Repository creation**: New repositories created from template
- **User invitations**: Team leaders added to their repositories

## Error Handling

The script includes comprehensive error handling:

- **Rate limiting**: Automatic delays between API calls
- **Duplicate repositories**: Skips existing repositories
- **Invalid users**: Logs warnings for users not found
- **Network errors**: Retries with exponential backoff
- **Validation**: Checks for required files and permissions

## Troubleshooting

### Common Issues

1. **"GitHub token is required"**
   - Ensure your `.env` file contains a valid `GITHUB_TOKEN`

2. **"Template repository not found"**
   - Verify the template repository exists and is named correctly
   - Check that the repository is marked as a template

3. **"Excel file not found"**
   - Ensure the Excel file exists at the specified path
   - Check the `EXCEL_FILE_PATH` configuration

4. **"Could not find GitHub user"**
   - Verify the email addresses in your Excel file
   - Ensure users have public GitHub profiles or are organization members

5. **"Permission denied"**
   - Check that your GitHub token has sufficient permissions
   - Verify you have admin access to the organization

### Debug Mode

For detailed debugging, you can modify the logging level in `github_repo_creator.py`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for sensitive data
- Regularly rotate your GitHub personal access token
- Grant minimum required permissions to the token

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.