import base64
from pathlib import Path

import anthropic

QUESTIONS = [
    ("relationship", "How do you know this person?"),
    ("work_context", "Where/how did you work together?"),
    ("duration", "How long have you known or worked with them?"),
    ("skills", "What specific skills or qualities do you want to highlight?"),
    ("accomplishments", "Any accomplishments or moments worth calling out?"),
]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


def ask_questions():
    print("\nAnswer a few questions and I'll write the recommendation.\n")
    answers = {}
    for key, question in QUESTIONS:
        print(f"  {question}")
        answers[key] = input("  > ").strip()
        print()
    return answers


def _load_image(path):
    suffix = Path(path).suffix.lower()
    media_type = MEDIA_TYPES.get(suffix, "image/png")
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, media_type


def _build_content(name, linkedin_url, profile_input, answers):
    content = []

    if profile_input:
        profile_path = Path(profile_input)
        if profile_path.exists() and profile_path.suffix.lower() in IMAGE_EXTENSIONS:
            image_data, media_type = _load_image(profile_input)
            content.append({
                "type": "text",
                "text": f"Here is the LinkedIn profile screenshot for {name} ({linkedin_url}):",
            })
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": image_data},
            })
        elif profile_path.exists():
            profile_text = profile_path.read_text(encoding="utf-8")
            content.append({
                "type": "text",
                "text": f"LinkedIn profile text for {name} ({linkedin_url}):\n\n{profile_text}",
            })
        else:
            # Treat as raw pasted text
            content.append({
                "type": "text",
                "text": f"LinkedIn profile text for {name} ({linkedin_url}):\n\n{profile_input}",
            })
    else:
        content.append({
            "type": "text",
            "text": f"LinkedIn profile: {name} — {linkedin_url}",
        })

    answers_text = "\n".join([
        f"- How they know {name}: {answers['relationship']}",
        f"- Work context: {answers['work_context']}",
        f"- Duration known/worked together: {answers['duration']}",
        f"- Skills/qualities to highlight: {answers['skills']}",
        f"- Accomplishments to mention: {answers['accomplishments']}",
    ])

    content.append({
        "type": "text",
        "text": f"""You are writing a LinkedIn recommendation for {name}.

The recommender provided the following context:
{answers_text}

Write a LinkedIn recommendation following these rules strictly.

VOICE:
Write like a person who genuinely means it, not like someone filling out a form. Warm and specific beats polished and generic. Build toward a scene or moment — earn the punchline, don't open with it. Open with context and feeling, not just title and timeframe. The reader should sense the relationship before they know the org chart. Write declaratively. No hedging, no qualifiers. At least one sentence must be true only about this specific person and no one else.

Quality benchmark — a great rec:
- Names one intangible quality and immediately proves it with behavioral evidence
- Builds to a specific scene or moment with real detail
- Closes by naming something only this person would leave behind, or pulls the reader into their future

STRUCTURE (3 paragraphs):
1. Relationship and context — unmistakable in the first sentence, feeling before org chart
2. Specific accomplishment with evidence — one real situation beats a list of traits; include a growth arc if the relationship spanned enough time
3. Forward-looking endorsement — specific and memorable, not a platitude

WHAT TO INCLUDE:
- Lead with a number or quantified result in the first two sentences if possible
- Include at least one high-stakes situation the subject navigated well
- Show the subject made the recommender's job easier (imply trust and ownership without using those words)
- Mention cross-functional reach if applicable
- Name specific role fit when possible ("ready for a team lead role," "ideal for a player-coach position")
- For peer recommendations, emphasize colleagues sought this person out, not just management
- Use role-specific technical language naturally
- Use the subject's name 2–3 times
- Close with "I'd hire them again" or equivalent if the tone supports it; "Whoever hires her is getting someone rare" also works

WHAT TO AVOID:
- No filler openers ("I had the pleasure of...", "It is my honor to...")
- No superlative stacking — pick one strong word and back it with evidence
- No em dashes (—) under any circumstances
- No generic business language ("synergy," "leverage")
- No specific calendar dates or years — use relative framing ("during our two years together"); stating duration is fine
- No platitude closings ("I recommend her without hesitation," "I highly recommend")
- No perfect-person recs — briefly acknowledge a challenge where natural

LENGTH: 100–150 words. 125 is ideal.

Output only the recommendation text. No intro, no labels, no quotes.""",
    })

    return content


def generate_recommendation(name, linkedin_url, profile_input, answers):
    client = anthropic.Anthropic()
    content = _build_content(name, linkedin_url, profile_input, answers)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text.strip()
