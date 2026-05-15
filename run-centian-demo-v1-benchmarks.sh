#!/usr/bin/env bash

set -euo pipefail

CENTIAN_BIN="${CENTIAN_BIN:-$(command -v centian || true)}"
REPEAT="${REPEAT:-10}"
TIMEOUT="${TIMEOUT:-30m}"
TEMPLATE_DIRS="${TEMPLATE_DIRS:-current=task-templates}"
CODEX_CONFIG_PATH="${CODEX_CONFIG_PATH:-}"
SUITE_PATH="${SUITE_PATH:-}"
CENTIAN_CONFIG_PATH="${CENTIAN_CONFIG_PATH:-}"
DRY_RUN=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Keep future additions here. The wizard and CLI both read from this catalog.
SCENARIO_IDS=(
  "claude-haiku"
  "claude-sonnet"
  "claude-opus"
  "gemini-pro"
  "gemini-flash"
  "codex-gpt-5.4"
  "codex-gpt-5.4-mini"
  "codex-ollama-gemma4"
  "codex-ollama-qwen35"
)
SCENARIO_LABELS=(
  "claude / haiku"
  "claude / sonnet"
  "claude / opus"
  "gemini / gemini-3.1-pro-preview"
  "gemini / gemini-3-flash-preview"
  "codex / gpt-5.4"
  "codex / gpt-5.4-mini"
  "codex-ollama / gemma4"
  "codex-ollama / qwen35"
)
SCENARIO_AGENTS=(
  "claude"
  "claude"
  "claude"
  "gemini"
  "gemini"
  "codex"
  "codex"
  "codex-ollama"
  "codex-ollama"
)
SCENARIO_MODELS=(
  "haiku"
  "sonnet"
  "opus"
  "gemini-3.1-pro-preview"
  "gemini-3-flash-preview"
  "gpt-5.4"
  "gpt-5.4-mini"
  "gemma4-local"
  "qwen35-local"
)
SCENARIO_CODEX_CONFIGS=(
  ""
  ""
  ""
  ""
  ""
  "benchmarks/centian_demo_v1/agent_configs/codex_config.toml"
  "benchmarks/centian_demo_v1/agent_configs/codex_config.toml"
  "benchmarks/centian_demo_v1/agent_configs/codex_ollama_config.toml"
  "benchmarks/centian_demo_v1/agent_configs/codex_ollama_config.toml"
)

SELECTED_SCENARIO_IDS=()

usage() {
  cat <<'EOF'
Usage:
  ./run-centian-demo-v1-benchmarks.sh
  ./run-centian-demo-v1-benchmarks.sh --suite context_sprawl_v1 --scenario codex-gpt-5.4 --repeat 1

Options:
  --suite <id|path>          Known ids: centian_demo_v1, context_sprawl_v1.
                             A direct suite path is also accepted.
  --scenario <id>            Scenario id from --list-scenarios. Repeat to run multiple.
  --all-scenarios            Run every catalogued scenario.
  --repeat <count>           Repeat count passed to Centian.
  --timeout <duration>       Timeout passed to Centian. Default: 30m.
  --centian-config <path>    Override suite-specific Centian config path.
  --codex-config <path>      Override scenario-specific Codex config defaults.
  --template-dirs <values>   Comma-separated template-dir values.
  --dry-run                  Print commands without executing them.
  --list-suites              Print known suite ids.
  --list-scenarios           Print known scenario ids.
  -h, --help                 Show this help.

With no arguments, the script launches a small interactive wizard.
Environment variables still work: CENTIAN_BIN, SUITE_PATH, REPEAT, TIMEOUT,
CENTIAN_CONFIG_PATH, CODEX_CONFIG_PATH, TEMPLATE_DIRS.
EOF
}

list_suites() {
  cat <<'EOF'
centian_demo_v1     benchmarks/centian_demo_v1
context_sprawl_v1   benchmarks/context_sprawl_v1
EOF
}

list_scenarios() {
  local i
  for i in "${!SCENARIO_IDS[@]}"; do
    printf '%-24s %s\n' "${SCENARIO_IDS[$i]}" "${SCENARIO_LABELS[$i]}"
  done
}

set_suite_defaults() {
  local suite="$1"

  case "${suite}" in
    centian_demo_v1|demo)
      SUITE_PATH="benchmarks/centian_demo_v1"
      [[ -n "${CENTIAN_CONFIG_PATH}" ]] || CENTIAN_CONFIG_PATH="benchmarks/centian_demo_v1/centian_config.json"
      ;;
    context_sprawl_v1|sprawl)
      SUITE_PATH="benchmarks/context_sprawl_v1"
      [[ -n "${CENTIAN_CONFIG_PATH}" ]] || CENTIAN_CONFIG_PATH="benchmarks/context_sprawl_v1/centian_config.json"
      ;;
    *)
      SUITE_PATH="${suite}"
      ;;
  esac
}

apply_known_suite_defaults_from_path() {
  case "${SUITE_PATH}" in
    benchmarks/centian_demo_v1|./benchmarks/centian_demo_v1)
      [[ -n "${CENTIAN_CONFIG_PATH}" ]] || CENTIAN_CONFIG_PATH="benchmarks/centian_demo_v1/centian_config.json"
      ;;
    benchmarks/context_sprawl_v1|./benchmarks/context_sprawl_v1)
      [[ -n "${CENTIAN_CONFIG_PATH}" ]] || CENTIAN_CONFIG_PATH="benchmarks/context_sprawl_v1/centian_config.json"
      ;;
  esac
}

materialize_centian_config_if_needed() {
  local source_path="${CENTIAN_CONFIG_PATH}"

  if [[ -z "${source_path}" || ! -f "${source_path}" ]]; then
    return
  fi
  if ! grep -q "__DOCS_SERVER__" "${source_path}"; then
    return
  fi

  local docs_server_path="${SCRIPT_DIR}/benchmarks/context_sprawl_v1/server/get_docs_server.mjs"
  local rendered_path
  rendered_path="$(dirname "${source_path}")/.centian_config.rendered.json"

  python3 - "${source_path}" "${rendered_path}" "${docs_server_path}" <<'PY'
from pathlib import Path
import sys

source_path, rendered_path, docs_server_path = map(Path, sys.argv[1:])
content = source_path.read_text()
rendered_path.write_text(content.replace("__DOCS_SERVER__", str(docs_server_path)))
PY

  CENTIAN_CONFIG_PATH="${rendered_path}"
}

scenario_index_for_id() {
  local wanted="$1"
  local i

  for i in "${!SCENARIO_IDS[@]}"; do
    if [[ "${SCENARIO_IDS[$i]}" == "${wanted}" ]]; then
      printf '%s\n' "${i}"
      return 0
    fi
  done

  return 1
}

add_scenario_by_id() {
  local scenario_id="$1"

  if ! scenario_index_for_id "${scenario_id}" >/dev/null; then
    echo "error: unknown scenario id: ${scenario_id}" >&2
    echo "Use --list-scenarios to see valid values." >&2
    exit 1
  fi

  SELECTED_SCENARIO_IDS+=("${scenario_id}")
}

add_all_scenarios() {
  SELECTED_SCENARIO_IDS=("${SCENARIO_IDS[@]}")
}

prompt_with_default() {
  local prompt="$1"
  local default_value="$2"
  local answer

  read -r -p "${prompt} [${default_value}]: " answer
  printf '%s\n' "${answer:-${default_value}}"
}

choose_suite_interactively() {
  local answer

  echo
  echo "Choose benchmark suite:"
  echo "  1) centian_demo_v1"
  echo "  2) context_sprawl_v1"
  read -r -p "Suite [1]: " answer

  case "${answer:-1}" in
    1|centian_demo_v1|demo)
      set_suite_defaults "centian_demo_v1"
      ;;
    2|context_sprawl_v1|sprawl)
      set_suite_defaults "context_sprawl_v1"
      ;;
    *)
      echo "error: invalid suite selection: ${answer}" >&2
      exit 1
      ;;
  esac
}

choose_scenarios_interactively() {
  local answer
  local normalized
  local choice
  local index

  echo
  echo "Choose scenario(s):"
  for index in "${!SCENARIO_IDS[@]}"; do
    printf '  %d) %s\n' "$((index + 1))" "${SCENARIO_LABELS[$index]}"
  done
  echo "  a) all scenarios"
  read -r -p "Selections, separated by commas or spaces [6]: " answer

  answer="${answer:-6}"
  if [[ "${answer}" == "a" || "${answer}" == "all" ]]; then
    add_all_scenarios
    return
  fi

  normalized="${answer//,/ }"
  for choice in ${normalized}; do
    if ! [[ "${choice}" =~ ^[0-9]+$ ]] || (( choice < 1 || choice > ${#SCENARIO_IDS[@]} )); then
      echo "error: invalid scenario selection: ${choice}" >&2
      exit 1
    fi
    add_scenario_by_id "${SCENARIO_IDS[$((choice - 1))]}"
  done
}

run_wizard() {
  choose_suite_interactively
  choose_scenarios_interactively
  REPEAT="$(prompt_with_default "Repeat count" "${REPEAT}")"
  TIMEOUT="$(prompt_with_default "Timeout" "${TIMEOUT}")"

  echo
  echo "Optional overrides:"
  CODEX_CONFIG_PATH="$(prompt_with_default "Global Codex config override" "${CODEX_CONFIG_PATH:-<scenario default>}")"
  [[ "${CODEX_CONFIG_PATH}" == "<scenario default>" ]] && CODEX_CONFIG_PATH=""
  CENTIAN_CONFIG_PATH="$(prompt_with_default "Centian config path" "${CENTIAN_CONFIG_PATH}")"
  TEMPLATE_DIRS="$(prompt_with_default "Template dirs" "${TEMPLATE_DIRS}")"
}

print_command() {
  local arg
  for arg in "$@"; do
    printf '%q ' "${arg}"
  done
  printf '\n'
}

run_scenario() {
  local scenario_id="$1"
  local index
  local label
  local agent
  local model
  local scenario_codex_config

  index="$(scenario_index_for_id "${scenario_id}")"
  label="${SCENARIO_LABELS[$index]}"
  agent="${SCENARIO_AGENTS[$index]}"
  model="${SCENARIO_MODELS[$index]}"
  scenario_codex_config="${CODEX_CONFIG_PATH:-${SCENARIO_CODEX_CONFIGS[$index]}}"

  echo
  echo "==> Starting scenario: ${label}"
  echo "    agent=${agent} model=${model} repeat=${REPEAT}"

  local cmd=(
    "${CENTIAN_BIN}"
    benchmark
    run
    --suite "${SUITE_PATH}"
    --agent "${agent}"
    --repeat "${REPEAT}"
    --timeout "${TIMEOUT}"
  )

  if [[ "${agent}" == "codex-ollama" ]]; then
    cmd+=(--profile "${model}")
  else
    cmd+=(--model "${model}")
  fi

  if [[ ( "${agent}" == "codex" || "${agent}" == "codex-ollama" ) && -n "${scenario_codex_config}" ]]; then
    cmd+=(--codex-config "${scenario_codex_config}")
  fi
  if [[ -n "${CENTIAN_CONFIG_PATH}" ]]; then
    cmd+=(--centian-config "${CENTIAN_CONFIG_PATH}")
  fi
  if [[ -n "${TEMPLATE_DIRS}" ]]; then
    IFS=',' read -r -a template_dirs <<< "${TEMPLATE_DIRS}"
    local template_dir
    for template_dir in "${template_dirs[@]}"; do
      [[ -n "${template_dir}" ]] && cmd+=(--template-dir "${template_dir}")
    done
  fi

  if [[ "${DRY_RUN}" == true ]]; then
    print_command "${cmd[@]}"
  else
    "${cmd[@]}"
  fi

  echo "==> Finished scenario: ${label}"
}

parse_args() {
  while (( $# > 0 )); do
    case "$1" in
      --suite)
        set_suite_defaults "$2"
        shift 2
        ;;
      --scenario)
        add_scenario_by_id "$2"
        shift 2
        ;;
      --all-scenarios)
        add_all_scenarios
        shift
        ;;
      --repeat)
        REPEAT="$2"
        shift 2
        ;;
      --timeout)
        TIMEOUT="$2"
        shift 2
        ;;
      --centian-config)
        CENTIAN_CONFIG_PATH="$2"
        shift 2
        ;;
      --codex-config)
        CODEX_CONFIG_PATH="$2"
        shift 2
        ;;
      --template-dirs)
        TEMPLATE_DIRS="$2"
        shift 2
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --list-suites)
        list_suites
        exit 0
        ;;
      --list-scenarios)
        list_scenarios
        exit 0
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "error: unknown argument: $1" >&2
        usage >&2
        exit 1
        ;;
    esac
  done
}

if (( $# == 0 )) && [[ -t 0 ]]; then
  run_wizard
else
  parse_args "$@"
fi

if [[ -z "${SUITE_PATH}" ]]; then
  set_suite_defaults "centian_demo_v1"
else
  apply_known_suite_defaults_from_path
fi
materialize_centian_config_if_needed
if (( ${#SELECTED_SCENARIO_IDS[@]} == 0 )); then
  add_scenario_by_id "codex-gpt-5.4"
fi

if [[ ! -x "${CENTIAN_BIN}" ]]; then
  echo "error: centian binary not found or not executable at ${CENTIAN_BIN}" >&2
  exit 1
fi
if [[ ! -d "${SUITE_PATH}" ]]; then
  echo "error: benchmark suite not found at ${SUITE_PATH}" >&2
  exit 1
fi

echo "Centian binary: ${CENTIAN_BIN}"
echo "Suite: ${SUITE_PATH}"
echo "Repeat count: ${REPEAT}"
echo "Timeout: ${TIMEOUT}"
echo "Scenarios:"
for scenario_id in "${SELECTED_SCENARIO_IDS[@]}"; do
  index="$(scenario_index_for_id "${scenario_id}")"
  echo "  - ${SCENARIO_LABELS[$index]}"
done

if [[ -n "${CODEX_CONFIG_PATH}" ]]; then
  echo "Codex config override: ${CODEX_CONFIG_PATH}"
else
  echo "Codex config override: <scenario default>"
fi
if [[ -n "${CENTIAN_CONFIG_PATH}" ]]; then
  echo "Centian config: ${CENTIAN_CONFIG_PATH}"
fi
if [[ -n "${TEMPLATE_DIRS}" ]]; then
  echo "Template dirs: ${TEMPLATE_DIRS}"
fi

for scenario_id in "${SELECTED_SCENARIO_IDS[@]}"; do
  run_scenario "${scenario_id}"
done

echo
if [[ "${DRY_RUN}" == true ]]; then
  echo "Dry run finished."
else
  echo "All benchmark scenarios finished."
fi
