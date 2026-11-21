# 霍格沃茨周边 · 第一批地标

三处现有地标的位置可以沿用。先把远处能读出的轮廓和步行近看时的入口做清楚，再确定地图中的摆放尺寸。概念图右栏决定本批三处主体的轮廓，电影形态参考用于观察打人柳和棚屋，游戏宣传图用于核对冷青环境、深色材质和局部暖光。猫头鹰邮局照片提供拱洞与栖木细节，细塔和塔帽的比例来自概念图。[《魔法觉醒》黑湖宣传图](https://www.harrypottermagicawakened.com/pc/gw/20201020114844/img/bg_1159d29.jpg) · [网易禁林插画](https://nie.res.netease.com/r/pic/20221019/5dd216f5-8e05-420b-a8e5-e3fb5019efc9.jpg)

| 地标 | Blender 文件 | 渲染 | 模型尺寸 |
| --- | --- | --- | --- |
| 打人柳 | [willow.blend](willow.blend) | [主视角](willow.png) · [背面](willow-rear.png) | 根至枝尖约 11 m，冠幅约 13.5 m |
| 尖叫棚屋 | [shack.blend](shack.blend) | [主视角](shack.png) · [背面](shack-rear.png) | 含烟囱约 8.4 m 高 |
| 猫头鹰棚屋 | [owlery.blend](owlery.blend) | [主视角](owlery.png) · [背面](owlery-rear.png) | 含塔尖约 21.4 m 高 |

打人柳把弯曲的树干、贴地根和透空树冠作为主体，根下布置舱盖。棚屋采用交叉山墙、凹垂屋脊、错排石板瓦和钉板窗，保留东侧通道门。猫头鹰棚屋采用八面塔身、两层有进深的拱窗、外挑的檐下托木和独立石阶。背面、门窗位置及细部为原创补全。当前石阶和窗洞的比例适合核对外观，地图落点高度与碰撞需在装配时测量。

[查看正背面总览](review.jpg)

每个 Blender 文件都包含可追加的地标资产集合。暮色灯光、地形和机位放在审阅集合中。材质由 Blender 节点生成，文件可独立打开。用 Blender 5.3 核对了三份源文件、主视角和背面，检查了屋面接缝、墙洞进深、塔基入口及树根接地。当前渲染保留较清晰的石板纹和砖缝，概念图具有更平面的笔触。三个模型作为本地审阅样件交付。

从仓库根目录重建 Blender 文件及六张机位渲染。

```sh
blender -b --factory-startup --python-exit-code 1 -P world/model/landmark-studies/build.py
```

在命令后追加 `-- willow`、`-- shack` 或 `-- owlery` 可重建单件。
