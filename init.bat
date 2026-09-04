@echo off
REM init.bat - add the repo's scripts\ folder to PATH for THIS cmd session
REM so you can type the one-letter runners (c, r, t, s, p, w, d, wc, a, v)
REM from the repo root instead of scripts\c.bat, scripts\r.bat, ...
REM
REM Usage (from the repo root, in cmd):
REM     init
REM Then:  c   (activate env)   r / t / w / v ...   wc config\config_wordcloud.json
REM
REM Note: run it as `init` (not in a child shell) so the PATH change stays in
REM your current session. %~dp0 is this .bat's folder (repo root, with trailing \).

set "PATH=%~dp0scripts;%PATH%"
echo Added "%~dp0scripts" to PATH for this session.
echo You can now run: c  r  t  s  p  w  d  wc  a  v   (e.g. "c" then "r").
