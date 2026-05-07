# BioMedArena

BioMedArena is a biomedical agent evaluation harness for comparing
LLM backbones, tool-use modes, scorers, and datasets behind one CLI.
The manuscript describes BioMedArena as a six-layer substrate for
benchmark loading, tool exposure, tool selection, harness mode, context
management, and scoring. In the paper scope, BioMedArena covers 147
biomedical benchmarks, 75 biomedical tools grouped into 9 functional
families, 6 harness families, and 6 context-management strategies.

This public release currently has 156 registered benchmark names, 75 tools,
4 modes, and 22 registered model IDs in the CLI. The CLI count includes
compatibility aliases and lightweight smoke/utility entries; the paper
count reports the benchmark scope used for the manuscript.

The project is designed as a practical research surface: add a dataset,
choose a harness mode, expose a tool pack, run a matrix, and compare
whether agentic behavior actually improves biomedical, medical,
chemistry, biology, protein, genomics, DNA/RNA, and healthcare tasks.

## Quick Check

After installing dependencies, run the offline smoke suite:

```bash
python3 scripts/run_quick_suite.py
```

Expected healthy output:

- 156 registered benchmarks
- 147 biomedical benchmarks in the manuscript scope
- 75 registered tools
- 4 registered modes
- 20/20 scorer checks passed

For the stricter offline release gate:

```bash
python3 scripts/release_gate.py --strict
```

## Installation

```bash
git clone <anonymous-repository-url>
cd BioMedArena

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install -e ".[dev,eval,provider-gemini]"

cp .env.example .env
```

Fill at least one model provider key in `.env`:

```bash
OPENAI_API_KEY=<your-openai-api-key>
ANTHROPIC_API_KEY=<your-anthropic-api-key>
GEMINI_API_KEY=<your-gemini-api-key>
HF_TOKEN=<your-huggingface-token-for-gated-benchmarks>
```

Gated HuggingFace datasets also require accepting the dataset terms in
the browser before `HF_TOKEN` can load them. See `.env.example` for
optional domain-specific keys such as NCBI, OMIM, Serper, and Jina.

BioMedArena also supports OpenAI-compatible model servers and hosted
routers. This covers most HuggingFace/self-hosted LLM inference stacks
that expose `/v1/chat/completions`, including vLLM, TGI, SGLang,
Ollama, LM Studio, llama.cpp, HuggingFace Inference Providers, Groq,
Together, Fireworks, and xAI/Grok. Examples:

```bash
# Local vLLM
LOCAL_LLM_MODEL=meta-llama/Llama-3.1-8B-Instruct
VLLM_BASE_URL=http://localhost:8000/v1
bioagent run --benchmark medcalc --backbone vllm --tools off --limit 5

# xAI / Grok
XAI_API_KEY=<your-xai-key>
XAI_MODEL=grok-4
bioagent run --benchmark medcalc --backbone grok --tools off --limit 5

# Generic OpenAI-compatible endpoint
OPENAI_COMPATIBLE_MODEL=<served-model-id>
OPENAI_COMPATIBLE_BASE_URL=https://example.invalid/v1
OPENAI_COMPATIBLE_API_KEY=<optional-key>
bioagent run --benchmark medcalc --backbone openai-compatible --tools off --limit 5
```

## Basic Usage

List available resources:

```bash
bioagent list-benchmarks
bioagent list-backbones
bioagent list-modes
```

The package name is `biomedarena`; the command-line entry point remains
`bioagent` for compatibility. Environment variables use the `BIOAGENT_`
prefix for the same reason.

Run one benchmark cell:

```bash
bioagent run \
  --benchmark medcalc \
  --backbone gemini-2.5-flash \
  --tools biomed --reasoning-mode light \
  --limit 5 \
  --output result.json
```

Run a small matrix cell:

```bash
python3 scripts/run_matrix.py \
  --config configs/matrix_default.yaml \
  --only medcalc,gemini,simple_llm \
  --limit-override 1
```

Check official source accessibility before spending model budget:

```bash
python3 scripts/verify_benchmark_sources.py --benchmarks all
```

## Execution Modes

The public CLI exposes four modes:

| Mode | Purpose |
| --- | --- |
| `simple_llm` | Pure model baseline, no tools. |
| `deep_think` | Native model reasoning/thinking path where supported. |
| `light` | Single-turn function/tool calling with scratchpad working memory. |
| `heavy` | Multi-turn ReAct loop with tool retrieval. |

The manuscript-level harness taxonomy groups these public modes with
self-consistency wrappers and Mutual-Evolve variants. The release CLI
keeps the stable operational surface above while exposing
`--self-consistency` as a wrapper around any mode.

A unified CLI interface is also available via `--tools` / `--reasoning-mode` /
`--enable-thinking` flags, which map to the modes above:

| `--tools` | `--reasoning-mode` | Internal mode | Thinking |
| --- | --- | --- | --- |
| `off` | (n/a) | `deep_think` | ON (default) |
| `off` + `--enable-thinking 0` | (n/a) | `simple_llm` | OFF |
| `biomed` / `search` / `all` | `light` | `light` | OFF |
| `biomed` / `search` / `all` | `heavy` | `heavy` | ON |

The legacy `--mode` / `--web-tools` flags remain supported for backward
compatibility. Add `--self-consistency` to wrap any mode with majority voting.

## Context Management

BioMedArena implements the six context-management strategies described
in the paper. Scratchpad-style planning is enabled by default in light
mode and remains ablatable through environment settings; the remaining
strategies can be composed for long traces or recovery runs.

| Strategy | Core idea | Protects against | Setting |
| --- | --- | --- | --- |
| Planning / scratchpad | Compact working notes, unresolved subgoals, accumulated evidence | Loss of useful intermediate state | Light-mode default; ablatable |
| Memory | Persistent salient facts and prior findings, re-injected on demand | Cross-turn or cross-session knowledge loss | Paper default; optional in CLI |
| Summarization | Compressed older dialogue, tool outputs, and evidence summaries | Long traces crowding out useful context | Optional; length-triggered |
| Clearing | Compact placeholders for stale tool outputs, reasoning traces, or media | Low-value context bulk | Optional; horizon-triggered |
| Truncation | Sliding windows, first-last retention, token budgets | Provider context overflow | Optional; budget-triggered |
| Rollback | Removal of the most recent low-value turn with corrective guidance | Repeated queries, tool errors, early loops | Optional; loop-triggered |

## Documentation

The root README stays short on purpose. Detailed release information
lives in `docs/`:

- [Benchmark dataset inventory](docs/benchmark_datasets.md)
- [Tools and skills inventory](docs/tools_and_skills.md)
- [API reference](docs/api_reference.md)
- [Metrics guide](docs/metrics_guide.md)

## Security

`python_exec` can execute model-supplied Python with timeout and basic
denylist checks. Treat this as a convenience guard, not a hardened
sandbox. Run untrusted workloads in an isolated container or VM, keep
secrets out of the working directory, and disable code-execution or
web-search tools for private data unless you have reviewed the policy.

External tools may call third-party APIs and public databases. Review
the benchmark and tool inventories before running sensitive workloads.

## Testing

```bash
python3 scripts/run_quick_suite.py
python3 scripts/release_gate.py --strict
python3 -m pytest tests/unit -q
python3 -m pytest tests/smoke -q -m "not slow"
```

## Citation

```bibtex
@article{anonymous2026biomedarena,
  title={BioMedArena: a Biomedical Deep-Research Agent Evaluation Harness},
  author={Anonymous Authors},
  xxx={xxx},
  year={2026}
}
```

## License

See [LICENSE](LICENSE). Ported life-science skill attribution is tracked
in [harness/tools/openai_ported/NOTICE.md](harness/tools/openai_ported/NOTICE.md).
