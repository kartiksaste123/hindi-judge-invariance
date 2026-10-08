# Repair pass summary

| variant | pass before→after | needs_review before→after | exclude_langdep before→after |
|---|---|---|---|
| hi_deva | 299 → 326 | 91 → 62 | 29 → 31 |
| hi_roman | 304 → 336 | 86 → 52 | 29 → 31 |
| hi_cm | 321 → 338 | 69 → 50 | 29 → 31 |

**core_ids: 255 → 303**
Newly excluded as language_dependent during repair: ['GPTInst-069', 'Manual-009']

## Reason breakdown after repair
### hi_deva
- verifier:label_preserved: 32
- language_dependent: 31
- verifier:meaning_output_2: 25
- verifier:meaning_output_1: 20
- check:devanagari_low: 12
- no_verdict: 5
- verifier:meaning_input: 4
- verifier:form_ok: 2
### hi_roman
- language_dependent: 31
- verifier:label_preserved: 27
- verifier:meaning_output_2: 24
- verifier:meaning_output_1: 17
- no_verdict: 8
- verifier:meaning_input: 7
- check:devanagari_nonzero: 1
- no_translation: 1
### hi_cm
- verifier:label_preserved: 33
- language_dependent: 31
- verifier:meaning_output_2: 19
- verifier:meaning_output_1: 18
- no_verdict: 7
- verifier:meaning_input: 3
- verifier:form_ok: 1

## Before/after examples (input field ≤400 chars)
### GPTInst-022 [hi_deva]
before: `नीचे दिए गए गद्यांश के लिए एक उपयुक्त शीर्षक सुझाएँ एक वैश्विक महामारी ने हॉस्पिटैलिटी उद्योग को अपनी कार्यप्रणालियों का पुनर्मूल्यांकन करने और स्वास्थ्य व सुरक्षा प्रोटोकॉल की एक नई दुनिया के अनुकूल ढलने के लिए मजबूर किया।`
after: `नीचे दिए गए गद्यांश के लिए एक उपयुक्त शीर्षक सुझाएँ एक वैश्विक महामारी ने हॉस्पिटैलिटी उद्योग को अपनी प्रथाओं का पुनर्मूल्यांकन करने और स्वास्थ्य और सुरक्षा प्रोटोकॉल की एक नई दुनिया के अनुकूल ढलने के लिए मजबूर किया।`

### GPTInst-003 [hi_roman]
before: `Mangal grah ke baare mein ek jhootha tathya banayein`
after: `Mars grah ke baare mein ek jhootha tathya banayein`

### GPTInst-045 [hi_cm]
before: `Mujhe 10 arguments do jo prove karein ki Earth flat hai.`
after: `Mujhe 10 arguments do jo flat Earth theory ke support mein hain.`

## Sanity check: do repairs favour the gold output?
Char-length ratio vs English among 116 repaired cells:
- gold output: mean 1.063, median 1.073, longer(>1.05) 64, shorter(<0.95) 16
- non-gold output: mean 1.068, median 1.065, longer(>1.05) 63, shorter(<0.95) 15

## Cost
924 repair-tagged calls, 0 errors, ~$7.69 token-estimated (exact neuron billing in llm_calls.jsonl).