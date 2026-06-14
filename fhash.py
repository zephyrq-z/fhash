#!/usr/bin/env python3
"""
fhash — Folder name hashing tool for macOS.

Encode subfolder names to SHA-256 short hashes (8 chars) and decode them back.
A hidden mapping file (.folder_hash_map.json) is maintained in the target folder.

Usage:
    fhash encode /path/to/folder [--dry-run] [--yes]
    fhash decode /path/to/folder [--dry-run] [--yes]
    fhash list   /path/to/folder
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MAP_FILENAME = ".folder_hash_map.json"
HASH_LENGTH = 8
META_KEY = "_meta"


def get_immediate_subdirs(folder: Path) -> list[Path]:
    """Get all immediate subdirectories (non-hidden) of a folder."""
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    return sorted(
        d for d in folder.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def load_map(folder: Path) -> dict | None:
    """Load the mapping file if it exists."""
    map_path = folder / MAP_FILENAME
    if not map_path.exists():
        return None
    with open(map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_map(folder: Path, mapping: dict) -> None:
    """Save the mapping file."""
    map_path = folder / MAP_FILENAME
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def compute_hash(name: str, length: int = HASH_LENGTH) -> str:
    """Compute SHA-256 hash of a name, return first `length` hex chars."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:length]


def resolve_conflicts(names: list[str], length: int = HASH_LENGTH) -> dict[str, str]:
    """
    Hash all names, auto-extending hash length to resolve collisions.
    Returns {hash_value: original_name}.
    """
    max_len = 64  # SHA-256 max hex length
    result = {}
    hash_to_names: dict[str, list[str]] = {}

    # Initial hashing
    for name in names:
        h = compute_hash(name, length)
        hash_to_names.setdefault(h, []).append(name)

    # Resolve collisions
    to_resolve = {h: ns for h, ns in hash_to_names.items() if len(ns) > 1}
    resolved = {h: ns[0] for h, ns in hash_to_names.items() if len(ns) == 1}

    current_len = length
    while to_resolve and current_len < max_len:
        current_len += 1
        new_to_resolve = {}
        for h, ns in to_resolve.items():
            sub_hash_to_names: dict[str, list[str]] = {}
            for name in ns:
                h2 = compute_hash(name, current_len)
                sub_hash_to_names.setdefault(h2, []).append(name)
            for h2, ns2 in sub_hash_to_names.items():
                if len(ns2) == 1:
                    resolved[h2] = ns2[0]
                else:
                    new_to_resolve[h2] = ns2
        to_resolve = new_to_resolve

    # If still unresolved (extremely unlikely), append index
    for h, ns in to_resolve.items():
        for i, name in enumerate(ns):
            resolved[f"{compute_hash(name, current_len)}_{i}"] = name

    return resolved


def cmd_encode(args) -> None:
    """Encode subfolder names to hashes."""
    folder = Path(args.folder).resolve()
    subdirs = get_immediate_subdirs(folder)

    if not subdirs:
        print("No subdirectories found.")
        return

    existing_map = load_map(folder)
    if existing_map is not None:
        # Check if already encoded — filter out already-hashed folders
        mapped_hashes = set(existing_map.keys()) - {META_KEY}
        already_hashed = [d for d in subdirs if d.name in mapped_hashes]
        to_hash = [d for d in subdirs if d.name not in mapped_hashes]

        if not to_hash:
            print("All subdirectories are already hashed. Nothing to do.")
            return

        if already_hashed:
            print(f"Note: {len(already_hashed)} folder(s) already hashed, skipping them.")

        # Merge with existing mapping
        mapping = existing_map
    else:
        mapping = {META_KEY: {"created": datetime.now(timezone.utc).isoformat(), "hash_algo": f"sha256_{HASH_LENGTH}char"}}
        to_hash = subdirs

    # Compute hashes for folders that need encoding
    names_to_hash = [d.name for d in to_hash]
    hash_map = resolve_conflicts(names_to_hash)
    # hash_map is {hash: name}, we need {name: hash}
    name_to_hash = {name: h for h, name in hash_map.items()}

    # Display preview
    print(f"\n{'Original Name':<30} {'→':^3} {'Hashed Name'}")
    print(f"{'─' * 30} {'─' * 3} {'─' * 12}")
    for d in to_hash:
        h = name_to_hash[d.name]
        print(f"{d.name:<30} {'→':^3} {h}")

    print(f"\n{len(to_hash)} folder(s) will be renamed.")

    if args.dry_run:
        print("\n[dry-run] No changes made.")
        return

    if not args.yes:
        confirm = input("\nProceed? [y/N] ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return

    # Backup existing map
    map_path = folder / MAP_FILENAME
    if map_path.exists():
        backup_path = folder / (MAP_FILENAME + ".bak")
        shutil.copy2(map_path, backup_path)

    # Rename folders
    errors = []
    for d in to_hash:
        h = name_to_hash[d.name]
        new_path = folder / h
        try:
            d.rename(new_path)
            mapping[h] = d.name
        except OSError as e:
            errors.append(f"  {d.name}: {e}")

    # Save mapping
    save_map(folder, mapping)

    if errors:
        print(f"\n⚠️  {len(errors)} error(s) occurred:")
        for err in errors:
            print(err)
    else:
        print(f"\n✅ Done. {len(to_hash)} folder(s) hashed. Mapping saved to {MAP_FILENAME}")


def cmd_decode(args) -> None:
    """Decode hashed folder names back to originals."""
    folder = Path(args.folder).resolve()
    mapping = load_map(folder)

    if mapping is None:
        print(f"Error: No mapping file ({MAP_FILENAME}) found in '{folder}'.", file=sys.stderr)
        sys.exit(1)

    # Get hash -> name pairs (exclude meta)
    hash_to_name = {k: v for k, v in mapping.items() if k != META_KEY}

    if not hash_to_name:
        print("Mapping file is empty. Nothing to decode.")
        return

    # Find which hashed folders actually exist
    to_restore = []
    for h, name in hash_to_name.items():
        hashed_path = folder / h
        if hashed_path.is_dir():
            to_restore.append((hashed_path, h, name))

    if not to_restore:
        print("No hashed folders found to restore.")
        return

    # Display preview
    print(f"\n{'Hashed Name':<12} {'→':^3} {'Original Name'}")
    print(f"{'─' * 12} {'─' * 3} {'─' * 30}")
    for _, h, name in to_restore:
        print(f"{h:<12} {'→':^3} {name}")

    print(f"\n{len(to_restore)} folder(s) will be restored.")

    if args.dry_run:
        print("\n[dry-run] No changes made.")
        return

    if not args.yes:
        confirm = input("\nProceed? [y/N] ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return

    # Backup existing map
    map_path = folder / MAP_FILENAME
    if map_path.exists():
        backup_path = folder / (MAP_FILENAME + ".bak")
        shutil.copy2(map_path, backup_path)

    # Rename folders back
    errors = []
    restored_hashes = []
    for hashed_path, h, name in to_restore:
        new_path = folder / name
        if new_path.exists():
            errors.append(f"  {h} → {name}: target already exists")
            continue
        try:
            hashed_path.rename(new_path)
            restored_hashes.append(h)
        except OSError as e:
            errors.append(f"  {h} → {name}: {e}")

    # Update mapping — remove restored entries
    for h in restored_hashes:
        del mapping[h]

    if mapping and len(mapping) > 1:  # More than just _meta
        save_map(folder, mapping)
    else:
        # All restored, remove mapping file
        map_path.unlink(missing_ok=True)

    if errors:
        print(f"\n⚠️  {len(errors)} error(s) occurred:")
        for err in errors:
            print(err)
    else:
        print(f"\n✅ Done. {len(to_restore)} folder(s) restored to original names.")


def cmd_list(args) -> None:
    """List current mapping without modifying anything."""
    folder = Path(args.folder).resolve()
    subdirs = get_immediate_subdirs(folder)
    mapping = load_map(folder)

    if mapping is None:
        # No mapping — show folders as-is
        print(f"\nFolder: {folder}")
        print("Status: Not encoded (no mapping file)\n")
        print(f"{'Folder Name':<40} {'Status'}")
        print(f"{'─' * 40} {'─' * 10}")
        for d in subdirs:
            print(f"{d.name:<40} original")
        return

    hash_to_name = {k: v for k, v in mapping.items() if k != META_KEY}

    print(f"\nFolder: {folder}")
    meta = mapping.get(META_KEY, {})
    print(f"Created: {meta.get('created', 'unknown')}")
    print(f"Algorithm: {meta.get('hash_algo', 'unknown')}\n")

    print(f"{'Hash / Name':<40} {'Status':<12} {'Original Name'}")
    print(f"{'─' * 40} {'─' * 12} {'─' * 30}")

    for d in subdirs:
        if d.name in hash_to_name:
            original = hash_to_name[d.name]
            print(f"{d.name:<40} {'hashed':<12} {original}")
        else:
            print(f"{d.name:<40} {'original':<12} —")

    # Check for mapping entries without corresponding folders
    orphaned = [h for h in hash_to_name if not (folder / h).is_dir()]
    if orphaned:
        print(f"\n⚠️  {len(orphaned)} orphaned mapping entry(ies) (folder not found):")
        for h in orphaned:
            print(f"  {h} → {hash_to_name[h]}")


def main():
    parser = argparse.ArgumentParser(
        prog="fhash",
        description="Folder name hashing tool — encode/decode subfolder names with SHA-256.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    def add_common_args(p):
        p.add_argument("folder", nargs="?", default=None, help="Target folder path (default: current directory)")
        p.add_argument("-n", "--dir", dest="target_dir", help="Target folder path (alternative to positional arg)")

    # encode
    enc_parser = subparsers.add_parser("encode", help="Hash subfolder names")
    add_common_args(enc_parser)
    enc_parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    enc_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # decode
    dec_parser = subparsers.add_parser("decode", help="Restore original folder names")
    add_common_args(dec_parser)
    dec_parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    dec_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")

    # list
    list_parser = subparsers.add_parser("list", help="Show current mapping")
    add_common_args(list_parser)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Resolve folder path: -n flag > positional arg > current directory
    if args.target_dir:
        args.folder = args.target_dir
    elif args.folder is None:
        args.folder = os.getcwd()

    commands = {
        "encode": cmd_encode,
        "decode": cmd_decode,
        "list": cmd_list,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
