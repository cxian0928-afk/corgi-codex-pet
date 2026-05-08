#!/bin/sh
set -eu

PACKAGE_DIR=""
CODEX_HOME_VALUE="${CODEX_HOME:-}"
SKIP_BACKUP=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --package-dir)
      PACKAGE_DIR="${2:-}"
      shift 2
      ;;
    --codex-home)
      CODEX_HOME_VALUE="${2:-}"
      shift 2
      ;;
    --skip-backup)
      SKIP_BACKUP=1
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

if [ -z "$PACKAGE_DIR" ]; then
  PACKAGE_DIR="$REPO_ROOT/build/package"
fi

if [ -z "$CODEX_HOME_VALUE" ]; then
  CODEX_HOME_VALUE="$HOME/.codex"
fi

PACKAGE_DIR="$(cd "$PACKAGE_DIR" && pwd)"
CODEX_HOME_VALUE="$(mkdir -p "$CODEX_HOME_VALUE" && cd "$CODEX_HOME_VALUE" && pwd)"

PET_JSON="$PACKAGE_DIR/pet.json"
SPRITESHEET="$PACKAGE_DIR/spritesheet.webp"

if [ ! -f "$PET_JSON" ]; then
  echo "Missing pet.json in package directory: $PET_JSON" >&2
  echo "Please run: python scripts/build_pet_package.py" >&2
  exit 1
fi

if [ ! -f "$SPRITESHEET" ]; then
  echo "Missing spritesheet.webp in package directory: $SPRITESHEET" >&2
  echo "Please run: python scripts/build_pet_package.py" >&2
  exit 1
fi

PET_ID="$(python - <<'PY' "$PET_JSON"
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data.get('id', ''))
PY
)"

PET_NAME="$(python - <<'PY' "$PET_JSON"
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data.get('displayName', ''))
PY
)"

if [ -z "$PET_ID" ]; then
  echo "pet.json is missing a pet id." >&2
  exit 1
fi

PETS_ROOT="$CODEX_HOME_VALUE/pets"
TARGET_DIR="$PETS_ROOT/$PET_ID"
BACKUP_ROOT="$CODEX_HOME_VALUE/pets-backups"

echo "[corgi-pet] Package directory: $PACKAGE_DIR"
echo "[corgi-pet] Codex home: $CODEX_HOME_VALUE"
echo "[corgi-pet] Target pet id: $PET_ID"

mkdir -p "$PETS_ROOT"

case "$TARGET_DIR" in
  "$CODEX_HOME_VALUE"/*) ;;
  *)
    echo "Refusing to modify path outside Codex home: $TARGET_DIR" >&2
    exit 1
    ;;
esac

if [ -d "$TARGET_DIR" ] && [ "$SKIP_BACKUP" -ne 1 ]; then
  mkdir -p "$BACKUP_ROOT"
  TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
  BACKUP_DIR="$BACKUP_ROOT/$PET_ID-$TIMESTAMP"
  echo "[corgi-pet] Backing up existing install to: $BACKUP_DIR"
  cp -R "$TARGET_DIR" "$BACKUP_DIR"
fi

if [ -d "$TARGET_DIR" ]; then
  echo "[corgi-pet] Removing previous install"
  rm -rf "$TARGET_DIR"
fi

echo "[corgi-pet] Copying new pet package"
cp -R "$PACKAGE_DIR" "$TARGET_DIR"

if [ ! -f "$TARGET_DIR/pet.json" ] || [ ! -f "$TARGET_DIR/spritesheet.webp" ]; then
  echo "Install completed but expected files were not found in $TARGET_DIR" >&2
  exit 1
fi

echo
echo "Install complete."
echo "Pet name: $PET_NAME"
echo "Installed to: $TARGET_DIR"
echo "Restart or refresh Codex if the pet is already open."
