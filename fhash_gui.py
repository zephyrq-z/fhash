#!/usr/bin/env python3
"""
fhash GUI — Cross-platform folder name hashing tool.
Works on macOS and Windows with tkinter.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sys
import threading
import tkinter as tk
from datetime import datetime, timezone
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ── Constants ──────────────────────────────────────────────────────────────
MAP_FILENAME = ".folder_hash_map.json"
HASH_LENGTH = 8
META_KEY = "_meta"
APP_NAME = "fhash"
APP_VERSION = "1.0.0"


# ── Core Logic (same as CLI, extracted for reuse) ─────────────────────────
def get_immediate_subdirs(folder: Path) -> list[Path]:
    """Get all immediate subdirectories (non-hidden) of a folder."""
    if not folder.is_dir():
        return []
    return sorted(
        d for d in folder.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def load_map(folder: Path) -> dict | None:
    map_path = folder / MAP_FILENAME
    if not map_path.exists():
        return None
    with open(map_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_map(folder: Path, mapping: dict) -> None:
    map_path = folder / MAP_FILENAME
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)


def compute_hash(name: str, length: int = HASH_LENGTH) -> str:
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:length]


def resolve_conflicts(names: list[str], length: int = HASH_LENGTH) -> dict[str, str]:
    max_len = 64
    hash_to_names: dict[str, list[str]] = {}
    for name in names:
        h = compute_hash(name, length)
        hash_to_names.setdefault(h, []).append(name)

    to_resolve = {h: ns for h, ns in hash_to_names.items() if len(ns) > 1}
    resolved = {h: ns[0] for h, ns in hash_to_names.items() if len(ns) == 1}

    current_len = length
    while to_resolve and current_len < max_len:
        current_len += 1
        new_to_resolve = {}
        for h, ns in to_resolve.items():
            sub: dict[str, list[str]] = {}
            for name in ns:
                h2 = compute_hash(name, current_len)
                sub.setdefault(h2, []).append(name)
            for h2, ns2 in sub.items():
                if len(ns2) == 1:
                    resolved[h2] = ns2[0]
                else:
                    new_to_resolve[h2] = ns2
        to_resolve = new_to_resolve

    for h, ns in to_resolve.items():
        for i, name in enumerate(ns):
            resolved[f"{compute_hash(name, current_len)}_{i}"] = name

    return resolved


def do_encode(folder: Path, dry_run: bool = False) -> dict:
    """
    Encode subfolder names. Returns result dict with keys:
      status: 'success' | 'already' | 'empty' | 'error'
      message: human-readable summary
      changes: list of (original, hashed) tuples
      dry_run: bool
    """
    subdirs = get_immediate_subdirs(folder)
    if not subdirs:
        return {"status": "empty", "message": "No subdirectories found.", "changes": [], "dry_run": dry_run}

    existing_map = load_map(folder)
    if existing_map is not None:
        mapped_hashes = set(existing_map.keys()) - {META_KEY}
        to_hash = [d for d in subdirs if d.name not in mapped_hashes]
        if not to_hash:
            return {"status": "already", "message": "All subdirectories are already hashed.", "changes": [], "dry_run": dry_run}
        mapping = existing_map
    else:
        mapping = {META_KEY: {"created": datetime.now(timezone.utc).isoformat(), "hash_algo": f"sha256_{HASH_LENGTH}char"}}
        to_hash = subdirs

    names_to_hash = [d.name for d in to_hash]
    hash_map = resolve_conflicts(names_to_hash)
    name_to_hash = {name: h for h, name in hash_map.items()}

    changes = [(d.name, name_to_hash[d.name]) for d in to_hash]

    if dry_run:
        return {"status": "success", "message": f"[Preview] {len(to_hash)} folder(s) would be hashed.", "changes": changes, "dry_run": True}

    # Backup existing map
    map_path = folder / MAP_FILENAME
    if map_path.exists():
        backup_path = folder / (MAP_FILENAME + ".bak")
        shutil.copy2(map_path, backup_path)

    errors = []
    for d in to_hash:
        h = name_to_hash[d.name]
        new_path = folder / h
        try:
            d.rename(new_path)
            mapping[h] = d.name
        except OSError as e:
            errors.append(f"{d.name}: {e}")

    save_map(folder, mapping)

    if errors:
        return {"status": "error", "message": f"{len(to_hash) - len(errors)} hashed, {len(errors)} error(s):\n" + "\n".join(errors), "changes": changes, "dry_run": False}
    return {"status": "success", "message": f"✅ {len(to_hash)} folder(s) hashed.", "changes": changes, "dry_run": False}


def do_decode(folder: Path, dry_run: bool = False) -> dict:
    mapping = load_map(folder)
    if mapping is None:
        return {"status": "error", "message": f"No mapping file ({MAP_FILENAME}) found.", "changes": [], "dry_run": dry_run}

    hash_to_name = {k: v for k, v in mapping.items() if k != META_KEY}
    if not hash_to_name:
        return {"status": "empty", "message": "Mapping file is empty.", "changes": [], "dry_run": dry_run}

    to_restore = []
    for h, name in hash_to_name.items():
        if (folder / h).is_dir():
            to_restore.append((h, name))

    if not to_restore:
        return {"status": "empty", "message": "No hashed folders found to restore.", "changes": [], "dry_run": dry_run}

    changes = [(h, name) for h, name in to_restore]

    if dry_run:
        return {"status": "success", "message": f"[Preview] {len(to_restore)} folder(s) would be restored.", "changes": changes, "dry_run": True}

    map_path = folder / MAP_FILENAME
    if map_path.exists():
        backup_path = folder / (MAP_FILENAME + ".bak")
        shutil.copy2(map_path, backup_path)

    errors = []
    restored_hashes = []
    for h, name in to_restore:
        hashed_path = folder / h
        new_path = folder / name
        if new_path.exists():
            errors.append(f"{h} → {name}: target already exists")
            continue
        try:
            hashed_path.rename(new_path)
            restored_hashes.append(h)
        except OSError as e:
            errors.append(f"{h} → {name}: {e}")

    for h in restored_hashes:
        del mapping[h]

    if mapping and len(mapping) > 1:
        save_map(folder, mapping)
    else:
        map_path.unlink(missing_ok=True)

    if errors:
        return {"status": "error", "message": f"{len(to_restore) - len(errors)} restored, {len(errors)} error(s):\n" + "\n".join(errors), "changes": changes, "dry_run": False}
    return {"status": "success", "message": f"✅ {len(to_restore)} folder(s) restored.", "changes": changes, "dry_run": False}


def do_list(folder: Path) -> list[dict]:
    """Return list of {name, status, original_or_hash} for each subfolder."""
    subdirs = get_immediate_subdirs(folder)
    mapping = load_map(folder)
    result = []

    if mapping is None:
        for d in subdirs:
            result.append({"name": d.name, "status": "original", "detail": "—"})
        return result

    hash_to_name = {k: v for k, v in mapping.items() if k != META_KEY}
    for d in subdirs:
        if d.name in hash_to_name:
            result.append({"name": d.name, "status": "hashed", "detail": hash_to_name[d.name]})
        else:
            result.append({"name": d.name, "status": "original", "detail": "—"})
    return result


# ── GUI ────────────────────────────────────────────────────────────────────
class FhashApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} — Folder Hasher v{APP_VERSION}")
        self.root.geometry("720x520")
        self.root.minsize(600, 400)

        # macOS-specific tweaks
        if platform.system() == "Darwin":
            try:
                self.root.tk.call("::tk::unsupported::MacWindowStyle", "style", self.root._w, "document", "closeBox collapseBox")
            except tk.TclError:
                pass

        self._build_ui()

        # If launched with a folder argument, use it
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            self.path_var.set(sys.argv[1])
            self.root.after(100, self._refresh_list)

    def _build_ui(self):
        # ── Top: Folder selector ──
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        ttk.Label(top_frame, text="📁 Folder:", font=("", 13, "bold")).pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(top_frame, textvariable=self.path_var, font=("", 12))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 4))
        self.path_var.trace_add("write", lambda *_: self._on_path_change())

        ttk.Button(top_frame, text="Browse…", command=self._browse).pack(side=tk.LEFT)

        # ── Middle: Treeview table ──
        mid_frame = ttk.Frame(self.root, padding=(10, 0, 10, 0))
        mid_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("name", "status", "detail")
        self.tree = ttk.Treeview(mid_frame, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("name", text="Folder Name")
        self.tree.heading("status", text="Status")
        self.tree.heading("detail", text="Detail")
        self.tree.column("name", width=260, minwidth=120)
        self.tree.column("status", width=80, minwidth=60, anchor=tk.CENTER)
        self.tree.column("detail", width=260, minwidth=120)

        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Bottom: Action buttons + status ──
        bot_frame = ttk.Frame(self.root, padding=10)
        bot_frame.pack(fill=tk.X)

        self.btn_encode = ttk.Button(bot_frame, text="🔒 Encode", command=lambda: self._action("encode"))
        self.btn_decode = ttk.Button(bot_frame, text="🔓 Decode", command=lambda: self._action("decode"))
        self.btn_preview = ttk.Button(bot_frame, text="👁 Preview Encode", command=lambda: self._action("preview_encode"))
        self.btn_preview_dec = ttk.Button(bot_frame, text="👁 Preview Decode", command=lambda: self._action("preview_decode"))
        self.btn_refresh = ttk.Button(bot_frame, text="🔄 Refresh", command=self._refresh_list)

        self.btn_encode.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_decode.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_preview.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_preview_dec.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_refresh.pack(side=tk.RIGHT)

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Ready. Select a folder to begin.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(10, 4))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _browse(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.path_var.set(folder)

    def _on_path_change(self):
        path = self.path_var.get().strip()
        if path and os.path.isdir(path):
            self.root.after(50, self._refresh_list)

    def _refresh_list(self):
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            self.status_var.set("⚠️ Invalid folder path.")
            return

        folder = Path(path).resolve()
        items = do_list(folder)

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in items:
            tag = item["status"]
            self.tree.insert("", tk.END, values=(item["name"], item["status"], item["detail"]), tags=(tag,))

        # Tag styling
        self.tree.tag_configure("hashed", foreground="#2e7d32")  # green
        self.tree.tag_configure("original", foreground="#1565c0")  # blue

        mapping = load_map(folder)
        if mapping:
            hashed_count = sum(1 for i in items if i["status"] == "hashed")
            original_count = sum(1 for i in items if i["status"] == "original")
            self.status_var.set(f"📂 {folder} — {hashed_count} hashed, {original_count} original")
        else:
            self.status_var.set(f"📂 {folder} — {len(items)} folder(s), not encoded")

    def _action(self, action: str):
        path = self.path_var.get().strip()
        if not path or not os.path.isdir(path):
            messagebox.showwarning("Invalid Path", "Please select a valid folder first.")
            return

        folder = Path(path).resolve()

        if action == "preview_encode":
            result = do_encode(folder, dry_run=True)
            self._show_preview("Preview: Encode", result)
            return

        if action == "preview_decode":
            result = do_decode(folder, dry_run=True)
            self._show_preview("Preview: Decode", result)
            return

        if action == "encode":
            # First show preview
            preview = do_encode(folder, dry_run=True)
            if preview["status"] in ("empty", "already"):
                messagebox.showinfo("Encode", preview["message"])
                self._refresh_list()
                return

            changes_text = "\n".join(f"  {orig} → {hashed}" for orig, hashed in preview["changes"])
            confirm = messagebox.askyesno(
                "Confirm Encode",
                f"The following {len(preview['changes'])} folder(s) will be hashed:\n\n{changes_text}\n\nProceed?",
            )
            if not confirm:
                return

            result = do_encode(folder, dry_run=False)
            self.status_var.set(result["message"])
            if result["status"] == "error":
                messagebox.showerror("Encode Error", result["message"])
            else:
                messagebox.showinfo("Encode Complete", result["message"])
            self._refresh_list()

        elif action == "decode":
            preview = do_decode(folder, dry_run=True)
            if preview["status"] in ("empty", "error"):
                messagebox.showinfo("Decode", preview["message"])
                self._refresh_list()
                return

            changes_text = "\n".join(f"  {hashed} → {orig}" for hashed, orig in preview["changes"])
            confirm = messagebox.askyesno(
                "Confirm Decode",
                f"The following {len(preview['changes'])} folder(s) will be restored:\n\n{changes_text}\n\nProceed?",
            )
            if not confirm:
                return

            result = do_decode(folder, dry_run=False)
            self.status_var.set(result["message"])
            if result["status"] == "error":
                messagebox.showerror("Decode Error", result["message"])
            else:
                messagebox.showinfo("Decode Complete", result["message"])
            self._refresh_list()

    def _show_preview(self, title: str, result: dict):
        if result["status"] in ("empty", "already", "error"):
            messagebox.showinfo(title, result["message"])
            return

        # Show preview in a popup window
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("500x400")
        win.transient(self.root)

        ttk.Label(win, text=result["message"], font=("", 13, "bold"), padding=10).pack(anchor=tk.W)

        cols = ("from", "to")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        if "Encode" in title:
            tree.heading("from", text="Original Name")
            tree.heading("to", text="→ Hashed Name")
        else:
            tree.heading("from", text="Hashed Name")
            tree.heading("to", text="→ Original Name")
        tree.column("from", width=220)
        tree.column("to", width=220)

        for a, b in result["changes"]:
            tree.insert("", tk.END, values=(a, b))

        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        ttk.Label(win, text="[Preview only — no changes made]", foreground="gray", padding=(10, 0, 10, 10)).pack()


def main():
    root = tk.Tk()

    # High-DPI support on Windows
    if platform.system() == "Windows":
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

    # Theme
    style = ttk.Style()
    available_themes = style.theme_names()
    if platform.system() == "Darwin" and "aqua" in available_themes:
        style.theme_use("aqua")
    elif "clam" in available_themes:
        style.theme_use("clam")

    app = FhashApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
