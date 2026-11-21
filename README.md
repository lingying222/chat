# tdwx · 目录导航

本仓库存放微信聊天记录归档（HTML），根目录的 `index.html` 是导航页，会自动列出所有页面与子文件夹，点击即打开对应内容。

## 页面

- 线上：`https://yml-222.github.io/chat/`（需在仓库 Settings → Pages 选择 main 分支根目录）
- 本地：直接双击 `index.html` 打开即可

## 目录清单怎么来的

导航页不写死条目，而是读取 `manifest.js`（由 `build_manifest.py` 扫描目录生成）。

新增、删除 HTML 后，任选一种方式刷新清单：

| 方式 | 操作 |
|---|---|
| 手动生成一次 | `python build_manifest.py` |
| 监听自动刷新 | 双击 `启动监听刷新.bat`，目录一变就更新 |
| 推送后自动更新 | 提交并 push，GitHub Actions 会重建清单（`.github/workflows/manifest.yml`） |

生成后页面每 5 秒重新拉取一次清单，浏览器里会自动出现新条目（可在右上角关闭自动刷新）。

## 目录结构

```
tdwx/
├── index.html            # 导航页
├── build_manifest.py     # 扫描目录生成清单
├── manifest.js           # 供页面加载的清单（自动生成，勿手改）
├── manifest.json         # 同内容 JSON 版（自动生成）
├── 启动监听刷新.bat        # 双击开启目录监听
└── *.html                # 聊天记录等页面
```

## 注意

- `index.html` 本身不会被列入清单，避免自我引用。
- 只收录 `.html` 文件；其他类型文件不显示在导航里。
- 静态托管无法"感知"文件变化，线上刷新依赖 Actions 重新生成清单；本地则可用监听脚本实时刷新。
