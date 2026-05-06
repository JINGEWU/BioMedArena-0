# Benchmark Dataset Inventory

This file is generated from the current CLI registry and loader metadata. It is the public source-of-truth for what the repository supports at release time.

- CLI benchmark registrations: **156**
- Core/non-HF registrations: **26**
- Generic HuggingFace registrations exposed in CLI: **130**
- CLI modes: **4**

Count semantics: core benchmark counts are the default loader scope where the code pins one; HF counts use registry metadata when present. `unknown upstream split size` means the loader follows the official HuggingFace split but the repository does not pin a static count, so users should inspect the current upstream dataset card or run a source audit in their environment.

## Core Benchmarks

| Benchmark | Source | Count | Content | Input type | Task type | Answer/scorer | Gated | Needs network | Offline cache | Multimodal | Loader |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `aa_lcr` | ArtificialAnalysis/AA-LCR | upstream split size | long-context reasoning over documents | text, optional retrieved documents | long-context QA | openText | no | yes on first run | yes | no | `load_aa_lcr_tasks` |
| `agentclinic` | AgentClinic official release | loader default | doctor-patient diagnostic scenarios | text dialogue | clinical simulation | openText | no | source-dependent | yes | no | `load_agentclinic_tasks` |
| `bioasq` | BioASQ official/local source | loader default | factoid/list/yes-no biomedical questions | text | biomedical QA | openText | no | source-dependent | yes | no | `load_bioasq_tasks` |
| `bioprobench` | BioProBench official data | official benchmark scope | biological protocol understanding and repair | text | protocol QA | mixed | no | yes on first run | yes | no | `load_bioprobench_tasks` |
| `bixbench` | futurehouse/BixBench | 205 | closed-book biomedical information tasks | text | bioinformatics QA | openText | no | yes | yes | no | `load_bixbench_tasks` |
| `genotex` | GenoTEX official data | loader default | genomics text reasoning | text/genomics | genomics QA | openText | no | source-dependent | yes | no | `load_genotex_tasks` |
| `gpqa_bio` | Idavidrein/gpqa:gpqa_diamond/train | 198 | graduate-level biology/chemistry/medicine questions | text | graduate science MCQ | multipleChoice | yes | yes | yes | no | `load_gpqa_bio_tasks` |
| `healthbench` | OpenAI HealthBench official data | official benchmark scope | consumer-health answer quality and safety | text conversation | health conversation | openText | source-dependent | yes on first run | yes | no | `load_healthbench_tasks` |
| `hle_gold` | futurehouse/hle-gold-bio-chem:train | 149 | HLE Gold bio/chem subset | text | expert QA | mixed | yes | yes | yes | no | `load_hle_gold_tasks` |
| `labbench` | futurehouse/lab-bench | loader default subsets | LitQA, cloning, protocol tasks | text | biomedical agent QA | mixed | yes | yes | yes | no | `load_labbench_tasks` |
| `labbench2` | EdisonScientific/labbench2 text-only subsets | 821 | LAB-Bench 2 text-only evaluation subset | text | literature/database/patent QA | openText | yes | yes | yes | no by default | `load_labbench2_tasks` |
| `medagentbench` | MedAgentBench official data | loader default | clinical workflow and EHR tasks | text/EHR | medical agent workflow | mixed | no | source-dependent | yes | no | `load_medagentbench_tasks` |
| `medcalc` | ncbi/MedCalc-Bench-v1.2:test | 1100 | medical calculator word problems | text | clinical calculation | exactNumeric | no | yes | yes | no | `load_medcalc_tasks` |
| `medhelm` | MedHELM official/public sources | official benchmark scope | medical QA, safety, and scenario tasks | text | medical HELM tasks | mixed | source-dependent | yes on first run | yes | no | `load_medhelm_tasks` |
| `medmcqa` | openlifescienceai/medmcqa | loader default split | medical entrance-exam questions | text | medical MCQ | multipleChoice | no | yes | yes | no | `load_medical_qa_tasks` |
| `medqa` | GBaker/MedQA-USMLE-4-options | loader default split | USMLE-style questions | text | USMLE MCQ | multipleChoice | no | yes | yes | no | `load_medical_qa_tasks` |
| `medxpertqa` | TsinghuaC3I/MedXpertQA | loader default Text subset | expert medical reasoning questions | text | expert medical MCQ | multipleChoice | no | yes | yes | no | `load_medxpertqa_tasks` |
| `medxpertqa_mm` | TsinghuaC3I/MedXpertQA-MM | official multimodal subset | expert medical multimodal questions | text with optional images | medical VQA/MCQ | multipleChoice | no | yes | yes | yes; text fallback by default | `load_medxpertqa_mm_tasks` |
| `mmlu` | MMLU medical/biology subjects | loader default subjects | MMLU anatomy, medicine, biology, genetics subjects | text | academic MCQ | multipleChoice | no | yes | yes | no | `load_mmlu_tasks` |
| `pathvqa` | PathVQA official/HF source | loader default split | pathology image questions | text+image | pathology VQA | openText | no | yes | yes | yes | `load_pathvqa_tasks` |
| `pubmedqa` | qiaojin/PubMedQA or OpenLifeScience mirror | loader default split | yes/no/maybe biomedical literature questions | text abstract | PubMed abstract QA | multipleChoice | no | yes | yes | no | `load_medical_qa_tasks` |
| `quick_suite` | built-in repository fixtures | 20 | 5 MCQ, 5 exact, 5 numeric, 5 open-text scorer checks | text | offline smoke | mixed | no | no | not needed | no | `load_quick_suite_tasks` |
| `rag_essential` | built-in RAG essential tasks | 12 | tasks designed to reward retrieval/tool use | text | retrieval/tool-use QA | openText | no | no | not needed | no | `load_rag_essential_tasks` |
| `super_chemistry` | ZehuaZhao/SUPERChem:SUPERChem-500.parquet | 500 text rows by default; 500 official rows total | advanced chemistry questions | text, optional images | chemistry MCQ | multipleChoice | no | yes | yes | yes; text fallback by default | `load_super_chemistry_tasks` |
| `superchem` | SuperChem official data | loader default | chemistry evaluation tasks | text | chemistry QA | mixed | source-dependent | yes on first run | yes | no | `load_superchem_tasks` |
| `supergpqa` | SuperGPQA official data | loader default | graduate-level science questions | text | science MCQ | multipleChoice | source-dependent | yes on first run | yes | no | `load_supergpqa_tasks` |

## HuggingFace Benchmarks

All `hf_*` entries load from the official HuggingFace dataset repo listed below via `harness.eval.bench_hf_benchmark.load_hf_benchmark_tasks`. First run needs network access; subsequent runs can use the HuggingFace datasets cache. The current generic HF loader normalizes rows to text/structured tasks and does not register multimodal HF datasets.

| Benchmark | Source | Config | Split | Count | Domain | Task type | Answer/scorer | Gated | Network | Offline cache | Multimodal |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| `hf_adaptllm_chemprot` | [`AdaptLLM/medicine-tasks`](https://huggingface.co/datasets/AdaptLLM/medicine-tasks) | ChemProt | default | unknown | biomedical | mcq | multipleChoice | no | yes | yes | no |
| `hf_adaptllm_medicine_tasks` | [`AdaptLLM/medicine-tasks`](https://huggingface.co/datasets/AdaptLLM/medicine-tasks) | USMLE | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_adaptllm_mqp` | [`AdaptLLM/medicine-tasks`](https://huggingface.co/datasets/AdaptLLM/medicine-tasks) | MQP | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_adaptllm_rct` | [`AdaptLLM/medicine-tasks`](https://huggingface.co/datasets/AdaptLLM/medicine-tasks) | RCT | default | unknown | biomedical | mcq | multipleChoice | no | yes | yes | no |
| `hf_ade_corpus_v2` | [`bigbio/ade_corpus_v2`](https://huggingface.co/datasets/bigbio/ade_corpus_v2) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_anatem` | [`bigbio/anatem`](https://huggingface.co/datasets/bigbio/anatem) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_asclepius_clinical_notes` | [`starmpcc/Asclepius-Synthetic-Clinical-Notes`](https://huggingface.co/datasets/starmpcc/Asclepius-Synthetic-Clinical-Notes) |  | default | unknown | clinical | summarization | openText | no | yes | yes | no |
| `hf_augmented_clinical_notes` | [`AGBonnet/augmented-clinical-notes`](https://huggingface.co/datasets/AGBonnet/augmented-clinical-notes) |  | default | unknown | clinical | summarization | openText | no | yes | yes | no |
| `hf_bc2gm` | [`bigbio/bc2gm`](https://huggingface.co/datasets/bigbio/bc2gm) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_bc5cdr` | [`bigbio/bc5cdr`](https://huggingface.co/datasets/bigbio/bc5cdr) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_biosses` | [`bigbio/biosses`](https://huggingface.co/datasets/bigbio/biosses) |  | default | unknown | biomedical | regression | exactNumeric | no | yes | yes | no |
| `hf_blue_benchmark` | [`ncbi-nlp/BLUE_Benchmark`](https://huggingface.co/datasets/ncbi-nlp/BLUE_Benchmark) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_blurb` | [`EMBO/BLURB`](https://huggingface.co/datasets/EMBO/BLURB) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_careqa` | [`careqa/CareQA`](https://huggingface.co/datasets/careqa/CareQA) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_ccdv_pubmed_summarization` | [`ccdv/pubmed-summarization`](https://huggingface.co/datasets/ccdv/pubmed-summarization) |  | default | unknown | biomedical | summarization | openText | no | yes | yes | no |
| `hf_chembench` | [`jablonkagroup/ChemBench`](https://huggingface.co/datasets/jablonkagroup/ChemBench) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_chemistry_qa` | [`avaliev/ChemistryQA`](https://huggingface.co/datasets/avaliev/ChemistryQA) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_chemllmbench` | [`AI4Chem/ChemLLMBench`](https://huggingface.co/datasets/AI4Chem/ChemLLMBench) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_chinese_medbench` | [`open-compass/MedBench`](https://huggingface.co/datasets/open-compass/MedBench) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_clinical_sts` | [`bigbio/medsts`](https://huggingface.co/datasets/bigbio/medsts) |  | default | unknown | clinical | regression | exactNumeric | no | yes | yes | no |
| `hf_cmb` | [`FreedomIntelligence/CMB`](https://huggingface.co/datasets/FreedomIntelligence/CMB) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_cmexam` | [`bigbio/cmexam`](https://huggingface.co/datasets/bigbio/cmexam) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_ddi_corpus_2013` | [`bigbio/ddi_corpus`](https://huggingface.co/datasets/bigbio/ddi_corpus) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_discoverybench_biomedical` | [`allenai/discoverybench`](https://huggingface.co/datasets/allenai/discoverybench) |  | default | unknown | biomedical | qa | openText | no | yes | yes | no |
| `hf_ebm_nlp` | [`bigbio/ebm_nlp`](https://huggingface.co/datasets/bigbio/ebm_nlp) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_evidence_inference` | [`bigbio/evidence_inference`](https://huggingface.co/datasets/bigbio/evidence_inference) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_fgbench` | [`chembench/FGBench`](https://huggingface.co/datasets/chembench/FGBench) |  | default | unknown | chemistry | mcq | multipleChoice | no | yes | yes | no |
| `hf_fluorescence_prediction` | [`proteinglm/fluorescence_prediction`](https://huggingface.co/datasets/proteinglm/fluorescence_prediction) |  | default | unknown | protein | classification | exactMatch | no | yes | yes | no |
| `hf_gad` | [`bigbio/gad`](https://huggingface.co/datasets/bigbio/gad) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_gaianet_chemistry` | [`gaianet/chemistry`](https://huggingface.co/datasets/gaianet/chemistry) |  | default | unknown | chemistry | text | openText | no | yes | yes | no |
| `hf_genbio_proteingym_dms` | [`genbio-ai/ProteinGYM-DMS`](https://huggingface.co/datasets/genbio-ai/ProteinGYM-DMS) |  | default | unknown | protein | protein_fitness | exactNumeric | no | yes | yes | no |
| `hf_geneturing` | [`liuhu/GeneTuring`](https://huggingface.co/datasets/liuhu/GeneTuring) |  | default | unknown | genomics | qa | openText | no | yes | yes | no |
| `hf_hallmarks_of_cancer` | [`bigbio/hallmarks_of_cancer`](https://huggingface.co/datasets/bigbio/hallmarks_of_cancer) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_headqa` | [`dvilares/head_qa`](https://huggingface.co/datasets/dvilares/head_qa) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_healthcare_data` | [`Nicolybgs/healthcare_data`](https://huggingface.co/datasets/Nicolybgs/healthcare_data) |  | default | unknown | healthcare | classification | exactMatch | no | yes | yes | no |
| `hf_icliniq_10k` | [`lavita/ChatDoctor-HealthCareMagic-100k`](https://huggingface.co/datasets/lavita/ChatDoctor-HealthCareMagic-100k) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_jnlpba` | [`bigbio/jnlpba`](https://huggingface.co/datasets/bigbio/jnlpba) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_bace` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | bace | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_bbbp` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | bbbp | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_clintox` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | clintox | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_esol` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | esol | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_freesolv` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | freesolv | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_hiv` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | hiv | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_sider` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | sider | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_katielink_moleculenet_tox21` | [`katielink/moleculenet-benchmark`](https://huggingface.co/datasets/katielink/moleculenet-benchmark) | tox21 | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_lavita_medmcqa` | [`lavita/medical-qa-datasets`](https://huggingface.co/datasets/lavita/medical-qa-datasets) | medmcqa | validation | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_lavita_usmle_step1` | [`lavita/medical-qa-datasets`](https://huggingface.co/datasets/lavita/medical-qa-datasets) | usmle-self-assessment-step1 | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_lavita_usmle_step2` | [`lavita/medical-qa-datasets`](https://huggingface.co/datasets/lavita/medical-qa-datasets) | usmle-self-assessment-step2 | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_lavita_usmle_step3` | [`lavita/medical-qa-datasets`](https://huggingface.co/datasets/lavita/medical-qa-datasets) | usmle-self-assessment-step3 | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_litcovid` | [`ncats/litcovid`](https://huggingface.co/datasets/ncats/litcovid) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_liveqa_med` | [`bigbio/liveqa_med`](https://huggingface.co/datasets/bigbio/liveqa_med) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_longhealth` | [`longhealth/LongHealth`](https://huggingface.co/datasets/longhealth/LongHealth) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_lpm24_eval_caption` | [`language-plus-molecules/LPM-24_eval-caption`](https://huggingface.co/datasets/language-plus-molecules/LPM-24_eval-caption) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_lpm24_eval_molgen` | [`language-plus-molecules/LPM-24_eval-molgen`](https://huggingface.co/datasets/language-plus-molecules/LPM-24_eval-molgen) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_medcase_reasoning` | [`medical-reasoning/MedCaseReasoning`](https://huggingface.co/datasets/medical-reasoning/MedCaseReasoning) |  | default | unknown | clinical | qa | openText | no | yes | yes | no |
| `hf_medconceptsqa` | [`ofir408/MedConceptsQA`](https://huggingface.co/datasets/ofir408/MedConceptsQA) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_medexqa` | [`bigbio/medexqa`](https://huggingface.co/datasets/bigbio/medexqa) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_medical_question_pairs` | [`curaihealth/medical_questions_pairs`](https://huggingface.co/datasets/curaihealth/medical_questions_pairs) |  | default | unknown | medical | pair_classification | exactMatch | no | yes | yes | no |
| `hf_medication_qa` | [`bigbio/medication_qa`](https://huggingface.co/datasets/bigbio/medication_qa) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_medmcqa_explanations` | [`openlifescienceai/medmcqa`](https://huggingface.co/datasets/openlifescienceai/medmcqa) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_mednli` | [`bigbio/mednli`](https://huggingface.co/datasets/bigbio/mednli) |  | default | unknown | clinical | classification | exactMatch | no | yes | yes | no |
| `hf_mednli_augmented` | [`bigbio/mednli`](https://huggingface.co/datasets/bigbio/mednli) |  | default | unknown | clinical | classification | exactMatch | no | yes | yes | no |
| `hf_medpub_qa` | [`medpub/MedPub-QA`](https://huggingface.co/datasets/medpub/MedPub-QA) |  | default | unknown | biomedical | qa | openText | no | yes | yes | no |
| `hf_medqa_taiwan` | [`xuxuxuxuxu/MedQA_Taiwan_test`](https://huggingface.co/datasets/xuxuxuxuxu/MedQA_Taiwan_test) |  | default | unknown | medical | mcq | multipleChoice | no | yes | yes | no |
| `hf_medquad` | [`keivalya/MedQuad-MedicalQnADataset`](https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_meds_bench` | [`Henrychur/MedS-Bench`](https://huggingface.co/datasets/Henrychur/MedS-Bench) |  | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_medsts` | [`bigbio/medsts`](https://huggingface.co/datasets/bigbio/medsts) |  | default | unknown | clinical | regression | exactNumeric | no | yes | yes | no |
| `hf_meqsum` | [`bigbio/meqsum`](https://huggingface.co/datasets/bigbio/meqsum) |  | default | unknown | medical | summarization | openText | no | yes | yes | no |
| `hf_mol_instructions_pubchemqa` | [`zjunlp/Mol-Instructions`](https://huggingface.co/datasets/zjunlp/Mol-Instructions) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_moleculeace` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL1862_Ki | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculeace_chembl1871_ki` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL1871_Ki | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculeace_chembl204_ki` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL204_Ki | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculeace_chembl214_ki` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL214_Ki | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculeace_chembl228_ki` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL228_Ki | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculeace_chembl237_ec50` | [`karina-zadorozhny/moleculeace`](https://huggingface.co/datasets/karina-zadorozhny/moleculeace) | CHEMBL237_EC50 | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_bace` | [`scikit-fingerprints/MoleculeNet_BACE`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_BACE) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_bbbp` | [`scikit-fingerprints/MoleculeNet_BBBP`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_BBBP) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_clintox` | [`scikit-fingerprints/MoleculeNet_ClinTox`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_ClinTox) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_esol` | [`scikit-fingerprints/MoleculeNet_ESOL`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_ESOL) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_freesolv` | [`scikit-fingerprints/MoleculeNet_FreeSolv`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_FreeSolv) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_hiv` | [`scikit-fingerprints/MoleculeNet_HIV`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_HIV) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_lipophilicity` | [`scikit-fingerprints/MoleculeNet_Lipophilicity`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_Lipophilicity) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_sider` | [`scikit-fingerprints/MoleculeNet_SIDER`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_SIDER) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_moleculenet_toxcast` | [`scikit-fingerprints/MoleculeNet_ToxCast`](https://huggingface.co/datasets/scikit-fingerprints/MoleculeNet_ToxCast) |  | default | unknown | chemistry | molecule_property | exactMatch | no | yes | yes | no |
| `hf_mollangbench` | [`ChemFM/MolLangBench`](https://huggingface.co/datasets/ChemFM/MolLangBench) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_ms2` | [`bigbio/ms2`](https://huggingface.co/datasets/bigbio/ms2) |  | default | unknown | biomedical | summarization | openText | no | yes | yes | no |
| `hf_mts_dialogue_clinical_note` | [`har1/MTS_Dialogue-Clinical_Note`](https://huggingface.co/datasets/har1/MTS_Dialogue-Clinical_Note) |  | default | unknown | clinical | summarization | openText | no | yes | yes | no |
| `hf_ncbi_disease` | [`bigbio/ncbi_disease`](https://huggingface.co/datasets/bigbio/ncbi_disease) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_nlmchem` | [`bigbio/nlmchem`](https://huggingface.co/datasets/bigbio/nlmchem) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_openddi` | [`bigbio/ddi_corpus`](https://huggingface.co/datasets/bigbio/ddi_corpus) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_pgr` | [`bigbio/pgr`](https://huggingface.co/datasets/bigbio/pgr) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_ppi_benchmark` | [`bigbio/ppi`](https://huggingface.co/datasets/bigbio/ppi) |  | default | unknown | protein | classification | exactMatch | no | yes | yes | no |
| `hf_protein_fluorescence` | [`proteinea/fluorescence`](https://huggingface.co/datasets/proteinea/fluorescence) |  | default | unknown | protein | regression | exactNumeric | no | yes | yes | no |
| `hf_protein_solubility` | [`proteinea/solubility`](https://huggingface.co/datasets/proteinea/solubility) |  | default | unknown | protein | classification | exactMatch | no | yes | yes | no |
| `hf_protein_stability` | [`SaProtHub/Dataset-Meta-scale-protein-stability`](https://huggingface.co/datasets/SaProtHub/Dataset-Meta-scale-protein-stability) |  | default | unknown | protein | regression | exactNumeric | no | yes | yes | no |
| `hf_proteinlmbench_enzyme_cot` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | Enzyme_CoT | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_disease` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Involvement in disease | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_function` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Function | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_induction` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Induction | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_ptm` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Post-translational modification | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_subunit` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Subunit structure | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_proteinlmbench_uniprot_tissue` | [`tsynbio/ProteinLMBench`](https://huggingface.co/datasets/tsynbio/ProteinLMBench) | UniProt_Tissue specificity | default | unknown | protein | qa | openText | no | yes | yes | no |
| `hf_pubmed_200k_rct` | [`pietrolesci/pubmed-200k-rct`](https://huggingface.co/datasets/pietrolesci/pubmed-200k-rct) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_pubmed_abstract_classification` | [`uiyunkim-hub/pubmed-abstract`](https://huggingface.co/datasets/uiyunkim-hub/pubmed-abstract) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_pubmed_rct20k` | [`armanc/pubmed-rct20k`](https://huggingface.co/datasets/armanc/pubmed-rct20k) |  | default | unknown | biomedical | classification | exactMatch | no | yes | yes | no |
| `hf_raredis` | [`bigbio/raredis`](https://huggingface.co/datasets/bigbio/raredis) |  | default | unknown | medical | classification | exactMatch | no | yes | yes | no |
| `hf_rna_expression_hek` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | expression_HEK | default | unknown | rna | regression | exactNumeric | no | yes | yes | no |
| `hf_rna_expression_muscle` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | expression_Muscle | default | unknown | rna | regression | exactNumeric | no | yes | yes | no |
| `hf_rna_expression_pc3` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | expression_pc3 | default | unknown | rna | regression | exactNumeric | no | yes | yes | no |
| `hf_rna_mean_ribosome_load` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | mean_ribosome_load | default | unknown | rna | regression | exactNumeric | no | yes | yes | no |
| `hf_rna_modification_site` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | modification_site | default | unknown | rna | classification | exactMatch | no | yes | yes | no |
| `hf_rna_ncrna_family_bnoise0` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | ncrna_family_bnoise0 | default | unknown | rna | classification | exactMatch | no | yes | yes | no |
| `hf_rna_splice_site_acceptor` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | splice_site_acceptor | default | unknown | rna | classification | exactMatch | no | yes | yes | no |
| `hf_rna_splice_site_donor` | [`genbio-ai/rna-downstream-tasks`](https://huggingface.co/datasets/genbio-ai/rna-downstream-tasks) | splice_site_donor | default | unknown | rna | classification | exactMatch | no | yes | yes | no |
| `hf_smiles_caption_mol2text` | [`zjunlp/Mol-Instructions`](https://huggingface.co/datasets/zjunlp/Mol-Instructions) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |
| `hf_traitgym_mendelian_dna` | [`bolinas-dna/evals-traitgym_mendelian_v2_harness_255`](https://huggingface.co/datasets/bolinas-dna/evals-traitgym_mendelian_v2_harness_255) |  | default | unknown | dna | classification | exactMatch | no | yes | yes | no |
| `hf_usmle_step_series` | [`lavita/medical-qa-datasets`](https://huggingface.co/datasets/lavita/medical-qa-datasets) | usmle-self-assessment-step1 | default | unknown | medical | qa | openText | no | yes | yes | no |
| `hf_uspto_reaction_prediction` | [`yerevann/uspto`](https://huggingface.co/datasets/yerevann/uspto) |  | default | unknown | chemistry | qa | openText | no | yes | yes | no |

## Verification

Use the offline gate first:

```bash
python3 scripts/run_quick_suite.py
python3 scripts/release_gate.py --strict
```

For live source checks, run a tiny loader audit in an environment with HuggingFace access and accepted gated dataset terms:

```bash
python3 scripts/verify_benchmark_sources.py --benchmarks all
```
