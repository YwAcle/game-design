# 模型与重建

所有 `.blend` 为可编辑的原创场景。原始纹理已打包到最终 `.blend` 或保存在各场景旁的 `textures/`。每个目录内的说明记录参考、补全和实际修正。

## 六处新室内场景

分别查看 `potions/REFINEMENT.md`、`divination/REFINEMENT.md`、`gryffindor/SOURCE-DESIGN-DIFFERENCES.md`、`slytherin/SOURCE-DESIGN-DIFFERENCES.md`、`ravenclaw/REFERENCE_AND_BUILD.md`、`hufflepuff/REFERENCE_AND_BUILD.md`。先渲染核对，再按各目录的导出脚本生成 `scene-assets/<id>/scene.glb`，最后执行网页构建。静态光照已烘焙，浏览器不向这些表面重复打光。

## 礼堂与决斗场

这两处均在前序独立交付基础上重新修订并烘焙。导出脚本调用同层 `bake_coordinates.py` 保持合并前的源纹理坐标，再通过 `normalize_baked_glb.py` 仅把明确命名的烘焙材质规范为 unlit；灯火与透明材质保留独立语义。

- 礼堂：本轮编辑 `hall/Great_Hall_ArtRefined.blend`。`Great_Hall_Refined.blend` 是第二阶段基础。`hall/Foundation.blend` 是首次制作时的完整建筑基础，供 `refine_hall.py` 重建使用。执行 Blender 后台 `--python model/hall/refine_hall.py`，再执行 `--python model/hall/revise_hall.py`，最后 `--python model/hall/export_hall.py`；`verify_hall.py` 检查三条中轴步行线与法线。
- 决斗场：编辑 `arena/Dueling_Club.blend`。重建用 `--python model/arena/build_arena.py`，导出用 `--python model/arena/export_arena.py`；先用 Python/Pillow 运行 `make_textures.py` 与 `paint_stone_variants.py` 生成本轮石材色块，再执行建模脚本。
- 旧场景导出到 `scene-assets/hall`、`scene-assets/arena`，保持原有文件名。它们使用本地 Draco，解码器随网页构建附带。

脚本使用 Blender 5.3 的 Cycles 与 CUDA。机器不支持 CUDA 时需在脚本中按实际 GPU 后端或 CPU 配置调整；已交付的网页不依赖 Blender。每次重新导出后都需检查真实浏览器，不能将 Blender 渲染当作网页验收。

礼堂和决斗场的最初来源与限制分别见 `../src/hall/REFERENCES.md`、`../src/arena/REFERENCES.md`。新场景来源见项目根目录 `REFERENCES.md`。
