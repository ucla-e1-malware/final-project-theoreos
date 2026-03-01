#!/bin/bash

# 1. Get the current absolute path
APP_PATH=$(pwd)

# 2. Make the script executable
chmod +x "$APP_PATH/game.py"

EXEC_CMD="sh -c 'zenity --info --text=\"Game Loading...\" --title=\"Among Us\" --timeout=2 & python3 $GAME_FILE'"

# 3. Create the .desktop file dynamically
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=Among Us
Exec=python3 $APP_PATH/game.py
Icon=$APP_PATH/icon.png
Terminal=true
Categories=Game;" > ~/.local/share/applications/my_game.desktop

echo "Installation complete! Look for 'Among Us' in your apps."