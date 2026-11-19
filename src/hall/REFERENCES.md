# 礼堂参考与实现取舍

查阅日期：2026-11-17。

- [《魔法觉醒》官方礼堂画面](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map2_5059475.jpg)：主要造型和色彩依据。灰褐石墙、深木结构、瘦长尖拱、雕刻火盆、灰蓝高窗与克制金色烛光。参考图片未作为网页贴图使用。
- [官方场景介绍](https://www.harrypottermagicawakened.com/global/)及[礼堂游戏截图检索](https://www.google.com/search?q=哈利波特+魔法觉醒+礼堂+游戏+场景&udm=2)：核对游戏中的氛围和宴席陈设；检索结果混有电影和其它游戏，不全部作为结构依据。
- [ab192130/threejs-bakemap-trials](https://github.com/ab192130/threejs-bakemap-trials)，实际阅读 [src/index.js](https://github.com/ab192130/threejs-bakemap-trials/blob/master/src/index.js)：参考 GLB + 烘焙纹理 + MeshBasicMaterial 的室内呈现流程。未复制该项目模型或图片，也未沿用旧版 encoding API。
- [Three.js 官方 bloom 示例](https://github.com/mrdoob/three.js/blob/dev/examples/webgl_postprocessing_unreal_bloom.html)：参考 EffectComposer → RenderPass → UnrealBloomPass → OutputPass 的流程；本项目仅让高亮火焰和窗光产生柔光。

本场景在已有原创 Blender 结构上细化，是游戏画风的同人解释，非游戏资产提取、非官方复刻。保留四列长桌、中轴通道、教师席和高窗；当前可探索范围限礼堂，未接入完整城堡。网页使用本地资源，静态间接光照烘焙，火焰与尘埃实时渲染。
