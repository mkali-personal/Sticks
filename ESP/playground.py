import cv2
import os
import subprocess

def video_to_gif(video_path: str, output_gif_path: str = None, target_fps: float = 10.0):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Generate output path if not provided
    if output_gif_path is None:
        base, _ = os.path.splitext(video_path)
        output_gif_path = base + f"_{int(target_fps)}fps.gif"

    # Temporary path for intermediate .mp4
    temp_video = "temp_converted.mp4"

    # Load video with cv2 and save frames with adjusted fps
    cap = cv2.VideoCapture(video_path)
    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, target_fps, (width, height))

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()

    # Write all frames to temp video with new fps
    for frame in frames:
        out.write(frame)
    out.release()

    # Use ffmpeg to convert temp video to gif
    cmd = [
        "ffmpeg",
        "-y",  # overwrite without asking
        "-i", temp_video,
        "-vf", f"fps={target_fps},scale=640:-1:flags=lanczos",  # resize for efficiency
        "-loop", "0",
        output_gif_path
    ]
    subprocess.run(cmd, check=True)

    # Clean up temp video
    os.remove(temp_video)

    print(f"GIF saved to: {output_gif_path}")

video_path = r"C:\Users\michaeka\Desktop\20250417_080553_100fps.mp4"
output_gif_path = r"C:\Users\michaeka\Desktop\20250417_080553_100fps.gif"
video_to_gif(video_path, output_gif_path, target_fps=100.0)
# %%
import cv2
import os

def change_video_fps(video_path: str, target_fps: float, output_path: str = None,
                     start_time: float = None, end_time: float = None):
    """
    Change the playback speed of a video by setting a new fps.
    Optionally trim the video between start_time and end_time (in seconds).

    :param video_path: Path to the input video file.
    :param target_fps: Desired frame rate for output video.
    :param output_path: Optional path for the output video file.
    :param start_time: Optional start time in seconds.
    :param end_time: Optional end time in seconds.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    # Derive output path if not given
    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_{int(target_fps)}fps{ext}"

    cap = cv2.VideoCapture(video_path)
    orig_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Time -> frame number conversion
    start_frame = int(start_time * orig_fps) if start_time is not None else 0
    end_frame = int(end_time * orig_fps) if end_time is not None else total_frames

    start_frame = max(0, start_frame)
    end_frame = min(total_frames, end_frame)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

    print(f"Original FPS: {orig_fps} -> New FPS: {target_fps}")
    print(f"Saving trimmed video from {start_frame / orig_fps:.2f}s to {end_frame / orig_fps:.2f}s")
    print(f"Output path: {output_path}")

    current_frame = start_frame
    while current_frame < end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    print("Done.")

# Example usage:
if __name__ == "__main__":
    change_video_fps(video_path, target_fps=100.0, start_time=104.0, end_time=134.0)
# %%
video_path = r"C:\Users\michaeka\Desktop\20250417_080553_100fps - Copy.mp4"

import subprocess
import os

def convert_video_for_whatsapp_and_windows(input_path: str, output_path: str = None, crf: int = 23):
    """
    Convert a video to H.264 MP4 format, compatible with WhatsApp and Windows Photos app.

    :param input_path: Path to the input video file.
    :param output_path: Optional path to the output file (defaults to _converted.mp4).
    :param crf: Constant Rate Factor (lower means better quality, typical: 18–28).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Video not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_converted.mp4"

    command = [
        'ffmpeg',
        '-i', input_path,
        '-vcodec', 'libx264',
        '-acodec', 'aac',       # Optional, but improves compatibility
        '-movflags', 'faststart',
        '-crf', str(crf),       # Lower crf = better quality, 23 is default
        '-preset', 'medium',    # Can be: ultrafast, superfast, faster, fast, medium, slow, slower, veryslow
        output_path
    ]

    print(f"Running ffmpeg command:\n{' '.join(command)}")
    subprocess.run(command, check=True)
    print(f"Conversion complete: {output_path}")

# Example usage:
if __name__ == "__main__":
    convert_video_for_whatsapp_and_windows(video_path)
