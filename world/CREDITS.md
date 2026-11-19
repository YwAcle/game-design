# 霍格沃茨室外地图美术来源

- 城堡使用 Sebastian Holthausen 的《Hogwarts HD》，Icosa Gallery 标注 Creative Commons Attribution。此版在 Blender 中调整尺度和摆放，重做石墙及板岩屋面的材质与 UV，打包纹理，并对网页导出副本减面。原作者署名适用于城堡底模。[作品与许可](https://icosa.gallery/view/8tgxicKay0K)
- 温室使用 Michiel Swerts 的《Greenhouse landegem》，Icosa Gallery 标注 Creative Commons Attribution。本版调整比例、简化网格和玻璃颜色。[作品与许可](https://icosa.gallery/view/b-T7XOa2VUK)
- 霍格莫德村舍、站房、船屋、球场看台、小屋与谷桥使用 Kay Lousberg 的 KayKit Medieval Hexagon Pack 1.0，许可为 CC0。使用版本 84fa4e91，建筑在 Blender 中重新编排与调色。[原作与许可](https://github.com/KayKit-Game-Assets/KayKit-Medieval-Hexagon-Pack-1.0)
- 城堡石墙、屋瓦使用 Quaternius 的 Medieval Village MegaKit，许可为 CC0。颜色依照冷灰屋面、暖灰石墙调整，纹理嵌入源模型及 GLB。[作者页](https://quaternius.com/packs/medievalvillagemegakit.html) · [使用版本](https://github.com/J-Ponzo/gltf-medieval-village-megakit/tree/21104b4045261c28fc312360841ed1a7b0ac8782)
- 美术参考核对日期为 2026 年 11 月 18 日。官网黑湖渡船图展示近处船影、远处城堡和暖灯。廊桥图展示木柱重复节奏和深色边框。电影模型展示了礼堂、圆塔与不同高度尖顶的组合。地图自行设计了船屋至礼堂、谷桥至球场、东翼至禁林三段步行距离。[游戏黑湖宣传图](https://www.harrypottermagicawakened.com/pc/gw/20201020114844/img/bg_1159d29.jpg) · [游戏廊桥图](https://nie.res.netease.com/r/pic/20230719/c190fca5-8fbf-4ea2-a29a-b3c33bfb87d0.jpg) · [电影模型及制作说明](https://www.wbstudiotour.co.uk/explore-the-tour/art-department/)

- 湖面与天空采用 Poly Haven 的 Kloofendal 38d Partly Cloudy Pure Sky，许可为 CC0。云层重新定色，黑湖水面通过镜像相机反射天空和岸上物体。[天空原作](https://polyhaven.com/a/kloofendal_38d_partly_cloudy_puresky)
- 湖岸采用 Poly Haven 的 Coastal Cliff 02，草地与路径使用 Forest Floor 和 Rock Boulder Dry 的颜色纹理。树冠是 Fir Tree 01 在 Blender 中两个方向的透明渲染。靠近树干仍能辨认出交叉树片。各资产采用 CC0。[岩岸](https://polyhaven.com/a/coastal_cliff_02) · [林地](https://polyhaven.com/a/forest_floor) · [路面](https://polyhaven.com/a/rock_boulder_dry) · [冷杉](https://polyhaven.com/a/fir_tree_01)
- 船屋、码头栏杆、石阶、门廊、木桥屋面和站台使用 Quaternius 的 Medieval Village MegaKit 建筑部件。球场使用 KayKit 四色学院旗。门边的火把使用 Kay Lousberg 的 Dungeon Remastered 1.0，调整了尺寸及发光材质，许可为 CC0。[火把原作](https://github.com/KayKit-Game-Assets/KayKit-Dungeon-Remastered-1.0)

### 固定机位与设计取舍

栈桥取游戏官网的冷色月夜、船与城堡剪影为参考。上山转角使用电影微缩模型考察临崖建筑和礼堂屋面之间的遮挡。礼堂入口参考游戏室内的石材与暖灯，外门造型、路长、灯位和钟庭连接关系是本版的游览设计。在总图中，A、B、C 对应栈桥、转角、礼堂门前，具体机位保存在 `layout.json` 与源 Blender 场景。对照图保留来源与实景各自的画幅和曝光。

### 黑湖泊位

木划艇采用 Google 的《Rowboat》，铁灯采用 Michael Pretz 的《lantern》，两件作品均由 Icosa Gallery 标注 CC Attribution。在 Blender 中调整了尺度与泊位，并将灯具改为安装在木柱上的油灯。[划艇原作](https://icosa.gallery/view/dt1yhb5AYXD) · [铁灯原作](https://icosa.gallery/view/08BJnpQZs-4)

码头木板颜色与法线、河床石砾、岸石以及岸草来自 Poly Haven，使用 CC0 许可。素材在 Blender 和网页中按月夜光照重新布置。月面使用 NASA Scientific Visualization Studio 的 2024 月相序列第 528 帧，缩放裁切后用于天空和倒影。[木板](https://polyhaven.com/a/wood_planks_grey) · [河床](https://polyhaven.com/a/river_small_rocks) · [岸石](https://polyhaven.com/a/rock_boulder_dry) · [岸草](https://polyhaven.com/a/grass_medium_02) · [NASA 月相序列](https://svs.gsfc.nasa.gov/5187/)

Three.js r180 的 Reflector 生成岸景倒影。波纹贴图由本项目的方向性波谱生成，三层法线随风错速移动。近岸使用导航地形深度和河床贴图近似透视水底，浅浅的碎浪跟随水线。[Three.js Reflector 源码](https://github.com/mrdoob/three.js/blob/r180/examples/jsm/objects/Reflector.js)

### 山谷廊桥与黑湖画风对照

廊桥采用网易发布的霍格沃茨廊桥插画作为参考。原图里有重复的尖拱、四叶装饰、暗色屋架，以及斜穿木板路的夕光。本版在 Blender 中重新组合 Quaternius 的屋顶、木栏、承托和地板部件，并将项目自有礼堂的尖拱及四叶花饰改为木雕窗格。桥板纹理调整自 Poly Haven 木板。西谷的球场位置、22 米桥长和行走时渐入的暮色是本版设计。[网易廊桥原图](https://nie.res.netease.com/r/pic/20230719/c190fca5-8fbf-4ea2-a29a-b3c33bfb87d0.jpg) · [Quaternius](https://quaternius.com/packs/medievalvillagemegakit.html) · [木板纹理](https://polyhaven.com/a/wood_planks_grey)

黑湖采用官网渡船宣传插画对照色彩、光照和主次。本版压低暗水与岸边环境光，在小船上放置一盏油灯，保留泊位和导航需要的栈桥。官方图中满载人物的船队、被雾遮住的城堡、宽阔而有棱角的浪面与本版仍有差异。官方插画和网页机位不同。[黑湖官方参考](https://www.harrypottermagicawakened.com/pc/gw/20201020114844/img/bg_1159d29.jpg)

### 西谷魁地奇球场

观察《击球、游走、起飞，魁地奇》官方宣传片约 00:05.7 和 00:21.5 的塔楼比例、格纹面料、草地划线和屋顶投影。球场采用原创的塔楼间距、入口、木座席和布料花纹。Blender 围绕现有西谷地形重新组合 Quaternius 的木栏、屋顶、木板、立柱和砖墙，并使用 KayKit 的院旗。三枚球门提取自 Thomas DR 的《quidditch game parts》，Icosa Gallery 标注 CC Attribution。已重做球门的木杆与铜环材质。对照图的官方帧只用于美术说明。[官方赛季宣传片](https://nie.v.netease.com/nie/2023/1010/cdab6a2770ecb48f0683b18a058bc1b6qt.mp4) · [球门授权原作](https://icosa.gallery/view/fqJ4MXwpKrV)

### 全地图初版 · 东线、北线和钟庭

- **总体关系。** 城堡、崖岸和礼堂的高低轮廓延续电影微缩模型的启发。城堡外的区域尺度、路径、树线、月台和站屋相互位置经重新安排。游戏画面的轮廓、明暗和局部暖灯用于美术方向。[电影模型及制作说明](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/art-department/) · [游戏官网](https://www.harrypottermagicawakened.com/cn/)
- **草药温室。** 官方赛季片约 00:34 的温室段落提供暖色侧光和植物色块，片场照片提供玻璃与栽培台的关系。在 Blender 内编辑既有 Landegem 玻璃温室的架体和玻璃，整理出面向步道的种植区。花槽与叶丛采用 Quaternius 构件。[官方赛季片](https://nie.v.netease.com/nie/2023/1010/cdab6a2770ecb48f0683b18a058bc1b6qt.mp4) · [片场温室](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/professor-sprouts-greenhouse-2/) · [温室底模](https://icosa.gallery/view/b-T7XOa2VUK)
- **海格小屋与禁林。** 石面、木框和暖灯参考片场。林缘参考游戏官网禁林插画的近景树干与暖光，片场林门用于对照铁栅尺度。近路树干使用 Poly Haven 冷杉模型减面，背后的枝冠沿用 Blender 渲染的剪影贴片。人物和原画的戏剧性光效不在实景对照中。[小屋片场照片](https://www.wbstudiotour.co.uk/wp-content/uploads/2026/01/Hagrids-Hut.webp) · [游戏官网禁林图](https://nie.res.netease.com/r/pic/20221019/5dd216f5-8e05-420b-a8e5-e3fb5019efc9.jpg) · [片场禁林](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/the-forbidden-forest/) · [冷杉模型](https://polyhaven.com/a/fir_tree_01)
- **霍格莫德与车站。** 村街、屋脊、集市和月台采用原有 KayKit、Quaternius 构件重组。静态蒸汽机车使用 Gianni Polito 的《Steam Locomotive》，许可 CC Attribution，在 Blender 中改为绛红锅炉、深色底架。站屋与铁轨的布局按户外游览设计。[机车原作](https://icosa.gallery/view/5aE2a34t012) · [电影机车与月台](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/platform-9-%c2%be/)

### 入校与校园细化

- 禁林继续参考网易的禁林宣传插画。背景保留冷色树冠和少量暖点，前景用原创粗树干、偏斜枝杈和互相遮挡的树冠形成纵深。电影片场的粗树干提供尺度参考。版本采用原有网易图档。两次浏览器实景使用同一机位，官方插画的构图和照明另有差异。[禁林原图](https://nie.res.netease.com/r/pic/20221019/5dd216f5-8e05-420b-a8e5-e3fb5019efc9.jpg) · [电影片场](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/the-forbidden-forest/)
- 蜂蜜公爵使用现有霍格莫德村舍，增设原创绿漆凸窗、莓红珐琅嵌板、糖果和招牌。四处学院门道具与反馈台词为原创。叩桶、问答、画像守门和地下隐门取自学院入口描述。礼堂入校引导沿用原有《魔法觉醒》室内美术，电影分院段落用于选择观看方向和路线终点。[官方霍格莫德设定](https://www.harrypotter.com/fact-file/locations/hogsmeade) · [学院入口设定](https://www.harrypotter.com/writing-by-jk-rowling/hufflepuff-common-room) · [电影礼堂](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/the-great-hall/)
- 各区域共享带月光的暮色天空，廊桥和村街保留暖色局部照明。可编辑道具在 `model/Hogwarts_Grounds.blend` 的 `Campus · painted landmarks` 集合内。使用 `blender -b world/model/Hogwarts_Grounds.blend --python-exit-code 1 -P world/model/refine_campus.py` 重做该集合，再运行现有模型导出和贴图打包脚本。

### 校园漫游地图

- 沿用本项目已保存的《魔法觉醒》温室赛季画面和禁林宣传插画。温室内廊的玻璃骨架、栽培台与暖灯参考温室画面，植物造型、开放通道和位置为原创。禁林内环加了岩块、倒木和暖灯。南瓜地、露台与车站站名牌使用同一套模块色面，平面布局服务于连续步行。[游戏赛季画面](https://nie.v.netease.com/nie/2023/1010/cdab6a2770ecb48f0683b18a058bc1b6qt.mp4) · [禁林插画](https://nie.res.netease.com/r/pic/20221019/5dd216f5-8e05-420b-a8e5-e3fb5019efc9.jpg) · [片场温室](https://www.wbstudiotour.co.uk/the-experience/explore-the-tour/sets/professor-sprouts-greenhouse-2/)
- 温室内廊、南瓜垄、观星望远镜、林深空地和月台陈设均可在同一个 Blender 源文件里编辑。细化脚本会更新导航障碍数据。网页路线和总图使用同一份 `layout.json`。
