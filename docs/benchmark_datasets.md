# Benchmark Dataset Inventory

This document separates the manuscript benchmark scope from the current
CLI registry. The distinction is intentional: the manuscript reports the
biomedical evaluation substrate, while the release CLI also retains
compatibility aliases and lightweight smoke/utility entries.

- Manuscript benchmark scope: **147 biomedical benchmarks**
- CLI benchmark registrations: **156**
- Core/non-HF CLI registrations: **26**
- Canonical HuggingFace CLI registrations: **119**
- Deprecated compatibility aliases: **11**
- CLI modes: **4**

Use the manuscript scope when describing the paper contribution. Use
the CLI registration count when describing what `bioagent
list-benchmarks` prints in this repository.

## Headline Experiment Benchmarks

The paper's headline evaluation uses 8 representative biomedical
benchmarks. These are the counts reported in the manuscript.

| Benchmark | Evaluated questions | Domain | Capability | Answer format | Scoring |
| --- | ---: | --- | --- | --- | --- |
| MedXpertQA Text | 2,450 | Clinical medicine | Expert MCQ reasoning | 10-option MCQ | Rule |
| Medbullets op4 | 308 | Clinical medicine | USMLE-style reasoning | MCQ | Rule |
| ProteinLM Bench | 944 | Proteins | Protein-domain knowledge | MCQ | Rule |
| HealthBench Hard | 1,000 | Health dialog | Open-ended generation | Open text | Rubric judge |
| BixBench | 205 | Computational biology | Biomedical reasoning | Adapted MCQ | Rule |
| HLE-Gold Bio/Chem verified | 149 | Bio/Chem/Med | Expert frontier reasoning | MCQ + open | Rule + judge |
| SUPERChem | 500 | Chemistry | Text and image chemistry reasoning | MCQ | Rule |
| LAB-Bench 2 | 821 | Biomedical research | Literature, patent, trial, database, figure, and table QA | Mixed text | Rule + judge |

LAB-Bench 2 is reported over its seven text-oriented subsets:

| Subset | Questions | Evidence type | Capability |
| --- | ---: | --- | --- |
| LitQA3 | 168 | Literature | Paper-grounded QA |
| PatentQA | 121 | Patents | Technical document QA |
| TrialQA | 120 | Clinical trials | Trial-grounded QA |
| DBQA2 | 86 | Databases | Structured retrieval |
| SuppQA2 | 125 | Supplementary material | Document grounding |
| FigQA2 | 101 | Figures | Figure QA, text-only release path |
| TableQA2 | 100 | Tables | Table QA, text-only release path |

HLE-Gold contains 107 biology questions and 42 chemistry questions in
the verified Bio/Chem subset. SUPERChem contains 265 text questions and
235 image-associated questions; the public loader can run a text
fallback when image assets are unavailable.

## Current CLI Registry

The current release exposes the following core/non-HF benchmark names:

| Benchmark | Source / role | Notes |
| --- | --- | --- |
| `aa_lcr` | ArtificialAnalysis/AA-LCR | Long-context reasoning over documents |
| `agentclinic` | AgentClinic official release | Doctor-patient diagnostic scenarios |
| `bioasq` | BioASQ official/local source | Biomedical factoid, list, yes/no QA |
| `bioprobench` | BioProBench official data | Biological protocol understanding |
| `bixbench` | futurehouse/BixBench | Biomedical information reasoning |
| `genotex` | GenoTEX official data | Genomics text reasoning |
| `gpqa_bio` | GPQA biology/chemistry/medicine subset | Graduate-level science MCQ |
| `healthbench` | OpenAI HealthBench official data | Health conversation quality and safety |
| `hle_gold` | futurehouse HLE-Gold Bio/Chem | Expert frontier reasoning |
| `labbench` | futurehouse LAB-Bench | Biomedical agent QA |
| `labbench2` | EdisonScientific LAB-Bench 2 | Text-oriented biomedical research QA |
| `medagentbench` | MedAgentBench official data | Clinical workflow and EHR tasks |
| `medcalc` | NCBI MedCalc-Bench | Clinical calculation tasks |
| `medhelm` | MedHELM public sources | Medical QA, safety, and scenario tasks |
| `medmcqa` | OpenLifeScienceAI MedMCQA | Medical exam MCQ |
| `medqa` | MedQA-USMLE four-option source | USMLE-style MCQ |
| `medxpertqa` | TsinghuaC3I MedXpertQA | Expert medical text MCQ |
| `medxpertqa_mm` | TsinghuaC3I MedXpertQA-MM | Multimodal medical QA, with text fallback |
| `mmlu` | Medical and biology MMLU subjects | Academic MCQ |
| `pathvqa` | PathVQA official/HF source | Pathology VQA |
| `pubmedqa` | PubMedQA official/mirror source | PubMed abstract QA |
| `quick_suite` | Built-in fixtures | Offline smoke and scorer checks |
| `rag_essential` | Built-in retrieval tasks | Retrieval/tool-use sanity checks |
| `super_chemistry` | ZehuaZhao SUPERChem | Chemistry MCQ, text/image release path |
| `superchem` | SuperChem official data | Compatibility loader for chemistry tasks |
| `supergpqa` | SuperGPQA official data | Graduate-level science questions |

The HuggingFace registry contains 119 canonical `hf_*` entries in
`harness/eval/hf_benchmark_registry.py`. They load through
`harness.eval.bench_hf_benchmark.load_hf_benchmark_tasks`, normalize
rows into the common BioMedArena task schema, and require network access
on first use unless the dataset is already cached locally.

The release also keeps 11 deprecated aliases so older configs do not
break immediately:

| Alias | Canonical target |
| --- | --- |
| `hf_chinese_medbench` | `hf_cmb` |
| `hf_mednli_augmented` | `hf_mednli` |
| `hf_pubmed_20k_rct` | `hf_pubmed_200k_rct` |
| `hf_pubmed_rct20k` | `hf_pubmed_200k_rct` |
| `hf_blue_benchmark` | `hf_blurb` |
| `hf_openddi` | `hf_ddi_corpus_2013` |
| `hf_lavita_medmcqa` | `medmcqa` |
| `hf_lavita_usmle_step1` | `medqa` |
| `hf_lavita_usmle_step2` | `medqa` |
| `hf_lavita_usmle_step3` | `medqa` |
| `hf_usmle_step_series` | `medqa` |

## Verification

Use the offline gate first:

```bash
python3 scripts/run_quick_suite.py
python3 scripts/release_gate.py --strict
```

For live source checks, run a loader audit in an environment with
HuggingFace access and accepted gated dataset terms:

```bash
python3 scripts/verify_benchmark_sources.py --benchmarks all
```
