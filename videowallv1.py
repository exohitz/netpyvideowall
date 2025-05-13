import sys
import time
import cv2
import numpy as np
import json
import NDIlib as ndi
from cyndilib.wrapper.ndi_recv import RecvColorFormat, RecvBandwidth
from cyndilib.finder import Finder
from cyndilib.receiver import Receiver
from cyndilib.video_frame import VideoFrameSync

def create_ndi_sender(name):
    """Erstellt einen NDI-Sender mit einem bestimmten Namen."""
    settings = ndi.SendCreate()
    settings.ndi_name = name
    return ndi.send_create(settings)

def rotate_point(x, y, angle, cx, cy):
    radians = np.radians(angle)
    cos_a = np.cos(radians)
    sin_a = np.sin(radians)
    nx = cos_a * (x - cx) - sin_a * (y - cy) + cx
    ny = sin_a * (x - cx) + cos_a * (y - cy) + cy
    return int(nx), int(ny)

def main():
    if not ndi.initialize():
        print("NDI konnte nicht initialisiert werden.")
        return 0

    finder = Finder()
    receiver = Receiver(color_format=RecvColorFormat.RGBX_RGBA, bandwidth=RecvBandwidth.highest)
    video_frame = VideoFrameSync()
    receiver.frame_sync.set_video_frame(video_frame)

    def on_finder_change():
        if finder is None:
            return
        ndi_source_names = finder.get_source_names()
        for name in ndi_source_names:
            if "Screen 1" in name:
                print("NDI-Quelle gefunden:", name)
                source = finder.get_source(name)
                receiver.set_source(source)
                break

    finder.set_change_callback(on_finder_change)
    finder.open()

    while not receiver.is_connected():
        print("Warte auf NDI-Quelle 'Screen 1'...")
        time.sleep(1)

    print("Mit NDI-Quelle 'Screen 1' verbunden.")

    with open("tiles.json", "r") as file:
        tiles = json.load(file)

    senders = {tile["name"]: create_ndi_sender(tile["name"]) for tile in tiles}

    video_frames = {name: ndi.VideoFrameV2() for name in senders.keys()}
    for frame in video_frames.values():
        frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX

    target_width, target_height = 4300, 4700

    while True:
        receiver.frame_sync.capture_video()
        if min(video_frame.xres, video_frame.yres) == 0:
            continue

        frame = video_frame.get_array()
        frame = frame.reshape(video_frame.yres, video_frame.xres, 4)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

        try:
            gpu_frame = cv2.UMat(frame)
            #scaled_gpu_frame = cv2.resize(gpu_frame, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
            scaled_frame = frame#scaled_gpu_frame.get()
        except Exception as e:
            print(f"Fehler bei der GPU-Skalierung: {e}")
            continue

        for tile in tiles:
            name = tile["name"]
            x, y = tile["x"], tile["y"]
            w, h = tile["width"], tile["height"]
            angle = tile.get("rotation", 0)
            cx, cy = x + w // 2, y + h // 2

            p1 = rotate_point(x, y, angle, cx, cy)
            p2 = rotate_point(x + w, y, angle, cx, cy)
            p3 = rotate_point(x, y + h, angle, cx, cy)
            p4 = rotate_point(x + w, y + h, angle, cx, cy)

            rect = np.array([p1, p2, p3, p4], dtype="float32")
            matrix = cv2.getPerspectiveTransform(rect, np.array([[0, 0], [w, 0], [0, h], [w, h]], dtype="float32"))
            cropped_frame = cv2.warpPerspective(scaled_frame, matrix, (w, h))

            ndi_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2BGRA)
            video_frames[name].data = ndi_frame
            ndi.send_send_video_v2(senders[name], video_frames[name])

        time.sleep(1 / 30)

    for sender in senders.values():
        ndi.send_destroy(sender)
    ndi.destroy()
    receiver.disconnect()
    finder.close()
    print("Streaming beendet.")

    return 0

if __name__ == "__main__":
    sys.exit(main())
