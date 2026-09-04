@echo off
REM Word cloud data batch (Phase W3). Optional arg: a JSON config file in config\.
REM   wc                                  -> config\config_wordcloud.json (or in-file defaults)
REM   wc config\config_wordcloud.json     -> explicit config
call conda activate learn-better
python code\make_wordcloud.py %1
