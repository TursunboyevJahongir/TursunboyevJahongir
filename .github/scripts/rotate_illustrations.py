"""Rotate only the profile artwork; requires Python's standard library."""

from pathlib import Path
import random
import re


START = "<!-- profile-illustration:start -->"
END = "<!-- profile-illustration:end -->"

# Selected by Jahongir. Remote GIFs are linked directly, without copying them.
# Collection: https://github.com/Anmol-Baranwal/Cool-GIFs-For-GitHub
IMAGES = {
    "light": (
        "./img/freelance_day.gif",
        "./img/developer.gif",
        "./img/Designer.gif",
        "./img/ai-collaboration-light.gif",
        "./img/ai-cat-boss-light.gif",
        "./img/ai-robot-classroom-light.gif",
        "./img/ai-teach-your-neighbor-light.gif",
        # Coding Vibe (#4).
        "https://user-images.githubusercontent.com/74038190/212749447-bfb7e725-6987-49d9-ae85-2015e3e7cc41.gif",
        # Automatic Typing (#7).
        "https://user-images.githubusercontent.com/74038190/212749168-86d6c7ab-98da-409b-998f-c5b74721badd.gif",
        # Old Man Working (#8).
        "https://user-images.githubusercontent.com/74038190/212746035-d5c61762-973c-44c0-aec7-887f3b7690e3.gif",
    ),
    "dark": (
        "./img/freelance_night.gif",
        "./img/SpaceLamp.gif",
        "./img/ai-agents-dark.gif",
        "./img/ai-nap-time-dark.gif",
        "./img/ai-bug-pingpong-dark.gif",
        "./img/ai-code-review-dark.gif",
    ),
}


def rotate(readme: str) -> str:
    """Preserve all content outside the uniquely marked artwork block."""
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must contain exactly one illustration marker pair")

    start = readme.index(START)
    end = readme.index(END)
    if end < start:
        raise ValueError("Illustration markers are out of order")

    block = readme[start:end]
    selected = {}
    for theme, images in IMAGES.items():
        source = re.search(
            rf'<source media="\(prefers-color-scheme: {theme}\)" srcset="([^"]+)">',
            block,
        )
        if source is None:
            raise ValueError(f"Missing {theme} illustration source")
        choices = [image for image in images if image != source.group(1)]
        selected[theme] = random.choice(choices)

    replacement = f'''{START}
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="{selected['dark']}">
  <source media="(prefers-color-scheme: light)" srcset="{selected['light']}">
  <img align="right" alt="Coding illustration" width="320" src="{selected['light']}">
</picture>
{END}'''
    return readme[:start] + replacement + readme[end + len(END):]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    for images in IMAGES.values():
        for image in images:
            if image.startswith("./") and not (root / image).is_file():
                raise ValueError(f"Missing local illustration: {image}")
    path = root / "README.md"
    original = path.read_text(encoding="utf-8")
    updated = rotate(original)
    path.write_text(updated, encoding="utf-8")
    print("Updated light and dark profile illustrations")


if __name__ == "__main__":
    main()
