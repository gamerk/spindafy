rmdir .\badspinda2 /s /q

@REM robocopy .\badspinda .\badspinda2 /s /e

@REM powershell.exe -Command "Get-ChildItem .\badspinda2\*.png | Rename-Item -NewName {$_.Name -replace '_0x.+?$', '.png'}"

ffmpeg.exe -y -framerate 30 -i ".\adef_spinda\frame%%07d.png" -vf scale="ceil(iw/2)*2:ceil(ih/2)*2" -c:v libx264 -sws_flags neighbor out.mp4

ffmpeg.exe -y -i .\out.mp4 -i .\adef_video.webm -filter_complex "[1:v]scale=128:-1[v2];[0:v][v2]overlay=main_w-overlay_w-5:5" -c:v libx264 -c:a mp3 out2.mp4