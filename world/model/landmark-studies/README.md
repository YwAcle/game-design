# 霍格沃茨周边 · 第一批地标

三处现有地标的位置可以沿用。先把远处能读出的轮廓和步行近看时的入口做清楚，再确定地图中的摆放尺寸。概念图右栏决定本批三处主体的轮廓，电影形态参考用于观察打人柳和棚屋，游戏宣传图用于核对冷青环境、深色材质和局部暖光。猫头鹰邮局照片提供拱洞与栖木细节，细塔和塔帽的比例来自概念图。[《魔法觉醒》黑湖宣传图](https://www.harrypottermagicawakened.com/pc/gw/20201020114844/img/bg_1159d29.jpg) · [网易禁林插画](https://nie.res.netease.com/r/pic/20221019/5dd216f5-8e05-420b-a8e5-e3fb5019efc9.jpg)

| 地标 | Blender 文件 | 渲染 | 模型尺寸 |
| --- | --- | --- | --- |
| 打人柳 | [willow.blend](willow.blend) | [45° 场景](willow.png) · [正面](willow-front.png) · [侧面](willow-side.png) · [背面](willow-rear.png) | 根至枝尖约 11 m，冠幅约 17 m |
| 尖叫棚屋 | [shack.blend](shack.blend) | [45° 场景](shack.png) · [正面](shack-front.png) · [侧面](shack-side.png) · [背面](shack-rear.png) | 含烟囱约 8.4 m 高 |
| 猫头鹰棚屋 | [owlery.blend](owlery.blend) | [45° 场景](owlery.png) · [正面](owlery-front.png) · [侧面](owlery-side.png) · [背面](owlery-rear.png) · [阁楼](owlery-loft.png) | 含塔尖约 21.4 m 高 |

根据用户补充的三视图和材质近景，把打人柳主干半径增加 30%，冠幅从约 13.5 m 扩大到约 17 m。粗横枝压低树冠两侧，断枝露出年轮，根系伸入带苔石、枯枝、草簇和层叠冷杉的地形。尖叫棚屋的墙、门框和屋顶共用同一倾斜变形，配合缺瓦露出的木条、钉板窗、风化墙脚、门铰铁件和藤蔓。猫头鹰棚屋的上层设有八个贯通的尖拱和外挑的落脚石，下层有可见的木楼板。用横梁、鸟巢、羽毛和静态猫头鹰表现栖息空间。

[查看四视角总览](review.jpg)

每个 Blender 文件都包含可追加的地标资产集合。暮色灯光、地形和机位放在审阅集合中。材质由 Blender 节点生成，文件可独立打开。用 Blender 5.3 重开了三份源文件，核对屋面接缝、拱洞进深、塔基入口及树根接地，并检查了三个正交方向、场景透视和阁楼近景。地形与背景使用简化高地，光照和材质服务于样件审阅。地图内的摆放高度与碰撞留到装配时测量。第一轮源文件与渲染保存在提交 `aaf40c6`。

从仓库根目录重建 Blender 文件及十三张机位渲染。

```sh
blender -b --factory-startup --python-exit-code 1 -P world/model/landmark-studies/build.py
```

在命令后追加 `-- willow`、`-- shack` 或 `-- owlery` 可重建单件。
