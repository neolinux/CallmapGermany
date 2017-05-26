#!/bin/bash
echo "This will delete all data from DB. Proceed? (y/n) "
read inp
if [ "$inp" == "y" ]; then
    sqlite3 calls.db "DELETE FROM Callsigns; DROP TABLE IF EXISTS CallsignsTmp; VACUUM;";
    echo "Done"
fi
