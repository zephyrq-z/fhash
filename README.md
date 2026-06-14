<p align="center">
  <img src="assets/icon.png" alt="fhash" width="128" />
</p>

<h1 align="center">fhash</h1>

<p align="center">
  <strong>Hash your folder names with SHA-256, restore them anytime.</strong><br>
  CLI · GUI · macOS Right-Click · Open Source
</p>

<p align="center">
  <strong>English</strong> | <a href="README.zh-CN.md">中文</a>
</p>

<p align="center">
  <a href="#installation"><img src="https://img.shields.io/badge/macOS-✓-000000?logo=apple" alt="macOS"></a>
  <a href="#installation"><img src="https://img.shields.io/badge/Windows-✓-0078D4?logo=windows" alt="Windows"></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.9%2B-yellow?logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/github/stars/zephyrq-z/fhash?style=social" alt="Stars"></a>
</p>

---

## ✨ What is fhash?

**fhash** replaces all subfolder names in a directory with short SHA-256 hashes (8 hex characters), while keeping a mapping file so you can restore the original names at any time.

Think of it as a **reversible "anonymizer" for folder structures** — useful for privacy, testing, or sharing project layouts without revealing sensitive names.

### Before & After

```
my_projects/                    my_projects/
├── 我的项目/          ──→      ├── 9ce557b3/
├── test_data/         ──→      ├── e7d87b73/
├── 2024年报告/         ──→      ├── 7c330497/
└── backend-api/       ──→      └── d753230e/
```

### Use Cases

| Scenario | How fhash helps |
|----------|----------------|
| 🔒 **Privacy** | Obscure folder names before sharing or uploading |
| 📦 **Anonymization** | Remove identifiable names from project structures |
| 🧪 **Testing** | Simulate opaque folder naming in CI/CD pipelines |
| 🎯 **Organization** | Temporarily hide project names while keeping structure intact |
| 📸 **Screenshots** | Hide sensitive folder names when taking screenshots |

## 🚀 Features

- **SHA-256 hashing** — 8-character hex hash per folder name (≈2.8 trillion combinations)
- **Fully reversible** — Restore original names from the mapping file at any time
- **Idempotent** — Running encode twice won't double-hash
- **Collision-safe** — Auto-extends hash length (8→9→10...) on collision
- **Dry-run preview** — See all changes before applying (`--dry-run`)
- **Hidden folder aware** — Skips `.` prefixed folders automatically
- **Unicode support** — Full CJK / emoji / Unicode folder name support
- **Auto backup** — Creates `.bak` before each operation
- **macOS Right-Click** — Native Finder Quick Actions (no third-party apps)
- **GUI App** — Cross-platform tkinter GUI, buildable as macOS `.app` and Windows `.exe`
- **Zero dependencies** — Pure Python stdlib (no `pip install` needed)

## 📦 Installation

<a id="installation"></a>

### Option 1: Full Install (CLI + macOS Right-Click) — *Recommended for macOS*

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash

# Install CLI to ~/bin/fhash
bash install.sh

# Install Finder right-click Quick Actions
bash install_quick_actions.sh
```

### Option 2: CLI Only (macOS / Linux / WSL)

Requires **Python 3.9+** — no pip packages needed.

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
bash install.sh

# Or run directly without installing:
python3 fhash.py --help
```

### Option 3: GUI from Source

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
python3 fhash_gui.py
```

### Option 4: Download Pre-built App

| Platform | File | How to use |
|----------|------|------------|
| macOS | `fhash.app` | Drag to `/Applications`, double-click to run |
| Windows | `fhash.exe` | Double-click to run, no install needed |

> Download from [Releases](../../releases) (coming soon).

## 📖 Usage

### macOS Right-Click (Quick Actions)

After running `bash install_quick_actions.sh`:

1. Open **Finder**
2. Select a folder
3. **Right-click** → **Quick Actions** →
   - **fhash Encode** — Hash all subfolder names
   - **fhash Decode** — Restore original folder names
4. A notification will appear when done

> **Tip:** If Quick Actions don't appear, go to **System Settings → Privacy & Security → Extensions → Finder** and enable fhash.

### CLI

```bash
# Encode — hash all subfolder names
fhash encode /path/to/folder

# Preview only (dry-run, no changes)
fhash encode /path/to/folder --dry-run

# Decode — restore original names
fhash decode /path/to/folder

# List — view current mapping (read-only)
fhash list /path/to/folder

# Current directory (no path needed)
cd /path/to/folder && fhash encode

# Use -n to specify path
fhash encode -n /path/to/folder

# Skip confirmation prompt
fhash encode /path/to/folder --yes
```

#### CLI Output Examples

```bash
$ fhash encode ~/projects --dry-run

Original Name                   →  Hashed Name
────────────────────────────── ─── ────────────
2024年报告                         →  7c330497
backend-api                     →  d753230e
test_data                       →  e7d87b73
我的项目                            →  9ce557b3

4 folder(s) will be renamed.

[dry-run] No changes made.
```

```bash
$ fhash decode ~/projects --yes

Hashed Name   →  Original Name
──────────── ─── ──────────────────────────────
7c330497      →  2024年报告
d753230e      →  backend-api
e7d87b73      →  test_data
9ce557b3      →  我的项目

✅ Done. 4 folder(s) restored to original names.
```

### GUI

Launch the app and:

1. **Select a folder** — Click "Browse…" or paste a path
2. **Preview** — Click "👁 Preview Encode" to see what will change
3. **Encode** — Click "🔒 Encode" to hash folder names
4. **Decode** — Click "🔓 Decode" to restore original names
5. **Refresh** — Click "🔄 Refresh" to reload the folder list

## 🔧 How It Works

```
Target Folder/
├── .folder_hash_map.json   ← Hidden mapping file (JSON)
├── a3f1b2c7/               ← Was "我的项目"
├── 8d4e2f01/               ← Was "test_data"
└── e7c93a12/               ← Was "2024年报告"
```

**Mapping file** (`.folder_hash_map.json`):

```json
{
  "_meta": {
    "created": "2026-06-14T02:42:19.845934+00:00",
    "hash_algo": "sha256_8char"
  },
  "a3f1b2c7": "我的项目",
  "8d4e2f01": "test_data",
  "e7c93a12": "2024年报告"
}
```

**Algorithm:**
1. Compute `SHA-256(folder_name)` and take the first 8 hex characters
2. If a collision occurs, auto-extend to 9, 10, ... up to 64 characters
3. Rename each subfolder to its hash value
4. Store the `hash → original_name` mapping in `.folder_hash_map.json`
5. Hidden folders (`.` prefix) are always skipped
6. A `.bak` backup of the mapping file is created before each operation

## 🏗️ Build from Source

### macOS .app

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
pip3 install pyinstaller pillow
bash build_mac.sh
# Output: dist/fhash.app
```

### Windows .exe

On a Windows machine with Python 3.9+:

```powershell
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
pip install pyinstaller pillow
build_win.bat
# Output: dist\fhash.exe
```

### Regenerate Icons

```bash
pip install pillow
python3 assets/gen_icon.py
# Generates assets/icon.icns (macOS) and assets/icon.ico (Windows)
```

## 📁 Project Structure

```
fhash/
├── fhash.py                   # CLI tool (core logic)
├── fhash_gui.py               # GUI application (tkinter, cross-platform)
├── fhash-encode-runner.sh     # macOS Quick Action runner (encode)
├── fhash-decode-runner.sh     # macOS Quick Action runner (decode)
├── install.sh                 # CLI installer (symlink to ~/bin)
├── install_quick_actions.sh   # macOS Finder Quick Actions installer
├── build_mac.sh               # macOS .app builder (PyInstaller)
├── build_win.bat              # Windows .exe builder (PyInstaller)
├── assets/
│   ├── gen_icon.py            # App icon generator (Pillow)
│   ├── icon.icns              # macOS icon
│   └── icon.ico               # Windows icon
├── README.md                  # English docs (this file)
├── README.zh-CN.md            # 中文文档
├── LICENSE                    # MIT License
└── .gitignore
```

## ❓ FAQ

<details>
<summary><strong>Is this real encryption?</strong></summary>
<br>
No, it's hashing with a mapping file. The SHA-256 hash itself is one-way (irreversible), but the <code>.folder_hash_map.json</code> stores the original names for restoration. Anyone with access to the mapping file can see the original names. If you need true encryption, consider adding a password-protected mapping file (see Contributing ideas).
</details>

<details>
<summary><strong>What happens if I delete the mapping file?</strong></summary>
<br>
The hashed folder names will remain, but you won't be able to restore them automatically. Always keep a backup of <code>.folder_hash_map.json</code>. Fortunately, a <code>.bak</code> backup is created before each operation.
</details>

<details>
<summary><strong>Can I hash nested (deep) folders?</strong></summary>
<br>
No, fhash only processes immediate subfolders (one level deep). This is by design for safety and simplicity. Use fhash on each directory separately if you need deeper hashing.
</details>

<details>
<summary><strong>Will file contents be affected?</strong></summary>
<br>
No. Only folder <strong>names</strong> are changed. All files, nested directories, and contents remain completely untouched.
</details>

<details>
<summary><strong>What if two folder names produce the same hash?</strong></summary>
<br>
The hash length auto-extends (8 → 9 → 10 chars) until all collisions are resolved. This is extremely rare with 8-char hashes (2.8 trillion combinations).
</details>

<details>
<summary><strong>Why is the Quick Action not showing in Finder?</strong></summary>
<br>
Go to <strong>System Settings → Privacy & Security → Extensions → Finder</strong> and enable fhash Encode / fhash Decode. You may also need to restart Finder (<code>killall Finder</code>) after installation.
</details>

<details>
<summary><strong>Does it work with symlinks?</strong></summary>
<br>
Symlinks to directories are not followed — only real directories are processed. This prevents unintended renames across your filesystem.
</details>

<details>
<summary><strong>Can I use it on Windows / Linux?</strong></summary>
<br>
Yes! The CLI and GUI work on any platform with Python 3.9+. The Finder Quick Actions are macOS-only, but the CLI and GUI are fully cross-platform.
</details>

## 🤝 Contributing

Issues and PRs are welcome! Here are some ideas for contributors:

- [ ] GUI drag-and-drop folder support
- [ ] Linux .AppImage / Nautilus right-click integration
- [ ] Windows Explorer right-click context menu (registry)
- [ ] Regex-based folder name filtering
- [ ] Password-encrypted mapping file option
- [ ] Batch mode for multiple directories
- [ ] Undo history (multi-level rollback)
- [ ] i18n: add more languages

## 📄 License

[MIT License](LICENSE) — free for personal and commercial use.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=zephyrq-z/fhash&type=Date)](https://star-history.com/#zephyrq-z/fhash&Date)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/zephyrq-z">zephyrq-z</a>
</p>
