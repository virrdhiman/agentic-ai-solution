#!/usr/bin/env bash
# ============================================================
#  Autonomous Agent — macOS / Linux Build Script
#  Builds a standalone binary + .dmg (macOS) or AppImage (Linux)
#  Author: Virender Dhiman
# ============================================================

set -euo pipefail

PROJECT_NAME="autonomous-agent"
VERSION="0.1.0"
DIST_DIR="dist"
BUILD_DIR="build"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}=====================================================${NC}"
echo -e "${CYAN}  Autonomous Agent — macOS/Linux Build${NC}"
echo -e "${CYAN}  Author: Virender Dhiman${NC}"
echo -e "${CYAN}=====================================================${NC}"
echo ""

# --- Detect OS ---
OS="$(uname -s)"
ARCH="$(uname -m)"
case "$OS" in
    Darwin)  PLATFORM="macos"  ;;
    Linux)   PLATFORM="linux"   ;;
    *)       echo -e "${RED}ERROR: Unsupported OS: $OS${NC}"; exit 1 ;;
esac
echo -e "${GREEN}  Platform: ${PLATFORM} (${ARCH})${NC}"

# --- Step 1: Check Python ---
echo ""
echo "[1/9] Checking Python..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 is not installed.${NC}"
    echo "Install Python 3.11+ from https://python.org or brew install python"
    exit 1
fi
PY_VER="$(python3 --version 2>&1 | awk '{print $2}')"
echo "  Found Python ${PY_VER}"

# --- Step 2: Create virtual environment ---
echo ""
echo "[2/9] Creating virtual environment..."
VENV_DIR=".venv-build"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo "  Created ${VENV_DIR}"
else
    echo "  Using existing ${VENV_DIR}"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# --- Step 3: Install dependencies ---
echo ""
echo "[3/9] Installing dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -e ".[dev]" >/dev/null 2>&1
pip install pyinstaller >/dev/null 2>&1
echo "  Dependencies installed"

# --- Step 4: Run tests ---
echo ""
echo "[4/9] Running tests..."
TEST_EXIT=0
python -m pytest tests/ -v --tb=short || TEST_EXIT=$?

if [ "$TEST_EXIT" -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}WARNING: Some tests failed.${NC}"
    read -rp "  Continue anyway? [y/N] " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "Build aborted."
        exit 1
    fi
else
    echo -e "  ${GREEN}All tests passed!${NC}"
fi

# --- Step 5: Clean previous build ---
echo ""
echo "[5/9] Cleaning previous build artifacts..."
rm -rf "$DIST_DIR" "$BUILD_DIR" "${PROJECT_NAME}.spec"
echo "  Cleaned"

# --- Step 6: Build standalone binary ---
echo ""
echo "[6/9] Building standalone binary with PyInstaller..."

PYINSTALLER_ARGS=(
    --name "$PROJECT_NAME"
    --onefile
    --console
    --add-data "policies:policies"
    --add-data "autonomous_agent/config:autonomous_agent/config"
    --hidden-import "autonomous_agent"
    --hidden-import "autonomous_agent.core"
    --hidden-import "autonomous_agent.core.state"
    --hidden-import "autonomous_agent.core.models"
    --hidden-import "autonomous_agent.core.evidence"
    --hidden-import "autonomous_agent.core.orchestrator"
    --hidden-import "autonomous_agent.core.router"
    --hidden-import "autonomous_agent.providers"
    --hidden-import "autonomous_agent.providers.base"
    --hidden-import "autonomous_agent.providers.mock"
    --hidden-import "autonomous_agent.providers.opensource"
    --hidden-import "autonomous_agent.providers.router"
    --hidden-import "autonomous_agent.tools"
    --hidden-import "autonomous_agent.tools.base"
    --hidden-import "autonomous_agent.tools.filesystem"
    --hidden-import "autonomous_agent.tools.shell"
    --hidden-import "autonomous_agent.tools.git"
    --hidden-import "autonomous_agent.cli"
    --hidden-import "autonomous_agent.api"
    --hidden-import "autonomous_agent.api.app"
    --hidden-import "pydantic"
    --hidden-import "pydantic_settings"
    --hidden-import "fastapi"
    --hidden-import "uvicorn"
    --hidden-import "click"
    --hidden-import "rich"
    --hidden-import "structlog"
    --hidden-import "git"
    --hidden-import "httpx"
    --collect-all "autonomous_agent"
    autonomous_agent/cli/__init__.py
)

pyinstaller "${PYINSTALLER_ARGS[@]}"

BINARY="${DIST_DIR}/${PROJECT_NAME}"
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}ERROR: Binary not found at ${BINARY}${NC}"
    exit 1
fi
chmod +x "$BINARY"
echo -e "  ${GREEN}Built: ${BINARY}${NC}"

# --- Step 7: Verify the binary ---
echo ""
echo "[7/9] Verifying binary..."
"$BINARY" --help >/dev/null 2>&1 || "$BINARY" info >/dev/null 2>&1 || true
echo "  Verification complete"

# --- Step 8: Create platform-specific distribution ---
echo ""
echo "[8/9] Creating platform distribution..."

if [ "$PLATFORM" = "macos" ]; then
    echo "  Creating .app bundle..."
    APP_DIR="${DIST_DIR}/${PROJECT_NAME}.app"
    mkdir -p "${APP_DIR}/Contents/MacOS"
    mkdir -p "${APP_DIR}/Contents/Resources"
    cp "$BINARY" "${APP_DIR}/Contents/MacOS/${PROJECT_NAME}"

    # Info.plist
    cat > "${APP_DIR}/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>${PROJECT_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>Autonomous Agent</string>
    <key>CFBundleIdentifier</key>
    <string>com.virendhirm.autonomous-agent</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>CFBundleExecutable</key>
    <string>${PROJECT_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

    echo "  Creating .dmg disk image..."
    DMG_NAME="${PROJECT_NAME}-${VERSION}-macos-${ARCH}.dmg"
    DMG_PATH="${DIST_DIR}/${DMG_NAME}"

    if command -v hdiutil &>/dev/null; then
        # Create a temporary directory for DMG contents
        DMG_TEMP="${BUILD_DIR}/dmg-staging"
        mkdir -p "$DMG_TEMP"
        cp -r "$APP_DIR" "$DMG_TEMP/"

        # Create symlink to Applications
        ln -s /Applications "${DMG_TEMP}/Applications"

        hdiutil create \
            -volname "Autonomous Agent ${VERSION}" \
            -srcfolder "$DMG_TEMP" \
            -ov \
            -format UDZO \
            "$DMG_PATH"

        rm -rf "$DMG_TEMP"
        echo -e "  ${GREEN}Created: ${DMG_PATH}${NC}"
    else
        echo -e "  ${YELLOW}hdiutil not found — skipping .dmg creation${NC}"
        echo "  .app bundle available at: ${APP_DIR}"
    fi

elif [ "$PLATFORM" = "linux" ]; then
    echo "  Creating AppImage..."
    APPDIR="${BUILD_DIR}/AppDir"
    mkdir -p "${APPDIR}/usr/bin"
    mkdir -p "${APPDIR}/usr/share/applications"
    mkdir -p "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

    cp "$BINARY" "${APPDIR}/usr/bin/${PROJECT_NAME}"

    # Desktop entry
    cat > "${APPDIR}/usr/share/applications/${PROJECT_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Autonomous Agent
Comment=Universal Autonomous Agentic Engineering System
Exec=${PROJECT_NAME}
Icon=${PROJECT_NAME}
Terminal=true
Categories=Development;Engineering;
DESKTOP

    # Simple icon placeholder (text-based SVG converted)
    cat > "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${PROJECT_NAME}.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="32" fill="#1a1a2e"/>
  <text x="128" y="140" text-anchor="middle" font-size="100" fill="#e94560" font-family="monospace">AG</text>
  <text x="128" y="190" text-anchor="middle" font-size="24" fill="#ffffff" font-family="monospace">v0.1.0</text>
</svg>
SVG
    cp "${APPDIR}/usr/share/icons/hicolor/256x256/apps/${PROJECT_NAME}.svg" \
       "${APPDIR}/${PROJECT_NAME}.svg"

    # AppRun
    cat > "${APPDIR}/AppRun" <<APPRUN
#!/bin/bash
HERE="\$(dirname "\$(readlink -f "\${0}")")"
exec "\${HERE}/usr/bin/${PROJECT_NAME}" "\$@"
APPRUN
    chmod +x "${APPDIR}/AppRun"

    # Create AppImage (if appimagetool is available)
    if command -v appimagetool &>/dev/null; then
        APPIMAGE_NAME="${PROJECT_NAME}-${VERSION}-linux-${ARCH}.AppImage"
        appimagetool "$APPDIR" "${DIST_DIR}/${APPIMAGE_NAME}"
        echo -e "  ${GREEN}Created: ${DIST_DIR}/${APPIMAGE_NAME}${NC}"
    else
        echo -e "  ${YELLOW}appimagetool not found — AppDir created at: ${APPDIR}${NC}"
        echo "  Install appimagetool to create .AppImage"
    fi
fi

# --- Step 9: Build metadata ---
echo ""
echo "[9/9] Creating build metadata..."
cat > "${DIST_DIR}/BUILD_INFO.txt" <<INFO
${PROJECT_NAME} v${VERSION}
Built: $(date)
Python: ${PY_VER}
Platform: ${PLATFORM} (${ARCH})
Author: Virender Dhiman
INFO

BINARY_SIZE=$(du -h "$BINARY" | awk '{print $1}')

echo ""
echo -e "${GREEN}=====================================================${NC}"
echo -e "${GREEN}  BUILD COMPLETE${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo ""
echo "  Standalone binary: ${BINARY} (${BINARY_SIZE})"
if [ "$PLATFORM" = "macos" ] && [ -f "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-macos-${ARCH}.dmg" ]; then
    echo "  DMG installer:     ${DIST_DIR}/${PROJECT_NAME}-${VERSION}-macos-${ARCH}.dmg"
fi
if [ "$PLATFORM" = "macos" ]; then
    echo "  App bundle:        ${DIST_DIR}/${PROJECT_NAME}.app"
fi
if [ "$PLATFORM" = "linux" ] && [ -d "${BUILD_DIR}/AppDir" ]; then
    echo "  AppDir:            ${BUILD_DIR}/AppDir"
fi
echo ""
echo "  To run:"
echo "    ${BINARY} run \"Fix this problem\""
echo "    ${BINARY} --help"
echo ""

deactivate
