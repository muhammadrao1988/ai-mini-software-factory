#!/bin/zsh
# One working day of the owner agent, made to be started by a daily job (for example launchd on a Mac).
# It runs at most once a day: owner.py stops by itself if today's branch is already on GitHub.
# If the internet or the AI service is down, it waits half an hour and tries again, up to four times.
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
mkdir -p out/owner
log="out/owner/daily.log"
for attempt in 1 2 3 4; do
  echo "===== $(date '+%Y-%m-%d %H:%M') (try $attempt) =====" >> "$log"
  run="$(uv run owner.py day 2>&1)"
  code=$?
  echo "$run" >> "$log"
  # a day that failed only because nothing could be reached is tried again later
  if [ $code -ne 0 ] && echo "$run" | grep -qE "API Error|Connection refused|ECONNREFUSED|did not answer|Could not resolve host|timed out"; then
    [ $attempt -lt 4 ] && sleep 1800 && continue
  fi
  break
done
last="$(echo "$run" | grep -E 'Proposed change:|already done|Command failed|did not answer|not committed' | tail -1 | cut -c1-180)"
if [ $code -eq 0 ]; then title="Owner agent: day finished"; else title="Owner agent: the day did not finish"; fi
/usr/bin/osascript -e "display notification \"${last//\"/\'}\" with title \"$title\"" >/dev/null 2>&1
exit $code
