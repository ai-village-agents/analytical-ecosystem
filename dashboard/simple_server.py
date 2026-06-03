from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

os.chdir('/tmp/analytical-ecosystem/dashboard')

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/simple_dashboard.html'
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json, datetime
            response = {
                "status": "healthy",
                "timestamp": datetime.datetime.now().isoformat(),
                "service": "Analytical Ecosystem Dashboard",
                "version": "1.0.0"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        elif self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            import json, datetime
            response = {
                "current": {
                    "stars": 0,
                    "forks": 0,
                    "watchers": 0
                },
                "status": "operational",
                "phase1_progress": {
                    "task1": 100,
                    "task2": 70,
                    "task3": 100,
                    "task4": 100,
                    "task5": 100
                }
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        return super().do_GET()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5000), DashboardHandler)
    print("Dashboard server started on http://0.0.0.0:5000")
    print("Press Ctrl+C to stop")
    server.serve_forever()
