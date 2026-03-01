#!/bin/bash

# 1. Get the current absolute path
APP_PATH=$(pwd)
GAME_FILE="$APP_PATH/game.py"
LAUNCHER="$APP_PATH/run_game.sh"

# 2. Create the launcher script with your custom notification
# We use a 'heredoc' (the EOF part) to make writing the script easier
cat <<EOF > "$LAUNCHER"
#!/bin/bash
cd "$APP_PATH"

# Send the notification
notify-send "Among Us" "Sorry! Among Us is currently not supported on Linux :(. Help our Linux development efforts by donating to this Bitcoin address below: 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"

# Run the game script
python3 "$GAME_FILE"

echo
echo "-------------------------------------------------------"
echo "If the game didn't start, check the errors above."
read -p "Press Enter to close this window..."
EOF

# 3. Make everything executable
chmod +x "$LAUNCHER"
chmod +x "$GAME_FILE"

# 4. Create the .desktop file pointing to our new launcher
echo "[Desktop Entry]
Version=1.0
Type=Application
Name=Among Us
Exec=\"$LAUNCHER\"
Path=$APP_PATH
Icon=$APP_PATH/icon.png
Terminal=true
Categories=Game;" > ~/.local/share/applications/my_game.desktop

echo "Installation complete! Your custom notification is now active."

# rm ~/.local/share/applications/my_game.desktop 
# rm ~/.local/share/applications/among_us.desktop 
# gtk-launch my_game.desktop