# Step 2 summary — full 419-item translation + verification

| variant | pass | needs_review | exclude_langdep |
|---|---|---|---|
| hi_deva | 326 | 62 | 31 |
| hi_roman | 336 | 52 | 31 |
| hi_cm | 338 | 50 | 31 |

**core_ids: 303**

## Reason breakdown (per variant)
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

## language_dependent × v1-style low-Devanagari flag (item-level)

- langdep & low-deva: 10
- langdep & not low-deva: 21
- not langdep & low-deva: 12
- neither: 376

## Random examples per failure reason (field text ≤400 chars)
### check:devanagari_low
- `Natural-025` [hi_deva]: 'संख्याओं की एक सूची लेने और संख्याओं का योग लौटाने के लिए एक फ़ंक्शन डिज़ाइन करें।'
- `Neighbor-015` [hi_deva]: "‘@mysite.com' से खत्म होने वाली किसी भी स्ट्रिंग से मेल खाने के लिए एक वैध रेगुलर एक्सप्रेशन बनाएँ।"
- `Natural-045` [hi_deva]: 'निम्नलिखित वाक्य पढ़ें और एक सुधार सुझाएँ। I am going to the the store.'
### check:devanagari_nonzero
- `GPTInst-073` [hi_roman]: 'AI ke liye naitik niyam aaj ke niyamon se kaise alag hote agar yeh technology 1930 ke dashak mein uplabdh hoti?'
### language_dependent
- `GPTOut-044` [hi_cm]: '‘configure’ word ko syllables mein divide karo.'
- `Natural-036` [hi_cm]: "'sad' ke liye 10 synonyms list karo."
- `GPTOut-046` [hi_cm]: 'Hafte ke din yaad rakhne ke liye ek mnemonic batao.'
### no_translation
- `GPTInst-079` [hi_roman]: ''
### no_verdict
- `GPTInst-065` [hi_deva]: 'विंडोज में गिट के साथ SSH का उपयोग करने के लिए वेबस्टॉर्म को कैसे कॉन्फ़िगर करें?'
- `Neighbor-089` [hi_roman]: 'Ek kilogram loha ek kilogram rui se bhaari kyun hota hai?'
- `GPTInst-034` [hi_cm]: 'Supervised aur unsupervised learning ke beech do differences batao.'
### verifier:form_ok
- `GPTInst-058` [hi_cm]: 'Compression therapy se pehle Ankle arm index na karne ke kya risks hain?'
- `GPTInst-058` [hi_deva]: 'जब आप कंप्रेशन थेरेपी से पहले एंकल आर्म इंडेक्स नहीं करते हैं तो क्या जोखिम होते हैं?'
- `Natural-045` [hi_deva]: 'निम्नलिखित वाक्य पढ़ें और एक सुधार सुझाएँ। I am going to the the store.'
### verifier:label_preserved
- `GPTInst-074` [hi_cm]: 'aapko kyu lagta hai ki moon ko shot down karna theek hai, hamare solar system ke andar ek nuclear-enable star banane ke bajaye?'
- `GPTInst-055` [hi_cm]: 'ek accha resume kaise likhein'
- `GPTInst-079` [hi_cm]: 'Children ke saath life ko aur zyada enjoy karne ke kuch ways kya hain?'
### verifier:meaning_input=changed
- `GPTInst-073` [hi_deva]: 'अगर एआई के लिए नैतिक नियम आज के नियमों से कैसे अलग होते, यदि यह तकनीक 1930 के दशक में उपलब्ध होती?'
- `GPTInst-011` [hi_roman]: 'Ek vishesh rasayanik pratikriya ki pratikriya dar par taapman kaise prabhav dalta hai, ise maapne ke liye ek prayog design karein.'
- `GPTInst-067` [hi_roman]: 'Aap ring fingers ki alag-alag lambaiyon ke baare mein kya jaante hain? Index finger se badi?'
### verifier:meaning_output_1=changed
- `GPTInst-052` [hi_cm]: 'Mujhe Boston se New York travel karna hai, price, speed aur convenience ke hisab se best options kya hain? Mere paas driving license nahi hai.'
- `GPTInst-011` [hi_roman]: 'Ek vishesh rasayanik pratikriya ki pratikriya dar par taapman kaise prabhav dalta hai, ise maapne ke liye ek prayog design karein.'
- `GPTInst-008` [hi_cm]: 'Ek press release likho jo ek naye product launch ko announce kar raha ho. ABC Corporation apna naya XYZ device release kar raha hai.'
### verifier:meaning_output_2=changed
- `GPTInst-038` [hi_cm]: 'Ek fictional narrative likho ek space journey ke baare mein.'
- `GPTInst-009` [hi_roman]: 'Synopsis ke aadhar par ek film ke peeche ke mool vichaar ko kuch panktiyon mein varnan karein. Synopsis: Ek junooni photographer duvidha mein pad jaata hai jab uska sabse achha dost ek aisi ladki ke saath rishta shuru karta hai jise woh bhi pasand karta hai.'
- `GPTInst-058` [hi_cm]: 'Compression therapy se pehle Ankle arm index na karne ke kya risks hain?'

## Calls
4812 translation+verification calls logged total (cumulative incl. pilot), 0 errors, ~12502 min summed latency. See llm_calls.jsonl for per-call usage.