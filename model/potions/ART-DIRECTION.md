# Potions classroom refinement

Reference: the saved official `references/map6_a177a0c.jpg`, inspected directly alongside the V1 browser capture. The official picture is promotional art; this is an original modeled interpretation, not extracted game geometry.

The V2 source replaces the conventional Gothic lancet with a tapering, two-leaf fan window: angled glazing, a hanging center mullion, sharp polygonal carved hood, and a solid wall spandrel cut to the real glazing outline. Transverse ribs now intersect diagonal stone ribs over each vault bay; broad ceiling panels replace the small repeated checkerboard segments. The front worktop crosses the composition, with the next worktops staggered in depth. A continuous passage remains behind it and between the central stations.

Shelving now mixes tall storage vessels, squat lidded crocks, handled jugs, pear-shaped flasks and irregular gaps. Foreground groups have different sizes and include a specimen rack, recipes, a mortar, books and a balance. The main light comes from the fan window, with restrained front bounce and one shelf candle. Shelf materials and architectural planes were edited directly; the change is not an exposure-only adjustment.

The authoring source retains separate objects, packed texture studies, lights and named cameras. `build_scene.py` regenerates `scene.blend` and metadata; `export_scene.py` bakes coordinate-stable color atlases and writes embedded Draco GLB with explicit unlit materials. Camera metadata gives vertical FOV for the saved 16:9 composition. Spawn and obstacle rectangles remain on the existing ground-plane navigation contract.

Remaining differences: official vessel silhouettes and painted edge strokes are more individually authored; the reference foreground is denser, the ceiling silhouette and decorative glyphs differ, and the unseen reverse side and walk route are original extrapolations. Baked lighting is static. Blender and browser captures are different renderers and must be labeled separately.

Browser integration camera correction: the source script, metadata and saved blend now place the main camera 0.24 m farther forward to stay inside the viewer bounds; the third camera target was lowered to remain inside the orbit polar limit. The retained Blender preview predates this small camera correction. Geometry and the lighting bake are unchanged; the final browser capture is the delivery comparison view.
