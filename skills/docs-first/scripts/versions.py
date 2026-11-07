#!/usr/bin/env python3
"""Compare the versions a project uses with the latest stable releases.

Usage: python3 versions.py [repo_path] [--only name1,name2] [--offline] [--workers N]

Reads manifests and lockfiles (npm, PyPI, Go, Cargo, RubyGems, Composer, pub),
asks the public registries and endoflife.date for the latest versions, and
prints a Markdown table with a docs link per package. Direct dependencies
only. Standard library only, Python 3.8+.
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None

UA = "wolfin-senior-versions/1.0"
TIMEOUT = 8
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", "vendor", "venv", ".venv",
             "__pycache__", "target", ".dart_tool", ".wolfin-senior", "Pods", ".gradle"}


class Dep:
    def __init__(self, eco, name, declared, installed=None, source=""):
        self.eco, self.name, self.declared, self.installed, self.source = eco, name, declared, installed, source
        self.latest, self.docs, self.error = None, None, None


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def load_toml(path):
    if tomllib is None:
        return None
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except (OSError, ValueError):
        return None


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


# ---------- manifest parsers ----------

def parse_npm(dirpath, deps, runtimes):
    data = json.loads(read(os.path.join(dirpath, "package.json")) or "{}")
    lock = {}
    lock_text = read(os.path.join(dirpath, "package-lock.json"))
    if lock_text:
        try:
            lock = json.loads(lock_text).get("packages", {})
        except ValueError:
            lock = {}
    for section in ("dependencies", "devDependencies"):
        for name, spec in (data.get(section) or {}).items():
            installed = None
            pj = read(os.path.join(dirpath, "node_modules", name, "package.json"))
            if pj:
                try:
                    installed = json.loads(pj).get("version")
                except ValueError:
                    pass
            if not installed:
                installed = (lock.get("node_modules/" + name) or {}).get("version")
            deps.append(Dep("npm", name, str(spec), installed, dirpath))
    node = (data.get("engines") or {}).get("node")
    for f in (".nvmrc", ".node-version"):
        txt = read(os.path.join(dirpath, f))
        if txt and txt.strip():
            node = txt.strip()
    if node:
        runtimes.setdefault("nodejs", node)


PEP508_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(\[[^\]]*\])?\s*(.*)$")


def normalize_py(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def venv_versions(dirpath):
    found = {}
    for venv in (".venv", "venv", "env"):
        lib = os.path.join(dirpath, venv, "lib")
        if not os.path.isdir(lib):
            continue
        for py in os.listdir(lib):
            site = os.path.join(lib, py, "site-packages")
            if not os.path.isdir(site):
                continue
            for entry in os.listdir(site):
                m = re.match(r"^(.+)-([^-]+)\.dist-info$", entry)
                if m:
                    found[normalize_py(m.group(1))] = m.group(2)
    return found


def py_lock_versions(dirpath):
    found = {}
    for lock in ("poetry.lock", "uv.lock"):
        data = load_toml(os.path.join(dirpath, lock))
        for pkg in (data or {}).get("package", []):
            if pkg.get("name") and pkg.get("version"):
                found[normalize_py(pkg["name"])] = pkg["version"]
    return found


def parse_python(dirpath, files, deps, runtimes):
    specs = []
    for f in files:
        if f.startswith("requirements") and f.endswith(".txt"):
            for line in (read(os.path.join(dirpath, f)) or "").splitlines():
                line = line.split("#", 1)[0].strip()
                if not line or line.startswith(("-", "git+", "http")) or "://" in line:
                    continue
                specs.append(line.split(";", 1)[0])
    if "pyproject.toml" in files:
        data = load_toml(os.path.join(dirpath, "pyproject.toml")) or {}
        project = data.get("project") or {}
        specs.extend(project.get("dependencies") or [])
        if project.get("requires-python"):
            runtimes.setdefault("python", project["requires-python"])
        poetry = ((data.get("tool") or {}).get("poetry") or {})
        for group in [poetry.get("dependencies") or {}] + [
                (g or {}).get("dependencies") or {} for g in (poetry.get("group") or {}).values()]:
            for name, spec in group.items():
                if name.lower() == "python":
                    runtimes.setdefault("python", str(spec))
                    continue
                version = spec.get("version", "") if isinstance(spec, dict) else str(spec)
                specs.append(f"{name}{version if version[:1] in '<>=!~^' else ('==' + version if version and version != '*' else '')}")
    txt = read(os.path.join(dirpath, ".python-version"))
    if txt and txt.strip():
        runtimes["python"] = txt.strip().splitlines()[0]
    if not specs:
        return
    installed = {**py_lock_versions(dirpath), **venv_versions(dirpath)}
    seen = set()
    for spec in specs:
        m = PEP508_NAME.match(spec)
        if not m:
            continue
        name = m.group(1)
        key = normalize_py(name)
        if key in seen:
            continue
        seen.add(key)
        deps.append(Dep("pypi", name, m.group(3).strip() or "*", installed.get(key), dirpath))


def parse_go(dirpath, deps, runtimes):
    text = read(os.path.join(dirpath, "go.mod")) or ""
    m = re.search(r"^go\s+(\S+)", text, re.M)
    if m:
        runtimes.setdefault("go", m.group(1))
    in_block = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("require ("):
            in_block = True
            continue
        if in_block and line == ")":
            in_block = False
            continue
        if "// indirect" in line:
            continue
        m = re.match(r"^(?:require\s+)?(\S+)\s+(v\S+)", line) if (in_block or line.startswith("require ")) else None
        if m:
            deps.append(Dep("go", m.group(1), m.group(2), m.group(2), dirpath))


def parse_cargo(dirpath, deps):
    data = load_toml(os.path.join(dirpath, "Cargo.toml"))
    if data is None:
        return
    lock = {p["name"]: p["version"] for p in (load_toml(os.path.join(dirpath, "Cargo.lock")) or {}).get("package", [])
            if "name" in p and "version" in p}
    for section in ("dependencies", "dev-dependencies"):
        for name, spec in (data.get(section) or {}).items():
            if isinstance(spec, dict):
                if "path" in spec or "git" in spec:
                    continue
                name = spec.get("package", name)
                spec = spec.get("version", "*")
            deps.append(Dep("crates", name, str(spec), lock.get(name), dirpath))


def parse_ruby(dirpath, deps, runtimes):
    gemfile = read(os.path.join(dirpath, "Gemfile")) or ""
    lock = read(os.path.join(dirpath, "Gemfile.lock")) or ""
    locked = dict(re.findall(r"^    ([A-Za-z0-9_.-]+) \(([^)]+)\)", lock, re.M))
    for m in re.finditer(r"""^\s*gem\s+["']([^"']+)["'](?:\s*,\s*["']([^"']+)["'])?""", gemfile, re.M):
        deps.append(Dep("rubygems", m.group(1), m.group(2) or "*", locked.get(m.group(1)), dirpath))
    txt = read(os.path.join(dirpath, ".ruby-version"))
    if txt and txt.strip():
        runtimes.setdefault("ruby", txt.strip())


def parse_composer(dirpath, deps, runtimes):
    try:
        data = json.loads(read(os.path.join(dirpath, "composer.json")) or "{}")
        lock = json.loads(read(os.path.join(dirpath, "composer.lock")) or "{}")
    except ValueError:
        return
    locked = {p["name"]: p.get("version") for p in (lock.get("packages") or []) + (lock.get("packages-dev") or [])}
    for section in ("require", "require-dev"):
        for name, spec in (data.get(section) or {}).items():
            if name == "php":
                runtimes.setdefault("php", spec)
                continue
            if "/" not in name:  # ext-*, lib-*
                continue
            deps.append(Dep("packagist", name, spec, locked.get(name), dirpath))


def parse_pub(dirpath, deps):
    text = read(os.path.join(dirpath, "pubspec.yaml")) or ""
    lock = read(os.path.join(dirpath, "pubspec.lock")) or ""
    locked = dict(re.findall(r'^  ([a-z0-9_]+):\n(?:    .*\n)*?    version: "([^"]+)"', lock, re.M))
    section = None
    for line in text.splitlines():
        if re.match(r"^(dependencies|dev_dependencies):\s*$", line):
            section = line.split(":")[0]
            continue
        if line and not line.startswith(" "):
            section = None
            continue
        m = re.match(r"^  ([a-z0-9_]+):\s*(\S*)\s*$", line)
        if section and m and m.group(1) not in {"flutter", "flutter_test", "flutter_localizations"}:
            deps.append(Dep("pub", m.group(1), m.group(2) or "*", locked.get(m.group(1)), dirpath))


def collect(root):
    deps, runtimes = [], {}
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        names = set(files)
        if "package.json" in names:
            parse_npm(dirpath, deps, runtimes)
        if "pyproject.toml" in names or any(f.startswith("requirements") and f.endswith(".txt") for f in names) \
                or ".python-version" in names:
            parse_python(dirpath, names, deps, runtimes)
        if "go.mod" in names:
            parse_go(dirpath, deps, runtimes)
        if "Cargo.toml" in names:
            parse_cargo(dirpath, deps)
        if "Gemfile" in names:
            parse_ruby(dirpath, deps, runtimes)
        if "composer.json" in names:
            parse_composer(dirpath, deps, runtimes)
        if "pubspec.yaml" in names:
            parse_pub(dirpath, deps)
    return deps, runtimes


# ---------- registry lookups ----------

def go_escape(module):
    return "".join("!" + c.lower() if c.isupper() else c for c in module)


def pick_docs(urls):
    for key in ("Documentation", "Docs", "documentation", "Homepage", "Home", "homepage", "Source"):
        if urls.get(key):
            return urls[key]
    return next(iter(urls.values()), None) if urls else None


def lookup(dep):
    try:
        if dep.eco == "npm":
            d = get_json("https://registry.npmjs.org/" + urllib.parse.quote(dep.name, safe="@") + "/latest")
            dep.latest, dep.docs = d.get("version"), d.get("homepage")
        elif dep.eco == "pypi":
            info = get_json(f"https://pypi.org/pypi/{urllib.parse.quote(dep.name)}/json")["info"]
            dep.latest, dep.docs = info.get("version"), pick_docs(info.get("project_urls") or {}) or info.get("home_page")
        elif dep.eco == "go":
            d = get_json(f"https://proxy.golang.org/{go_escape(dep.name)}/@latest")
            dep.latest, dep.docs = d.get("Version"), f"https://pkg.go.dev/{dep.name}"
        elif dep.eco == "crates":
            c = get_json(f"https://crates.io/api/v1/crates/{urllib.parse.quote(dep.name)}")["crate"]
            dep.latest = c.get("max_stable_version") or c.get("newest_version")
            dep.docs = c.get("documentation") or f"https://docs.rs/{dep.name}"
        elif dep.eco == "rubygems":
            d = get_json(f"https://rubygems.org/api/v1/gems/{urllib.parse.quote(dep.name)}.json")
            dep.latest, dep.docs = d.get("version"), d.get("documentation_uri") or d.get("homepage_uri")
        elif dep.eco == "packagist":
            versions = get_json(f"https://repo.packagist.org/p2/{dep.name}.json")["packages"][dep.name]
            dep.latest, dep.docs = versions[0].get("version", "").lstrip("v"), versions[0].get("homepage")
        elif dep.eco == "pub":
            latest = get_json(f"https://pub.dev/api/packages/{dep.name}")["latest"]
            spec = latest.get("pubspec") or {}
            dep.latest = latest.get("version")
            dep.docs = spec.get("documentation") or spec.get("homepage") or f"https://pub.dev/packages/{dep.name}"
    except Exception as exc:  # network, 404, unexpected shape
        dep.error = type(exc).__name__


EOL_PRODUCTS = {"nodejs": "Node.js", "python": "Python", "go": "Go", "ruby": "Ruby", "php": "PHP"}


def runtime_latest(product):
    try:
        cycles = get_json(f"https://endoflife.date/api/{product}.json")
    except Exception as exc:
        return {"error": type(exc).__name__}
    newest = cycles[0]
    lts = next((c for c in cycles if c.get("lts")), None) if product == "nodejs" else None
    return {"latest": newest.get("latest"), "lts": lts.get("latest") if lts else None, "cycles": cycles}


# ---------- comparison ----------

def numbers(version):
    m = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version or "")
    return tuple(int(x) for x in m.groups() if x is not None) if m else None


def status(dep):
    if dep.error:
        return f"? lookup failed ({dep.error})"
    current = numbers(dep.installed) or numbers(dep.declared)
    latest = numbers(dep.latest)
    if not current or not latest:
        return "?"
    if current[0] < latest[0] or (current[0] == 0 == latest[0] and current[1:2] < latest[1:2]):
        return f"⚠️ major behind ({'.'.join(map(str, current))} → {dep.latest})"
    if current < latest[: len(current)]:
        return "minor/patch behind"
    return "✅ latest"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--only", help="comma-separated package names to check")
    ap.add_argument("--offline", action="store_true", help="don't query registries")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"not a directory: {root}")

    deps, runtimes = collect(root)
    if args.only:
        wanted = {n.strip().lower() for n in args.only.split(",") if n.strip()}
        deps = [d for d in deps if d.name.lower() in wanted or d.name.lower().rsplit("/", 1)[-1] in wanted]
    if not args.offline:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            list(pool.map(lookup, deps))

    print(f"# Versions: `{root}`\n")
    if tomllib is None:
        print("> Python < 3.11: pyproject.toml, Cargo.toml and lockfiles in TOML were skipped.\n")
    if not deps:
        print("No direct dependencies found in known manifests.\n")
    else:
        order = {"⚠": 0, "?": 1, "m": 2, "✅": 3}
        rows = sorted(deps, key=lambda d: (order.get(status(d)[:1], 1), d.eco, d.name.lower()))
        print("| Ecosystem | Package | Declared | Installed | Latest | Status | Docs |")
        print("|---|---|---|---|---|---|---|")
        for d in rows:
            where = os.path.relpath(d.source, root)
            name = d.name if where == "." else f"{d.name} ({where})"
            latest = "(offline)" if args.offline else (d.latest or "?")
            print(f"| {d.eco} | {name} | `{d.declared}` | {d.installed or '—'} | {latest} | {status(d) if not args.offline else '—'} | {d.docs or '—'} |")
        print()

    if runtimes:
        print("## Runtimes\n")
        print("| Runtime | Project uses | Latest | Note |")
        print("|---|---|---|---|")
        for product, used in sorted(runtimes.items()):
            if args.offline or product not in EOL_PRODUCTS:
                print(f"| {EOL_PRODUCTS.get(product, product)} | `{used}` | — | — |")
                continue
            info = runtime_latest(product)
            if "error" in info:
                print(f"| {EOL_PRODUCTS[product]} | `{used}` | ? | lookup failed ({info['error']}) |")
                continue
            note = ""
            used_nums = numbers(used)
            if used_nums:
                cycle = next((c for c in info["cycles"] if numbers(str(c.get("cycle"))) == used_nums[: len(numbers(str(c.get("cycle"))) or ())]), None)
                eol = cycle.get("eol") if cycle else None
                if eol is True or (isinstance(eol, str) and eol <= date.today().isoformat()):
                    note = "⚠️ end of life" + (f" since {eol}" if isinstance(eol, str) else "")
                elif isinstance(eol, str):
                    note = f"supported until {eol}"
            lts = f" (LTS {info['lts']})" if info.get("lts") else ""
            print(f"| {EOL_PRODUCTS[product]} | `{used}` | {info['latest']}{lts} | {note} |")
        print()

    print("Next: read the docs for the installed major version of each library this change uses, "
          "plus the changelog up to the latest release (docs-first skill).")


if __name__ == "__main__":
    main()
