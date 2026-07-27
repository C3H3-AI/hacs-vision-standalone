# HACS (Home Assistant Community Store)

> **📦 这是 HACS 与 HACS Vision 的合并版（hacs-vision-standalone）。**
> 内置 HACS Vision 面板，集成 domain 仍为 `hacs`。安装即用，无需再单独安装独立的 HACS Vision 集成。
>
> **当前版本：7.0** ｜ 自我更新源：`C3H3-AI/hacs-vision-standalone`（跟本仓库，不跟官方 hacs）

_Manage (Install, track, upgrade) and discover custom elements for Home Assistant directly from the UI._

## What?

HACS is an integration that gives the user a powerful UI to handle downloads of custom needs.

**Highlights of what HACS can do:**

- Help you discover new custom elements.
- Help you download new custom elements.
- Help you keep track of your custom elements.
  - Manage(download/update/remove)
  - Shortcuts to repositories/issue tracker

## Useful links

- [General documentation](https://hacs.xyz/)
- [Configuration](https://hacs.xyz/docs/use/configuration/basic)
- [FAQ](https://hacs.xyz/docs/faq)
- [GitHub](https://github.com/hacs)
- [Discord](https://discord.ga/apgchf8)
- [Become a GitHub sponsor? ❤️](https://github.com/sponsors/ludeeus)
- [BuyMe~~Coffee~~Beer? 🍺🙈](https://buymeacoffee.com/ludeeus)


## Issues

~~If~~ When you experience issues/bugs with this the best way to report them is to open an issue in **this** repo.

[Issue link](https://hacs.xyz/docs/help/issues)

---

## 从独立 HACS Vision 升级到本合并版

如果你之前安装的是独立的 **HACS Vision**（`hacs_vision` 集成），升级到本合并版（domain 为 `hacs`）时请注意以下兼容性问题。

### ⚠️ 关键：删除旧集成 ≠ 清理仓库记录

- 在 **HA 设置 → 设备与服务 → 删除 hacs_vision 集成**（删 config entry）**不会**清理 HACS 的 `hacs.repositories` 记录。
- 残留记录会让 HACS 每次自动更新去调用已不存在的 `hacs_vision.auto_update_reload_settings` 服务，从而报错。
- **正确的清理方式**：进入 **HACS 面板 → 找到 hacs_vision 仓库 → 点击「移除仓库」**。只有这步才会从 `hacs.repositories` 真正删除记录（代码路径：`hacs/repositories/remove` → `repository.remove()` → `repositories.unregister()` → 写回存储）。

### 升级步骤（推荐）

1. 在 HACS 面板「移除」原来的 hacs_vision 仓库（清 `hacs.repositories` 残留记录）。
2. 添加本合并版仓库；**若本合并版发布在与原 hacs_vision 相同的 GitHub 仓库（同一 full_name），此步可跳过，直接在 HACS 内「更新」即可**。
3. 安装/更新，HACS 会把合并版写入 `custom_components/hacs/`，覆盖原版 hacs 与独立 hacs_vision 目录。
4. 重启 Home Assistant，并清理 `__pycache__` 避免旧 pyc 缓存。
5. **数据自动继承**：合并版沿用了 `hacs_vision_*.json` 存储路径（GitHub token / 收藏 / 设置），存量用户无需重新登录。

### 关于仓库地址（存量用户迁移成本）

- **复用原仓库（推荐）**：把本合并版发布在 hacs_vision 原来的 GitHub 仓库（保持同一 full_name）。存量用户 HACS 内已添加的仓库地址不变，点「更新」即升级，迁移成本最低。
- **独立新仓库**：需在 HACS 移除旧仓库、添加新仓库，迁移步骤更多。

> 注意：无论哪种方式，升级后都需确认 HACS 面板里已无 hacs_vision 仓库记录，否则自动更新仍会报错。
