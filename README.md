# Localization classroom
Run `python server.py`, open http://localhost:8000. Python standard library only.
Deploy: push this directory into a Git repository, create Render Web Service (Python, free), build `python -m py_compile server.py`, start `python server.py`, configure ADMIN_KEY with a strong secret. Or import render.yaml as Blueprint. Teacher can reset each poll using this secret. Free Render filesystem is ephemeral: votes can be lost on restart or deploy; persistent storage needs separate configuration. Anonymous browser ID permits updating votes, not secure identity verification. Results refresh every 2 seconds. Rank scoring 8 to 1 points, average across voters. No sample ballots.

Word submissions: one game per line, no fixed number limit; 50 characters per name and 1 MiB request safety limit. All distinct titles are displayed.
