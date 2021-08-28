from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
# %%
video = VideoFileClip(r"Donuts.mp4")

subvideo = video.subclip(60, 70)
# %%

def txt_generator(txt):
    return TextClip(txt, font='Arial-Bold', fontsize=43, color='white', stroke_color='black', stroke_width=1)

subtitles = SubtitlesClip(r"Donuts.srt", txt_generator)

result = CompositeVideoClip([video, subtitles.set_position(lambda t: ('center', 550) )])

# result = result.subclip(4,6)

result.write_videofile(r"Doughnuts_with_subs.mp4", fps=video.fps, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")


