@echo off
REM Whisper transcription (Phase C). Optional arg: a JSON config file in config\.
REM   w                                   -> config\config_transcribe.json (or in-file defaults)
REM   w config\config_transcribe.id.json  -> transcribe by video id
REM   w config\config_transcribe.name.json-> transcribe by name substring
REM   w config\config_transcribe.all.json -> transcribe every audio file (slow)
call conda activate learn-better
python code\transcribe_audio.py %1
