# tdwx · 微信聊天记录归档导航

本仓库存放微信聊天记录归档（HTML）。根目录的 `index.html` 是导航页，自动列出所有归档页面，点击即打开对应内容；清单按日期分组，最新在前。

## 页面

- 线上：`https://lingying222.github.io/chat/`（需在仓库 Settings → Pages 选择 main 分支根目录）
- 本地：直接双击 `index.html` 打开即可

## 目录结构

```
tdwx/
├── index.html                  # 导航页（日期分组 + 清单轮询）
├── chats/                      # 聊天记录归档 HTML（被导航列出）
├── assets/
│   ├── images/                 # 归档中引用的图片（按内容 hash 命名入库）
│   ├── lib/                    # 本地离线渲染库：marked、DOMPurify、render-markdown.js
│   └── weixin/<通道名>/         # CowAgent 微信通道入站附件归档（按通道名+日期命名）
├── build_manifest.py           # 扫描 chats/ 生成清单 manifest.js / manifest.json
├── archive_builder.py          # 归档重建：图片入库、注入 Markdown 渲染
├── manifest.js / manifest.json # 清单（自动生成，勿手改）
├── 启动监听刷新.bat             # 双击开启目录监听，变化即重建清单
└── 一键上传GitHub.bat           # 双击提交并推送到 GitHub
```

## 清单怎么来的

导航页不写死条目，读取 `manifest.js`（由 `build_manifest.py` 扫描 `chats/` 生成，忽略 `assets/`）。

归档 HTML 有新增或变动后，任选一种方式刷新清单：

| 方式 | 操作 |
|---|---|
| 手动生成一次 | `python build_manifest.py` |
| 监听自动刷新 | 双击 `启动监听刷新.bat`，目录一变就更新 |
| 推送后自动更新 | 提交并 push，GitHub Actions 重建清单（`.github/workflows/manifest.yml`） |

生成后页面每 5 秒重新拉取一次清单，浏览器里自动出现新条目。

## 按日期分组展示

- 日期取文件名里的 `YYYY-MM-DD`；文件名取不到日期的归为「未知日期」；
- 日期分组从新到旧，最新一天带「最新」角标；组内按文件名排序。

## Markdown 渲染

归档页面内的纯文本气泡会用本地离线库渲染 Markdown（标题、加粗、列表、代码块、表格、链接等）：

- 库文件在 `assets/lib/`，不依赖外网；
- 已含图片/附件节点的气泡不整泡重渲染，避免附件被冲掉；
- 渲染结果经 DOMPurify 消毒。

## 附件归档说明

- **图片**：归档引用的图片复制入库到 `assets/images/`，线上可直接查看。
- **视频 / 压缩包等大文件**：不纳入 git，归档里只保留本机 `file://` 文本链接，仅在本机可打开。
- **CowAgent 通道附件**：微信通道入站图片/文件会持久化复制到 `assets/weixin/<通道名>/`，文件名格式 `通道名_YYYY-MM-DD_短hash.扩展名`（如 `小潘_2026-11-21_cb5409.jpg`），不使用陌生的实例 ID。归档目录在 CowAgent 通道配置（`team.json` 的 `archive_dir`）中指定。

## 注意

- `index.html` 本身不会被列入清单，避免自我引用。
- 导航只收录 `chats/` 下的 `.html` 文件；其他类型文件不显示在导航里。
- 静态托管无法"感知"文件变化，线上刷新依赖 Actions 重新生成清单；本地可用监听脚本实时刷新。
- 归档记录如需移除，手动删除 `chats/` 下对应 HTML 后重建清单即可；页面与静态托管不提供在线删除能力。
