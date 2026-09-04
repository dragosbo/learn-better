@echo off
REM Word cloud data (Phase W). Runs make_wordcloud.py -> data\wordclouds\*.word_cloud.json
REM   d   -> build word_cloud.json for the INPUT set at the top of the script
call conda activate learn-better
python code\make_wordcloud.py
