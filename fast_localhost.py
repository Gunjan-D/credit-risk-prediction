import http.server
import socketserver
import os

PORT = 3000

# Lightweight handler for faster responses
class FastHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=r"C:\Users\gdeshpande\Downloads\AMS560_project copy", **kwargs)
    
    def end_headers(self):
        # Add headers to prevent caching issues
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def do_GET(self):
        # Redirect root to our app
        if self.path == '/' or self.path == '/index.html':
            self.path = '/credit_risk_app.html'
        return super().do_GET()

try:
    # Use threading server for better performance
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
    
    with ThreadedTCPServer(("", PORT), FastHandler) as httpd:
        print(f"⚡ FAST Server running at http://localhost:{PORT}")
        print("🚀 Optimized for quick loading!")
        print("🔄 Press Ctrl+C to stop")
        httpd.serve_forever()
        
except OSError:
    print("❌ Port 3000 busy. Try opening the file directly:")
    print("   Double-click: credit_risk_app.html")
except KeyboardInterrupt:
    print("\n⏹️ Server stopped")