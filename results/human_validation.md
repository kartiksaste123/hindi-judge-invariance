# Human validation — rater agreement

cells rated by both: 251

## Overall agreement
```json
{
 "meaning": {
  "n": 251,
  "raw": 0.912,
  "kappa": 0.188,
  "AC1": 0.907,
  "PABAK": 0.825
 },
 "label": {
  "n": 251,
  "raw": 0.976,
  "kappa": 0.0,
  "AC1": 0.976,
  "PABAK": 0.952
 },
 "naturalness": {
  "n": 251,
  "exact": 0.669,
  "within1": 0.996,
  "quad_kappa_observed": 0.361,
  "quad_kappa_1to5": 0.361,
  "mean_A": 3.92,
  "mean_B": 4.2
 }
}
```
## Per variant
```json
{
 "hi_deva": {
  "meaning": {
   "n": 91,
   "raw": 0.901,
   "kappa": 0.271,
   "AC1": 0.894,
   "PABAK": 0.802
  },
  "label": {
   "n": 91,
   "raw": 0.967,
   "kappa": 0.0,
   "AC1": 0.966,
   "PABAK": 0.934
  },
  "naturalness": {
   "n": 91,
   "exact": 0.582,
   "within1": 0.989,
   "quad_kappa_observed": 0.258,
   "quad_kappa_1to5": 0.258,
   "mean_A": 3.88,
   "mean_B": 4.29
  }
 },
 "hi_roman": {
  "meaning": {
   "n": 81,
   "raw": 0.901,
   "kappa": 0.167,
   "AC1": 0.895,
   "PABAK": 0.802
  },
  "label": {
   "n": 81,
   "raw": 0.988,
   "kappa": 0.0,
   "AC1": 0.988,
   "PABAK": 0.975
  },
  "naturalness": {
   "n": 81,
   "exact": 0.654,
   "within1": 1.0,
   "quad_kappa_observed": 0.377,
   "quad_kappa_1to5": 0.377,
   "mean_A": 3.85,
   "mean_B": 4.12
  }
 },
 "hi_cm": {
  "meaning": {
   "n": 79,
   "raw": 0.937,
   "kappa": 0.0,
   "AC1": 0.935,
   "PABAK": 0.873
  },
  "label": {
   "n": 79,
   "raw": 0.975,
   "kappa": 0.0,
   "AC1": 0.974,
   "PABAK": 0.949
  },
  "naturalness": {
   "n": 79,
   "exact": 0.785,
   "within1": 1.0,
   "quad_kappa_observed": 0.504,
   "quad_kappa_1to5": 0.504,
   "mean_A": 4.03,
   "mean_B": 4.19
  }
 }
}
```
## Meaning/Label disagreements

| variant | id | type | A(m/l) | B(m/l) | B notes |
|---|---|---|---|---|---|
| hi_cm | GPTInst-029 | REVIEW | Yes/Yes | Partly/Yes | Output 2 renders 'immediately after' as 'achanak baad' (suddenly after), losing the specified assessment timing. |
| hi_cm | GPTInst-030 | REVIEW | Yes/Yes | Partly/Yes | Output 2 drops 'increased' from customer engagement in the conclusion, changing growth to mere occurrence. |
| hi_cm | Natural-023 | SAMPLE | Yes/Yes | Partly/No | Output 1 reverses prediction inputs/targets; listed Output 2 has source-level factual errors about catastrophic forgetti |
| hi_cm | Natural-055 | SAMPLE | Yes/Yes | Partly/Yes | Output 1 changes the requested scraper from the assistant to the user. |
| hi_cm | Neighbor-085 | SAMPLE | Yes/Yes | Partly/Yes | The instruction narrows emails about topic 'x' to emails whose subject is 'x'. |
| hi_cm | Neighbor-086 | SAMPLE | Yes/Yes | Yes/No | Source-label concern: Output 1 offers more useful prevention advice; Output 2 overstates surface smoothness. |
| hi_deva | GPTInst-010 | REVIEW | Yes/Yes | Partly/Yes | निर्देश में 'deep' छूट गया है; केवल सामान्य रूप से वन कहा गया है। |
| hi_deva | GPTInst-016 | REVIEW | Yes/Yes | Partly/Yes | Output 1 changes nervously twitching spines into contracted spines. |
| hi_deva | GPTInst-044 | REVIEW | Yes/Yes | Partly/Yes | Output 2 में 'negotiation skills' को सामान्य बातचीत कौशल बना दिया गया है। |
| hi_deva | GPTInst-067 | REVIEW | Yes/Yes | Partly/Yes | Output 2 translates 'tentatively' as 'temporarily'; the pinky-finger error is already in the English. |
| hi_deva | GPTInst-076 | REVIEW | Yes/Yes | Partly/Yes | Output 1 translates a stage musical as 'music'; the self-fulfilling-prophecy phrasing is also awkward. |
| hi_deva | GPTInst-091 | SAMPLE | Yes/Yes | Partly/Yes | Output 2 turns “in various capacities” into users' abilities, rather than different ways of assisting. |
| hi_deva | GPTOut-001 | SAMPLE | Yes/Yes | Yes/No | Source-label concern: Output 1 includes an employee ID and concrete table; Output 2 omits an ID and department field. |
| hi_deva | Manual-031 | REVIEW | Partly/Yes | Yes/Yes |  |
| hi_deva | Manual-032 | SAMPLE | Yes/Yes | Partly/Yes | Output 1 translates “critical thinking” as “important thinking,” changing the named skill. |
| hi_deva | Manual-036 | REVIEW | Yes/Yes | Partly/Yes | 'Emergent properties' को 'आकस्मिक गुण' कहना अर्थ बदलता है; Output 2 की गलत संज्ञा स्रोत में भी है। |
| hi_deva | Manual-043 | SAMPLE | Yes/Yes | Yes/No | Source-label concern: Output 1 quotes the requested comparison; Output 2 does not cite it. |
| hi_deva | Neighbor-086 | SAMPLE | Yes/Yes | Yes/No | Source-label concern: Output 1 gives concrete adhesion remedies; Output 2's smoother-surface advice is unreliable. |
| hi_roman | GPTInst-016 | REVIEW | Yes/Yes | Partly/Yes | Output_1 changes nervously twitching spines to contracted spines and a legend to a proverb. |
| hi_roman | GPTInst-049 | REVIEW | Yes/Yes | Partly/Yes | Output_1 mistranslates plateaus as rocks. |
| hi_roman | GPTInst-051 | REVIEW | Yes/Yes | Partly/Yes | Output_2's greeting wishes for email delivery rather than the recipient's well-being. |
| hi_roman | GPTInst-058 | REVIEW | Yes/Yes | Partly/Yes | Output 2 repeatedly changes the source's 'compression psychotherapy' to 'compression therapy'. |
| hi_roman | GPTInst-073 | REVIEW | Yes/Yes | Partly/Yes | Output 1 turns the 1800s into a decade; both outputs repeatedly contain mixed-script 'manदंडon'. |
| hi_roman | GPTInst-076 | REVIEW | Yes/Yes | Partly/Yes | Output 1 drops 'seemed,' presenting the witch's unfair villainization as certain. |
| hi_roman | GPTOut-001 | SAMPLE | Yes/Yes | Yes/No | Source label questionable: Output 1 gives a concrete table and ID; Output 2 promises department reporting without a depa |
| hi_roman | Natural-035 | REVIEW | Partly/Yes | Yes/Yes |  |
| hi_roman | Neighbor-113 | SAMPLE | Yes/Yes | Partly/Yes | Instruction translates 'produce' as only vegetables, omitting fruit. |

## B Label=No items (source-label disagreements with LLMBar gold; not blocking)

- Natural-023 [hi_cm]: Output 1 reverses prediction inputs/targets; listed Output 2 has source-level factual errors about catastrophic forgetting.
- Neighbor-086 [hi_cm]: Source-label concern: Output 1 offers more useful prevention advice; Output 2 overstates surface smoothness.
- GPTOut-001 [hi_deva]: Source-label concern: Output 1 includes an employee ID and concrete table; Output 2 omits an ID and department field.
- Manual-043 [hi_deva]: Source-label concern: Output 1 quotes the requested comparison; Output 2 does not cite it.
- Neighbor-086 [hi_deva]: Source-label concern: Output 1 gives concrete adhesion remedies; Output 2's smoother-surface advice is unreliable.
- GPTOut-001 [hi_roman]: Source label questionable: Output 1 gives a concrete table and ID; Output 2 promises department reporting without a department field.

## Fixes applied

- hi_cm / source A: 5
- hi_cm / source B: 5
- hi_deva / source A: 7
- hi_deva / source A+B: 1
- hi_deva / source B: 8
- hi_deva / source B (A same issue): 1
- hi_roman / source A: 7
- hi_roman / source B: 8
- hi_roman / source B (A same issue): 1
- hi_roman / source B (extended to all occurrences): 1

## Rejected fixes

- hi_cm Natural-099 output_1 (src A): Meaning already Yes; fix turns the code-mixed variant into pure Hindi, violating the hi_cm definition (30-50% English).
- hi_deva GPTInst-010 input (src A): Superseded by B; adds "dense", not in source.
- hi_deva Natural-067 output_2 (src A): Superseded by B; English gloss in parentheses would leak the source word.

## Final status counts

| variant | status | n |
|---|---|---|
| hi_cm | dropped_no_translation | 1 |
| hi_cm | exclude_langdep | 31 |
| hi_cm | pass | 387 |
| hi_deva | dropped_no_translation | 1 |
| hi_deva | exclude_langdep | 31 |
| hi_deva | pass | 387 |
| hi_roman | dropped_no_translation | 1 |
| hi_roman | exclude_langdep | 31 |
| hi_roman | pass | 387 |

**core_ids: 387**