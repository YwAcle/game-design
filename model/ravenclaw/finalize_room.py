"""Run reviewed source render, export bake and read-only source verification in one job."""
import runpy
from pathlib import Path
here=Path(__file__).resolve().parent
for name in ['build_rooms.py','export_rooms.py','verify_source.py']:
    print('FINALIZE_STAGE',name,flush=True)
    runpy.run_path(str(here/name),run_name='__main__')
print('FINALIZE_ROOM_COMPLETE',flush=True)
