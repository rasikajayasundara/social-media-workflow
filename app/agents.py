from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app import config
from app.state import ContentBrief, PostState, PostCopy, ImagePrompt, Review
from pathlib import Path
import base64
import httpx
import json

from datetime import datetime

from openai import AzureOpenAI

def get_llm():
    return AzureChatOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_KEY,
        api_version=config.AZURE_OPENAI_VERSION,
        azure_deployment=config.AZURE_OPEN_AI_CHAT_DEPLOYMENT_NAME,
    )

BRAND = "Brand: ProjeX. Audience: project managers. Voice: friendly, clear, no hype."


def copywriter(state: dict) -> dict:
    messages = [
        SystemMessage(
            "You are a social media copywriter. Write ONE post for Facebook and LinkedIn. "
            "Simple English, short paragraphs, a strong first line, max 2 emojis.\n" + BRAND
        ),
        HumanMessage(f"Structured brief: {state['brief']}"),
    ]
    llm = get_llm().with_structured_output(PostCopy)
    reply = llm.invoke(messages)
    print("Copywriter got:", reply)
    print(".....")
    return {"copy": reply.model_dump()}   # store a plain dict in state


def strategist(state: dict) -> dict:
    llm = get_llm().with_structured_output(ContentBrief)
    print("Strategist got user brief:", state.get("user_brief"))
    print(".....")
    brief = llm.invoke([
        SystemMessage("You are a social media strategist. Plan ONE useful, non-salesy post.\n" + BRAND),
        HumanMessage(f"Idea from the user: {state.get('user_brief') or 'choose yourself'}"),
    ])

    print("Strategist got:", brief)
    print(".....")
    return {"brief": brief.model_dump()}   # store a plain dict in state


IMAGES = Path("data/images")
IMAGES.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str) -> str:
    url = f"{config.AZURE_MAI_ENDPOINT.rstrip('/')}"
    file_name = datetime.now().strftime("%Y%m%d%H%M%S") + ".png"
    r = httpx.post(
        url,
        headers={"api-key": config.AZURE_OPENAI_KEY, "Content-Type": "application/json"},
        json={
            "model": config.AZURE_MAI_IMAGE_DEPLOYMENT_NAME,   # your deployment name
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
        },
        timeout=120,      # image generation can be slow
    )
    if r.status_code != 200:
        print(r.text)     # shows Azure's real error message
    r.raise_for_status()

    path = IMAGES / file_name
    path.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    return str(path)

def designer(state: dict) -> dict:
    llm = get_llm().with_structured_output(ImagePrompt)
    #image_style = "Square 1:1 social media post, clean modern corporate design. White background with "
    "large smooth organic wave and blob shapes in royal blue (#1E4FA3) and soft light blue "
    "(#C9D8F0), flowing in from one side. One rounded or circular photo cut-out with a blue "
    "duotone tint, showing {image_subject}. Bold dark-blue sans-serif headline, large and "
    f"left-aligned: {state['brief']['image_wording']}. Below it, one short line in small regular text: {{subtext}}. "
    'At the bottom, small and centred: "projex.nz". Flat design, lots of white space, '
    "no extra text, no other logos."
    image_prompt = f"""Design a bold, modern editorial-style social media flyer graphic, in the style of a professional B2B software and project management brand poster.

Use this content for the flyer: {state['brief']['image_wording']}

Layout: one large photo or illustration placed on one side (or bleeding off the edge). Put a big stacked headline on the opposite side, or overlapping the negative space. The headline is 3 short punchy words or phrases on separate lines, taken from the content above, in large bold uppercase letters. Add one small supporting line or tag near the bottom.

Image subject: choose the subject directly from the meaning of the content above, so the picture and the words clearly belong together. It can be a real person with a natural or emotional expression, a team, an animal, a vehicle, a job site, a workplace scene, a dashboard, or a simple concept. Do not repeat the same type of image every time. Avoid gyms, fitness equipment and athletic imagery.

Typography: extra bold, tall condensed or heavy sans-serif font, all caps, generous space between the stacked lines. The headline colour should contrast softly with the background (muted grey on light, or white on dark).

Background: soft flat neutral tone (light grey, off-white or navy) with a very subtle element behind the headline, such as thin curved lines, arcs or a faint geometric shape. Keep it minimal.

Footer: bottom left shows the text "projex.nz" in a small clean sans-serif font, with tiny social media icons and a "Follow us" label, all in one accent colour.

Visual style: clean high-quality photography or flat illustration in navy blue and white, or one muted accent tint. High contrast, professional and trustworthy, lots of negative space, premium SaaS brand feel.

Format: square 1:1, under 800KB, suitable for a Facebook or Instagram business post."""

    # ip = llm.invoke([
    #     SystemMessage("You are an art director. Write a prompt for a square social media image. follwow the style guide below. Use the image concept and wording from the brief. "),
    #     HumanMessage(f"Image idea for post: {state['brief']['image_concept']}, base design style: {image_style}"),
    # ])
    print("-------------------------------------")
    print("-------------------------------------")
    #print("Designer got:", ip)
    print("-------------------------------------")
    print("image_prompt:", image_prompt)
    print("-------------------------------------")
    path = generate_image(image_prompt)
    #return {"image_prompt": ip.model_dump(), "image_path": path}
    return {"image_path": path}



def reviewer(state: dict) -> dict:
    img = base64.b64encode(Path(state["image_path"]).read_bytes()).decode()
    llm = get_llm().with_structured_output(Review)
    review = llm.invoke([
        SystemMessage("You are a strict brand reviewer. Check the post text and the image. "
                      "severity=major only if it must not be posted.\n" + BRAND),
        HumanMessage(content=[
            {"type": "text", "text": json.dumps(state["copy"])},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}},
        ]),
    ])
    return {"review": review.model_dump()}













if __name__ == "__main__":
    reply = get_llm().invoke("Say hello in 5 words")
    print(reply.content)
    #print(reply.usage_metadata)   # tokens used, you will need this later