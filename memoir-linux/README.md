# 魔法留声 · Hogwarts, Always

献给《哈利波特：魔法觉醒》玩家的非官方互动回忆录。目前仅提供回忆录，三维地图原型及旧探索版文件已删除。

## 打开方式

Mac 和 Windows 均可完整解压 `魔法留声-回忆录-Windows-Mac.zip`，双击其中的 `index.html`。也可直接打开本目录的 `index.html`。无需安装依赖、联网或启动服务器，建议使用新版 Chrome、Edge 或 Safari。页面使用 WebGL 绘制可选光点；浏览器不支持时，回忆录仍可阅读。

## 回忆录

- 切换四幅场景插画，浏览廊桥、天文塔和宿舍等熟悉的地方。
- 选择学院，写下回忆，阅读、珍藏并筛选自己的故事。
- 导出 JSON 文字备份和 PNG 纪念卡；目前没有 JSON 导入。
- 主动开启后播放原创 Web Audio 钟琴氛围，不使用游戏原声。
- 支持桌面和手机布局、键盘操作及减少动态效果偏好。

故事和学院选择只保存在当前浏览器，使用 localStorage 键 `hogwarts-always-v1`。清除网站数据、换浏览器或改变打开方式可能无法读到旧记录，请定期导出备份。已有数据无法解析时，网页不会自动覆盖它。初始三篇故事标为「回忆灵感」，并非玩家投稿。

网页参考游戏官方展示的复古手绘插画、细金边和纸张质感。场景素材来源记录在 `assets/sources.json`；这是玩家自发的非官方纪念项目。

## 验证

在 Linux Chromium 上使用 Playwright 检查回忆保存、筛选、备份、纪念卡导出、手机布局及无网络打开。尚未在 Mac、Windows 或 Safari 真机验证。

```sh
NODE_PATH=/path/to/node_modules node tests/smoke.cjs
```

Playwright 仅用于开发测试，不是打开网页的依赖。
