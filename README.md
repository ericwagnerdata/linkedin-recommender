# LinkedIn Recommender

An easy way to write up LinkedIn recommendations for colleagues who deserve it.

## Why this exists

Most LinkedIn recommendations read the same: a job title, a few adjectives, a closing line about hiring the person again. They're easy to write and easy to forget. The people who actually deserve a recommendation deserve better than that.

This tool is opinionated. It enforces a specific voice (warm, specific, scene-driven) and a specific structure (three paragraphs, 100–150 words, at least one sentence that could only be true about this one person). The writing rules live in [CLAUDE.md](CLAUDE.md) if you want to tune them to your own voice.

## Example output

> I worked with Jane for three years at Acme, first as her skip-level and later as her
> direct manager during the payments rewrite. What stood out early was how she treated
> ambiguity as information rather than an obstacle. When the vendor migration stalled and
> three teams were pointing at each other, Jane was the one quietly pulling the thread,
> mapping dependencies on a whiteboard at 7pm on a Tuesday because she wanted the answer
> before standup.
>
> She shipped the new reconciliation flow in a quarter, cut failed transactions by 40%, and
> somehow did it without a single escalation to me. Engineers on other teams started looping
> her into their design reviews uninvited, which is the clearest signal I know.
>
> Jane is ready for a staff role. Whoever gets her next is getting someone rare.

## Requirements

- Python 3.10+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

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

The recommendation (targeting around 125 words, 100–150 range) is saved to
`data/recommendations/<name>.md`.

### View a saved recommendation

```bash
python main.py show "Jane Doe"
```

## Data

- `data/pipeline.json` — tracks everyone in your pipeline with status (pending/completed)
- `data/recommendations/` — one `.md` file per person