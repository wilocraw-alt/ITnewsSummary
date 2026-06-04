#!/usr/bin/env bash
# 논문 현재 상태(소스 + 빌드 산출물)를 versions/vNNN-<날짜>[-라벨]/ 로 스냅샷한다.
# 사용: ./snapshot.sh [라벨]      예) ./snapshot.sh planning-focused
# 고쳐쓰기 전에 실행하면 직전 버전이 그대로 보존된다.
set -euo pipefail
cd "$(dirname "$0")"

label="${1:-}"
date_tag="$(date +%Y%m%d)"

mkdir -p versions
# 마지막 vNNN 찾아 +1
last="$(ls -1 versions 2>/dev/null | grep -oE '^v[0-9]+' | sort | tail -1 | tr -d 'v' || true)"
n="$(printf 'v%03d' "$(( 10#${last:-0} + 1 ))")"
name="${n}-${date_tag}${label:+-${label}}"
dest="versions/${name}"
mkdir -p "${dest}/sections" "${dest}/figures"

# 소스
cp -f main.tex references.bib Makefile build_docx.py snapshot.sh "${dest}/" 2>/dev/null || true
cp -f sections/*.tex "${dest}/sections/" 2>/dev/null || true
# 그림(정본 svg + 변환 pdf/png)
cp -f figures/* "${dest}/figures/" 2>/dev/null || true
# 산출물(있으면)
cp -f main.pdf main.docx "${dest}/" 2>/dev/null || true

echo "스냅샷 저장: ${dest}"
ls -1 "${dest}"
