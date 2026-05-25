import time
import threading
import syslog

from PIR_motion_sensor import PIRMonitor
from camera import CameraImageSaver
from shared_camera import SharedCamera
from webpage import WebServer


# -----------------------------------
# SYSLOG
# -----------------------------------

syslog.openlog(
    "APP",
    syslog.LOG_PID,
    syslog.LOG_USER
)


# -----------------------------------
# SHARED CAMERA OBJECT
# -----------------------------------

shared_camera = SharedCamera()

camera = CameraImageSaver()


# -----------------------------------
# CAMERA THREAD
# continuously captures frames
# -----------------------------------

def camera_thread():

    shared_camera.start()


# -----------------------------------
# PIR THREAD
# waits for motion and saves image
# -----------------------------------

def pir_monitor_thread():

    pir = PIRMonitor()

    print("Monitoring motion...")

    motion_active = False

    while True:

        motion_detected = pir.wait_for_motion()

        # Trigger only once
        if motion_detected and not motion_active:

            motion_active = True

            print("Motion detected")

            # Get latest frame
            frame = shared_camera.get_frame()

            # Save image
            filepath = camera.save_frame(frame)

            if filepath:

                syslog.syslog(
                    syslog.LOG_INFO,
                    f"Image captured: {filepath}"
                )

        # Reset when motion stops
        elif not motion_detected:

            motion_active = False

        time.sleep(0.2)


# -----------------------------------
# WEB SERVER THREAD
# handles browser streaming
# -----------------------------------

def web_server_thread():

    web = WebServer(shared_camera, camera)

    web.start()


# -----------------------------------
# MAIN
# -----------------------------------

def main():

    # Camera capture thread
    cam_thread = threading.Thread(
        target=camera_thread
    )

    # PIR monitoring thread
    pir_thread = threading.Thread(
        target=pir_monitor_thread
    )

    # Web server thread
    web_thread = threading.Thread(
        target=web_server_thread
    )

    # Start all threads
    cam_thread.start()

    pir_thread.start()

    web_thread.start()

    # Wait forever
    cam_thread.join()

    pir_thread.join()

    web_thread.join()


# -----------------------------------
# ENTRY
# -----------------------------------

if __name__ == "__main__":

    main()



