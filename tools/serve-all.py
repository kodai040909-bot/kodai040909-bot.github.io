# 公開先と同じ並びで手元に配る：/ → app-hub、/nemuri-garden/ → nemuri-garden、/kintore/ → kintore
# 使い方（ワークスペースの直下から）：python app-hub/tools/serve-all.py 8125
# 開発の道具として、PUT /icons/<名前>.png で app-hub/icons に保存できる（localhost からだけ）
import http.server, os, re, sys

WS = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
MOUNTS = [('/nemuri-garden/', os.path.join(WS, 'nemuri-garden')), ('/kintore/', os.path.join(WS, 'kintore')), ('/', os.path.join(WS, 'app-hub'))]

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split('?', 1)[0].split('#', 1)[0]
        for prefix, root in MOUNTS:
            if p.startswith(prefix) or p + '/' == prefix:
                rest = p[len(prefix):] if p.startswith(prefix) else ''
                full = os.path.normpath(os.path.join(root, *[x for x in rest.split('/') if x and x != '..']))
                return full if full.startswith(root) else root
        return os.path.join(WS, 'app-hub')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def do_PUT(self):
        m = re.fullmatch(r'/icons/([a-z0-9-]{1,40})\.png', self.path)
        n = int(self.headers.get('Content-Length', 0))
        if not m or n <= 0 or n > 5_000_000 or self.client_address[0] not in ('127.0.0.1', '::1'):
            self.send_response(403); self.end_headers(); return
        data = self.rfile.read(n)
        if not data.startswith(b'\x89PNG'):
            self.send_response(400); self.end_headers(); return
        folder = os.path.join(WS, 'app-hub', 'icons'); os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, m.group(1) + '.png'), 'wb') as f: f.write(data)
        self.send_response(201); self.end_headers()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8125
    http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
