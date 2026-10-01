from typing import Any, Dict, List


def build_comic_layout(
    story_data: Dict[str, Any],
    image_paths: List[str],
) -> Dict[str, Any]:

    panels = []

    stories = story_data.get("panels", [])

    for index, panel in enumerate(stories):

        image = (
            image_paths[index]
            if index < len(image_paths)
            else ""
        )

        panels.append(
            {
                "panel_number": panel.get(
                    "panel_number",
                    index + 1,
                ),
                "narration": panel.get(
                    "narration",
                    "",
                ),
                "dialogue": panel.get(
                    "dialogue",
                    "",
                ),
                "image_prompt": panel.get(
                    "image_prompt",
                    "",
                ),
                "image": image,
            }
        )

    return {
        "title": story_data.get(
            "title",
            "My Comic",
        ),
        "panels": panels,
    }