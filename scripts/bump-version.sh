#!/usr/bin/env bash
# Bump the version everywhere, commit and tag it: ./scripts/bump-version.sh 1.2.4
set -euo pipefail

version="${1:?usage: $0 X.Y.Z}"
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "version must look like X.Y.Z" >&2; exit 1; }

cd "$(dirname "$0")/.."

git diff --cached --quiet || { echo "files are already staged, commit or unstage them first" >&2; exit 1; }
! git rev-parse -q --verify "refs/tags/v$version" >/dev/null || { echo "tag v$version already exists" >&2; exit 1; }

sed -i -E "0,/^version = \".*\"/s//version = \"$version\"/" backend/pyproject.toml
sed -i -E "s/^(    version=)\".*\",/\1\"$version\",/" backend/main.py

(cd backend && uv lock && uv run generate_openapi.py)  # uv.lock + openapi.json
(cd frontend && npm version "$version" --no-git-tag-version --allow-same-version)  # package.json + lock

git add backend/pyproject.toml backend/main.py backend/uv.lock backend/openapi.json frontend/package.json frontend/package-lock.json
git commit -m "chore: bump version to $version"
git tag -a "v$version" -m "Release v$version"

echo "Done. Push with: git push && git push origin v$version"
