"""Structural checks for every skill, so a broken skill never ships.

Run from the repository root:  python3 -m unittest discover -s tests -v
"""

import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")
COMMANDS = {"grill", "review", "audit", "handoff", "retro"}


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise AssertionError(f"{path}: no frontmatter")
    fields = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if not sep or line.startswith(" "):
            raise AssertionError(f"{path}: unexpected frontmatter line {line!r}")
        fields[key.strip()] = value.strip()
    return fields, text[match.end():]


def skill_dirs():
    return sorted(d for d in os.listdir(SKILLS) if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))


class Skills(unittest.TestCase):
    def test_expected_skills_and_commands_exist(self):
        names = set(skill_dirs())
        self.assertTrue(COMMANDS <= names, COMMANDS - names)
        self.assertEqual(len(names - COMMANDS), 15, sorted(names - COMMANDS))

    def test_frontmatter_is_valid(self):
        for name in skill_dirs():
            with self.subTest(skill=name):
                fields, body = frontmatter(os.path.join(SKILLS, name, "SKILL.md"))
                self.assertEqual(fields.get("name"), name)
                desc = fields.get("description", "")
                self.assertTrue(40 <= len(desc) <= 1024, len(desc))
                self.assertNotIn("<", desc)
                self.assertNotIn(">", desc)
                if not desc.startswith(('"', "'")):
                    self.assertNotIn(": ", desc, "unquoted YAML value can't contain ': '")
                self.assertLess(len(body.splitlines()), 500, "keep SKILL.md under 500 lines")

    def test_commands_are_user_invoked_and_skills_are_not(self):
        for name in skill_dirs():
            with self.subTest(skill=name):
                fields, _ = frontmatter(os.path.join(SKILLS, name, "SKILL.md"))
                user_only = fields.get("disable-model-invocation") == "true"
                self.assertEqual(user_only, name in COMMANDS)

    def test_commands_load_existing_skills(self):
        for name in COMMANDS:
            with self.subTest(command=name):
                _, body = frontmatter(os.path.join(SKILLS, name, "SKILL.md"))
                for target in re.findall(r"wolfin-senior:([a-z-]+)", body):
                    self.assertTrue(os.path.isfile(os.path.join(SKILLS, target, "SKILL.md")), target)

    def test_referenced_files_exist(self):
        pattern = re.compile(r"`((?:\.\./)*[a-z-]+(?:/[A-Za-z0-9_.-]+)*\.(?:md|py|mjs|sh))`")
        for name in skill_dirs():
            base = os.path.join(SKILLS, name)
            for dirpath, _, files in os.walk(base):
                for file in files:
                    if not file.endswith(".md"):
                        continue
                    path = os.path.join(dirpath, file)
                    with open(path, encoding="utf-8") as fh:
                        text = fh.read()
                    for ref in pattern.findall(text):
                        if not ref.startswith(("references/", "scripts/", "../")):
                            continue
                        candidates = [os.path.normpath(os.path.join(base, ref)),
                                      os.path.normpath(os.path.join(dirpath, ref))]
                        with self.subTest(file=os.path.relpath(path, ROOT), ref=ref):
                            self.assertTrue(any(os.path.isfile(c) for c in candidates))

    def test_router_maps_every_skill_and_command(self):
        _, router = frontmatter(os.path.join(SKILLS, "using-wolfin-senior", "SKILL.md"))
        for name in skill_dirs():
            if name == "using-wolfin-senior":
                continue
            with self.subTest(skill=name):
                needle = f"/wolfin-senior:{name}" if name in COMMANDS else f"`{name}`"
                self.assertIn(needle, router)


class Repository(unittest.TestCase):
    def test_no_arabic_text_in_tracked_sources(self):
        arabic = re.compile("[%s-%s]" % (chr(0x0600), chr(0x06FF)))
        for dirpath, dirnames, files in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in {".git", ".wolfin-senior", "node_modules"}]
            for file in files:
                if file.endswith((".png", ".jpg", ".webp", ".zip", ".pyc")):
                    continue
                path = os.path.join(dirpath, file)
                with open(path, encoding="utf-8", errors="ignore") as fh:
                    with self.subTest(file=os.path.relpath(path, ROOT)):
                        self.assertIsNone(arabic.search(fh.read()))

    def test_manifests_agree(self):
        with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
            plugin = json.load(fh)
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as fh:
            market = json.load(fh)
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(plugin["name"], "wolfin-senior")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        if "version" in entry:
            self.assertEqual(entry["version"], plugin["version"])
        with open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8") as fh:
            self.assertIn(f"## {plugin['version']}", fh.read())


if __name__ == "__main__":
    unittest.main()
