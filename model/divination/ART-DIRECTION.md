# Divination classroom refinement

Reference: the saved official `references/map8_f1502e7.jpg`, inspected directly alongside the V1 browser capture. This source models an original interpretation of the selected promotional composition.

V2 restores raised teaching platforms along both sides, visible plank nosings and stepped heights of 0.24 and 0.34 m. Furniture and carpets actually sit on those surfaces. The low center aisle remains continuous into the rear teaching area. Existing obstacle rectangles block the platforms, so the viewer does not need to invent a walking height or let the camera clip through risers.

Ceiling cloth and the front valance have a bowed, gravity-like belly and slightly higher outer attachment, with restrained folds, sewn borders and small tassels. Their wine-colored, matte material replaces the previous bright regular satin stripes. The teacher chair is reduced relative to the composition, the former simple triangular frame becomes a thick pointed stone archivolt, and the two rear cupboards differ in proportion. Tables, stool counts, offsets and rug rotations vary across the room.

Crystal globes use independent translucent shells, irregular interior mist volumes and curved glints. They remain separate from the static lighting bake. The exported materials are unlit with alpha blending: this is an artistic cloudy-glass approximation, not physically accurate refraction or a dynamic reflection system. The remaining room uses coordinate-stable baked atlases, with window/candle emission isolated.

`build_scene.py` regenerates the editable packed `scene.blend` and metadata; `export_scene.py` creates the self-contained Draco GLB. Named cameras use vertical FOV corresponding to 16:9. The source pole construction avoids coincident sphere/lathe pole rings and normalizes face winding before saving.

Remaining differences: the official cloth has richer asymmetric embroidery, stronger floor sunlight and more individually modeled furniture; the owl relief is simplified, and the tower depth and unseen reverse side are original additions. Actual browser captures must be compared independently of the Blender drafts.

Browser integration camera correction: the source script, metadata and saved blend now place the main camera 0.30 m farther forward to stay inside the viewer bounds. The retained Blender preview predates this small correction. Geometry and the lighting bake are unchanged; the final browser capture is the delivery comparison view.
