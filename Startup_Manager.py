#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import configparser
import glob
import webbrowser
from pathlib import Path
import threading
import json
import re
import sys

class ModernStartupManager:
    def __init__(self, root):
        self.root = root
        # Set WM_CLASS for taskbar icon matching
        self.root.wm_group(self.root)
        self.root.option_add('*tearOff', tk.FALSE)

        self.root.title("🚀 Startup Manager")
        self.root.geometry("1100x750")
        self.root.configure(bg='#1e1e2e')

        # Set window icon
        try:
            icon_path = self.resource_path("build_assets/icon.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, img)
            else:
                # Fallback to system icon if installed
                system_icon = "/usr/share/icons/hicolor/256x256/apps/startup-manager.png"
                if os.path.exists(system_icon):
                    img = tk.PhotoImage(file=system_icon)
                    self.root.iconphoto(True, img)
        except Exception as e:
            print(f"Error loading icon: {e}")

        # Modern color scheme
        self.colors = {
            'bg_primary': '#1e1e2e',
            'bg_secondary': '#313244',
            'bg_tertiary': '#45475a',
            'surface': '#585b70',
            'text_primary': '#cdd6f4',
            'text_secondary': '#bac2de',
            'accent': '#89b4fa',
            'accent_hover': '#74c7ec',
            'success': '#a6e3a1',
            'warning': '#f9e2af',
            'error': '#f38ba8',
            'gradient_start': '#89b4fa',
            'gradient_end': '#cba6f7'
        }

        # Configure ttk styles
        self.setup_styles()

        # Paths for desktop files and autostart
        self.desktop_paths = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            f"{Path.home()}/.local/share/applications"
        ]
        self.autostart_path = Path.home() / ".config" / "autostart"
        self.autostart_path.mkdir(parents=True, exist_ok=True)

        # Snap paths
        self.snap_desktop_path = "/var/lib/snapd/desktop/applications"

        # Flatpak paths
        self.flatpak_system_path = "/var/lib/flatpak/app"
        self.flatpak_user_path = Path.home() / ".local" / "share" / "flatpak" / "app"

        # Animation variables
        self.animation_id = None
        self.search_animation_id = None

        # Check package managers
        self.flatpak_available = self.check_command_available('flatpak')
        self.snap_available = self.check_command_available('snap')

        # Initialize data storage
        self.applications = {}
        self.filtered_apps = {}
        self.filter_var = tk.StringVar(value="all")

        self.setup_ui()
        # Moved load_applications after setup_ui to ensure widgets exist
        self.load_applications()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def check_command_available(self, command):
        """Check if a command is available in the system"""
        try:
            result = subprocess.run(['which', command],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def setup_styles(self):
        """Setup modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        # Configure styles
        style.configure('Main.TFrame',
                       background=self.colors['bg_primary'],
                       borderwidth=0)

        style.configure('Card.TFrame',
                       background=self.colors['bg_secondary'],
                       relief='flat',
                       borderwidth=1)

        style.configure('Modern.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))

        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_hover']),
                            ('pressed', self.colors['gradient_end'])])

        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['bg_primary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))

        style.configure('Danger.TButton',
                       background=self.colors['error'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))

        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       insertcolor=self.colors['accent'])

        style.configure('Modern.Treeview',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_tertiary'],
                       borderwidth=0,
                       font=('Segoe UI', 10))

        style.configure('Modern.Treeview.Heading',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0)

        style.map('Modern.Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])

    def setup_ui(self):
        """Setup the UI"""
        # Main container
        main_container = ttk.Frame(self.root, style='Main.TFrame')
        main_container.pack(fill='both', expand=True)

        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Header section
        self.create_header(main_container)

        # Content area
        content_frame = ttk.Frame(main_container, style='Main.TFrame')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 20))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)

        # Search section
        self.create_search_section(content_frame)

        # Applications section
        self.create_apps_section(content_frame)

        # Control panel
        self.create_control_panel(content_frame)

        # Details panel
        self.create_details_panel(content_frame)

        # Status bar
        self.create_status_bar(main_container)

        # Footer
        self.create_footer(main_container)

    def create_header(self, parent):
        """Create header with gradient effect"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=120)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)

        # Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(expand=True, fill='both')

        title_label = tk.Label(title_frame,
                              text="🚀 Startup Manager",
                              font=('Segoe UI', 28, 'bold'),
                              bg=self.colors['bg_primary'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(25, 5))

        # Build subtitle based on available package managers
        subtitle_parts = ["Manage your system startup applications"]
        supported = []
        if self.flatpak_available:
            supported.append("Flatpak")
        if self.snap_available:
            supported.append("Snap")
        if supported:
            subtitle_parts.append(f"Supporting: {', '.join(supported)}")

        subtitle_label = tk.Label(title_frame,
                                 text=" • ".join(subtitle_parts),
                                 font=('Segoe UI', 12),
                                 bg=self.colors['bg_primary'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack()

    def create_search_section(self, parent):
        """Create search section"""
        search_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        search_card.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        search_card.columnconfigure(1, weight=1)

        # Search icon
        search_icon = tk.Label(search_card, text="🔍", font=('Segoe UI', 16),
                              bg=self.colors['bg_secondary'], fg=self.colors['accent'])
        search_icon.grid(row=0, column=0, padx=(0, 15))

        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_applications())
        self.search_entry = ttk.Entry(search_card, textvariable=self.search_var,
                                     style='Modern.TEntry', font=('Segoe UI', 12))
        self.search_entry.grid(row=0, column=1, sticky='ew', padx=(0, 15))

        # Placeholder
        self.search_placeholder = "Search applications..."
        self.setup_search_placeholder()

        # Filter dropdown
        filter_menu = ttk.Combobox(search_card, textvariable=self.filter_var,
                                   values=["all", "enabled", "disabled", "native", "flatpak", "snap", "custom"],
                                   state="readonly", width=12)
        filter_menu.grid(row=0, column=2, padx=(0, 15))
        filter_menu.bind('<<ComboboxSelected>>', lambda e: self.filter_applications())

        # Refresh button
        refresh_btn = ttk.Button(search_card, text="🔄 Refresh",
                               style='Modern.TButton',
                               command=self.refresh_with_animation)
        refresh_btn.grid(row=0, column=3)

    def setup_search_placeholder(self):
        """Setup search placeholder effect"""
        def on_focus_in(event):
            if self.search_entry.get() == self.search_placeholder:
                self.search_entry.delete(0, tk.END)

        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, self.search_placeholder)

        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.bind('<FocusIn>', on_focus_in)
        self.search_entry.bind('<FocusOut>', on_focus_out)

    def create_apps_section(self, parent):
        """Create applications list section"""
        apps_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        apps_card.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
        apps_card.columnconfigure(0, weight=1)
        apps_card.rowconfigure(1, weight=1)

        # Section header
        header_frame = ttk.Frame(apps_card, style='Card.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 15))

        apps_label = tk.Label(header_frame, text="📱 Applications",
                             font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['bg_secondary'],
                             fg=self.colors['text_primary'])
        apps_label.pack(side='left')

        # Stats label
        self.stats_label = tk.Label(header_frame, text="",
                                   font=('Segoe UI', 10),
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_secondary'])
        self.stats_label.pack(side='right')

        # Treeview container
        tree_container = ttk.Frame(apps_card, style='Card.TFrame')
        tree_container.grid(row=1, column=0, sticky='nsew')
        tree_container.columnconfigure(0, weight=1)
        tree_container.rowconfigure(0, weight=1)

        # Treeview
        self.apps_tree = ttk.Treeview(tree_container,
                                     columns=('status', 'type', 'exec', 'delay'),
                                     show='tree headings',
                                     style='Modern.Treeview',
                                     height=15)

        # Configure columns
        self.apps_tree.heading('#0', text='📋 Application')
        self.apps_tree.heading('status', text='⚡ Status')
        self.apps_tree.heading('type', text='📦 Type')
        self.apps_tree.heading('exec', text='💻 Command')
        self.apps_tree.heading('delay', text='⏱️ Delay')

        self.apps_tree.column('#0', width=300, minwidth=200)
        self.apps_tree.column('status', width=100, minwidth=80)
        self.apps_tree.column('type', width=100, minwidth=80)
        self.apps_tree.column('exec', width=400, minwidth=200)
        self.apps_tree.column('delay', width=80, minwidth=60)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical',
                                command=self.apps_tree.yview)
        self.apps_tree.configure(yscrollcommand=scrollbar.set)

        self.apps_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

        # Bind double-click
        self.apps_tree.bind('<Double-Button-1>', self.toggle_startup)
        self.apps_tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def create_control_panel(self, parent):
        """Create control panel"""
        control_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        control_card.grid(row=2, column=0, sticky='ew')

        buttons_frame = ttk.Frame(control_card, style='Card.TFrame')
        buttons_frame.pack()

        # Add to startup button
        add_btn = ttk.Button(buttons_frame, text="✅ Enable Startup",
                           style='Success.TButton',
                           command=self.add_to_startup)
        add_btn.pack(side='left', padx=(0, 10))

        # Remove from startup button
        remove_btn = ttk.Button(buttons_frame, text="❌ Disable Startup",
                              style='Danger.TButton',
                              command=self.remove_from_startup)
        remove_btn.pack(side='left', padx=(0, 10))

        # Set delay button
        delay_btn = ttk.Button(buttons_frame, text="⏱️ Set Delay",
                             style='Modern.TButton',
                             command=self.set_startup_delay)
        delay_btn.pack(side='left', padx=(0, 10))

        # Add custom app button
        custom_btn = ttk.Button(buttons_frame, text="➕ Add Custom",
                              style='Modern.TButton',
                              command=self.add_custom_app)
        custom_btn.pack(side='left', padx=(0, 10))

        # Open folder button
        folder_btn = ttk.Button(buttons_frame, text="📁 Open Folder",
                              style='Modern.TButton',
                              command=self.open_autostart_folder)
        folder_btn.pack(side='left', padx=(0, 10))

        # Export/Import buttons
        export_btn = ttk.Button(buttons_frame, text="💾 Export",
                              style='Modern.TButton',
                              command=self.export_config)
        export_btn.pack(side='left', padx=(0, 10))

        import_btn = ttk.Button(buttons_frame, text="📥 Import",
                              style='Modern.TButton',
                              command=self.import_config)
        import_btn.pack(side='left', padx=(0, 10))

        # Run Now button
        run_btn = ttk.Button(buttons_frame, text="🚀 Run Now",
                           style='Modern.TButton',
                           command=self.run_app_now)
        run_btn.pack(side='left')

    def create_details_panel(self, parent):
        """Create a dedicated area for application details"""
        self.details_card = ttk.Frame(parent, style='Card.TFrame', padding=15)
        self.details_card.grid(row=3, column=0, sticky='ew', pady=(20, 0))
        
        self.details_text = tk.Text(self.details_card, height=4, 
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_secondary'],
                                  font=('Segoe UI', 10),
                                  relief='flat', state='disabled',
                                  padx=10, pady=10)
        self.details_text.pack(fill='x')

    def update_details_panel(self, app_name):
        """Update details panel with app information"""
        app_info = self.filtered_apps.get(app_name, self.applications.get(app_name))
        if not app_info:
            return

        self.details_text.configure(state='normal')
        self.details_text.delete('1.0', tk.END)
        
        details = [
            f"📍 Name: {app_name}",
            f"💻 Command: {app_info['exec']}",
            f"📦 Type: {app_info.get('type', 'native').capitalize()}"
        ]
        
        if app_info.get('desktop_file'):
            details.append(f"📁 Source: {app_info['desktop_file']}")
            
        self.details_text.insert(tk.END, "\n".join(details))
        self.details_text.configure(state='disabled')

    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        status_frame = tk.Frame(parent, bg=self.colors['bg_tertiary'], height=40)
        status_frame.grid(row=2, column=0, sticky='ew')
        status_frame.grid_propagate(False)

        status_content = tk.Frame(status_frame, bg=self.colors['bg_tertiary'])
        status_content.pack(fill='both', expand=True, padx=20)

        self.status_label = tk.Label(status_content,
                                   textvariable=self.status_var,
                                   bg=self.colors['bg_tertiary'],
                                   fg=self.colors['text_secondary'],
                                   font=('Segoe UI', 9))
        self.status_label.pack(side='left', pady=12)

        self.loading_label = tk.Label(status_content, text="",
                                    bg=self.colors['bg_tertiary'],
                                    fg=self.colors['accent'],
                                    font=('Segoe UI', 9))
        self.loading_label.pack(side='right', pady=12)

    def create_footer(self, parent):
        """Create footer"""
        footer_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=50)
        footer_frame.grid(row=3, column=0, sticky='ew')
        footer_frame.grid_propagate(False)

        footer_content = tk.Frame(footer_frame, bg=self.colors['bg_primary'])
        footer_content.pack(fill='both', expand=True, padx=20, pady=10)

        created_label = tk.Label(footer_content,
                                text="Created with ❤️ by Grouvya!",
                                bg=self.colors['bg_primary'],
                                fg=self.colors['text_secondary'],
                                font=('Segoe UI', 10))
        created_label.pack(side='left', pady=8)

        donate_btn = tk.Button(footer_content,
                              text="☕ Donate",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['warning'],
                              fg=self.colors['bg_primary'],
                              relief='flat',
                              bd=0,
                              padx=20,
                              pady=8,
                              cursor='hand2',
                              command=self.open_donate_link)
        donate_btn.pack(side='right', pady=4)

        def on_enter(e):
            donate_btn.configure(bg='#fab387')
        def on_leave(e):
            donate_btn.configure(bg=self.colors['warning'])

        donate_btn.bind("<Enter>", on_enter)
        donate_btn.bind("<Leave>", on_leave)

    def open_donate_link(self):
        """Open donation link"""
        try:
            webbrowser.open("https://revolut.me/grouvya")
            self.status_var.set("☕ Thank you for considering a donation!")
        except Exception as e:
            self.show_message("Error", f"Failed to open donation link: {str(e)}", 'error')

    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.apps_tree.selection()
        if selection:
            item = self.apps_tree.item(selection[0])
            app_name = self.extract_app_name(item['text'])
            self.status_var.set(f"Selected: {app_name}")
            self.update_details_panel(app_name)


    def run_app_now(self):
        """Run the selected application immediately"""
        result = self.get_selected_app()
        if not result:
            return
        
        app_name, app_info = result
        try:
            cmd = app_info['exec']
            # Remove % field codes if still present
            cmd = re.sub(r'%[fFuUnNdDiIcCkKvV]', '', cmd).strip()
            
            subprocess.Popen(cmd, shell=True, start_new_session=True)
            self.status_var.set(f"🚀 Launched {app_name}")
        except Exception as e:
            self.show_message("Error", f"Failed to launch {app_name}: {str(e)}", 'error')


    def extract_app_name(self, display_name):
        """Extract clean app name from display name"""
        # Remove emoji icon if present
        if ' ' in display_name:
            return display_name.split(' ', 1)[1]
        return display_name

    def refresh_with_animation(self):
        """Refresh with animation"""
        def refresh():
            self.load_applications()
            self.root.after(0, lambda: self.status_var.set("✅ Refresh complete"))

        threading.Thread(target=refresh, daemon=True).start()
        self.status_var.set("🔄 Refreshing applications...")

    def get_snap_apps(self):
        """Get list of installed Snap applications"""
        snap_apps = {}

        if not self.snap_available:
            return snap_apps

        try:
            result = subprocess.run(['snap', 'list'],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 1:
                            app_name = parts[0]

                            desktop_file = f"{self.snap_desktop_path}/{app_name}_{app_name}.desktop"
                            if os.path.exists(desktop_file):
                                app_info = self.parse_desktop_file(desktop_file)
                                if app_info:
                                    app_info['type'] = 'snap'
                                    snap_apps[app_info['name']] = app_info
                            else:
                                snap_apps[app_name] = {
                                    'name': app_name,
                                    'exec': f'snap run {app_name}',
                                    'desktop_file': None,
                                    'startup_enabled': False,
                                    'type': 'snap',
                                    'delay': 0
                                }

        except Exception as e:
            print(f"Error getting Snap apps: {e}")

        return snap_apps

    def get_flatpak_apps(self):
        """Get list of installed Flatpak applications"""
        flatpak_apps = {}

        if not self.flatpak_available:
            return flatpak_apps

        try:
            result = subprocess.run(['flatpak', 'list', '--app', '--columns=application,name'],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip() and '\t' in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            app_id = parts[0].strip()
                            app_name = parts[1].strip()

                            # Prioritize exported desktop files as they have the correct 'flatpak run' Exec commands
                            system_export_path = f"/var/lib/flatpak/exports/share/applications/{app_id}.desktop"
                            user_export_path = f"{Path.home()}/.local/share/flatpak/exports/share/applications/{app_id}.desktop"
                            
                            desktop_paths = [
                                system_export_path,
                                user_export_path,
                                f"/var/lib/flatpak/app/{app_id}/current/active/files/share/applications/{app_id}.desktop",
                                f"{self.flatpak_user_path}/{app_id}/current/active/files/share/applications/{app_id}.desktop"
                            ]

                            desktop_file = None
                            for path in desktop_paths:
                                if os.path.exists(path):
                                    desktop_file = path
                                    break

                            if desktop_file:
                                app_info = self.parse_desktop_file(desktop_file)
                                if app_info:
                                    app_info['type'] = 'flatpak'
                                    app_info['app_id'] = app_id
                                    # Ensure exec command is correct for Flatpak
                                    if not app_info['exec'].startswith('flatpak run') and not app_info['exec'].startswith('/usr/bin/flatpak run'):
                                        app_info['exec'] = f"flatpak run {app_id}"
                                    flatpak_apps[app_info['name']] = app_info
                            else:
                                flatpak_apps[app_name] = {
                                    'name': app_name,
                                    'exec': f'flatpak run {app_id}',
                                    'desktop_file': None,
                                    'startup_enabled': False,
                                    'type': 'flatpak',
                                    'app_id': app_id,
                                    'delay': 0
                                }

        except Exception as e:
            print(f"Error getting Flatpak apps: {e}")

        return flatpak_apps

    def toggle_startup(self, event):
        """Toggle startup status on double-click"""
        selection = self.apps_tree.selection()
        if not selection:
            return

        item = self.apps_tree.item(selection[0])
        app_name = self.extract_app_name(item['text'])
        app_info = self.filtered_apps.get(app_name, self.applications.get(app_name))

        if app_info:
            if app_info.get('startup_enabled', False):
                self.remove_from_startup()
            else:
                self.add_to_startup()

    def add_to_startup(self):
        """Add selected app to startup"""
        result = self.get_selected_app()
        if not result:
            return

        app_name, app_info = result

        if app_info.get('startup_enabled', False):
            self.show_message("Already Added", f"{app_name} is already in startup.", 'info')
            return

        try:
            safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in app_name)
            desktop_filename = f"{safe_name}.desktop"
            autostart_file = self.autostart_path / desktop_filename

            # Load existing metadata if available
            original_config = {}
            if app_info.get('desktop_file') and os.path.exists(app_info['desktop_file']):
                try:
                    parser = configparser.ConfigParser(interpolation=None, strict=False)
                    parser.read(app_info['desktop_file'], encoding='utf-8')
                    if 'Desktop Entry' in parser:
                        for key in ['Icon', 'Comment', 'Categories', 'GenericName', 'Keywords']:
                            if key in parser['Desktop Entry']:
                                original_config[key] = parser['Desktop Entry'][key]
                except:
                    pass

            with open(autostart_file, 'w', encoding='utf-8') as f:
                f.write("[Desktop Entry]\n")
                f.write("Type=Application\n")
                f.write(f"Name={app_name}\n")

                delay = app_info.get('delay', 0)
                if delay > 0:
                    escaped_exec = app_info['exec'].replace("'", "'\\''")
                    f.write(f"Exec=sh -c 'sleep {delay} && {escaped_exec}'\n")
                else:
                    f.write(f"Exec={app_info['exec']}\n")

                f.write("Hidden=false\n")
                f.write("X-GNOME-Autostart-enabled=true\n")
                
                # Write preserved metadata
                for key, value in original_config.items():
                    f.write(f"{key}={value}\n")

                if app_info.get('type') == 'flatpak':
                    if 'Comment' not in original_config:
                        f.write(f"Comment=Flatpak: {app_info.get('app_id', '')}\n")
                elif app_info.get('type') == 'snap':
                    if 'Comment' not in original_config:
                        f.write("Comment=Snap Application\n")
                elif app_info.get('type') == 'custom':
                    if 'Comment' not in original_config:
                        f.write("Comment=Custom Application\n")

                if delay > 0:
                    f.write(f"X-GNOME-Autostart-Delay={delay}\n")

            os.chmod(autostart_file, 0o755)

            app_info['startup_enabled'] = True
            self.filter_applications()

            self.status_var.set(f"✅ Added {app_name} to startup")
            self.show_message("Success", f"{app_name} has been added to startup!", 'success')

        except Exception as e:
            self.show_message("Error", f"Failed to add {app_name}: {str(e)}", 'error')

    def remove_from_startup(self):
        """Remove selected app from startup"""
        result = self.get_selected_app()
        if not result:
            return

        app_name, app_info = result

        if not app_info.get('startup_enabled', False):
            self.show_message("Not in Startup", f"{app_name} is not in startup.", 'info')
            return

        try:
            removed = False
            for autostart_file in self.autostart_path.glob("*.desktop"):
                try:
                    config = configparser.ConfigParser()
                    config.read(autostart_file)
                    if config.has_section('Desktop Entry'):
                        if config['Desktop Entry'].get('Name', '') == app_name:
                            autostart_file.unlink()
                            removed = True
                            break
                except:
                    continue

            if removed:
                app_info['startup_enabled'] = False
                app_info['delay'] = 0
                self.filter_applications()
                self.status_var.set(f"✅ Removed {app_name} from startup")
                self.show_message("Success", f"{app_name} has been removed from startup!", 'success')
            else:
                self.show_message("Not Found", f"Could not find startup entry for {app_name}", 'warning')

        except Exception as e:
            self.show_message("Error", f"Failed to remove {app_name}: {str(e)}", 'error')

    def set_startup_delay(self):
        """Set startup delay for selected app"""
        result = self.get_selected_app()
        if not result:
            return

        app_name, app_info = result

        if not app_info.get('startup_enabled', False):
            self.show_message("Not in Startup", "Please add the application to startup first.", 'info')
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Set Startup Delay")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['bg_primary'])
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"+{x}+{y}")

        content = tk.Frame(dialog, bg=self.colors['bg_primary'])
        content.pack(fill='both', expand=True, padx=20, pady=20)

        label = tk.Label(content,
                        text=f"Set startup delay for {app_name} (seconds):",
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'],
                        font=('Segoe UI', 11))
        label.pack(pady=(0, 10))

        delay_var = tk.StringVar(value=str(app_info.get('delay', 0)))
        delay_entry = tk.Entry(content, textvariable=delay_var,
                              bg=self.colors['bg_tertiary'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 10))
        delay_entry.pack(pady=(0, 20))

        btn_frame = tk.Frame(content, bg=self.colors['bg_primary'])
        btn_frame.pack()

        def save_delay():
            try:
                delay = int(delay_var.get())
                if delay < 0:
                    delay = 0

                app_info['delay'] = delay

                for autostart_file in self.autostart_path.glob("*.desktop"):
                    try:
                        config = configparser.ConfigParser(interpolation=None, strict=False)
                        config.read(autostart_file, encoding='utf-8')
                        if config.has_section('Desktop Entry'):
                            if config['Desktop Entry'].get('Name', '') == app_name:
                                # Preserve existing metadata
                                entry = config['Desktop Entry']
                                entry['X-GNOME-Autostart-enabled'] = 'true'
                                entry['Hidden'] = 'false'
                                
                                if delay > 0:
                                    escaped_exec = app_info['exec'].replace("'", "'\\''")
                                    entry['Exec'] = f"sh -c 'sleep {delay} && {escaped_exec}'"
                                    entry['X-GNOME-Autostart-Delay'] = str(delay)
                                else:
                                    entry['Exec'] = app_info['exec']
                                    if 'X-GNOME-Autostart-Delay' in entry:
                                        del entry['X-GNOME-Autostart-Delay']
                                
                                with open(autostart_file, 'w', encoding='utf-8') as f:
                                    config.write(f, space_around_delimiters=False)
                                break
                    except Exception as e:
                        print(f"Error updating autostart file: {e}")
                        continue

                self.filter_applications()
                self.status_var.set(f"✅ Set {delay}s delay for {app_name}")
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number")

        save_btn = tk.Button(btn_frame, text="Save",
                            bg=self.colors['success'],
                            fg=self.colors['bg_primary'],
                            font=('Segoe UI', 10, 'bold'),
                            padx=20, pady=8,
                            command=save_delay)
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel",
                              bg=self.colors['surface'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 10),
                              padx=20, pady=8,
                              command=dialog.destroy)
        cancel_btn.pack(side='left', padx=5)

    def export_config(self):
        """Export startup configuration"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Configuration",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                config = {
                    'version': '1.0',
                    'startup_apps': []
                }

                for name, info in self.applications.items():
                    if info.get('startup_enabled', False):
                        config['startup_apps'].append({
                            'name': name,
                            'exec': info['exec'],
                            'type': info.get('type', 'native'),
                            'delay': info.get('delay', 0)
                        })

                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)

                self.status_var.set(f"✅ Exported {len(config['startup_apps'])} startup apps")
                self.show_message("Success", "Configuration exported successfully!", 'success')

        except Exception as e:
            self.show_message("Error", f"Failed to export: {str(e)}", 'error')

    def import_config(self):
        """Import startup configuration"""
        try:
            filename = filedialog.askopenfilename(
                title="Import Configuration",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)

                imported = 0
                for app in config.get('startup_apps', []):
                    try:
                        app_name = app['name']
                        safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in app_name)
                        desktop_filename = f"{safe_name}.desktop"
                        autostart_file = self.autostart_path / desktop_filename

                        with open(autostart_file, 'w') as f:
                            f.write("[Desktop Entry]\n")
                            f.write("Type=Application\n")
                            f.write(f"Name={app_name}\n")

                            delay = app.get('delay', 0)
                            if delay > 0:
                                escaped_exec = app['exec'].replace("'", "'\\''")
                                f.write(f"Exec=sh -c 'sleep {delay} && {escaped_exec}'\n")
                            else:
                                f.write(f"Exec={app['exec']}\n")

                            f.write("Hidden=false\n")
                            f.write("X-GNOME-Autostart-enabled=true\n")

                            if delay > 0:
                                f.write(f"X-GNOME-Autostart-Delay={delay}\n")

                        os.chmod(autostart_file, 0o755)
                        imported += 1

                    except Exception as e:
                        print(f"Failed to import {app.get('name', 'unknown')}: {e}")

                self.load_applications()
                self.status_var.set(f"✅ Imported {imported} startup apps")
                self.show_message("Success", f"Imported {imported} applications!", 'success')

        except Exception as e:
            self.show_message("Error", f"Failed to import: {str(e)}", 'error')

    def show_message(self, title, message, msg_type='info'):
        """Show styled message box"""
        if msg_type == 'success':
            messagebox.showinfo(f"✅ {title}", message)
        elif msg_type == 'warning':
            messagebox.showwarning(f"⚠️ {title}", message)
        elif msg_type == 'error':
            messagebox.showerror(f"❌ {title}", message)
        else:
            messagebox.showinfo(f"ℹ️ {title}", message)

    def load_applications(self):
        """Load all applications"""
        self.applications = {}

        # Load native desktop applications
        for desktop_path in self.desktop_paths:
            if os.path.exists(desktop_path):
                try:
                    for desktop_file in glob.glob(f"{desktop_path}/*.desktop"):
                        try:
                            app_info = self.parse_desktop_file(desktop_file)
                            if app_info and app_info['name'] not in self.applications:
                                app_info['type'] = 'native'
                                self.applications[app_info['name']] = app_info
                        except Exception as e:
                            print(f"Error parsing {desktop_file}: {e}")
                except Exception as e:
                    print(f"Error accessing {desktop_path}: {e}")

        # Load Flatpak applications
        if self.flatpak_available:
            try:
                flatpak_apps = self.get_flatpak_apps()
                for name, app_info in flatpak_apps.items():
                    if name not in self.applications:
                        self.applications[name] = app_info
            except Exception as e:
                print(f"Error loading Flatpak apps: {e}")

        # Load Snap applications
        if self.snap_available:
            try:
                snap_apps = self.get_snap_apps()
                for name, app_info in snap_apps.items():
                    if name not in self.applications:
                        self.applications[name] = app_info
            except Exception as e:
                print(f"Error loading Snap apps: {e}")

        # Check autostart entries
        try:
            if self.autostart_path.exists():
                for autostart_file in self.autostart_path.glob("*.desktop"):
                    try:
                        config = configparser.RawConfigParser(strict=False)
                        config.read(autostart_file, encoding='utf-8')

                        if config.has_section('Desktop Entry'):
                            entry = config['Desktop Entry']
                            app_name = entry.get('Name', '').strip()
                            exec_cmd = entry.get('Exec', '').strip()

                            if not app_name or not exec_cmd:
                                continue

                            delay = 0
                            actual_exec = exec_cmd

                            if 'sh -c' in exec_cmd and 'sleep' in exec_cmd:
                                try:
                                    match = re.search(r"sh -c ['\"]sleep (\d+) && (.+)['\"]", exec_cmd)
                                    if match:
                                        delay = int(match.group(1))
                                        actual_exec = match.group(2)
                                except:
                                    pass

                            if not delay:
                                try:
                                    delay = int(entry.get('X-GNOME-Autostart-Delay', '0'))
                                except:
                                    delay = 0

                            if app_name in self.applications:
                                self.applications[app_name]['startup_enabled'] = True
                                self.applications[app_name]['delay'] = delay
                            else:
                                app_type = 'custom'
                                if 'flatpak run' in actual_exec:
                                    app_type = 'flatpak'
                                elif 'snap run' in actual_exec:
                                    app_type = 'snap'

                                self.applications[app_name] = {
                                    'name': app_name,
                                    'exec': actual_exec,
                                    'desktop_file': str(autostart_file),
                                    'startup_enabled': True,
                                    'type': app_type,
                                    'delay': delay
                                }

                    except Exception as e:
                        print(f"Error parsing autostart file {autostart_file}: {e}")
        except Exception as e:
            print(f"Error accessing autostart directory: {e}")

        # Always schedule UI updates at the end
        self.root.after(0, self.filter_applications)
        self.root.after(0, self.update_stats)

    def filter_applications(self):
        """Filter applications based on search and filter criteria"""
        if not hasattr(self, 'apps_tree'):
            return

        search_term = self.search_var.get().lower()
        if search_term == self.search_placeholder.lower():
            search_term = ""

        filter_type = self.filter_var.get()

        self.filtered_apps = {}

        for name, info in self.applications.items():
            if search_term and not (search_term in name.lower() or
                                   search_term in info['exec'].lower() or
                                   search_term in info.get('type', '').lower()):
                continue

            if filter_type == "enabled" and not info.get('startup_enabled', False):
                continue
            elif filter_type == "disabled" and info.get('startup_enabled', False):
                continue
            elif filter_type in ["native", "flatpak", "snap", "custom"] and info.get('type') != filter_type:
                continue

            self.filtered_apps[name] = info

        self.populate_tree()
        self.update_stats()

    def populate_tree(self):
        """Populate tree view with filtered applications"""
        self.apps_tree.delete(*self.apps_tree.get_children())

        for name, info in sorted(self.filtered_apps.items()):
            if info.get('startup_enabled', False):
                status = "🟢 Enabled"
            else:
                status = "⚪ Disabled"

            app_type = info.get('type', 'native')
            type_display = {
                'flatpak': '📦 Flatpak',
                'snap': '📦 Snap',
                'custom': '⚙️ Custom',
                'native': '🖥️ Native'
            }.get(app_type, '🖥️ Native')

            icon = info.get('icon') or self.get_app_icon(info['exec'])
            display_name = f"{icon} {name}"

            delay = info.get('delay', 0)
            delay_display = f"{delay}s" if delay > 0 else "-"

            exec_display = info['exec'][:50] + "..." if len(info['exec']) > 50 else info['exec']

            self.apps_tree.insert('', 'end', text=display_name,
                                values=(status, type_display, exec_display, delay_display))

    def update_stats(self):
        """Update statistics display"""
        total = len(self.filtered_apps)
        enabled = sum(1 for app in self.filtered_apps.values()
                     if app.get('startup_enabled', False))

        type_counts = {}
        for app in self.filtered_apps.values():
            app_type = app.get('type', 'native')
            type_counts[app_type] = type_counts.get(app_type, 0) + 1

        stats_parts = [f"📊 {enabled}/{total} enabled"]

        if type_counts:
            type_stats = []
            if type_counts.get('flatpak'):
                type_stats.append(f"{type_counts['flatpak']} Flatpak")
            if type_counts.get('snap'):
                type_stats.append(f"{type_counts['snap']} Snap")
            if type_counts.get('custom'):
                type_stats.append(f"{type_counts['custom']} Custom")

            if type_stats:
                stats_parts.append(", ".join(type_stats))

        self.stats_label.configure(text=" • ".join(stats_parts))

    def get_app_icon(self, exec_cmd):
        """Get icon based on application type"""
        exec_lower = exec_cmd.lower()

        icon_map = {
            ('firefox', 'chrome', 'browser', 'web'): "🌐",
            ('code', 'editor', 'vim', 'atom', 'sublime', 'gedit'): "💻",
            ('music', 'audio', 'sound', 'spotify', 'rhythmbox'): "🎵",
            ('video', 'player', 'movie', 'vlc', 'mpv'): "🎬",
            ('chat', 'message', 'discord', 'slack', 'telegram', 'signal'): "💬",
            ('terminal', 'konsole', 'gnome-terminal', 'kitty', 'alacritty'): "⚡",
            ('file', 'manager', 'nautilus', 'dolphin', 'thunar'): "📁",
            ('steam', 'game', 'gaming', 'lutris'): "🎮",
            ('mail', 'thunderbird', 'evolution'): "✉️",
            ('image', 'photo', 'gimp', 'inkscape', 'krita'): "🎨",
            ('office', 'libreoffice', 'writer', 'calc'): "📄",
            ('torrent', 'transmission', 'qbittorrent'): "📥",
            ('snap run',): "📦",
            ('flatpak run',): "📦",
        }

        for keywords, icon in icon_map.items():
            if any(term in exec_lower for term in keywords):
                return icon

        return "⚙️"

    def parse_desktop_file(self, file_path):
        """Parse desktop file"""
        try:
            config = configparser.RawConfigParser(strict=False)
            config.read(file_path, encoding='utf-8')

            if 'Desktop Entry' not in config:
                return None

            entry = config['Desktop Entry']

            if entry.get('Type', '') != 'Application':
                return None
            if entry.get('NoDisplay', '').lower() == 'true':
                return None
            if entry.get('Hidden', '').lower() == 'true':
                return None

            name = entry.get('Name', os.path.basename(file_path).replace('.desktop', ''))
            exec_cmd = entry.get('Exec', '')

            if not exec_cmd:
                return None

            # Clean exec command (remove field codes)
            exec_cmd = exec_cmd.replace('%F', '').replace('%f', '')
            exec_cmd = exec_cmd.replace('%U', '').replace('%u', '')
            exec_cmd = exec_cmd.replace('%d', '').replace('%D', '')
            exec_cmd = exec_cmd.replace('%n', '').replace('%N', '')
            exec_cmd = exec_cmd.replace('%i', '').replace('%c', '')
            exec_cmd = exec_cmd.replace('%k', '').replace('%v', '')
            exec_cmd = exec_cmd.strip()

            return {
                'name': name,
                'exec': exec_cmd,
                'desktop_file': file_path,
                'startup_enabled': False,
                'delay': 0,
                'icon_name': entry.get('Icon', '')
            }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    def get_selected_app(self):
        """Get currently selected application"""
        selection = self.apps_tree.selection()
        if not selection:
            self.show_message("No Selection", "Please select an application first.", 'warning')
            return None

        item = self.apps_tree.item(selection[0])
        app_name = self.extract_app_name(item['text'])

        app_info = self.filtered_apps.get(app_name, self.applications.get(app_name))

        if not app_info:
            self.show_message("Error", "Application not found.", 'error')
            return None

        return app_name, app_info

    def add_custom_app(self):
        """Add custom application"""
        try:
            dialog = ModernCustomAppDialog(self.root, self.colors, self.flatpak_available, self.snap_available)
            self.root.wait_window(dialog.dialog)
            if dialog.result:
                app_name, exec_cmd, app_type, delay = dialog.result

                try:
                    safe_name = "".join(c if c.isalnum() or c in '-_' else '_' for c in app_name)
                    desktop_filename = f"{safe_name}.desktop"
                    autostart_file = self.autostart_path / desktop_filename

                    if autostart_file.exists():
                        result = messagebox.askyesno("File Exists",
                                                    f"A startup entry with similar name already exists.\n"
                                                    f"Do you want to overwrite it?")
                        if not result:
                            return

                    with open(autostart_file, 'w', encoding='utf-8') as f:
                        f.write("[Desktop Entry]\n")
                        f.write("Type=Application\n")
                        f.write(f"Name={app_name}\n")

                        if delay > 0:
                            escaped_exec = exec_cmd.replace("'", "'\\''")
                            f.write(f"Exec=sh -c 'sleep {delay} && {escaped_exec}'\n")
                        else:
                            f.write(f"Exec={exec_cmd}\n")

                        f.write("Hidden=false\n")
                        f.write("X-GNOME-Autostart-enabled=true\n")

                        if app_type == 'flatpak':
                            f.write("Comment=Custom Flatpak Application\n")
                        elif app_type == 'snap':
                            f.write("Comment=Custom Snap Application\n")
                        else:
                            f.write("Comment=Custom Application\n")

                        if delay > 0:
                            f.write(f"X-GNOME-Autostart-Delay={delay}\n")

                    os.chmod(autostart_file, 0o755)

                    self.applications[app_name] = {
                        'name': app_name,
                        'exec': exec_cmd,
                        'desktop_file': str(autostart_file),
                        'startup_enabled': True,
                        'type': app_type,
                        'delay': delay
                    }

                    self.filter_applications()
                    self.status_var.set(f"✅ Added custom app {app_name}")
                    self.show_message("Success", f"Custom application {app_name} has been added!", 'success')

                except Exception as e:
                    self.show_message("Error", f"Failed to add custom application: {str(e)}", 'error')
        except Exception as e:
            print(f"Error opening custom app dialog: {e}")

    def open_autostart_folder(self):
        """Open autostart folder"""
        try:
            folder_path = str(self.autostart_path)
            if os.path.exists(folder_path):
                # Try xdg-open first as it's more reliable for folders on Linux
                try:
                    subprocess.Popen(['xdg-open', folder_path], 
                                   start_new_session=True,
                                   stderr=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL)
                    self.status_var.set("📁 Opened autostart folder")
                except Exception:
                    # Fallback to webbrowser if xdg-open fails
                    webbrowser.open(folder_path)
                    self.status_var.set("📁 Opened autostart folder (fallback)")
            else:
                self.show_message("Error", "Autostart folder does not exist.", 'error')
        except Exception as e:
            self.show_message("Error", f"Failed to open folder: {str(e)}", 'error')


class ModernCustomAppDialog:
    def __init__(self, parent, colors, flatpak_available=False, snap_available=False):
        self.result = None
        self.colors = colors
        self.flatpak_available = flatpak_available
        self.snap_available = snap_available

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🚀 Add Custom Application")
        self.dialog.geometry("690x750")
        self.dialog.configure(bg=self.colors['bg_primary'])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)

        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - 345
        y = (self.dialog.winfo_screenheight() // 2) - 375
        self.dialog.geometry(f"+{x}+{y}")

        self.setup_dialog()

    def setup_dialog(self):
        """Setup dialog UI"""
        # Outer container with fixed pads
        main_frame = tk.Frame(self.dialog, bg=self.colors['bg_primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # 1. Header (pinned to top)
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        header_frame.pack(fill='x', side='top', pady=(0, 15))

        tk.Label(header_frame, text="➕ Add Custom Application",
                 font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack()

        subtitle_text = "Create a custom startup entry for any application or script"
        if self.flatpak_available or self.snap_available:
            subtitle_text += "\n(including package managers)"

        tk.Label(header_frame, text=subtitle_text, font=('Segoe UI', 10),
                 bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack(pady=(5, 0))

        # 2. Buttons (pinned to bottom)
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        button_frame.pack(fill='x', side='bottom', pady=(15, 0))

        cancel_btn = tk.Button(button_frame, text="❌ Cancel",
                              font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['surface'], fg=self.colors['text_primary'],
                              relief='flat', bd=0, padx=25, pady=10,
                              cursor='hand2', command=self.cancel)
        cancel_btn.pack(side='right', padx=(10, 0))

        add_btn = tk.Button(button_frame, text="✅ Add Application",
                           font=('Segoe UI', 11, 'bold'),
                           bg=self.colors['success'], fg=self.colors['bg_primary'],
                           relief='flat', bd=0, padx=25, pady=10,
                           cursor='hand2', command=self.add_app)
        add_btn.pack(side='right')

        # 3. Form (middle, expanding)
        form_frame = tk.Frame(main_frame, bg=self.colors['bg_secondary'], relief='flat', bd=0)
        form_frame.pack(fill='both', expand=True)

        # We can use a Canvas + Frame for scrolling if it's too tight, 
        # but let's first try just better packing
        form_content = tk.Frame(form_frame, bg=self.colors['bg_secondary'])
        form_content.pack(fill='both', expand=True, padx=25, pady=15)

        # Name
        tk.Label(form_content, text="� Application Name:", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(form_content, textvariable=self.name_var, font=('Segoe UI', 11),
                             bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                             insertbackground=self.colors['accent'], relief='flat', bd=8)
        name_entry.pack(fill='x', pady=(0, 15), ipady=5)

        # Type Selection
        if self.flatpak_available or self.snap_available:
            tk.Label(form_content, text="📦 Application Type:", font=('Segoe UI', 11, 'bold'),
                     bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
            
            type_frame = tk.Frame(form_content, bg=self.colors['bg_secondary'])
            type_frame.pack(fill='x', pady=(0, 15))
            self.app_type_var = tk.StringVar(value="native")

            types = [("🖥️ Native", "native")]
            if self.flatpak_available: types.append(("📦 Flatpak", "flatpak"))
            if self.snap_available: types.append(("📦 Snap", "snap"))

            for text, val in types:
                tk.Radiobutton(type_frame, text=text, variable=self.app_type_var, value=val,
                               bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                               selectcolor=self.colors['bg_tertiary'], font=('Segoe UI', 10)).pack(side='left', padx=(0, 15))
        else:
            self.app_type_var = tk.StringVar(value="native")

        # Command
        tk.Label(form_content, text="💻 Command to execute:", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
        cmd_frame = tk.Frame(form_content, bg=self.colors['bg_secondary'])
        cmd_frame.pack(fill='x', pady=(0, 15))
        
        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(cmd_frame, textvariable=self.cmd_var, font=('Segoe UI', 11),
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                 insertbackground=self.colors['accent'], relief='flat', bd=8)
        self.cmd_entry.pack(side='left', fill='x', expand=True, ipady=5, padx=(0, 10))

        browse_btn = tk.Button(cmd_frame, text="📁 Browse", font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['accent'], fg='white', relief='flat', 
                              padx=15, pady=5, cursor='hand2', command=self.browse_command)
        browse_btn.pack(side='right')

        # Delay
        tk.Label(form_content, text="⏱️ Startup Delay (seconds):", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['bg_secondary'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
        self.delay_var = tk.StringVar(value="0")
        tk.Entry(form_content, textvariable=self.delay_var, font=('Segoe UI', 11),
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                 insertbackground=self.colors['accent'], relief='flat', bd=8).pack(fill='x', ipady=5)

        # Help
        help_texts = ["💡 Examples: /usr/bin/firefox, python3 /path/to/script.py"]
        help_label = tk.Label(form_content, text="\n".join(help_texts), font=('Segoe UI', 9),
                             bg=self.colors['bg_secondary'], fg=self.colors['surface'], justify='left')
        help_label.pack(anchor='w', pady=(10, 0))

        # Hover effects
        def bind_hover(btn, normal_bg, hover_bg, normal_fg, hover_fg):
            btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg, fg=hover_fg))
            btn.bind("<Leave>", lambda e: btn.configure(bg=normal_bg, fg=normal_fg))

        bind_hover(add_btn, self.colors['success'], '#94e2d5', self.colors['bg_primary'], self.colors['bg_primary'])
        bind_hover(cancel_btn, self.colors['surface'], self.colors['bg_tertiary'], self.colors['text_primary'], self.colors['text_primary'])
        bind_hover(browse_btn, self.colors['accent'], self.colors['accent_hover'], 'white', 'white')

        name_entry.focus()
        self.dialog.bind('<Return>', lambda e: self.add_app())
        self.dialog.bind('<Escape>', lambda e: self.cancel())

    def browse_command(self):
        """Browse for executable file"""
        filename = filedialog.askopenfilename(
            title="Select Executable File",
            filetypes=[
                ("All files", "*"),
                ("Executable files", "*.sh"),
                ("Python files", "*.py"),
                ("Binary files", "*.bin"),
                ("Application files", "*.app")
            ]
        )
        if filename:
            self.cmd_var.set(filename)

    def add_app(self):
        """Add the custom application with validation"""
        name = self.name_var.get().strip()
        cmd = self.cmd_var.get().strip()
        app_type = self.app_type_var.get()

        try:
            delay = int(self.delay_var.get())
            if delay < 0:
                delay = 0
        except ValueError:
            delay = 0

        if not name:
            messagebox.showwarning("⚠️ Missing Information",
                                 "Please provide an application name.")
            return

        if not cmd:
            messagebox.showwarning("⚠️ Missing Information",
                                 "Please provide a command to execute.")
            return

        if app_type == 'flatpak' and not cmd.startswith('flatpak run '):
            result = messagebox.askyesno("⚠️ Command Format",
                                       "Flatpak commands should start with 'flatpak run '.\n\n"
                                       "Do you want to add 'flatpak run ' to the beginning?")
            if result:
                cmd = f"flatpak run {cmd}"

        if app_type == 'snap' and not cmd.startswith('snap run '):
            result = messagebox.askyesno("⚠️ Command Format",
                                       "Snap commands should start with 'snap run '.\n\n"
                                       "Do you want to add 'snap run ' to the beginning?")
            if result:
                cmd = f"snap run {cmd}"

        if app_type == 'native':
            cmd_parts = cmd.split()
            if cmd_parts and not (os.path.exists(cmd_parts[0]) or self.command_exists(cmd_parts[0])):
                result = messagebox.askyesno("⚠️ Command Not Found",
                                           f"The command '{cmd_parts[0]}' was not found in your system.\n\n"
                                           f"Do you want to add it anyway?")
                if not result:
                    return

        self.result = (name, cmd, app_type, delay)
        self.dialog.destroy()

    def command_exists(self, command):
        """Check if command exists in PATH"""
        try:
            subprocess.run(['which', command],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk(className='startup-manager')

    try:
        icon_img = tk.PhotoImage(width=16, height=16)
        icon_img.put('#89b4fa', (0, 0, 16, 16))
        root.iconphoto(True, icon_img)
    except:
        pass

    app = ModernStartupManager(root)

    root.minsize(900, 650)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()
