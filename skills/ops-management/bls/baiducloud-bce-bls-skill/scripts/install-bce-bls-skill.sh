#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_LOCAL_ZIP="${SKILL_DIR}/assets/bce-bls.zip"
DEFAULT_DOWNLOAD_URL="https://bls-skill.bj.bcebos.com/latest/bce-bls.zip"
LOCAL_ZIP="${BCE_BLS_SKILL_ZIP:-${BLS_SKILL_ZIP:-}}"
DOWNLOAD_URL="${BCE_BLS_SKILL_URL:-${BLS_SKILL_URL:-}}"
TARGET_DIR="${1:-${BCE_BLS_SKILLS_DIR:-${BLS_SKILLS_DIR:-${BCE_SKILLS_DIR:-}}}}"

usage() {
  cat <<'EOF'
Usage:
  install-bce-bls-skill.sh <target-skills-dir>

Environment:
  BCE_BLS_SKILL_ZIP   Use a local bce-bls.zip package.
  BCE_BLS_SKILL_URL   Override the official bce-bls.zip URL.
  BCE_BLS_SKILLS_DIR  Target skills directory when no positional argument is given.
  BLS_SKILL_*         Legacy aliases for the same options.

Example:
  bash install-bce-bls-skill.sh ~/.config/opencode/skills
EOF
}

if [[ -z "${TARGET_DIR}" || "${TARGET_DIR}" == "-h" || "${TARGET_DIR}" == "--help" ]]; then
  usage
  exit 2
fi

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "missing required command: $1" >&2
    exit 1
  }
}

tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${tmp_dir}"
}
trap cleanup EXIT

mkdir -p "${TARGET_DIR}"
zip_path=""

if [[ -n "${LOCAL_ZIP}" ]]; then
  zip_path="${LOCAL_ZIP}"
  if [[ ! -f "${zip_path}" ]]; then
    echo "local bce-bls zip was not found: ${zip_path}" >&2
    exit 1
  fi
elif [[ -n "${DOWNLOAD_URL}" ]]; then
  need_cmd curl
  zip_path="${tmp_dir}/bce-bls.zip"
  curl -fL "${DOWNLOAD_URL}" -o "${zip_path}"
elif [[ -f "${DEFAULT_LOCAL_ZIP}" ]]; then
  zip_path="${DEFAULT_LOCAL_ZIP}"
else
  need_cmd curl
  zip_path="${tmp_dir}/bce-bls.zip"
  curl -fL "${DEFAULT_DOWNLOAD_URL}" -o "${zip_path}"
fi

if command -v unzip >/dev/null 2>&1; then
  unzip -o "${zip_path}" -d "${TARGET_DIR}"
else
  need_cmd python3
  python3 - "${zip_path}" "${TARGET_DIR}" <<'PY'
import sys
from pathlib import Path
from zipfile import ZipFile

zip_path = Path(sys.argv[1])
target_dir = Path(sys.argv[2])
with ZipFile(zip_path) as archive:
    archive.extractall(target_dir)
PY
fi

if [[ ! -f "${TARGET_DIR}/bce-bls/SKILL.md" ]]; then
  echo "bce-bls/SKILL.md was not found after extraction in ${TARGET_DIR}" >&2
  exit 1
fi

echo "Installed bce-bls into ${TARGET_DIR}"
sed -n '1,12p' "${TARGET_DIR}/bce-bls/SKILL.md"
