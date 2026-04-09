# LinkedIn Recommender

An easy way to write up LinkedIn recommendations for colleagues who deserve it.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key:

   ```bash
   export ANTHROPIC_API_KEY=your_key_here
   ```

## Usage

### Add someone to your pipeline

```bash
python main.py add https://linkedin.com/in/janedoe
# You'll be prompted for their full name
```

### View your pipeline

```bash
python main.py list
```

### Write a recommendation

```bash
# Basic — paste profile text interactively, then answer questions
python main.py write "Jane Doe"

# With a screenshot of their LinkedIn profile
python main.py write "Jane Doe" --profile path/to/screenshot.png

# With a saved text file of their profile
python main.py write "Jane Doe" --profile path/to/profile.txt
```

You'll be asked 5 questions:

1. How do you know this person?
2. Where/how did you work together?
3. How long have you known or worked with them?
4. What specific skills or qualities do you want to highlight?
5. Any accomplishments or moments worth calling out?

The recommendation (100–200 words) is saved to `data/recommendations/<name>.md`.

### View a saved recommendation

```bash
python main.py show "Jane Doe"
```

## Data

- `data/pipeline.json` — tracks everyone in your pipeline with status (pending/completed)
- `data/recommendations/` — one `.md` file per person
