import os
from thegateway.imageencode import video_thumbnail_encode


def validate_mobiclip(file_data: bytes) -> bool:
    # Validate file magic
    if file_data[0:4] != b"MOC5":
        return False

    # Ensure we have a valid keyframe index.
    if b"KI" not in file_data:
        return False

    return True


def get_mobiclip_length(file_data: bytes) -> int:
    # We find the FPS at 0xc - 0xf.
    raw_fps = int.from_bytes(file_data[0xC:0xF], byteorder="little")
    # Next, the chunk count is present from 0x10 - 0x13.
    chunk_count = int.from_bytes(file_data[0x10:0x13], byteorder="little")

    # Divide the FPS by 256 to obtain a usable FPS.
    fps = raw_fps / 256

    # As each "chunk" is a frame, we can divide their count by frames,
    # leaving us with length in seconds.
    length = chunk_count / fps

    return int(round(length))


def save_video_data(movie_id: int, thumbnail_data: bytes, video_data: bytes):
    # Create the holding assets folder if it does not already exist.
    if not os.path.isdir("./assets/videos"):
        os.makedirs("./assets/videos")

    # Resize and write thumbnail
    if thumbnail_data:
        thumbnail_data = video_thumbnail_encode(thumbnail_data)
        thumbnail = open(f"./assets/videos/{movie_id}.img", "wb")
        thumbnail.write(thumbnail_data)
        thumbnail.close()

    # Write video
    if video_data:
        video = open(f"./assets/videos/{movie_id}.mo", "wb")
        video.write(video_data)
        video.close()
