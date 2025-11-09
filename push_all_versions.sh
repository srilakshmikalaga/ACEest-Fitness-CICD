#!/usr/bin/env bash
set -euo pipefail

REPO="kalyanimuppidi/ace-fitness-and-gym"

# simple two-column list: tag filename
# each line: tag|path
VERSIONS=$(
cat <<'EOF'
v1.0|app/ACEest_Fitness.py
v1.1|app/ACEest_Fitness-V1.1.py
v1.2|app/ACEest_Fitness-V1.2.py
v1.2.1|app/ACEest_Fitness-V1.2.1.py
v1.2.2|app/ACEest_Fitness-V1.2.2.py
v1.2.3|app/ACEest_Fitness-V1.2.3.py
v1.3|app/ACEest_Fitness-V1.3.py
EOF
)

echo "Make sure you are logged in: docker login"

while IFS='|' read -r tag file; do
  echo
  echo "=== Building ${REPO}:${tag} from ${file} ==="
  if [ ! -f "$file" ]; then
    echo "ERROR: source file not found: $file"
    exit 2
  fi

  docker build --platform linux/amd64 \
    --build-arg VERSION_FILE="${file}" \
    -t "${REPO}:${tag}" .

  echo "Pushing ${REPO}:${tag} ..."
  docker push "${REPO}:${tag}"
done <<EOF
$VERSIONS
EOF

echo
echo "All versions pushed."
