@echo off
REM Text-to-speech (todo2, Phase D). Runs generate_speech.py -> tts_output\*.<voice>.wav
REM   v                            -> config\config_tts.json (or in-file defaults)
REM   v config\config_tts.json     -> explicit config
call conda activate learn-better
python code\generate_speech.py %1
