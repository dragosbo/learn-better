@echo off
REM Audio re-encode / bitrate (todo1 item 4). Runs reencode_audio.py -> audio_reencoded\*.<bitrate>.<ext>
REM   a                              -> config\config_reencode.json (or in-file defaults)
REM   a config\config_reencode.json  -> explicit config
call conda activate learn-better
python code\reencode_audio.py %1
