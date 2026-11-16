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

# Sin atributos extendidos (Finder, cuarentena…): romperían la firma
xattr -cr "$APP"

# Firma: Developer ID de Cometa si está en el llavero (o WICK_SIGN_ID), si no, firma local.
SIGN_ID="${WICK_SIGN_ID:-$(security find-identity -v -p codesigning | sed -n 's/.*"\(Developer ID Application: [^"]*\)".*/\1/p' | head -n 1)}"
if [ -n "$SIGN_ID" ]; then
	codesign --force --options runtime --timestamp --entitlements Wick.entitlements --sign "$SIGN_ID" "$APP"
	echo "Firmada con: $SIGN_ID"
else
	codesign --force --sign - "$APP"
	echo "Sin Developer ID: firma local (macOS pedirá «Abrir igualmente»)"
fi

if [ "${1:-}" = "--dmg" ]; then
	# Wick.dmg: ventana con la app y un acceso a Aplicaciones (requiere .venv-dmg con dmgbuild)
	[ -x .venv-dmg/bin/dmgbuild ] || { python3 -m venv .venv-dmg && .venv-dmg/bin/pip install -q dmgbuild; }
	python3 art/dmg.py >/dev/null
	rm -f Wick.dmg
	.venv-dmg/bin/dmgbuild -s art/dmg-settings.py -D app="$PWD/$APP" "Wick" Wick.dmg >/dev/null
	[ -n "$SIGN_ID" ] && codesign --force --timestamp --sign "$SIGN_ID" Wick.dmg
	# Notarización (quita el aviso de macOS). Necesita un perfil guardado una vez con:
	#   xcrun notarytool store-credentials wick-notary --apple-id <correo> --team-id 9B9HGFXXJD
	if [ -n "$SIGN_ID" ] && xcrun notarytool history --keychain-profile wick-notary >/dev/null 2>&1; then
		xcrun notarytool submit Wick.dmg --keychain-profile wick-notary --wait
		xcrun stapler staple Wick.dmg
		echo "Notarizado"
	else
		echo "Sin notarizar (falta el perfil wick-notary)"
	fi
	echo "Listo: $APP y Wick.dmg"
elif [ "${1:-}" = "--zip" ]; then
	rm -f Wick.zip
	ditto -c -k --keepParent "$APP" Wick.zip
	echo "Listo: $APP y Wick.zip"
else
	echo "Listo: $APP"
fi
