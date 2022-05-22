from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import subprocess
# %%
video_name = "Unemployment"
video = VideoFileClip(f"{video_name}.mp4")
# %%
# sub_video = video.subclip(9, 12)

# %%
def txt_generator(txt):
    return TextClip(txt, font='Tahoma-Bold', fontsize=43, color='white', stroke_color='black', stroke_width=1)

subtitles = SubtitlesClip(f"{video_name}.srt", txt_generator)
# sub_subtitles = subtitles.subclip(9, 12)
# %%
result = CompositeVideoClip([video, subtitles.set_position(lambda t: ('center', 550) )])
# sub_result = CompositeVideoClip([sub_video, sub_subtitles.set_position(lambda t: ('center', 550) )])

# %%
# result = result.subclip(4,6)

result.write_videofile(f"{video_name}_with_subs.mp4", fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
# sub_result.write_videofile(f"sub_{video_name}_with_subs.mp4", fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
# %%


