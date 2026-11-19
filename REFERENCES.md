# 画面来源与创作边界

本项目为《哈利·波特：魔法觉醒》玩家纪念习作，非官方项目。三维空间为参考创作，不含原游戏提取模型。以下宣传图只作参考与对照，不作为模型表面贴图。原图保留原色，只在对比图中等比缩放。

## 本次六处室内场景

版本：国际官网 2023 路径中的室内场景宣传图；沿用前序任务于 2026-11-17 保存并核对的原图。页面：[游戏国际官网](https://www.harrypottermagicawakened.com/global/)。这是官方宣传画面，不能由单一视角推定完整游戏平面图。

| 场景 | 直接图片 | 可见特征及本次采用部分 |
|---|---|---|
| 魔药课教室 | [map6_a177a0c.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map6_a177a0c.jpg) | 压低的石砌拱顶、尖窗、两侧密集药瓶、坩埚、书与天平 |
| 占卜课教室 | [map8_f1502e7.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map8_f1502e7.jpg) | 酒红帷幔、暖色窄高窗、矮圆桌、水晶球与软垫 |
| 格兰芬多休息室 | [map3_378f7b8.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map3_378f7b8.jpg) | 大型吊灯、木屋顶、壁炉、红金织物、画像与中央茶几 |
| 斯莱特林休息室 | [map7_9cdc6ea.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map7_9cdc6ea.jpg) | 绿色窗光、尖拱、悬吊灯、壁炉、深色沙发及奖杯柜 |
| 拉文克劳休息室 | [map5_c040dd8.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map5_c040dd8.jpg) | 象牙色高柱、蓝金躺椅、圆形星图、天球仪与学院雕像 |
| 赫奇帕奇休息室 | [map4_304d69e.jpg](https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map4_304d69e.jpg) | 圆窗、黄绿色座椅、圆软凳、植物、暖木地板与门洞 |

看得见的主轮廓与色块用于设计；房间精确尺寸、遮挡部分、背面墙体、额外通行空间和细部纹样是原创补全。织物图案、书籍封面、人物肖像和雕像是简化原创造型，不主张与游戏原作细节相同。

各室的模型结构、灯光策略、可重跑方法与美术差距见 `model/<场景>/` 中的说明。`previews/blender-*.png` 是 Blender 渲染；`previews/<场景>.png` 是实际浏览器截图，二者分别标注。

## 前序已完成内容

- 烛光礼堂：完整参考沿用 `src/hall/REFERENCES.md`。
- 决斗场：完整参考沿用 `src/arena/REFERENCES.md`。
- 回忆录首页黑湖、廊桥、天文塔、宿舍等插画：沿用 `assets/sources.json`。首页插画入口与三维场景入口有明确区分。
- 运行技术：Three.js 0.180.0（MIT，许可随构建附带）；本地 Draco 解码资源随 Three.js 分发。构建工具 esbuild 0.25.11。模型由 Blender 5.3 制作。

官方图像与作品名称权利归各自权利人。此交付是本地学习与个人纪念用途的原创建模习作，不是完整游戏复刻。

## 本轮技术研究

GitHub 实际代码研究、固定提交、许可证判断和采用范围详见 `GITHUB_RESEARCH.md`。没有导入第三方游戏模型、房间或贴图。礼堂与决斗场也在本轮重新建模/烘焙；参考身份和隐藏区域的原创补全边界不变。
