#!/bin/sh
# Compila Wick.app (universal: Apple Silicon + Intel, macOS 13+).
#   ./build.sh          → Wick.app
#   ./build.sh --zip    → además Wick.zip para una release
set -eu
cd "$(dirname "$0")"

APP="Wick.app"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp Info.plist "$APP/Contents/Info.plist"
cp Resources/AppIcon.icns "$APP/Contents/Resources/AppIcon.icns"
cp -R Resources/mascot "$APP/Contents/Resources/mascot"
cp -R Resources/menubar "$APP/Contents/Resources/menubar"

TMP="$(mktemp -d)"
swiftc -Osize -target arm64-apple-macos13 Sources/*.swift -o "$TMP/arm64"
swiftc -Osize -target x86_64-apple-macos13 Sources/*.swift -o "$TMP/x86_64"
strip -x "$TMP/arm64" "$TMP/x86_64"
lipo -create "$TMP/arm64" "$TMP/x86_64" -output "$APP/Contents/MacOS/Wick"
rm -rf "$TMP"

codesign --force --sign - "$APP" >/dev/null 2>&1 || true

if [ "${1:-}" = "--zip" ]; then
	rm -f Wick.zip
	ditto -c -k --keepParent "$APP" Wick.zip
	echo "Listo: $APP y Wick.zip"
else
	echo "Listo: $APP"
fi
