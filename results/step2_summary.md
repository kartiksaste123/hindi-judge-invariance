# Step 2 summary — full 419-item translation + verification

| variant | pass | needs_review | exclude_langdep |
|---|---|---|---|
| hi_deva | 299 | 91 | 29 |
| hi_roman | 304 | 86 | 29 |
| hi_cm | 321 | 69 | 29 |

**core_ids: 255**

## Reason breakdown (per variant)
### hi_deva
- verifier:label_preserved: 52
- verifier:meaning_output_2: 36
- language_dependent: 29
- verifier:meaning_output_1: 26
- check:devanagari_low: 19
- verifier:form_ok: 8
- verifier:meaning_input: 6
- no_verdict: 5
- check:len_ratio:output_2: 1
### hi_roman
- verifier:label_preserved: 51
- verifier:meaning_output_2: 35
- language_dependent: 29
- verifier:meaning_output_1: 28
- check:devanagari_nonzero: 15
- verifier:meaning_input: 12
- no_verdict: 10
- verifier:form_ok: 7
- no_translation: 2
### hi_cm
- verifier:label_preserved: 48
- language_dependent: 29
- verifier:meaning_output_1: 27
- verifier:meaning_output_2: 24
- no_verdict: 8
- verifier:meaning_input: 8
- check:devanagari_nonzero: 2
- check:len_ratio:input: 1
- verifier:form_ok: 1

## language_dependent × v1-style low-Devanagari flag (item-level)

- langdep & low-deva: 9
- langdep & not low-deva: 20
- not langdep & low-deva: 19
- neither: 371

## Random examples per failure reason (field text ≤400 chars)
### check:devanagari_low
- `GPTOut-020` [hi_deva]: '2x^2 + 5x का अवकलज (derivative) ज्ञात करें।'
- `GPTOut-045` [hi_deva]: 'दिए गए शब्द पर छठी कक्षा के स्तर की शब्दावली प्रश्नोत्तरी बनाएँ। Vivacious'
- `Manual-009` [hi_deva]: 'इन्हें शब्दकोषीय क्रम में छाँटें: \n\napples, grapes, bananas, oranges, kiwi, pears, plums, oranges, cherries, apples, tangerines, peaches'
### check:devanagari_nonzero
- `Neighbor-101` [hi_roman]: 'Nimnalikhit entry ka saaransh dijiye'
- `Neighbor-086` [hi_roman]: 'Mujhe apne 3D prints ke printing surface se poora hone se pehle hi alag ho jaane mein pareshani ho rahi hai. Aisa kyon hota hai aur ise hone se rokne ke kuch tareeke kya hain?'
- `GPTInst-083` [hi_roman]: 'Ek teenager ke baare mein ek creative kahani likho jo smoking karne ke baare mein soch raha hai. Ek creative choose your own adventure kahani banao aur kahani ke agle hisse par jaane se pehle mujhse poochte raho ki ek option kaise chunein.'
### check:len_ratio:input
- `Neighbor-127` [hi_cm]: 'mujhe 5 saal ke bachche ki tarah samjhao'
### check:len_ratio:output_2
- `Neighbor-058` [hi_deva]: 'आपको यह वर्गीकृत करना है कि निम्नलिखित टेक्स्ट एक राय है या नहीं। अगर यह एक राय है तो "राय" आउटपुट करें, अगर यह एक राय नहीं है तो "तथ्य" आउटपुट करें। Apple शानदार फ़ोन बनाता है'
### language_dependent
- `GPTInst-086` [hi_deva]: 'क्या आप निम्नलिखित वाक्यों को सही कर सकते हैं?\n\nहमें हाल ही में देखी गई किसी फ़िल्म या टीवी सीरीज़ के बारे में बताएं। यह किस बारे में थी? इसमें क्या अच्छा था?\nमैंने रीसेंटली सिक्स सेंसेस के बारे में देखा।\nयह फिल इस बारे में है कि अगर आप धीरे-धीरे अपनी इंद्रियां खो देते हैं तो आपका जीवन कैसे बदल जाएगा।\nमैं उस तरह का व्यक्ति नहीं हूं जिसे धीमी गति वाली मूवी पसंद है।\nलेकिन मैंने इसे बिना किसी ब्रेक क'
- `Neighbor-052` [hi_deva]: '"umbrella" शब्द पर आधारित एक श्लेष बनाएँ।'
- `GPTOut-044` [hi_roman]: '‘configure’ shabd ko syllables mein baantein.'
### no_translation
- `Natural-007` [hi_roman]: ''
- `GPTInst-079` [hi_roman]: ''
### no_verdict
- `GPTInst-003` [hi_roman]: 'Mangal grah ke baare mein ek jhootha tathya banayein'
- `GPTOut-012` [hi_deva]: 'त्रिभुज का क्षेत्रफल ज्ञात करें। आधार: 5cm; ऊंचाई: 6cm'
- `GPTOut-007` [hi_roman]: 'Di gayi velocity aur cross-sectional area se volumetric flow rate nirdharit karein. Velocity: 2 m/s\nCross-sectional area: 5 m^2'
### verifier:form_ok
- `Neighbor-013` [hi_deva]: 'यूएसए में उन पाँच जगहों के नाम बताइए जो लोकप्रिय पर्यटन स्थल हैं।'
- `GPTOut-014` [hi_deva]: 'एक ऐरे को सॉर्ट करने के लिए एक स्यूडोकोड जेनरेट करें।'
- `Neighbor-086` [hi_roman]: 'Mujhe apne 3D prints ke printing surface se poora hone se pehle hi alag ho jaane mein pareshani ho rahi hai. Aisa kyon hota hai aur ise hone se rokne ke kuch tareeke kya hain?'
### verifier:label_preserved
- `Manual-036` [hi_deva]: 'मनोविज्ञान मनुष्यों और गैर-मनुष्यों में मन और व्यवहार का अध्ययन है। मनोवैज्ञानिक मस्तिष्क के आकस्मिक गुणों को समझने की कोशिश करते हैं, और इस अनुशासन को न्यूरोसाइंस से जोड़ते हैं। सामाजिक वैज्ञानिकों के रूप में, मनोवैज्ञानिकों का लक्ष्य व्यक्तियों और समूहों के व्यवहार को समझना है। क्या मनोविज्ञान का कोई ऐसा क्षेत्र है जो इस बात से संबंधित है कि कोई व्यक्ति अपने आसपास की वस्तुओं और स्थानों पर कैसे प'
- `Neighbor-041` [hi_roman]: 'Do logon ke beech ek vartalap banayein jo weekend ke liye apne plans par charcha kar rahe hain.'
- `Natural-013` [hi_deva]: 'टीकाकरण संक्रामक रोगों से व्यक्तियों और समुदायों की रक्षा के लिए कैसे काम करता है, और हर्ड इम्युनिटी क्या है?'
### verifier:meaning_input=changed
- `GPTInst-038` [hi_roman]: 'Ek antariksh yatra ke baare mein ek kalpanik kahani likhein'
- `GPTInst-087` [hi_deva]: 'नागार्जुन के विचार संप्रदाय के लिए मन का क्या महत्व है?'
- `Natural-096` [hi_roman]: 'Nimnlikhit vakya ko poora karein: "Yesterday it was raining, so I put on my ____."'
### verifier:meaning_output_1=changed
- `GPTInst-049` [hi_cm]: 'Ek detailed prompt likho jo ek image generator (jaise DALL-E, Midjourney ya Stable Diffusion) ke saath use kiya ja sake, jo sabse impressive rainforest ko depict kare.'
- `GPTInst-008` [hi_roman]: 'Ek press release likhein jo ek naye product launch ki ghoshna kar raha ho. ABC Corporation apna naya XYZ device release kar raha hai'
- `GPTInst-016` [hi_cm]: 'Ek rabbit jo jungle mein ek adventurous squirrel ke saath rehta hai, uske baare mein ek story banao.'
### verifier:meaning_output_2=changed
- `GPTInst-076` [hi_roman]: "Hi aap kaise hain.\n\nMera ek ajeeb sa sawaal hai. Wizard of Oz mein, ek ghar west ki witch par girta hai, lekin Glenda, 'good witch' kehti hai ki woh west ki evil witch hai aur us par bharosa nahi karna chahiye. Lekin uska sabse pehla kaam Dorothy ko dhokha dekar uski abhi-abhi mari hui behen ke joote churwana hai, aur phir Dorothy se jhoot bolna hai ki ghar jaane ka ek hi raasta hai, Glenda ke ekm"
- `GPTInst-056` [hi_roman]: 'Main McAffe ko kaise uninstall karun aur Windows Defender ko phir se enable karun?'
- `GPTInst-084` [hi_roman]: 'Automotive spare parts ki sales mein 3 startup ideas batao. Startup ideas ka mission strong aur compelling hona chahiye. Startup ideas ka naam cool aur interesting hona chahiye. Ideas itne compelling hone chahiye ki investors millions of dollars invest karne ke liye excited ho jaayein.'

## Calls
4812 translation+verification calls logged total (cumulative incl. pilot), 0 errors, ~12502 min summed latency. See llm_calls.jsonl for per-call usage.