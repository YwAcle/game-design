# Slytherin Common Room: V2 reference-guided original study

Reference: Harry Potter: Magic Awakened, official global-site promotional interior image, versioned path `20230516102258/img/v2`. Inspected on 2026-11-17.

Page: https://www.harrypottermagicawakened.com/global/

Image: https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map7_9cdc6ea.jpg

The official picture is reference evidence, not a texture. No official mesh, game texture, portrait or character was extracted. All room geometry, fabric pattern, heraldry, paintings and texture brushwork in this folder are original procedural studies.

## V2 changes and observed review

V2 replaces the thin roof bars with thick segmented transverse stone arches and projecting carved lips. The back wall is assembled around real pointed openings, with substantial piers, deep embrasures, recessed panes, layered capitals and individually shaped wedge stones at every window head. The chimney uses staggered block lengths; the hearth gains a tall cornice, stepped corbels, leaf relief, a serpent shield and a small upper memorial tablet.

The tall trophy cabinet has closed carved doors, an open display niche, varied trophy sizes and three different original embossed shields. The sofas have unequal lengths, back heights and rotations; cushions and stitching are varied. Window green light, a dark upper vault, a local cool reflection on the cabinet and warmer hearth light establish local contrast instead of uniformly tinting the room.

Actual draft review: the first V2 render still exposed too much flat upper ceiling. The second draft moved the camera back, restored a moderate downward angle, added deep wedge-shaped arch blocks and a local cabinet reflection. A final camera-only draft lowered the target to the hearth and revealed the full oval carpet and foreground flagstones. All three drafts were viewed before baking. The latest source draft and final source preview are ../../previews/blender-slytherin-draft.png and ../../previews/blender-slytherin.png; these are not browser screenshots.

Remaining differences: the full layout and hidden reverse wall are inferred from one promotional image. The masonry is still more regular, and carved serpents, upholstery creasing, window vines and aged surfaces are less detailed than the reference. Shields are original decorative designs. Static baking does not provide moving fire shadows; this is a refined original study, not an exact game reconstruction.

Technical analogy: itsLucas02/3d-room, commit aca0dc0348716cc6755a3f9e98d8954fc07b65d9, Baked.js / fragment.glsl, separates static baked base lighting from local illumination. The MeshBasic baked-lighting example in ab192130/threejs-bakemap-trials supports the same separation. This project applies that organization independently; no third-party model, texture or source code was copied.

The camera metadata now records each lens's vertical field of view, derived from Blender's 36mm sensor at 16:9, and retains the hero field of view at the top level for compatibility. New furniture footprints update the collision rectangles; the extended inferred reverse enclosure updates the walk boundary. Slytherin's back walk boundary stops in front of the thick window masonry.

## Files and reproducibility

- `build_room.py`: builds the full editable scene and writes the actual Blender preview and initial metadata. It runs relative to this folder with Blender 5.3.
- `geometry.py`: local original geometry helpers from the earlier project pipeline.
- `make_textures.py`: reruns only this room's original texture studies when invoked from this folder; requires Python, Pillow and NumPy.
- `export_room.py`: opens the editable blend, makes export copies, preserves each object's generated coordinates in a `PaintCoord` attribute, joins geometry into groups, lays out separate bake UVs, bakes 18-sample combined illumination and exports self-contained GLB.
- `<room>.blend`: editable room, lights, cameras and named mesh pieces.
- `textures/`: editable original surface/portrait/rug studies plus baked JPEG atlases. These author files are not fetched by the offline viewer.
- `audit.json`: read-only GLB container and offline reference audit.

Exported runtime materials are four explicit `KHR_materials_unlit` baked-color atlases plus separate emissive glass/flame/lamps. Lights are baked and intentionally omitted from GLB. Geometry is uncompressed, so no remote or local Draco decoder is required. The exporter converts Blender Z-up into glTF Y-up, and metadata uses exactly the same Y-up convention: `(x, y, z) -> (x, z, -y)`.

All source texture coordinates are stabilized before join. Exported atlas textures remain sRGB. The source camera uses AgX while the web viewer uses ACES; the web result must be visually checked separately, and a Blender preview is not a browser screenshot. Back-wall layout, exact dimensions and all hidden surfaces are original extrapolations. No moving shadows or physical fabric simulation are included.
