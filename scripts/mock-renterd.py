#!/usr/bin/env python3
"""
Simple mock renterd server for portal testing.
Provides minimal API endpoints for portal initialization.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import threading
import signal
import sys

class MockRenterdHandler(BaseHTTPRequestHandler):
    """Mock handler for renterd API endpoints."""
    
    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(json.dumps(data).encode())))
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            sys.stderr.write(f"Received GET request: {self.path}\n")
            sys.stderr.flush()
            if self.path == '/api/bus/state':
                # Return minimal bus state
                self.send_json_response({
                    'state': 'running',
                    'health': 'ok'
                })
            elif self.path == '/api/health':
                self.send_json_response({'status': 'ok'})
            else:
                self.send_json_response({'error': 'Not found'}, 404)
        except Exception as e:
            sys.stderr.write(f"Error handling GET request: {e}\n")
            sys.stderr.flush()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        sys.stderr.write(f"{self.address_string()} - {self.log_date_time_string()} - {format % args}\n")

def run_mock_server(port=8081):
    """Run mock renterd server."""
    server = ThreadingHTTPServer(('localhost', port), MockRenterdHandler)
    sys.stderr.write(f"Mock renterd server running on port {port}\n")
    sys.stderr.flush()
    
    def shutdown_handler(signum, frame):
        sys.stderr.write("\nShutting down mock server...\n")
        sys.stderr.flush()
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    
    server.serve_forever()

class MockRenterdHandler(BaseHTTPRequestHandler):
    """Mock handler for renterd API endpoints."""
    
    def send_json_response(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path == '/api/bus/state':
                # Return minimal bus state
                self.send_json_response({
                    'state': 'running',
                    'health': 'ok'
                })
            elif self.path == '/api/health':
                self.send_json_response({'status': 'ok'})
            else:
                self.send_json_response({'error': 'Not found'}, 404)
        except Exception as e:
            print(f"Error handling GET request: {e}")
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def run_mock_server(port=8081):
    """Run mock renterd server."""
    server = HTTPServer(('localhost', port), MockRenterdHandler)
    print(f"Mock renterd server running on port {port}")
    
    def shutdown_handler(signum, frame):
        print("\nShutting down mock server...")
        server.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    
    server.serve_forever()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    run_mock_server(port)
