# Startup Manager

A modern, feature-rich GUI application for managing Linux startup applications with support for native apps, Flatpak, and Snap packages. Built with Python and Tkinter, featuring a sleek dark theme and intuitive interface.

<img width="1232" height="909" alt="image" src="https://github.com/user-attachments/assets/7d30a710-f5fc-47c6-bfa4-aa80e82a300d" />


## Features

### Core Functionality
- **Universal Application Support**: Manage native Linux applications, Flatpak packages, and Snap packages
- **Visual Management**: Modern treeview interface showing all applications with their status
- **Quick Toggle**: Double-click any application to enable/disable startup
- **Startup Delay**: Configure custom delays for each application
- **Custom Applications**: Add any command or script to startup
- **Search & Filter**: Powerful search with type-based filtering (enabled/disabled/native/flatpak/snap/custom)

### Advanced Features
- **Configuration Export/Import**: Save and restore your startup configuration as JSON
- **Real-time Statistics**: View enabled/disabled counts and type breakdowns
- **Intelligent Detection**: Automatically detects installed applications from multiple sources
- **Safe Operations**: Validates commands and provides helpful warnings
- **Quick Access**: Direct access to autostart folder
- **Smart Icons**: Context-aware icons based on application type

## Requirements

### System Requirements
- Linux operating system
- Python 3.6 or higher
- Desktop environment with autostart support (GNOME, KDE, XFCE, etc.)

### Python Dependencies
**Required:**
- tkinter (usually included with Python)

**Optional (for package manager support):**
- Flatpak (for managing Flatpak applications)
- Snap (for managing Snap applications)

Install package managers if needed:
```bash
# For Flatpak
sudo apt install flatpak  # Debian/Ubuntu
sudo dnf install flatpak  # Fedora
sudo pacman -S flatpak    # Arch

# For Snap
sudo apt install snapd    # Debian/Ubuntu
sudo dnf install snapd    # Fedora
```

## Installation

1. Download the script:

2. Make it executable:
```bash
chmod +x Startup_Manager.py
```

3. Run the application:
```bash
./Startup_Manager.py
```

## Usage

### Managing Existing Applications

1. **View Applications**: All installed applications are displayed in the main list
2. **Enable Startup**: 
   - Double-click an application, or
   - Select it and click "Enable Startup"
3. **Disable Startup**: 
   - Double-click an enabled application, or
   - Select it and click "Disable Startup"
4. **Set Delay**: Select an enabled application and click "Set Delay" to configure startup delay

### Search and Filter

- **Search Bar**: Type to search by application name, command, or type
- **Filter Dropdown**: Choose from:
  - `all` - Show all applications
  - `enabled` - Show only startup-enabled applications
  - `disabled` - Show only disabled applications
  - `native` - Show only native Linux applications
  - `flatpak` - Show only Flatpak packages
  - `snap` - Show only Snap packages
  - `custom` - Show only custom entries

### Adding Custom Applications

1. Click "Add Custom" button
2. Fill in the application details:
   - **Application Name**: Display name for the application
   - **Application Type**: Choose native, Flatpak, or Snap
   - **Command**: Full command to execute (use Browse button for files)
   - **Startup Delay**: Optional delay in seconds
3. Click "Add Application"

#### Command Examples

**Native Applications:**
```bash
/usr/bin/firefox
/usr/bin/code
python3 /home/user/scripts/startup.py
```

**Flatpak Applications:**
```bash
flatpak run com.spotify.Client
flatpak run org.mozilla.firefox
```

**Snap Applications:**
```bash
snap run discord
snap run code
```

**Scripts with Arguments:**
```bash
sh -c 'notify-send "System" "Startup complete"'
bash /home/user/scripts/monitor.sh --autostart
```

### Configuration Management

**Export Configuration:**
1. Click "Export" button
2. Choose save location
3. Configuration saved as JSON with all enabled applications

**Import Configuration:**
1. Click "Import" button
2. Select previously exported JSON file
3. All applications from the file will be added to startup

### Application Icons

The manager automatically assigns icons based on application type:
- 🌐 Browsers (Firefox, Chrome, etc.)
- 💻 Code editors (VS Code, Vim, etc.)
- 🎵 Music players (Spotify, etc.)
- 🎬 Video players (VLC, MPV, etc.)
- 💬 Chat applications (Discord, Slack, etc.)
- ⚡ Terminals
- 📁 File managers
- 🎮 Gaming applications
- ✉️ Email clients
- 🎨 Graphics applications
- 📄 Office suites
- 📦 Package manager apps

## Technical Details

### File Locations

**Autostart Directory:**
```
~/.config/autostart/
```

**Desktop Files:**
- `/usr/share/applications/` - System-wide applications
- `/usr/local/share/applications/` - Local applications
- `~/.local/share/applications/` - User applications

**Flatpak:**
- `/var/lib/flatpak/app/` - System Flatpaks
- `~/.local/share/flatpak/app/` - User Flatpaks

**Snap:**
- `/var/lib/snapd/desktop/applications/` - Snap applications

### Desktop Entry Format

The manager creates standard `.desktop` files in the autostart directory:

```ini
[Desktop Entry]
Type=Application
Name=Application Name
Exec=command to execute
Hidden=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
```

For delayed startup, commands are wrapped:
```ini
Exec=sh -c 'sleep 5 && original-command'
```

## Keyboard Shortcuts

- **Refresh**: Press the Refresh button to reload application list
- **Enter**: In dialogs, confirms the action
- **Escape**: In dialogs, cancels the action

## Troubleshooting

### Application Not Appearing

**Check these locations:**
1. System applications: `/usr/share/applications/`
2. User applications: `~/.local/share/applications/`
3. For Flatpak: Run `flatpak list --app`
4. For Snap: Run `snap list`

### Startup Not Working

**Common issues:**
1. **Command not found**: Ensure the full path is specified for custom commands
2. **Permission denied**: Make sure the command/script is executable
3. **Desktop environment**: Some minimal desktop environments may not support autostart
4. **Dependencies**: Check that all required applications are installed

**Debug startup issues:**
```bash
# View autostart files
ls -la ~/.config/autostart/

# Check a specific file
cat ~/.config/autostart/your-app.desktop

# Test command manually
bash -c 'command from desktop file'
```

### Flatpak/Snap Not Detected

If the manager doesn't show Flatpak or Snap applications:
1. Ensure the package manager is installed
2. Run `which flatpak` or `which snap` to verify
3. Restart the application after installing package managers

### Delay Not Working

Some desktop environments handle delays differently:
- GNOME uses `X-GNOME-Autostart-Delay`
- The manager uses both the standard field and command wrapping for compatibility
- Delays are approximate and may vary by 1-2 seconds

## Tips and Best Practices

1. **Start Small**: Begin with a few essential applications
2. **Use Delays**: Stagger startup for resource-heavy applications
3. **Test First**: Manually run commands before adding them to startup
4. **Export Regularly**: Back up your configuration after major changes
5. **Monitor Resources**: Too many startup applications can slow boot time
6. **Use Full Paths**: Always specify full paths for scripts and executables
7. **Check Dependencies**: Ensure all dependencies are available at startup

## Security Considerations

- The manager creates files in `~/.config/autostart/` with standard permissions
- Custom commands are executed with user privileges
- Review all custom commands before adding them
- Be cautious when importing configurations from unknown sources
- Startup applications run automatically - only add trusted commands

## Limitations

- Requires a desktop environment with autostart support
- Does not manage system services (use systemd for those)
- Cannot manage startup applications from other desktop environments
- Delay precision depends on desktop environment implementation

## Contributing

This is an open-source project. Contributions, bug reports, and feature requests are welcome.

## Support

If you find this tool helpful, consider supporting the creator at:
https://revolut.me/grouvya

## Compatibility

Tested on:
- Ubuntu 20.04+
- Fedora 35+
- Arch Linux
- Pop!_OS
- Linux Mint

Desktop Environments:
- GNOME
- KDE Plasma
- XFCE
- Cinnamon
- MATE

## Version

Current version: 1.0 ALPHA

---

**Created with ❤️ by Grouvya**
