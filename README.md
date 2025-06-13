# LinkedIn-Comment

A Python automation tool to generate and post professional comments on LinkedIn posts using AI.

## Features

- Scrapes latest posts from specified LinkedIn profiles using Selenium
- Generates thoughtful, context-aware comments using HuggingFace or OpenAI models
- Saves results to CSV for easy review

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd LinkedIn-Comment
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root with your credentials:

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
# Optional: For OpenAI
OPENAI_API_KEY=your_openai_key
# Optional: For HuggingFace
HuggingFACE_API_KEY=your_huggingface_key
```

## Usage

### Run the main automation script

```bash
python linkedin_commenter.py
```

- The script will log in to LinkedIn, fetch the latest post from each profile in `LINKEDIN_PROFILE_URLS`, generate a comment, and save results to `linkedin_comments.csv`.

### Customization

- Edit `LINKEDIN_PROFILE_URLS` in `linkedin_commenter.py` to target different profiles.
- The comment generation logic can be customized in `caption_to_comment.py`.

## Workflow

1. The script logs in to LinkedIn using Selenium and your credentials.
2. It navigates to each profile, scrapes the latest post, and copies the post link.
3. It generates a comment using either HuggingFace or OpenAI (if API key is provided).
4. Results are saved to `linkedin_comments.csv`.

## Notes

- Use a dedicated LinkedIn account for automation to avoid account restrictions.
- For best results, use a GPU-enabled machine for HuggingFace models.
- All sensitive files and outputs are gitignored by default.

## Requirements

- Python 3.8+
- Chrome browser and [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) installed and in PATH

## License

MIT
