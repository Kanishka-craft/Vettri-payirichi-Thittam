def build_comic_layout(
    outline: list[dict],
    story: list[dict],
    image_paths: list[str],
) -> list[dict]:

    if len(outline) != len(story):
        raise RuntimeError(
            "Outline and story panel counts do not match."
        )

    if len(outline) != len(image_paths):
        raise RuntimeError(
            "Outline and image counts do not match."
        )

    layout = []

    for index, (outline_panel, story_panel, image_path) in enumerate(
        zip(outline, story, image_paths),
        start=1,
    ):
        layout.append(
            {
                "panel_number": index,
                "title": outline_panel.get(
                    "title",
                    f"Panel {index}",
                ),
                "scene_description": outline_panel.get(
                    "scene_description",
                    "",
                ),
                "image_prompt": outline_panel.get(
                    "image_prompt",
                    "",
                ),
                "caption": story_panel.get(
                    "caption",
                    "",
                ),
                "narration": story_panel.get(
                    "narration",
                    "",
                ),
                "dialogue": story_panel.get(
                    "dialogue",
                    "",
                ),
                "image_url": image_path,
            }
        )

    return layout