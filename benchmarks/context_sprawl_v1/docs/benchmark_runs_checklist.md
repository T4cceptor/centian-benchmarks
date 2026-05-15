## Benchmark runs

### Baseline runs

- [ ] Claude Code
    - [ ] Opus 4.6
        - I did one run with bedrock, but I think Bedrock API behaves differently to Anthropic directly, making this an unfair comparison, I will rerun this using Anthropics API
    - [ ] Sonnet 4.6
    - [x] Haiku 4.6
- [ ] Codex
    - [ ] GPT-5.4
    - [x] GPT-5.4-mini
- [x] Gemini CLI
    - [x] Gemini 3 Pro
    - [x] Gemini 3 Flash
- [ ] Codex-Ollama
    - [ ] Qwen 3.5
    - [ ] Qwen 3.6

#### Findings
- Bedrock vs. Anthropics API - I need to double check this, because they seem to behave differently!
    - 2/10 runs did not start
    - produced a surprising amount of tool errors
- Haiku - no longer 100% success, and struggling on the first-pass rate (only 1/10)
- Gemini 3 Flash - quite good, comparable to last time (10/10 success, 9/10 first pass vs. 8/10 last time)
