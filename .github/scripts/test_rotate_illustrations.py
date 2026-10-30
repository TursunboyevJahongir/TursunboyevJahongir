"""Checks for the automated README writer, without Git or network writes."""

from pathlib import Path
import re
import unittest
from unittest.mock import patch

import rotate_illustrations as rotation


README = (Path(__file__).resolve().parents[2] / "README.md").read_text(encoding="utf-8")


class RotationTests(unittest.TestCase):
    def test_profile_readme_is_not_shadowed_by_github_documentation(self):
        github_directory = Path(__file__).resolve().parents[1]
        shadowing_files = [
            path.name for path in github_directory.iterdir()
            if path.is_file() and path.name.casefold().split(".")[0] == "readme"
        ]
        self.assertEqual(
            shadowing_files, [],
            "A README in .github overrides the root profile README on GitHub",
        )

    def test_preserves_profile_text_and_social_icons_exactly(self):
        updated = rotation.rotate(README)
        self.assertEqual(README.split(rotation.START)[0], updated.split(rotation.START)[0])
        self.assertEqual(README.split(rotation.END)[1], updated.split(rotation.END)[1])

    def test_changes_each_theme_without_crossing_pools(self):
        current = README
        for _ in range(30):
            updated = rotation.rotate(current)
            for theme, images in rotation.IMAGES.items():
                pattern = rf'<source media="\(prefers-color-scheme: {theme}\)" srcset="([^"]+)">'
                previous = re.search(pattern, current).group(1)
                chosen = re.search(pattern, updated).group(1)
                self.assertIn(chosen, images)
                self.assertNotEqual(chosen, previous)
            light = re.search(r'prefers-color-scheme: light\)" srcset="([^"]+)"', updated).group(1)
            fallback = re.search(r'<img [^>]*src="([^"]+)"', updated).group(1)
            self.assertEqual(fallback, light)
            current = updated

    def test_all_sixteen_selected_images_are_reachable(self):
        reached = set()
        for images in rotation.IMAGES.values():
            for image in images:
                def select(choices, target=image):
                    return target if target in choices else choices[0]
                with patch.object(rotation.random, "choice", side_effect=select):
                    # A current image becomes eligible again on the second run.
                    first = rotation.rotate(README)
                    second = rotation.rotate(first)
                seen = set(re.findall(r'srcset="([^"]+)"', first + second))
                self.assertIn(image, seen)
                reached.update(seen)
        self.assertEqual(len(reached), 16)

    def test_rejects_missing_duplicate_and_reversed_markers(self):
        malformed = (
            README.replace(rotation.START, ""),
            README + rotation.END,
            rotation.END + "\n" + rotation.START,
        )
        for readme in malformed:
            with self.subTest(readme=readme), self.assertRaises(ValueError):
                rotation.rotate(readme)

    def test_rejects_a_missing_theme_source(self):
        readme = re.sub(r'  <source media="\(prefers-color-scheme: dark\)"[^\n]+\n', "", README)
        with self.assertRaises(ValueError):
            rotation.rotate(readme)


if __name__ == "__main__":
    unittest.main()
