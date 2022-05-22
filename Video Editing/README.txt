Save the subtitles as .ass file using Subtitle Edit 

replace the two format lines in the beginning with this:

Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Tahoma,16,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1,0,2,10,10,20,1


following this article, run the following cmd command from the directory of the files:
ffmpeg -hide_banner -y -threads "8" -strict "experimental" -i "original_video.mp4" -flags2 "+fast+ignorecrop+showall+export_mvs" -fflags "+ignidx+genpts+nofillin+discardcorrupt-fastseek" -movflags "+faststart+disable_chpl" -avoid_negative_ts "make_zero" -tune "zerolatency" -ignore_unknown -ss "00:00:01.001" -map_chapters "-1" -map_metadata "-1" -sn -vf "ass=subitiles_file_in_ass_format.ass" -preset "veryslow" -crf 21 -pix_fmt "yuv420p" -movflags "+faststart" -profile:v "baseline" -level "3.0" "video_output.mp4"

original post: https://gist.github.com/eladkarako/54746db67e13b944b84853de91007da5

notice that this configuration was dropped from the original syntax since it threw an exception:
-flags "+naq+low_delay+global_header-unaligned-ilme-cgop-loop-output_corrupt"


ffmpeg -hide_banner -y -threads "8" -strict "experimental" -i "Unemployment.mp4" -flags2 "+fast+ignorecrop+showall+export_mvs" -fflags "+ignidx+genpts+nofillin+discardcorrupt-fastseek" -movflags "+faststart+disable_chpl" -avoid_negative_ts "make_zero" -tune "zerolatency" -ignore_unknown -ss "00:00:01.001" -map_chapters "-1" -map_metadata "-1" -sn -vf "ass=Unemployment.ass" -preset "veryslow" -crf 21 -pix_fmt "yuv420p" -movflags "+faststart" -profile:v "baseline" -level "3.0" "Whistler_with_sub.mp4"