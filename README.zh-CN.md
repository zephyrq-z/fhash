<p align="center">
  <img src="assets/icon.png" alt="fhash" width="128" />
</p>

<h1 align="center">fhash</h1>

<p align="center">
  <strong>用 SHA-256 哈希你的文件夹名称，随时可还原。</strong><br>
  CLI · GUI · macOS 右键菜单 · 开源
</p>

<p align="center">
  <a href="README.md">English</a> | <strong>中文</strong>
</p>

<p align="center">
  <a href="#安装"><img src="https://img.shields.io/badge/macOS-✓-000000?logo=apple" alt="macOS"></a>
  <a href="#安装"><img src="https://img.shields.io/badge/Windows-✓-0078D4?logo=windows" alt="Windows"></a>
  <a href="#许可证"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
  <a href="#"><img src="https://img.shields.io/badge/python-3.9%2B-yellow?logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/github/stars/zephyrq-z/fhash?style=social" alt="Stars"></a>
</p>

---

## ✨ fhash 是什么？

**fhash** 可以将一个目录下的所有子文件夹名称替换为 SHA-256 短哈希值（8 位十六进制字符），同时保留映射文件，让你随时可以还原为原始名称。

你可以把它理解为一个**可逆的文件夹结构"匿名化"工具** —— 适用于隐私保护、测试、或者在不暴露敏感名称的情况下分享项目结构。

### 效果演示

```
my_projects/                    my_projects/
├── 我的项目/          ──→      ├── 9ce557b3/
├── test_data/         ──→      ├── e7d87b73/
├── 2024年报告/         ──→      ├── 7c330497/
└── backend-api/       ──→      └── d753230e/
```

### 适用场景

| 场景 | fhash 如何帮助你 |
|------|----------------|
| 🔒 **隐私保护** | 在分享或上传前隐藏文件夹名称 |
| 📦 **匿名化** | 移除项目结构中的可识别名称 |
| 🧪 **测试** | 在 CI/CD 流程中模拟不透明的文件夹命名 |
| 🎯 **整理** | 临时隐藏项目名称，但保持目录结构不变 |
| 📸 **截图** | 截图时隐藏敏感的文件夹名称 |

## 🚀 功能特点

- **SHA-256 哈希** — 每个文件夹名生成 8 位十六进制哈希（≈2.8 万亿种组合）
- **完全可逆** — 通过映射文件随时还原原始名称
- **幂等操作** — 重复执行 encode 不会二次哈希
- **碰撞安全** — 发生哈希碰撞时自动扩展长度（8→9→10...）
- **预览模式** — 执行前可预览所有变更（`--dry-run`）
- **隐藏文件夹感知** — 自动跳过以 `.` 开头的隐藏文件夹
- **Unicode 支持** — 完整中文 / CJK / Emoji / Unicode 文件夹名支持
- **自动备份** — 每次操作前自动创建 `.bak` 备份
- **macOS 右键菜单** — 原生 Finder 快速操作集成（无需第三方应用）
- **GUI 应用** — 跨平台 tkinter 界面，可构建为 macOS `.app` 和 Windows `.exe`
- **零依赖** — 纯 Python 标准库（无需 `pip install`）

## 📦 安装

<a id="安装"></a>

### 方式一：完整安装（CLI + macOS 右键菜单）— *macOS 推荐*

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash

# 安装 CLI 到 ~/bin/fhash
bash install.sh

# 安装 Finder 右键菜单（快速操作）
bash install_quick_actions.sh
```

### 方式二：仅安装 CLI（macOS / Linux / WSL）

需要 **Python 3.9+** — 无需任何 pip 包。

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
bash install.sh

# 或直接运行，无需安装：
python3 fhash.py --help
```

### 方式三：从源码运行 GUI

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
python3 fhash_gui.py
```

### 方式四：下载预编译应用

| 平台 | 文件 | 使用方式 |
|------|------|---------|
| macOS | `fhash.app` | 拖入 `/Applications`，双击运行 |
| Windows | `fhash.exe` | 双击运行，无需安装 |

> 从 [Releases](../../releases) 下载（即将发布）。

## 📖 使用方式

### macOS 右键菜单（快速操作）

运行 `bash install_quick_actions.sh` 后：

1. 打开 **Finder**
2. 选中一个文件夹
3. **右键** → **快速操作** →
   - **fhash Encode** — 哈希化所有子文件夹名称
   - **fhash Decode** — 还原为原始文件夹名称
4. 操作完成后会弹出通知

> **提示：** 如果看不到快速操作，请前往 **系统设置 → 隐私与安全性 → 扩展 → Finder**，启用 fhash。

### 命令行（CLI）

```bash
# 哈希化 — 将子文件夹名称替换为哈希值
fhash encode /path/to/folder

# 预览模式（仅显示变更，不实际执行）
fhash encode /path/to/folder --dry-run

# 还原 — 恢复原始文件夹名称
fhash decode /path/to/folder

# 查看 — 显示当前映射状态（不修改文件）
fhash list /path/to/folder

# 使用当前目录（无需指定路径）
cd /path/to/folder && fhash encode

# 使用 -n 指定路径
fhash encode -n /path/to/folder

# 跳过确认提示
fhash encode /path/to/folder --yes
```

#### CLI 输出示例

```bash
$ fhash encode ~/projects --dry-run

原始名称                        →  哈希值
────────────────────────────── ─── ────────────
2024年报告                         →  7c330497
backend-api                     →  d753230e
test_data                       →  e7d87b73
我的项目                            →  9ce557b3

4 个文件夹将被重命名。

[预览模式] 未做任何更改。
```

```bash
$ fhash decode ~/projects --yes

哈希值        →  原始名称
──────────── ─── ──────────────────────────────
7c330497      →  2024年报告
d753230e      →  backend-api
e7d87b73      →  test_data
9ce557b3      →  我的项目

✅ 完成。4 个文件夹已还原为原始名称。
```

### 图形界面（GUI）

启动应用后：

1. **选择文件夹** — 点击 "Browse…" 或粘贴路径
2. **预览** — 点击 "👁 Preview Encode" 查看即将发生的变更
3. **哈希化** — 点击 "🔒 Encode" 执行哈希化
4. **还原** — 点击 "🔓 Decode" 恢复原始名称
5. **刷新** — 点击 "🔄 Refresh" 重新加载文件夹列表

## 🔧 工作原理

```
目标文件夹/
├── .folder_hash_map.json   ← 隐藏映射文件（JSON）
├── a3f1b2c7/               ← 原名为 "我的项目"
├── 8d4e2f01/               ← 原名为 "test_data"
└── e7c93a12/               ← 原名为 "2024年报告"
```

**映射文件**（`.folder_hash_map.json`）：

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

**算法流程：**
1. 计算 `SHA-256(文件夹名称)`，取前 8 位十六进制字符
2. 如果发生碰撞，自动扩展到 9、10、... 最多 64 位
3. 将每个子文件夹重命名为其哈希值
4. 将 `哈希值 → 原始名称` 的映射关系存储在 `.folder_hash_map.json` 中
5. 隐藏文件夹（以 `.` 开头）始终被跳过
6. 每次操作前自动创建映射文件的 `.bak` 备份

## 🏗️ 从源码构建

### macOS .app

```bash
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
pip3 install pyinstaller pillow
bash build_mac.sh
# 输出：dist/fhash.app
```

### Windows .exe

在 Windows 机器上（需要 Python 3.9+）：

```powershell
git clone https://github.com/zephyrq-z/fhash.git
cd fhash
pip install pyinstaller pillow
build_win.bat
# 输出：dist\fhash.exe
```

### 重新生成图标

```bash
pip install pillow
python3 assets/gen_icon.py
# 生成 assets/icon.icns (macOS) 和 assets/icon.ico (Windows)
```

## 📁 项目结构

```
fhash/
├── fhash.py                   # CLI 工具（核心逻辑）
├── fhash_gui.py               # GUI 应用（tkinter，跨平台）
├── fhash-encode-runner.sh     # macOS 快速操作运行脚本（编码）
├── fhash-decode-runner.sh     # macOS 快速操作运行脚本（解码）
├── install.sh                 # CLI 安装脚本（创建 ~/bin 符号链接）
├── install_quick_actions.sh   # macOS Finder 快速操作安装脚本
├── build_mac.sh               # macOS .app 构建脚本（PyInstaller）
├── build_win.bat              # Windows .exe 构建脚本（PyInstaller）
├── assets/
│   ├── gen_icon.py            # 应用图标生成器（Pillow）
│   ├── icon.icns              # macOS 图标
│   └── icon.ico               # Windows 图标
├── README.md                  # 英文说明
├── README.zh-CN.md            # 中文说明（本文件）
├── LICENSE                    # MIT 许可证
└── .gitignore
```

## ❓ 常见问题

<details>
<summary><strong>这是真正的加密吗？</strong></summary>
<br>
不是加密，而是带映射文件的哈希。SHA-256 哈希本身是单向不可逆的，但 <code>.folder_hash_map.json</code> 存储了原始名称用于还原。任何能访问映射文件的人都可以看到原始名称。如果你需要真正的加密，可以考虑添加密码保护的映射文件（参见贡献想法）。
</details>

<details>
<summary><strong>如果我不小心删了映射文件怎么办？</strong></summary>
<br>
哈希化的文件夹名会保留，但无法自动还原。请务必保留 <code>.folder_hash_map.json</code> 的备份。好消息是，每次操作前都会自动创建 <code>.bak</code> 备份。
</details>

<details>
<summary><strong>可以哈希嵌套的子文件夹吗？</strong></summary>
<br>
不可以，fhash 只处理直接子文件夹（一层深度）。这是出于安全和简洁性的设计考虑。如果需要更深层的哈希，可以对每个目录分别执行 fhash。
</details>

<details>
<summary><strong>文件夹内的文件会受影响吗？</strong></summary>
<br>
不会。只有文件夹<strong>名称</strong>被修改，所有文件、嵌套目录和内容完全不受影响。
</details>

<details>
<summary><strong>如果两个文件夹名产生了相同的哈希值怎么办？</strong></summary>
<br>
哈希长度会自动扩展（8 → 9 → 10 位），直到所有碰撞都解决。8 位哈希有 2.8 万亿种组合，碰撞概率极低。
</details>

<details>
<summary><strong>为什么 Finder 里看不到快速操作？</strong></summary>
<br>
请前往 <strong>系统设置 → 隐私与安全性 → 扩展 → Finder</strong>，启用 fhash Encode / fhash Decode。安装后可能需要重启 Finder（<code>killall Finder</code>）。
</details>

<details>
<summary><strong>支持软链接吗？</strong></summary>
<br>
指向目录的软链接不会被跟踪——只处理真实的目录。这可以防止意外重命名文件系统中的其他位置。
</details>

<details>
<summary><strong>Windows / Linux 能用吗？</strong></summary>
<br>
可以！CLI 和 GUI 在任何安装了 Python 3.9+ 的平台上都能运行。Finder 快速操作仅限 macOS，但 CLI 和 GUI 是完全跨平台的。
</details>

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！以下是一些贡献想法：

- [ ] GUI 支持拖拽文件夹
- [ ] Linux .AppImage / Nautilus 右键菜单集成
- [ ] Windows 资源管理器右键菜单（注册表方式）
- [ ] 基于正则表达式的文件夹名过滤
- [ ] 密码加密映射文件选项
- [ ] 批量处理多个目录
- [ ] 撤销历史（多级回滚）
- [ ] 国际化：添加更多语言支持

## 📄 许可证

[MIT 许可证](LICENSE) — 个人和商业使用均免费。

## ⭐ Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=zephyrq-z/fhash&type=Date)](https://star-history.com/#zephyrq-z/fhash&Date)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/zephyrq-z">zephyrq-z</a>
</p>
