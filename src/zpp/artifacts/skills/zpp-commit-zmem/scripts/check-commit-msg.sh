#!/usr/bin/env sh
set -eu

CANONICAL_EVENTS="DECISION LESSON_LEARNT REFACTOR DEBT CONTEXT"
REQUIRE_ZMEM=false
if [ "${1:-}" = "--require-zmem" ]; then
  REQUIRE_ZMEM=true
  shift
fi

emit() {
  jq -n --argjson ok "$1" --argjson code "$2" --arg message "$3" \
    --arg cc_type "$4" --argjson annotations "$5" \
    '{ok:$ok,code:$code,message:$message,cc_type:$cc_type,annotations:$annotations}'
}

if [ "${1:-}" = "--file" ]; then
  [ -f "${2:-}" ] || { emit false 1 "message file not found: ${2:-}" "" 0; exit 1; }
  MSG=$(cat "$2")
else
  REF="${1:-HEAD}"
  MSG=$(git log -1 --format=%B "$REF" 2>/dev/null) || {
    emit false 1 "cannot read commit: $REF" "" 0; exit 1; }
fi

SUBJECT=$(printf '%s\n' "$MSG" | head -n1)
if ! printf '%s\n' "$SUBJECT" | rg -q '^[a-z]+(\([^)]*\))?!?: .+$'; then
  emit false 20 "subject is not a conventional commit: $SUBJECT" "" 0; exit 20
fi
if [ "$(printf '%s' "$SUBJECT" | wc -c)" -gt 72 ]; then
  emit false 21 "subject exceeds 72 chars" "" 0; exit 21
fi

CC_TYPE=$(printf '%s\n' "$SUBJECT" | sed -E 's/^([a-z]+).*/\1/')
ANNOTATIONS=0
LINE_NO=1
OLDIFS=$IFS; IFS='
'
for line in $(printf '%s\n' "$MSG" | tail -n +2); do
  LINE_NO=$((LINE_NO + 1))
  stripped=$(printf '%s' "$line" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
  [ -z "$stripped" ] && continue
  if printf '%s\n' "$stripped" | rg -q '^([-*][[:space:]]+)?zmem\([^)]+\): .+$'; then
    ANNOTATIONS=$((ANNOTATIONS + 1))
    event=$(printf '%s\n' "$stripped" | sed -E 's/^([-*][[:space:]]+)?zmem\(([^)]+)\).*/\2/')
    case " $CANONICAL_EVENTS " in
      *" $event "*) ;;
      *) emit false 24 "non-canonical event: $event (allowed: $CANONICAL_EVENTS)" "$CC_TYPE" "$ANNOTATIONS"; exit 24 ;;
    esac
    continue
  fi
  if printf '%s\n' "$stripped" | rg -q '^[-*] .+$'; then continue; fi
  emit false 22 "body line $LINE_NO is prose (must be zmem() or bullet): $stripped" "$CC_TYPE" "$ANNOTATIONS"; exit 22
done
IFS=$OLDIFS

if [ "$REQUIRE_ZMEM" = true ] && [ "$ANNOTATIONS" -eq 0 ]; then
  emit false 23 "memory-bearing validation requires a zmem() annotation" "$CC_TYPE" 0; exit 23
fi
emit true 0 "ok" "$CC_TYPE" "$ANNOTATIONS"
