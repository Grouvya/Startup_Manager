#!/bin/bash
set -e

APP_NAME="startup-manager"
VERSION="1.0.0"
APP_DIR="AppDir"
DEB_DIR="deb_package"

echo "🚀 Starting build process for $APP_NAME v$VERSION..."

# 1. Build binary with PyInstaller
echo "📦 Building binary with PyInstaller..."
./venv/bin/pyinstaller --noconfirm --onefile --windowed \
    --name "$APP_NAME" \
    --add-data "Startup_Manager.py:." \
    --add-data "build_assets/icon.png:build_assets" \
    Startup_Manager.py

# 2. Prepare AppImage (AppDir)
echo "📁 Preparing AppDir structure..."
mkdir -p $APP_DIR/usr/bin
mkdir -p $APP_DIR/usr/share/applications
mkdir -p $APP_DIR/usr/share/icons/hicolor/256x256/apps

cp dist/$APP_NAME $APP_DIR/usr/bin/
cp build_assets/startup-manager.desktop $APP_DIR/usr/share/applications/
cp build_assets/icon.png $APP_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png
cp build_assets/icon.png $APP_DIR/.DirIcon
ln -sf usr/share/icons/hicolor/256x256/apps/$APP_NAME.png $APP_DIR/$APP_NAME.png
ln -sf usr/share/applications/startup-manager.desktop $APP_DIR/

# AppRun script
cat <<EOF > $APP_DIR/AppRun
#!/bin/sh
SELF=\$(readlink -f "\$0")
HERE=\$(dirname "\$SELF")
export PATH="\$HERE/usr/bin:\$PATH"
exec "$APP_NAME" "\$@"
EOF
chmod +x $APP_DIR/AppRun

# 3. Prepare DEB Package
echo "📦 Preparing .deb package structure..."
mkdir -p $DEB_DIR/DEBIAN
mkdir -p $DEB_DIR/usr/bin
mkdir -p $DEB_DIR/usr/share/applications
mkdir -p $DEB_DIR/usr/share/icons/hicolor/256x256/apps

cat <<EOF > $DEB_DIR/DEBIAN/control
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Grouvya <grouvya@gmail.com>
Description: A modern startup manager for Linux
 Manage your system startup applications (Native, Flatpak, Snap).
EOF

cp dist/$APP_NAME $DEB_DIR/usr/bin/
cp build_assets/startup-manager.desktop $DEB_DIR/usr/share/applications/
cp build_assets/icon.png $DEB_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png

# Copy debian scripts and templates
cp build_assets/templates $DEB_DIR/DEBIAN/
cp build_assets/config $DEB_DIR/DEBIAN/
cp build_assets/postinst $DEB_DIR/DEBIAN/
cp build_assets/prerm $DEB_DIR/DEBIAN/

# Set permissions for debian scripts
chmod 755 $DEB_DIR/DEBIAN/config
chmod 755 $DEB_DIR/DEBIAN/postinst
chmod 755 $DEB_DIR/DEBIAN/prerm
chmod 644 $DEB_DIR/DEBIAN/templates

echo "🔨 Building .deb package..."
dpkg-deb --build $DEB_DIR "${APP_NAME}_${VERSION}_amd64.deb"

echo "✅ Build complete!"
echo "📍 DEB: ${APP_NAME}_${VERSION}_amd64.deb"
echo "📍 AppImage structure ready in $APP_DIR (Use appimagetool to finalize if available)"
