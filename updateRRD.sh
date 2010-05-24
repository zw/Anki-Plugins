#!/bin/bash

# If there are at least this many cards new+due, pop up a growl notification.
ACTIONABLE_NOTIFY_THRESHOLD=10

RRDTOOL=/opt/local/bin/rrdtool
SQLITE3=/opt/local/bin/sqlite3

ORIG_SRS_DB_PATH="$HOME/stuff/medicine/medicine.anki"
SRS_DB_PATH="/tmp/medicine.anki.tmp-for-updateRRD.sh"
RRD_PATH="$HOME/stuff/medicine/medicine.rrd"
DAY_GRAPH_PATH="$HOME/stuff/medicine/1past-day-medicine-srs-load.png"
WEEK_GRAPH_PATH="$HOME/stuff/medicine/2past-week-medicine-srs-load.png"
MONTH_GRAPH_PATH="$HOME/stuff/medicine/3past-month-medicine-srs-load.png"

# New: select count(*) from cards where type = 2 and priority != -3;
# Due: select count(*) from cards where (type = 0 or type = 1) and combinedDue < strftime('%s','now') and priority != -3;

cp $ORIG_SRS_DB_PATH $SRS_DB_PATH
# Old: $RRDTOOL update $RRD_PATH N:$($SQLITE3 -separator ':' $SRS_DB_PATH 'select revCount, newCount from decks;')
DUE=$($SQLITE3 $SRS_DB_PATH "select count(*) from cards where (type = 0 or type = 1) and combinedDue < strftime('%s','now') and priority != -3;")
NEW=$($SQLITE3 $SRS_DB_PATH "select count(*) from cards where type = 2 and priority != -3;")
echo "updating $RRD_PATH with:"
echo \
$RRDTOOL update $RRD_PATH --template due:new N:$DUE:$NEW
$RRDTOOL update $RRD_PATH --template due:new N:$DUE:$NEW
rm $SRS_DB_PATH

# Take the opportunity to warn me if load goes above $ACTIONABLE_NOTIFY_THRESHOLD.
if [ $(( DUE + NEW )) -ge $ACTIONABLE_NOTIFY_THRESHOLD ]; then
	~/bin/growlnotify -a Anki -m "You have $(( DUE + NEW )) items ($DUE due + $NEW new > $ACTIONABLE_NOTIFY_THRESHOLD"
fi

GRAPH_COMMON="-l 0 -w 800 -h 200 \
  DEF:due=$RRD_PATH:due:AVERAGE \
  DEF:new=$RRD_PATH:new:AVERAGE \
  AREA:due#FF0000:Due \
  AREA:new#00FF00:New:STACK"

$RRDTOOL graph $DAY_GRAPH_PATH   $GRAPH_COMMON
$RRDTOOL graph $WEEK_GRAPH_PATH  $GRAPH_COMMON --start end-1w  --end now
$RRDTOOL graph $MONTH_GRAPH_PATH $GRAPH_COMMON --start end-1m  --end now

exec $HOME/bin/SRS-day-load.sh
