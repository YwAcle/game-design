"""Python 3 fallback for the prebuilt, offline website. No packages required."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os, sys, threading, webbrowser

port = int(os.environ.get('MEMORIES_PORT', '4175'))
root = Path(__file__).resolve().parent / 'dist'
handler = partial(SimpleHTTPRequestHandler, directory=str(root))
server = ThreadingHTTPServer(('127.0.0.1', port), handler)
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
url = f'http://127.0.0.1:{port}'
print(f'Hogwarts, Always: {url}', flush=True)
if '--open' in sys.argv:
    webbrowser.open(url)
try:
    worker.join()
except KeyboardInterrupt:
    server.shutdown()
finally:
    server.server_close()

