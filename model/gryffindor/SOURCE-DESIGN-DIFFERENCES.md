# Gryffindor Common Room: V2 reference-guided original study

Reference: Harry Potter: Magic Awakened, official global-site promotional interior image, versioned path `20230516102258/img/v2`. Inspected on 2026-11-17.

Page: https://www.harrypottermagicawakened.com/global/

Image: https://www.harrypottermagicawakened.com/pc/gw/20230516102258/img/v2/map3_378f7b8.jpg

The official picture is reference evidence, not a texture. No official mesh, game texture, portrait or character was extracted. All room geometry, fabric pattern, heraldry, paintings and texture brushwork in this folder are original procedural studies.

## V2 changes and observed review

The V2 hero view uses a lower camera, moved back to retain the complete carpet front edge and low timber roof in a 16:9 frame. The inferred reverse enclosure was extended to contain this camera. The chandelier ring is reduced from 1.72m to 1.42m radius; its apparent screen size is further reduced by the changed camera.

The two sofas have different lengths, offsets and rotations; the rear seating combines one taller wingback and one lower chair. Loose cushions have seams and embroidery, while tartan throws follow curved geometry over the sofa backs and end in frayed tassels. The right bookcase is replaced by a closed oak cupboard with carved pointed panels.

The hearth has layered acanthus relief, raised shield edging and a sculpted lion-like face. Chimney blocks have alternating lengths and small offsets. Five original portraits now contain facial shadow planes, distinct hair/robes and restrained brush marks. The forest tapestry has clustered leaves and original heraldic deer; fabric has woven damask rather than wood-like grain, and the carpet has foliate medallions.

Actual draft review: the first V2 render still cropped the carpet and made the foreground furniture too large. The revised draft moved the camera back and added a local warm seating light while reducing the excessive hearth pool. Both drafts were viewed before baking. The latest source draft and final source preview are ../../previews/blender-gryffindor-draft.png and ../../previews/blender-gryffindor.png; these are not browser screenshots.

Remaining differences: proportions and the hidden reverse area are inferred from one promotional image. Carving, upholstery folds, irregular age marks and prop density remain simpler than the official artwork. The original portraits, heraldry and tapestry intentionally differ from official assets. Static baking cannot create moving fire shadows; this is a refined original study, not an exact game reconstruction.

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
