# Hufflepuff — second art pass

Original modeled interpretation of the selected Harry Potter: Magic Awakened promotional room. The official map4 image and V1 browser capture were viewed before editing. The separate `hogwarts-complete` delivery remains unchanged.

- Official page: https://www.harrypottermagicawakened.com/global/
- Selected image: https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map4_304d69e.jpg
- Type: official promotional still with text overlay, inspected 2026-11-17; not a measured plan.
- Geometry, portraits and patterns are original. Screenshot textures and extracted game assets are not used.

## Visible changes

Thick rear masonry, round doors, windows and cupboards bend into a common enclosure. The long base wall is subdivided before bending. Secondary blind arches, deep jamb returns, staggered quoins and irregular relief bricks create an overlapping rounded vocabulary.

Sofas face inward at unequal angles and are reduced in scale to open the center around a smaller pouffe. Cloth uses desaturated ochre/olive, subdued woven leaf patterns, directional brush marks, wear strokes and tension wrinkles. A draped linen tea cloth and loose russet throw add folds. Plain bookcases have become carved arch-headed cupboards with recessed displays.

Broad curled leaves replace narrow angular strips. Several hundred extra leaves create uneven ivy growth; potted undergrowth varies in width and direction. A local soft bounce gives the foliage color while warm window light and the hearth retain their own hierarchy.

## Framing and limitations

The main render is 16:9 with a 21.5 mm horizontal-fit lens. Metadata stores the corresponding actual vertical field of view. Final source preview: `../../previews/blender-hufflepuff.png`; browser screenshots are separate evidence.

Side/reverse walls, exact scale and portrait/textile motifs are original completions. The reference has richer irregular wall silhouettes, more accumulated clutter and finer drawn contours. Foliage is broader and denser than V1 but remains procedural geometry rather than a hand-painted game asset. No numeric likeness score is claimed.

## Rebuild and checks

The editable blend retains named source objects, modifiers and packed images. The original bitmap sources are in `textures/`. Run Python/Pillow and Blender 5.3 in this directory:

```text
python make_textures.py
python refine_textures.py
blender --background --python build_rooms.py -- hufflepuff draft
blender --background --python build_rooms.py -- hufflepuff
blender --background --python export_rooms.py -- hufflepuff
blender --background --python verify_source.py -- hufflepuff
```

Both texture generators intentionally update the two light-room sibling texture folders. The V2 pass is in `art_refinement.py`. During the active collaborative task, Blender runs through `work/art-refinement/run_blender.py` to serialize GPU work.

Export opens a fresh source blend and preserves its editability. It applies source cloth thickness in the export copy, freezes Generated coordinates before joining, then bakes four 2048 JPEG atlases at 20 Cycles samples. Static atlases normalize to `KHR_materials_unlit`; window/flame emission remains separate. Draco requires the locally bundled decoder. `verification.json` records finite geometry, positive transforms, packed images, lens/metadata correspondence and sampled navigation reachability for a 0.3 m-radius avatar. The GLB container audit and this metadata sampling do not replace actual browser viewing and walking.
