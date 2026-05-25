import socket
import cv2
import json
import threading
import platform


class WebServer:

    def __init__(self, shared_camera, camera_image_saver, host="0.0.0.0", port=1234):

        self.shared_camera = shared_camera
        self.camera_image_saver = camera_image_saver
        self.host = host
        self.port = port

        # Create TCP socket
        self.server = socket.socket()

        # Reuse port after restart
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind IP + port
        self.server.bind((self.host, self.port))

        # Listen for connections
        self.server.listen(5)

    def start(self):

        print(f"Web server running on port {self.port}")

        while True:

            # Wait for browser
            c, addr = self.server.accept()

            # Handle browser in separate thread
            threading.Thread(target=self.handle_client, args=(c, addr)).start()

    def handle_client(self, c, addr):

        print("Browser connected:", addr)

        try:

            request = c.recv(4096).decode()

            if not request:
                c.close()
                return

            print(request)

            # First request line
            first_line = request.split("\n")[0]

            # Example:
            # GET /video_feed HTTP/1.1
            path = first_line.split(" ")[1]

            # Remove query string
            if "?" in path:
                path = path.split("?")[0]

            print("Path:", path)

            # =====================
            # HOME PAGE
            # =====================
            if path == "/":

                with open("MPU_Camera.html", "r") as file:
                    html = file.read()

                response = f"""
HTTP/1.1 200 OK
Content-Type: text/html

{html}
"""

                c.send(response.encode())
                c.close()

            # =====================
            # LIVE STREAM
            # =====================
            elif path == "/video_feed":

                header = """
HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame

"""

                c.send(header.encode())

                try:

                    while True:

                        frame = self.shared_camera.get_frame()

                        if frame is None:
                            continue

                        ret, jpeg = cv2.imencode(".jpg", frame)

                        if not ret:
                            continue

                        image = jpeg.tobytes()

                        c.send(b"--frame\r\n")
                        c.send(b"Content-Type: image/jpeg\r\n\r\n")
                        c.send(image)
                        c.send(b"\r\n")

                except:

                    print("Browser disconnected")

                c.close()

            # =====================
            # IMAGE LIST
            # =====================
            elif path == "/api/images":

                header = """
HTTP/1.1 200 OK
Content-Type: application/json

"""

                image_list = []

                # Sort newest images first
                images = sorted(self.camera_image_saver.output_dir.glob("*.jpg"), reverse=True)

                for image in images:

                    image_info = {
                        "name": image.name,
                        "size": image.stat().st_size / 1024
                    }

                    image_list.append(image_info)

                data = json.dumps({
                    "images": image_list
                })

                c.send((header + data).encode())
                c.close()

            # =====================
            # SEND IMAGE
            # =====================
            elif path.startswith("/api/image/"):

                filename = path.replace("/api/image/", "")

                image_path = self.camera_image_saver.output_dir / filename

                if image_path.exists():

                    with open(image_path, "rb") as file:
                        image_bytes = file.read()

                    header = """
HTTP/1.1 200 OK
Content-Type: image/jpeg

"""

                    c.send(header.encode())
                    c.send(image_bytes)

                else:

                    response = """
HTTP/1.1 404 Not Found
Content-Type: text/html

<h1>Image Not Found</h1>
"""

                    c.send(response.encode())

                c.close()

            # =====================
            # STATS
            # =====================
            elif path == "/api/stats":

                images = list(self.camera_image_saver.output_dir.glob("*.jpg"))

                total_images = len(images)

                total_size = sum(image.stat().st_size for image in images)

                data = {
                    "total_images": total_images,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "hostname": "RaspberryPi 4"
                }

                header = """
HTTP/1.1 200 OK
Content-Type: application/json

"""

                c.send((header + json.dumps(data)).encode())
                c.close()

            # =====================
            # 404
            # =====================
            else:

                response = """
HTTP/1.1 404 Not Found
Content-Type: text/html

<h1>404 Not Found</h1>
"""

                c.send(response.encode())
                c.close()

        except Exception as e:

            print("Web server error:", e)
            c.close()

