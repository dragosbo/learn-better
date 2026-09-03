"""learn-better shared library.

Reusable helpers extracted from the entry scripts in code/ (Phase B of
mini_todo.md), so scripts stay short and the proven logic lives in one place:

  lib.net       - yt-dlp network options (proxy / cookies / impersonation)
  lib.textutil  - filename + VTT/subtitle text cleaning, language config
  lib.paths     - shared output folder names (audio/, transcripts/, data/)
  lib.youtube   - core operations: build_url, list_videos, list_playlists,
                  download_transcript, download_audio

Import as, e.g.:
    from lib import youtube, net, textutil
"""
