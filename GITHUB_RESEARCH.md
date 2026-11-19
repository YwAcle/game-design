# 本次 GitHub 技术参考

查阅日期：2026-11-17。通过 GitHub 搜索发现类似房间工程，再只读取得源代码并检查实际实现；未运行第三方安装脚本，未引入他人的房间、纹理或人物资产。下面记录的是已读代码，不以仓库名称代替证据。

## 1. 烘焙场景直接显示

[ab192130/threejs-bakemap-trials](https://github.com/ab192130/threejs-bakemap-trials)，已读提交 `9bab262b8fc2a1e9ae317dc19a94d8822fe62cb3` 的 [src/index.js](https://github.com/ab192130/threejs-bakemap-trials/blob/9bab262b8fc2a1e9ae317dc19a94d8822fe62cb3/src/index.js) 与 README。

实际做法：分别载入建筑/地面 GLB，为含光照颜色图设置 sRGB，并使用 MeshBasicMaterial；配本地 Draco 与 OrbitControls。它说明静态室内的光照可以在作者端完成，浏览器负责忠实呈现。

本次落实：六间教室/休息室继续用静态烘焙 unlit。礼堂与决斗场也把明确命名的烘焙组规范为 `KHR_materials_unlit`，保留独立灯火材质，移除礼堂对所有 emissive 材质统一抬到 2.5 倍的处理。GLB 规范化只处理 `Baked | ...` 材质，避免误伤真正的火焰、窗光和透明体。

未采用：旧版 Three.js 的 `outputEncoding`/`texture.encoding` API、仓库的模型和贴图。项目使用锁定的 Three.js 0.180.0 及当前颜色空间接口。其 README 声称 MIT，但该检出树中没有对应 LICENSE 文件；本次只参考做法，没有复制代码或资产。

## 2. 静态底图与局部灯光分离

[itsLucas02/3d-room](https://github.com/itsLucas02/3d-room)，已读提交 `aca0dc0348716cc6755a3f9e98d8954fc07b65d9` 的：

- [src/Experience/Baked.js](https://github.com/itsLucas02/3d-room/blob/aca0dc0348716cc6755a3f9e98d8954fc07b65d9/src/Experience/Baked.js)
- [烘焙 fragment shader](https://github.com/itsLucas02/3d-room/blob/aca0dc0348716cc6755a3f9e98d8954fc07b65d9/src/Experience/shaders/baked/fragment.glsl)
- [Renderer.js](https://github.com/itsLucas02/3d-room/blob/aca0dc0348716cc6755a3f9e98d8954fc07b65d9/src/Experience/Renderer.js) 与 [LICENSE](https://github.com/itsLucas02/3d-room/blob/aca0dc0348716cc6755a3f9e98d8954fc07b65d9/LICENSE)

实际做法：日/夜/中性烘焙图混合，RGB lightMap 三通道分别控制屏幕、桌灯和 PC 的局部色光。MIT 文件在检出树中可读。

本次落实：采用“固定间接光与局部发光分开”的组织方式，在 Blender 中重设窗、壁炉、蜡烛的局部光池，保留运行时单独的微光组；限制宽泛环境填充，避免整个房间一起变亮。占卜水晶使用独立透明材质组，未混入不透明烘焙家具。

未采用：日夜切换、RGB 灯光蒙版 shader 和外部资产。当前任务需要固定参考氛围，没有为使用参考技术而加入无关功能。

## 美术判断

这些方案能解决烘焙呈现、局部光和运行开销，不能自动生成《魔法觉醒》的建筑比例、雕像或手绘材质。本轮仍以官方参考的实际可见结构为准，原创修改窗洞/石拱、平台、弧墙、雕像、家具与纹理，并分别检查 Blender 草稿和最终网页截图。

## 黑湖水面 · 2026 年 11 月 19 日

- Three.js r180 的 Reflector 用镜像相机、斜裁切面和纹理矩阵渲染水上物体。本项目直接使用该组件，固定镜头复用倒影，转身或移动时更新。反射缓冲为 768 × 512，水面的波纹单独逐帧绘制。[源码](https://github.com/mrdoob/three.js/blob/r180/examples/jsm/objects/Reflector.js)
- Water2 展示了反射、折射与多方向法线的组合。黑湖沿用了多层水纹和随视角变化的反射权重，水深取自现有地形网格。[源码](https://github.com/mrdoob/three.js/blob/r180/examples/jsm/objects/Water2.js)
- Evan Wallace 的 WebGL Water 展示了入射角如何影响折射和反射。jbouny 的月夜海面演示用波谱产生水面法线和位移。黑湖选了适合缓风的短浪，离线生成可无缝重复的法线贴图。[WebGL Water](https://github.com/evanw/webgl-water/blob/master/renderer.js) · [FFT Ocean](https://github.com/jbouny/fft-ocean)
