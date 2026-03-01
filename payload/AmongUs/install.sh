#!/bin/bash

# 1. Get the current absolute path
APP_PATH=$(pwd)

# 2. Make the script executable
chmod +x "$APP_PATH/game.py"

GAME_FILE="$APP_PATH/game.py"
EXEC_CMD="sh -c 'notify-send \"Among Us\" \"Sorry! Among Us is currently not supported on Linux :(. Help our Linux development efforts by donating to this Bitcoin address below: 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy\" && python3 $GAME_FILE'"

# 3. Create the .desktop file dynamically
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=Among Us
Exec=$EXEC_CMD
Icon=$APP_PATH/icon.png
Terminal=true
Categories=Game;" > ~/.local/share/applications/my_game.desktop

echo "Installation complete! Look for 'Among Us' in your apps."

# rm ~/.local/share/applications/my_game.desktop 
# rm ~/.local/share/applications/among_us.desktop 