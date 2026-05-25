import cv2
import os
from datetime import datetime
from pathlib import Path


class CameraImageSaver:

    def __init__(self, output_dir=None, capture_dir=None):

        if output_dir is None:

            self.output_dir = Path.home() / "camera_images"

        else:

            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(f"Output: {self.output_dir}")


    def save_frame(self, frame, filename=None):

        if frame is None:
            return None

        if filename is None:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d_%H-%M-%S"
            )

            filename = f"image_{timestamp}.jpg"

        filepath = self.output_dir / filename

        cv2.imwrite(str(filepath), frame)

        os.sync()

        print(f"Saved: {filepath}")

        return filepath


