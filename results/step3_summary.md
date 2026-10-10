# Step 3 summary (with human adjudication) — full 419-item translation + verification

| variant | pass | needs_review | exclude_langdep |
|---|---|---|---|
| hi_deva | 387 | 0 | 31 |
| hi_roman | 387 | 0 | 31 |
| hi_cm | 387 | 0 | 31 |

**core_ids: 387**

## Reason breakdown (per variant)
### hi_deva
- verifier:label_preserved: 31
- language_dependent: 31
- verifier:meaning_output_2: 24
- verifier:meaning_output_1: 20
- check:devanagari_low: 12
- no_verdict: 5
- verifier:form_ok: 3
- verifier:meaning_input: 2
### hi_roman
- language_dependent: 31
- verifier:label_preserved: 28
- verifier:meaning_output_2: 24
- verifier:meaning_output_1: 17
- no_verdict: 8
- verifier:meaning_input: 7
- no_translation: 1
### hi_cm
- verifier:label_preserved: 32
- language_dependent: 31
- verifier:meaning_output_2: 18
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
### language_dependent
- `GPTOut-044` [hi_cm]: '‘configure’ word ko syllables mein divide karo.'
- `Natural-036` [hi_cm]: "'sad' ke liye 10 synonyms list karo."
- `GPTOut-046` [hi_cm]: 'Hafte ke din yaad rakhne ke liye ek mnemonic batao.'
### no_translation
- `GPTInst-079` [hi_roman]: ''
### no_verdict
- `GPTInst-065` [hi_deva]: 'विंडोज में गिट के साथ SSH का उपयोग करने के लिए वेबस्टॉर्म को कैसे कॉन्फ़िगर करें?'
- `Neighbor-089` [hi_roman]: 'Ek kilogram loha ek kilogram rui se bhaari kyun hota hai?'
- `GPTInst-034` [hi_deva]: 'सुपरवाइज़्ड और अनसुपरवाइज़्ड लर्निंग के बीच दो अंतर बताएं।'
### verifier:form_ok
- `GPTInst-058` [hi_cm]: 'Compression therapy se pehle Ankle arm index na karne ke kya risks hain?'
- `GPTInst-058` [hi_deva]: 'जब आप कंप्रेशन थेरेपी से पहले एंकल आर्म इंडेक्स नहीं करते हैं तो क्या जोखिम होते हैं?'
- `Natural-067` [hi_deva]: 'शब्द "कोजेंट" का विलोम क्या है?'
### verifier:label_preserved
- `GPTInst-074` [hi_cm]: 'aapko kyu lagta hai ki moon ko shot down karna theek hai, hamare solar system ke andar ek nuclear-enable star banane ke bajaye?'
- `GPTInst-055` [hi_cm]: 'ek accha resume kaise likhein'
- `GPTInst-079` [hi_cm]: 'Children ke saath life ko aur zyada enjoy karne ke kuch ways kya hain?'
### verifier:meaning_input=changed
- `GPTInst-083` [hi_cm]: "Ek teenager ke baare mein ek creative story likho jo smoking ke baare mein soch raha hai. Ek creative 'choose your own adventure' story develop karo aur story ke agle part par jaane se pehle mujhse hamesha pucho ki kaunsa option choose karna hai."
- `GPTInst-011` [hi_roman]: 'Ek vishesh rasayanik pratikriya ki pratikriya dar par taapman kaise prabhav dalta hai, ise maapne ke liye ek prayog design karein.'
- `GPTInst-067` [hi_roman]: 'Aap ring fingers ki alag-alag lambaiyon ke baare mein kya jaante hain? Index finger se badi?'
### verifier:meaning_output_1=changed
- `GPTInst-052` [hi_cm]: 'Mujhe Boston se New York travel karna hai, price, speed aur convenience ke hisab se best options kya hain? Mere paas driving license nahi hai.'
- `GPTInst-011` [hi_roman]: 'Ek vishesh rasayanik pratikriya ki pratikriya dar par taapman kaise prabhav dalta hai, ise maapne ke liye ek prayog design karein.'
- `GPTInst-008` [hi_cm]: 'Ek press release likho jo ek naye product launch ko announce kar raha ho. ABC Corporation apna naya XYZ device release kar raha hai.'
### verifier:meaning_output_2=changed
- `GPTInst-042` [hi_roman]: '"Subah Jaldi Uthne ke Fayde" vishay par teen paragraph ka ek nibandh taiyar karein.'
- `GPTInst-009` [hi_cm]: 'Synopsis ke basis par ek movie ke peeche ka basic idea kuch lines mein describe karo. Synopsis: Ek passionate photographer conflicted hai jab uska best friend ek aisi ladki ke saath relationship start karta hai jise woh bhi pasand karta hai.'
- `GPTInst-067` [hi_deva]: 'आप तर्जनी उंगली से लंबी अनामिका उंगलियों की विभिन्न लंबाइयों के बारे में क्या जानते हैं?'

## Calls
4855 translation+verification calls logged total (cumulative incl. pilot), 0 errors, ~12513 min summed latency. See llm_calls.jsonl for per-call usage.