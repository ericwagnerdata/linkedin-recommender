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

Write a warm, professional LinkedIn recommendation that:
- Is strictly 100–200 words
- Sounds genuine and personal, not generic or formulaic
- Weaves in specific details from the answers above
- Is written in first person
- Does not open with "I highly recommend" or similar clichés
- Never uses em dashes (—) under any circumstances
- Ends with a strong, confident endorsement

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
