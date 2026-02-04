#!/bin/bash
# ZenApp zrok health monitor - restarts zrok share if it dies

ZROK_SCREEN="zrokzenapp"
ZROK_RESERVED="zenapp"
ZROK_URL="https://zenapp.share.zrok.io"
CHECK_INTERVAL=180  # seconds (3 minutes)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

check_and_restart() {
    # Check if zrok process is running
    if ! screen -list | grep -q "$ZROK_SCREEN"; then
        log "⚠️  zrok screen session not found, restarting..."
        screen -dmS "$ZROK_SCREEN" zrok share reserved "$ZROK_RESERVED"
        sleep 5
        log "✅ zrok restarted"
        return
    fi

    # Check if URL responds
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ZROK_URL" --max-time 10 2>&1)
    if [ "$HTTP_CODE" != "200" ]; then
        log "⚠️  zrok not responding (HTTP $HTTP_CODE), restarting..."
        screen -S "$ZROK_SCREEN" -X quit 2>/dev/null
        sleep 2
        screen -dmS "$ZROK_SCREEN" zrok share reserved "$ZROK_RESERVED"
        sleep 5
        log "✅ zrok restarted"
    else
        log "✓ zrok healthy (HTTP 200)"
    fi
}

log "Starting ZenApp zrok monitor (checking every ${CHECK_INTERVAL}s)"
while true; do
    check_and_restart
    sleep $CHECK_INTERVAL
done
