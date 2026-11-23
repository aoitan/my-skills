#!/usr/bin/env python3
"""Incrementally explore a Markdown Digital Garden using only the stdlib."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Iterable


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.json"
CONFIG_ROOT_KEY = "garden_root"
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\[\]]+?)\]\]")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
HEADING_RE = re.compile(r"^#{1,6}\s+")
TYPE_ORDER = {"principle": 0, "decision": 1, "project": 2, "experiment": 3, "note": 4}


class GardenError(ValueError):
    pass


def emit_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def configured_root(config_path: Path) -> str:
    if not config_path.is_file():
        raise GardenError(
            "garden root is not configured; pass --root, set GARDEN_ROOT, "
            f"or create {config_path} from config.example.json"
        )
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GardenError(f"invalid JSON in garden config {config_path}: {exc.msg}") from exc
    if not isinstance(config, dict):
        raise GardenError(f"garden config must be a JSON object: {config_path}")
    value = config.get(CONFIG_ROOT_KEY)
    if not isinstance(value, str) or not value.strip():
        raise GardenError(
            f"garden config must define a non-empty {CONFIG_ROOT_KEY!r}: {config_path}"
        )
    return value


def root_path(raw: str | None, config: str | None = None) -> Path:
    value = raw or os.environ.get("GARDEN_ROOT")
    if not value:
        config_path = Path(config).expanduser() if config else DEFAULT_CONFIG
        value = configured_root(config_path)
    root = Path(value).expanduser()
    root = root.resolve()
    if not root.is_dir():
        raise GardenError(f"garden root is not a directory: {root}")
    return root


def resolve_inside(root: Path, raw: str, *, kind: str) -> Path:
    candidate_arg = Path(raw)
    if candidate_arg.is_absolute():
        raise GardenError(f"{kind} must be relative to the garden root: {raw}")
    candidate = (root / candidate_arg).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise GardenError(f"{kind} escapes the garden root: {raw}") from exc
    if kind == "directory" and not candidate.is_dir():
        raise GardenError(f"directory does not exist: {raw}")
    if kind == "node":
        if candidate.suffix.lower() != ".md":
            raise GardenError(f"node must be a Markdown file: {raw}")
        if not candidate.is_file():
            raise GardenError(f"node does not exist: {raw}")
    return candidate


def relative(root: Path, path: Path) -> str:
    value = path.relative_to(root).as_posix()
    return value or "."


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def split_front_matter(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[1:index]), "".join(lines[index + 1 :])
    return "", text


def scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [scalar(item) for item in inner.split(",")] if inner else []
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    return value


def parse_front_matter(front_matter: str) -> dict[str, Any]:
    """Parse the flat scalars and lists commonly used in Garden front matter."""
    result: dict[str, Any] = {}
    active_list: str | None = None
    for raw_line in front_matter.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s+-\s+(.*)$", raw_line)
        if list_match and active_list:
            current = result.setdefault(active_list, [])
            if isinstance(current, list):
                current.append(scalar(list_match.group(1)))
            continue
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if key_match:
            key, value = key_match.groups()
            if value.strip() == "":
                result[key] = []
                active_list = key
            else:
                result[key] = scalar(value)
                active_list = None
        else:
            active_list = None
    return result


def read_node(path: Path) -> tuple[dict[str, Any], str]:
    front_matter, body = split_front_matter(read_text(path))
    return parse_front_matter(front_matter), body


def title_from_body(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def strip_fenced_code(text: str) -> str:
    output: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker[0]
            elif marker[0] == fence:
                fence = None
            continue
        if fence is None:
            output.append(line)
    return "\n".join(output)


def extract_links(body: str) -> list[dict[str, str]]:
    searchable = strip_fenced_code(body)
    links: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for match in WIKILINK_RE.finditer(searchable):
        raw = match.group(1).strip()
        target_and_anchor, _, alias = raw.partition("|")
        target, _, anchor = target_and_anchor.partition("#")
        item = {"kind": "wikilink", "target": target.strip()}
        if anchor.strip():
            item["anchor"] = anchor.strip()
        if alias.strip():
            item["label"] = alias.strip()
        key = (item["kind"], item["target"])
        if item["target"] and key not in seen:
            seen.add(key)
            links.append(item)
    for match in MARKDOWN_LINK_RE.finditer(searchable):
        label, target = (part.strip() for part in match.groups())
        if target.startswith(("http://", "https://", "mailto:")):
            kind = "external"
        else:
            kind = "markdown"
        key = (kind, target)
        if target and key not in seen:
            seen.add(key)
            links.append({"kind": kind, "target": target, "label": label})
    return links


def summary_from_body(body: str) -> tuple[str, str]:
    paragraphs: list[list[str]] = []
    current: list[str] = []
    for line in strip_fenced_code(body).splitlines():
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(current)
                current = []
            continue
        if HEADING_RE.match(stripped) or stripped.startswith(("- ", "* ", ">", "|")):
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append(stripped)
    if current:
        paragraphs.append(current)
    if not paragraphs:
        return "", "none"
    return " ".join(paragraphs[0]), "extracted-opening-paragraph"


def markdown_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.md")):
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts):
            yield path


def node_metadata(root: Path, path: Path) -> dict[str, Any]:
    metadata, body = read_node(path)
    title = metadata.get("title") or title_from_body(body) or path.stem
    return {"path": relative(root, path), "title": title, **metadata}


def command_list(root: Path, raw_directory: str) -> None:
    directory = resolve_inside(root, raw_directory, kind="directory")
    children = []
    for path in sorted(directory.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            children.append({"name": path.name, "kind": "directory"})
        elif path.suffix.lower() == ".md" and path.name != "index.md":
            children.append({"name": path.name, "kind": "node"})
    emit_json(
        {
            "directory": relative(root, directory),
            "index": {"exists": (directory / "index.md").is_file(), "path": relative(root, directory / "index.md")},
            "children": children,
        }
    )


def command_index(root: Path, raw_directory: str) -> None:
    directory = resolve_inside(root, raw_directory, kind="directory")
    path = directory / "index.md"
    if not path.is_file():
        raise GardenError(f"index.md does not exist in: {raw_directory}")
    metadata, body = read_node(path)
    emit_json({"path": relative(root, path), "metadata": metadata, "content": body.rstrip(), "links": extract_links(body)})


def command_metadata(root: Path, raw_node: str) -> None:
    path = resolve_inside(root, raw_node, kind="node")
    emit_json(node_metadata(root, path))


def command_links(root: Path, raw_node: str) -> None:
    path = resolve_inside(root, raw_node, kind="node")
    _, body = read_node(path)
    emit_json({"path": relative(root, path), "links": extract_links(body)})


def command_summary(root: Path, raw_node: str) -> None:
    path = resolve_inside(root, raw_node, kind="node")
    metadata, body = read_node(path)
    description = metadata.get("description")
    if isinstance(description, str) and description.strip():
        summary, source = description.strip(), "front-matter-description"
    else:
        summary, source = summary_from_body(body)
    emit_json(
        {
            "path": relative(root, path),
            "metadata": {"title": metadata.get("title") or title_from_body(body) or path.stem, **metadata},
            "summary": summary,
            "summary_source": source,
            "links": extract_links(body),
        }
    )


def command_content(root: Path, raw_node: str) -> None:
    path = resolve_inside(root, raw_node, kind="node")
    _, body = read_node(path)
    print(body.rstrip())


def normalized_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).casefold() for item in value]
    if value is None:
        return []
    return [str(value).casefold()]


def command_find(root: Path, field: str, query: str) -> None:
    wanted = query.casefold()
    matches = []
    for path in markdown_files(root):
        metadata, _ = read_node(path)
        if wanted in normalized_values(metadata.get(field)):
            matches.append(node_metadata(root, path))
    emit_json({"query": {field: query}, "count": len(matches), "nodes": matches})


def link_key(value: str) -> str:
    """Normalize link text, including the backslash left by `\\|` inside tables."""
    cleaned = value.strip().removesuffix("\\").strip()
    return unicodedata.normalize("NFC", cleaned).casefold().removesuffix(".md").strip("/")


class LinkIndex:
    """Resolve wikilink text to Garden nodes, preferring the most specific match."""

    def __init__(self, root: Path) -> None:
        self.nodes: list[tuple[Path, dict[str, Any], str]] = []
        self.by_path: dict[str, str] = {}
        self.by_suffix: dict[str, set[str]] = {}
        self.by_alias: dict[str, set[str]] = {}
        self.by_title: dict[str, set[str]] = {}
        for path in markdown_files(root):
            metadata, body = read_node(path)
            self.nodes.append((path, metadata, body))
            node = relative(root, path)
            key = link_key(node)
            names = [key]
            if path.name.casefold() == "index.md" and path.parent != root:
                names.append(posixpath.dirname(key))
            for name in names:
                self.by_path.setdefault(name, node)
                parts = name.split("/")
                for start in range(1, len(parts)):
                    suffix = "/".join(parts[start:])
                    if suffix != "index":
                        self.by_suffix.setdefault(suffix, set()).add(node)
            for alias in normalized_values(metadata.get("aliases")):
                self.by_alias.setdefault(link_key(alias), set()).add(node)
            title = metadata.get("title") or title_from_body(body)
            if title:
                self.by_title.setdefault(link_key(str(title)), set()).add(node)

    def resolve(self, target: str, source_directory: str = "") -> tuple[set[str], str]:
        key = link_key(target)
        if target.strip().startswith(("./", "../")):
            key = link_key(posixpath.normpath(posixpath.join(source_directory, target.strip())))
        if key in self.by_path:
            return {self.by_path[key]}, "path"
        for table, resolution in (
            (self.by_suffix, "path-suffix"),
            (self.by_alias, "alias"),
            (self.by_title, "title"),
        ):
            if key in table:
                return table[key], resolution
        if "/" in key:
            name = posixpath.basename(key)
            if name in self.by_suffix:
                return self.by_suffix[name], "moved-filename"
        return set(), "unresolved"


def command_backlinks(root: Path, query: str) -> None:
    index = LinkIndex(root)
    wanted, _ = index.resolve(query)
    matches = []
    for path, metadata, body in index.nodes:
        source_directory = posixpath.dirname(relative(root, path))
        matched = []
        for link in extract_links(body):
            if link["kind"] != "wikilink":
                continue
            found, resolution = index.resolve(link["target"], source_directory)
            if wanted & found:
                item: dict[str, Any] = {**link, "resolution": resolution}
                if len(found) > 1:
                    item["candidates"] = len(found)
                matched.append(item)
            elif not wanted and not found and link_key(link["target"]) == link_key(query):
                matched.append({**link, "resolution": resolution})
        if matched:
            title = metadata.get("title") or title_from_body(body) or path.stem
            matches.append(
                {"path": relative(root, path), "title": title, **metadata, "matching_links": matched}
            )
    emit_json({"target": query, "resolved": sorted(wanted), "count": len(matches), "nodes": matches})


def command_context(root: Path, raw_nodes: list[str], max_chars: int) -> None:
    if max_chars <= 0:
        raise GardenError("--max-chars must be positive")
    selected = []
    for position, raw_node in enumerate(raw_nodes):
        path = resolve_inside(root, raw_node, kind="node")
        metadata, body = read_node(path)
        selected.append((TYPE_ORDER.get(str(metadata.get("type", "")).casefold(), 5), position, path, metadata, body))
    sections: list[str] = []
    used = 0
    for _, _, path, metadata, body in sorted(selected):
        heading = f"## [{metadata.get('type', 'unclassified')}] {metadata.get('title') or title_from_body(body) or path.stem}\n\nSource: {relative(root, path)}\n\n"
        remaining = max_chars - used - len(heading)
        if remaining <= 0:
            break
        content = body.strip()
        if len(content) > remaining:
            content = content[: max(0, remaining - 18)].rstrip() + "\n\n[TRUNCATED]"
        section = heading + content
        sections.append(section)
        used += len(section) + 2
        if used >= max_chars:
            break
    print("\n\n".join(sections))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--root",
        help="Garden content root (defaults to GARDEN_ROOT, then config.json)",
    )
    result.add_argument(
        "--config",
        help="Garden config path (defaults to config.json beside SKILL.md)",
    )
    subparsers = result.add_subparsers(dest="command", required=True)
    for name, help_text in (("list", "list a directory entry point"), ("index", "read a directory index")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("directory", nargs="?", default=".")
    for name, help_text in (
        ("metadata", "read node front matter"),
        ("links", "extract node links"),
        ("summary", "read bounded node summary information"),
        ("content", "read an explicitly selected node body"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("node")
    type_parser = subparsers.add_parser("find-type", help="find nodes by exact type")
    type_parser.add_argument("type")
    tag_parser = subparsers.add_parser("find-tag", help="find nodes by exact tag")
    tag_parser.add_argument("tag")
    backlinks_parser = subparsers.add_parser("backlinks", help="find wikilink backlinks")
    backlinks_parser.add_argument("target")
    context_parser = subparsers.add_parser("context", help="build bounded context from selected nodes")
    context_parser.add_argument("nodes", nargs="+")
    context_parser.add_argument("--max-chars", type=int, default=12000)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        root = root_path(args.root, args.config)
        if args.command == "list":
            command_list(root, args.directory)
        elif args.command == "index":
            command_index(root, args.directory)
        elif args.command == "metadata":
            command_metadata(root, args.node)
        elif args.command == "links":
            command_links(root, args.node)
        elif args.command == "summary":
            command_summary(root, args.node)
        elif args.command == "content":
            command_content(root, args.node)
        elif args.command == "find-type":
            command_find(root, "type", args.type)
        elif args.command == "find-tag":
            command_find(root, "tags", args.tag)
        elif args.command == "backlinks":
            command_backlinks(root, args.target)
        elif args.command == "context":
            command_context(root, args.nodes, args.max_chars)
        return 0
    except (GardenError, OSError, UnicodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
