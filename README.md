# centian-benchmarks
Repository to store and evaluate agent benchmarks on centian templates.

[Whats centian?](https://github.com/T4cceptor/centian)

## Benchmarks

- Centian TDD Workflow - [to benchmark](benchmarks/centian_demo_v1)

## Getting started

### Dependencies
- `centian` (`>=v0.4`) available on your `PATH`
    - To install run: `curl -fsSL https://raw.githubusercontent.com/T4cceptor/centian/main/scripts/install.sh | bash`
- `node` (tested with `v24.2.0`) and `npx` (tested with `11.3.0`) available on your `PATH` - required to launch filesystem and shell MCP servers, and run tests
- Claude Code, Gemini CLI, or OpenAI Codex installed and authenticated - Centian launches the selected agent in headless mode through its local CLI, so the demo will fail if that agent binary is missing or it's not signed in.
- For `codex-ollama`, make sure local Ollama is running at `http://localhost:11434/v1`. Centian provides built-in `gemma4` and `qwen3.5` Codex OSS profiles, and you can override the base Codex config with `--codex-config`.

### Run agents

Runs all agents configured in the script (Note: this will likely exhaust your quota if you are not on a highest-tier plan or using API)
```
./run-centian-demo-v1-benchmarks.sh
```

Run single benchmark
```
centian benchmark run \               main 
  --suite tests/integrationtests/taskverification/benchmarks/centian_demo_v1 \ # path to benchmark suite
  --agent gemini \ # agent harness: gemini, codex, claude, codex-ollama
  --model flash \ # haiku, sonnet, opus, gpt-5.4, gpt-5.4-mini, pro, flash, or a valid ollama profile
  --repeat 1 # number of times the benchmark run should be repeated
```
