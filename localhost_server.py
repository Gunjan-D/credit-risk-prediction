import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 3000

# Change to the directory containing the HTML file
os.chdir(r"C:\Users\gdeshpande\Downloads\AMS560_project copy")

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.path = '/credit_risk_app.html'
        return super().do_GET()

try:
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 AMS560 Credit Risk App Server running at http://localhost:{PORT}")
        print(f"📋 Open your browser and go to: http://localhost:{PORT}")
        print("🔄 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
            print("✅ Browser opened automatically!")
        except:
            print("⚠️ Please open http://localhost:3000 manually in your browser")
        
        httpd.serve_forever()
        
except OSError as e:
    if "Address already in use" in str(e):
        print("❌ Port 3000 is already in use!")
        print("💡 Try opening this file directly:")
        print("   C:\\Users\\gdeshpande\\Downloads\\AMS560_project copy\\credit_risk_app.html")
    else:
        print(f"❌ Error: {e}")
        
except KeyboardInterrupt:
    print("\n⏹️ Server stopped by user")
except Exception as e:
    print(f"❌ Unexpected error: {e}")