import pytesseract
from moviepy.editor import *

# %%
clip = VideoFileClip(r"Video Editing\Donuts.mp4")
# %%
clipped = clip.crop(x1=300, y1=620, x2=1000, y2=710)

# %%
t = 50

some_frame = clip.get_frame(t=t)
clip.save_frame(r"Video Editing\some_frame.png", t=t)

some_frame_clipped = clipped.get_frame(t=t)
clipped.save_frame(r"Video Editing\some_frame_clipped.png", t=t)



# %%
# saving a frame at 2 second

some_frame_clipped = some_frame.mean(axis=2)
txt = pytesseract.image_to_string(some_frame_clipped, lang='heb')
print(txt)
# %%

from PIL import Image
# from numpy import asarray
# load the image
image = Image.open('Video Editing\somple example.png')
txt = pytesseract.image_to_string(image, lang='heb')