#!/bin/zsh
# One working day of the owner agent, made to be started by a daily job (for example launchd on a Mac).
# It runs at most once a day: owner.py stops by itself if today's branch is already on GitHub.
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
mkdir -p out/owner
log="out/owner/daily.log"
echo "===== $(date '+%Y-%m-%d %H:%M') =====" >> "$log"
uv run owner.py day >> "$log" 2>&1
code=$?
last="$(grep -E 'Proposed change:|already done|Command failed|did not answer|not committed' "$log" | tail -1 | cut -c1-180)"
if [ $code -eq 0 ]; then title="Owner agent: day finished"; else title="Owner agent: the day did not finish"; fi
/usr/bin/osascript -e "display notification \"${last//\"/\'}\" with title \"$title\"" >/dev/null 2>&1
exit $code
