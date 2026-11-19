# Ravenclaw common room

## Current release

The library niche contains the user-supplied Meshy Ravenclaw statue, including its crescent staff and pedestal. The Blender source stores the reduced mesh (77,999 triangles) and packed textures. The web export preserves its UVs and uses the supplied 2048 px color texture with a cool tint matched to the room. The room exporter still bakes the four surrounding room atlases.

To export this release from the supplied editable `ravenclaw.blend`, run the following from this directory with Blender 5.3.

```sh
blender --background --python-exit-code 1 --python export_rooms.py -- ravenclaw
blender --background --python-exit-code 1 --python verify_source.py -- ravenclaw
```

The build scripts below reconstruct the historical second art pass.

## Second art pass

Original modeled interpretation of the selected Harry Potter: Magic Awakened official promotional room. The official map5 image and V1 browser capture were viewed before editing. The separate `hogwarts-complete` delivery remains unchanged.

- Official page: https://www.harrypottermagicawakened.com/global/
- Selected image: https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map5_c040dd8.jpg
- Type: official promotional still with text overlay, inspected 2026-11-17. It is not measured architectural documentation.
- Reference pixels, extracted meshes and third-party models are not used as production materials.

### Visible changes

The new statue has modeled chin, jaw, cheek, brow, nose, eyelids and mouth, articulated bent arms, palms/fingers, substantial carved hair and a diadem. Its asymmetrical full robe has a weighted hem, long folds, a diagonal shoulder sash and broad solid trailing sleeves. A three-layer wood/brass archivolt and leaf relief surround the recessed library niche. The eagle has broad wing masses and separated feathers.

The rear facade and attached furnishings curve into the room. Long wall sections are subdivided before bending. Columns have collars and carved leaves; starry cloth swags soften the upper edge. The former simple bookcase is a recessed twin-door cupboard with arch moldings, a medallion and cornice scrolls. A high-backed reading chair and loose throw interrupt the paired furniture. Armillary rings now rotate about their own center.

Ivory is cooler and darker, blue is less saturated, and stone/textiles have authored broad brush patches and worn linework. Window/candle light is localized with restrained fill. This is a geometry, material and lighting correction, not an exposure-only adjustment.

### Framing and limitations

The main render uses 16:9 and a 21.5 mm horizontal-fit lens. Metadata stores the vertical field of view calculated from the actual camera. Final source preview: `../../previews/blender-ravenclaw.png`. Browser captures are separate integration evidence.

The sculpture still has simpler anatomy, hair transitions and fine drapery than the reference. Side/reverse walls, exact scale, portraits, textile motifs and carvings are original completions. The reference's finer hand-painted contours and accumulated aging remain more elaborate. No numeric likeness score is claimed.

### Rebuild and checks

The editable blend retains named source objects, modifiers and packed images. The original bitmap sources are in `textures/`. Run Python/Pillow and Blender 5.3 in this directory:

```text
python make_textures.py
python refine_textures.py
blender --background --python build_rooms.py -- ravenclaw draft
blender --background --python build_rooms.py -- ravenclaw
blender --background --python export_rooms.py -- ravenclaw
blender --background --python verify_source.py -- ravenclaw
```

Both texture generators intentionally update the two light-room sibling texture folders. The V2 pass is in `art_refinement.py`. During the active collaborative task, Blender runs through `work/art-refinement/run_blender.py` to serialize GPU work.

Export opens a fresh source blend and preserves its editability. It applies source cloth thickness in the export copy, freezes Generated coordinates before joining, then bakes four 2048 JPEG atlases at 20 Cycles samples. Static atlases normalize to `KHR_materials_unlit`; window/flame emission remains separate. Draco requires the locally bundled decoder. `verification.json` records finite geometry, positive transforms, packed images, lens/metadata correspondence and sampled navigation reachability for a 0.3 m-radius avatar. The GLB container audit and this metadata sampling do not replace actual browser viewing and walking.
