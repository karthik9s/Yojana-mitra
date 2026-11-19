/* Yojana Mitra front-end (no build step). */
(() => {
  "use strict";

  const I18N = {
    en: {
      tagline: "Your guide to government schemes in Andhra Pradesh",
      heroTitle: "Tell us about yourself. We'll find the schemes you can claim.",
      heroLead: "Describe yourself in your own words, in English, Telugu or Hindi. Mention age, work, family, land, income, village or town.",
      placeholder: "e.g. I'm a 45-year-old woman farmer in a village near Guntur with 2 acres. My two children go to school. We have a white ration card.",
      speak: "Speak", listening: "Listening… speak now", find: "Find my schemes", tryExample: "Try:",
      yourProfile: "Your profile", edit: "Edit", done: "Close", update: "Update results",
      moreQuestions: "Answer to unlock more schemes", askTitle: "Ask a question",
      askHint: "e.g. \"What documents do I need for Talliki Vandanam?\"", askPh: "Type your question…", ask: "Ask",
      eligible: "You are eligible", need_info: "Need a few more details", if_applicable: "If this applies to you",
      not_eligible: "Not eligible right now",
      focusStudent: (x) => `You're a student, so schemes for ${x} are shown first. Other schemes you qualify for are further down.`,
      focusAsked: (x) => `Showing schemes for ${x} first, as you asked. Other schemes you qualify for are further down.`,
      focusEligible: (x) => `Eligible for ${x}`, focusNeed: (x) => `Possible for ${x} (answer a question)`,
      otherEligible: "You also qualify for (other schemes)", otherNeed: "Other schemes that need details",
      eligibleHint: "Based on what you told us. Conditions marked ❔ were assumed, so please confirm them.",
      need_infoHint: "Answer the questions on the left to confirm these.",
      if_applicableHint: "These depend on situations you didn't mention (disability, pregnancy, illness, business plans…).",
      not_eligibleHint: "At least one rule is not met.",
      show: "Show", hide: "Hide", explain: "Explain & how to apply", hideExplain: "Hide details",
      portal: "Official portal ↗", state: "AP State", central: "Central",
      unlocks: (n) => `unlocks ${n}`, yes: "Yes", emptyMsg: "Tell us a little about yourself first: age, work, family income, where you live.", no: "No", save: "Save", sources: "Sources",
      passages: "Guideline passages used", method_llm: "Understood with AI",
      method_rules: "Understood with offline rules (add a Groq API key for AI understanding)",
      method_form: "From the form", nothingFound: "Nothing here.", errorMsg: "Something went wrong. Please try again.",
      aiOn: "AI on", aiOff: "Offline mode", unknownQ: "Not sure",
      howTitle: "How it works", how1t: "1. Understand", how2t: "2. Match", how3t: "3. Explain",
      how1: "Your description is turned into a profile: age, gender, work, land, income and more.",
      how2: "A knowledge graph of schemes and their rules is queried, (Scheme)→REQUIRES→(Criterion).",
      how3: "Each match is explained from official guideline text, with sources you can check.",
      disclaimer: "Yojana Mitra is an independent helper, not a government website. Rules and amounts change, so always confirm at your Village/Ward Secretariat or the official portal before applying.",
    },
    te: {
      tagline: "ఆంధ్రప్రదేశ్ ప్రభుత్వ పథకాలకు మీ మార్గదర్శి",
      heroTitle: "మీ గురించి చెప్పండి. మీకు వర్తించే పథకాలను మేము కనుగొంటాం.",
      heroLead: "మీ మాటల్లో తెలుగు, ఇంగ్లీష్ లేదా హిందీలో చెప్పండి: వయస్సు, పని, కుటుంబం, భూమి, ఆదాయం, ఊరు.",
      placeholder: "ఉదా: నేను గుంటూరు దగ్గర గ్రామంలో 45 ఏళ్ల మహిళా రైతును, 2 ఎకరాల భూమి ఉంది. ఇద్దరు పిల్లలు బడికి వెళ్తున్నారు. తెల్ల రేషన్ కార్డు ఉంది.",
      speak: "మాట్లాడండి", listening: "వింటున్నాం… మాట్లాడండి", find: "నా పథకాలు చూపించు", tryExample: "ప్రయత్నించండి:",
      yourProfile: "మీ వివరాలు", edit: "మార్చు", done: "మూసివేయి", update: "ఫలితాలు నవీకరించు",
      moreQuestions: "మరిన్ని పథకాల కోసం సమాధానం ఇవ్వండి", askTitle: "ప్రశ్న అడగండి",
      askHint: "ఉదా: \"తల్లికి వందనం కోసం ఏ పత్రాలు కావాలి?\"", askPh: "మీ ప్రశ్న టైప్ చేయండి…", ask: "అడుగు",
      eligible: "మీరు అర్హులు", need_info: "మరికొన్ని వివరాలు కావాలి", if_applicable: "మీకు వర్తిస్తే",
      not_eligible: "ప్రస్తుతం అర్హత లేదు",
      focusStudent: (x) => `మీరు విద్యార్థి కాబట్టి ${x}కు సంబంధించిన పథకాలు ముందుగా చూపిస్తున్నాం. మిగతా పథకాలు కింద ఉన్నాయి.`,
      focusAsked: (x) => `మీరు అడిగినట్లు ${x}కు సంబంధించిన పథకాలు ముందుగా చూపిస్తున్నాం. మిగతా పథకాలు కింద ఉన్నాయి.`,
      focusEligible: (x) => `${x} కోసం మీరు అర్హులు`, focusNeed: (x) => `${x} కోసం సాధ్యమయ్యేవి (ప్రశ్నకు సమాధానం ఇవ్వండి)`,
      otherEligible: "ఇతర పథకాలకు కూడా అర్హులు", otherNeed: "వివరాలు కావాల్సిన ఇతర పథకాలు",
      eligibleHint: "మీరు చెప్పిన వివరాల ఆధారంగా. ❔ గుర్తు ఉన్నవి ఊహించినవి, దయచేసి నిర్ధారించండి.",
      need_infoHint: "ఎడమవైపు ప్రశ్నలకు సమాధానం ఇవ్వండి.",
      if_applicableHint: "మీరు చెప్పని పరిస్థితులపై ఆధారపడి ఉంటాయి (వైకల్యం, గర్భం, వ్యాధి, వ్యాపారం…).",
      not_eligibleHint: "కనీసం ఒక నిబంధన నెరవేరలేదు.",
      show: "చూపించు", hide: "దాచు", explain: "వివరాలు & దరఖాస్తు విధానం", hideExplain: "దాచు",
      portal: "అధికారిక పోర్టల్ ↗", state: "ఏపీ రాష్ట్రం", central: "కేంద్రం",
      unlocks: (n) => `${n} పథకాలు`, yes: "అవును", emptyMsg: "ముందుగా మీ గురించి కొంచెం చెప్పండి: వయస్సు, పని, కుటుంబ ఆదాయం, ఊరు.", no: "కాదు", save: "సేవ్", sources: "మూలాలు",
      passages: "ఉపయోగించిన మార్గదర్శక భాగాలు", method_llm: "AI ద్వారా అర్థం చేసుకున్నాం",
      method_rules: "ఆఫ్‌లైన్ నియమాలతో అర్థం చేసుకున్నాం", method_form: "ఫారం నుండి",
      nothingFound: "ఏమీ లేవు.", errorMsg: "ఏదో పొరపాటు జరిగింది. మళ్లీ ప్రయత్నించండి.",
      aiOn: "AI ఆన్", aiOff: "ఆఫ్‌లైన్", unknownQ: "తెలియదు",
      howTitle: "ఇది ఎలా పనిచేస్తుంది", how1t: "1. అర్థం చేసుకోవడం", how2t: "2. సరిపోల్చడం", how3t: "3. వివరించడం",
      how1: "మీ వివరణ నుండి వయస్సు, లింగం, పని, భూమి, ఆదాయం వంటి వివరాలు తీసుకుంటాం.",
      how2: "పథకాలు మరియు వాటి నిబంధనల నాలెడ్జ్ గ్రాఫ్‌లో వెతుకుతాం.",
      how3: "ప్రతి పథకాన్ని అధికారిక మార్గదర్శకాల ఆధారంగా, మూలాలతో వివరిస్తాం.",
      disclaimer: "యోజన మిత్ర ఒక స్వతంత్ర సహాయకుడు, ప్రభుత్వ వెబ్‌సైట్ కాదు. దరఖాస్తు చేసే ముందు గ్రామ/వార్డు సచివాలయంలో లేదా అధికారిక పోర్టల్‌లో నిర్ధారించుకోండి.",
    },
    hi: {
      tagline: "आंध्र प्रदेश की सरकारी योजनाओं के लिए आपका मार्गदर्शक",
      heroTitle: "अपने बारे में बताइए। हम आपकी योजनाएँ ढूँढेंगे।",
      heroLead: "अपने शब्दों में हिंदी, तेलुगु या अंग्रेज़ी में लिखें: उम्र, काम, परिवार, ज़मीन, आय, गाँव या शहर।",
      placeholder: "जैसे: मैं गुंटूर के पास एक गाँव में 45 साल की महिला किसान हूँ, 2 एकड़ ज़मीन है। दो बच्चे स्कूल जाते हैं।",
      speak: "बोलें", listening: "सुन रहे हैं… बोलिए", find: "मेरी योजनाएँ खोजें", tryExample: "आज़माएँ:",
      yourProfile: "आपकी जानकारी", edit: "बदलें", done: "बंद करें", update: "परिणाम अपडेट करें",
      moreQuestions: "और योजनाओं के लिए जवाब दें", askTitle: "सवाल पूछें",
      askHint: "जैसे: \"तल्लिकी वंदनम के लिए कौन से दस्तावेज़ चाहिए?\"", askPh: "अपना सवाल लिखें…", ask: "पूछें",
      eligible: "आप पात्र हैं", need_info: "कुछ और जानकारी चाहिए", if_applicable: "अगर आप पर लागू हो",
      not_eligible: "अभी पात्र नहीं",
      focusStudent: (x) => `आप छात्र हैं, इसलिए ${x} से जुड़ी योजनाएँ पहले दिखाई गई हैं। बाकी योजनाएँ नीचे हैं।`,
      focusAsked: (x) => `आपके पूछे अनुसार ${x} से जुड़ी योजनाएँ पहले दिखाई गई हैं। बाकी योजनाएँ नीचे हैं।`,
      focusEligible: (x) => `${x} के लिए आप पात्र हैं`, focusNeed: (x) => `${x} के लिए संभव (सवाल का जवाब दें)`,
      otherEligible: "अन्य योजनाएँ जिनके लिए आप पात्र हैं", otherNeed: "अन्य योजनाएँ जिनके लिए जानकारी चाहिए",
      eligibleHint: "आपकी दी गई जानकारी के आधार पर। ❔ वाली शर्तें मान ली गई हैं, कृपया पुष्टि करें।",
      need_infoHint: "बाईं ओर के सवालों का जवाब दें।",
      if_applicableHint: "ये उन स्थितियों पर निर्भर हैं जो आपने नहीं बताईं (दिव्यांगता, गर्भावस्था, बीमारी, व्यवसाय…)।",
      not_eligibleHint: "कम से कम एक शर्त पूरी नहीं होती।",
      show: "दिखाएँ", hide: "छिपाएँ", explain: "विवरण और आवेदन कैसे करें", hideExplain: "छिपाएँ",
      portal: "आधिकारिक पोर्टल ↗", state: "एपी राज्य", central: "केंद्र",
      unlocks: (n) => `${n} योजनाएँ`, yes: "हाँ", emptyMsg: "पहले अपने बारे में थोड़ा बताइए: उम्र, काम, परिवार की आमदनी, आप कहाँ रहते हैं।", no: "नहीं", save: "सेव", sources: "स्रोत",
      passages: "इस्तेमाल किए गए दिशानिर्देश अंश", method_llm: "AI से समझा गया",
      method_rules: "ऑफ़लाइन नियमों से समझा गया", method_form: "फ़ॉर्म से",
      nothingFound: "कुछ नहीं।", errorMsg: "कुछ गलत हुआ। फिर से कोशिश करें।",
      aiOn: "AI चालू", aiOff: "ऑफ़लाइन", unknownQ: "पता नहीं",
      howTitle: "यह कैसे काम करता है", how1t: "1. समझना", how2t: "2. मिलान", how3t: "3. समझाना",
      how1: "आपके विवरण से उम्र, लिंग, काम, ज़मीन, आय जैसी जानकारी निकाली जाती है।",
      how2: "योजनाओं और उनके नियमों के नॉलेज ग्राफ़ में खोज की जाती है।",
      how3: "हर योजना को आधिकारिक दिशानिर्देशों से, स्रोतों के साथ समझाया जाता है।",
      disclaimer: "योजना मित्र एक स्वतंत्र सहायक है, सरकारी वेबसाइट नहीं। आवेदन से पहले ग्राम/वार्ड सचिवालय या आधिकारिक पोर्टल पर पुष्टि करें।",
    },
  };
  // Copy for the redesigned, friendlier UI (overrides / additions per language).
  const COPY = {
    en: {
      heroTag: "43 schemes · Telugu, Hindi & English · free",
      heroTitle1: "Benefits you deserve,", heroTitle2: "found in seconds.",
      heroLead: "Just tell us about yourself the way you'd tell a friend. We'll match you to scholarships, pensions, farm support and more, and show you exactly how to claim them.",
      placeholder: "e.g. I'm 22, studying B.Tech, family income below 1 lakh, from a village near Guntur…",
      speakHint: "Tap the mic to speak", tryExample: "Or try someone like…", quickQ: "⚡ Quick questions",
      moreQuestions: "Answer to unlock more", yourProfile: "What we understood", askKicker: "💬 Ask anything", askTitle: "Got a question?",
      how1t: "Talk naturally", how1: "Type or speak in Telugu, Hindi or English. No forms to fill.",
      how2t: "Smart matching", how2: "We check your details against the real rules of every scheme.",
      how3t: "Know how to claim", how3: "Documents, steps and the official link for each benefit.",
      bigYes: (n) => `🎉 You can claim ${n} scheme${n === 1 ? "" : "s"}`,
      bigNone: "Let's find your benefits 🔍", subNone: "Answer a couple of quick questions and we'll check again.",
      sub: "Here's what we found for you. Tap a card to see how to apply.",
      chipEligible: (n) => `✅ ${n} eligible`, chipNeed: (n) => `🧩 ${n} almost there`, chipMaybe: (n) => `💡 ${n} if applicable`,
      whyMet: (n) => `<span class="tick">✓ ${n} met</span>`, whyConfirm: (n) => `<span class="q">❔ ${n} to confirm</span>`,
      whyMissing: (n) => `<span class="miss">? ${n} unknown</span>`, whyNot: (n) => `<span style="color:var(--bad)">✗ ${n} not met</span>`,
      explain: "How to apply", hideExplain: "Hide", portal: "Official site ↗",
      st_eligible: "Eligible", st_need_info: "Almost there",
      need_infoHint: "Answer the quick questions to confirm these.",
    },
    te: {
      heroTag: "43 పథకాలు · తెలుగు, హిందీ & ఇంగ్లీష్ · ఉచితం",
      heroTitle1: "మీకు దక్కాల్సిన ప్రయోజనాలు,", heroTitle2: "క్షణాల్లో కనుగొనండి.",
      heroLead: "స్నేహితుడికి చెప్పినట్టు మీ గురించి చెప్పండి. స్కాలర్‌షిప్‌లు, పింఛన్లు, రైతు సాయం వంటివి కనుగొని, ఎలా పొందాలో చూపిస్తాం.",
      placeholder: "ఉదా: నాకు 22 ఏళ్లు, బీటెక్ చదువుతున్నాను, కుటుంబ ఆదాయం లక్ష లోపు, గుంటూరు దగ్గర గ్రామం…",
      speakHint: "మాట్లాడటానికి మైక్ నొక్కండి", tryExample: "లేదా ఇలాంటి వారిని ప్రయత్నించండి…", quickQ: "⚡ చిన్న ప్రశ్నలు",
      moreQuestions: "మరిన్ని పథకాల కోసం సమాధానం ఇవ్వండి", yourProfile: "మేము అర్థం చేసుకున్నది", askKicker: "💬 ఏదైనా అడగండి", askTitle: "ప్రశ్న ఉందా?",
      how1t: "సహజంగా మాట్లాడండి", how1: "తెలుగు, హిందీ లేదా ఇంగ్లీష్‌లో టైప్ చేయండి లేదా మాట్లాడండి. ఫారాలు అక్కర్లేదు.",
      how2t: "తెలివైన సరిపోలిక", how2: "ప్రతి పథకం నిజమైన నిబంధనలతో మీ వివరాలను సరిచూస్తాం.",
      how3t: "ఎలా పొందాలో తెలుసుకోండి", how3: "ప్రతి పథకానికి పత్రాలు, దశలు, అధికారిక లింక్.",
      bigYes: (n) => `🎉 మీరు ${n} పథకాలు పొందవచ్చు`,
      bigNone: "మీ ప్రయోజనాలను కనుగొందాం 🔍", subNone: "కొన్ని చిన్న ప్రశ్నలకు సమాధానం ఇవ్వండి.",
      sub: "మీ కోసం కనుగొన్నవి ఇవే. దరఖాస్తు విధానం కోసం కార్డును నొక్కండి.",
      chipEligible: (n) => `✅ ${n} అర్హత`, chipNeed: (n) => `🧩 ${n} దాదాపు`, chipMaybe: (n) => `💡 ${n} వర్తిస్తే`,
      whyMet: (n) => `<span class="tick">✓ ${n} సరిపోయాయి</span>`, whyConfirm: (n) => `<span class="q">❔ ${n} నిర్ధారించాలి</span>`,
      whyMissing: (n) => `<span class="miss">? ${n} తెలియదు</span>`, whyNot: (n) => `<span style="color:var(--bad)">✗ ${n} సరిపోలేదు</span>`,
      explain: "ఎలా దరఖాస్తు చేయాలి", hideExplain: "దాచు", portal: "అధికారిక సైట్ ↗",
      st_eligible: "అర్హులు", st_need_info: "దాదాపు",
    },
    hi: {
      heroTag: "43 योजनाएँ · तेलुगु, हिंदी और अंग्रेज़ी · मुफ़्त",
      heroTitle1: "आपके हक़ के फ़ायदे,", heroTitle2: "पलों में खोजें।",
      heroLead: "जैसे किसी दोस्त को बताते हैं, वैसे अपने बारे में बताइए। हम छात्रवृत्ति, पेंशन, किसान सहायता जैसी योजनाएँ ढूँढकर बताएँगे कि कैसे पाएँ।",
      placeholder: "जैसे: मैं 22 साल का हूँ, बीटेक कर रहा हूँ, परिवार की आय 1 लाख से कम, गुंटूर के पास गाँव…",
      speakHint: "बोलने के लिए माइक दबाएँ", tryExample: "या इनमें से किसी को आज़माएँ…", quickQ: "⚡ छोटे सवाल",
      moreQuestions: "और योजनाओं के लिए जवाब दें", yourProfile: "हमने क्या समझा", askKicker: "💬 कुछ भी पूछें", askTitle: "कोई सवाल?",
      how1t: "सहज बात करें", how1: "तेलुगु, हिंदी या अंग्रेज़ी में लिखें या बोलें। कोई फ़ॉर्म नहीं।",
      how2t: "स्मार्ट मिलान", how2: "हर योजना के असली नियमों से आपकी जानकारी मिलाते हैं।",
      how3t: "पाने का तरीका जानें", how3: "हर योजना के दस्तावेज़, चरण और आधिकारिक लिंक।",
      bigYes: (n) => `🎉 आप ${n} योजनाओं का लाभ ले सकते हैं`,
      bigNone: "आइए आपके फ़ायदे खोजें 🔍", subNone: "कुछ छोटे सवालों के जवाब दें।",
      sub: "आपके लिए यह मिला। आवेदन का तरीका देखने के लिए कार्ड खोलें।",
      chipEligible: (n) => `✅ ${n} पात्र`, chipNeed: (n) => `🧩 ${n} लगभग`, chipMaybe: (n) => `💡 ${n} अगर लागू हो`,
      whyMet: (n) => `<span class="tick">✓ ${n} पूरी</span>`, whyConfirm: (n) => `<span class="q">❔ ${n} पुष्टि करें</span>`,
      whyMissing: (n) => `<span class="miss">? ${n} अज्ञात</span>`, whyNot: (n) => `<span style="color:var(--bad)">✗ ${n} पूरी नहीं</span>`,
      explain: "आवेदन कैसे करें", hideExplain: "छिपाएँ", portal: "आधिकारिक साइट ↗",
      st_eligible: "पात्र", st_need_info: "लगभग",
    },
  };
  for (const l of Object.keys(COPY)) Object.assign(I18N[l], COPY[l]);
  const CATEGORY_ICON = {
    education: ["🎓", "#e6e0ff"], pension: ["🤝", "#ffe0ec"], retirement_savings: ["🪙", "#fff1c9"],
    agriculture: ["🌾", "#e5f6d5"], women: ["👩", "#ffe3f1"], household: ["🔥", "#ffe6d6"],
    livelihood: ["💼", "#dff1ff"], health: ["🏥", "#dcf7ec"], housing: ["🏠", "#ffeccc"],
    insurance: ["🛡️", "#e3ecff"], savings: ["💰", "#fdf0c4"],
  };
  const VALUE_LABELS = {
    te: { female: "స్త్రీ", male: "పురుషుడు", transgender: "ట్రాన్స్‌జెండర్", rural: "గ్రామీణ", urban: "పట్టణ",
          farmer: "రైతు", tenant_farmer: "కౌలు రైతు", agricultural_labourer: "వ్యవసాయ కూలీ", fisherman: "మత్స్యకారుడు",
          weaver: "చేనేత", student: "విద్యార్థి", widowed: "వితంతువు", married: "వివాహిత", unmarried: "అవివాహిత",
          auto_driver: "ఆటో డ్రైవర్", street_vendor: "వీధి వ్యాపారి", true: "అవును", false: "కాదు" },
    hi: { female: "महिला", male: "पुरुष", transgender: "ट्रांसजेंडर", rural: "ग्रामीण", urban: "शहरी",
          farmer: "किसान", tenant_farmer: "बटाईदार किसान", agricultural_labourer: "खेत मज़दूर", fisherman: "मछुआरा",
          weaver: "बुनकर", student: "छात्र", widowed: "विधवा", married: "विवाहित", unmarried: "अविवाहित",
          auto_driver: "ऑटो चालक", street_vendor: "रेहड़ी वाला", true: "हाँ", false: "नहीं" },
  };
  const CATEGORY_LABELS = {
    en: { pension: "welfare pension", retirement_savings: "retirement savings", education: "education",
          agriculture: "farming", women: "women", household: "household", livelihood: "livelihood",
          health: "health", housing: "housing", insurance: "insurance", savings: "savings" },
    te: { pension: "సంక్షేమ పింఛను", retirement_savings: "పదవీ విరమణ పొదుపు", education: "విద్య",
          agriculture: "వ్యవసాయం", women: "మహిళలు", household: "గృహావసరాలు", livelihood: "ఉపాధి",
          health: "ఆరోగ్యం", housing: "గృహనిర్మాణం", insurance: "బీమా", savings: "పొదుపు" },
    hi: { pension: "कल्याण पेंशन", retirement_savings: "सेवानिवृत्ति बचत", education: "शिक्षा",
          agriculture: "खेती", women: "महिलाएँ", household: "घरेलू", livelihood: "आजीविका",
          health: "स्वास्थ्य", housing: "आवास", insurance: "बीमा", savings: "बचत" },
  };
  const SPEECH_LANG = { en: "en-IN", te: "te-IN", hi: "hi-IN" };
  const ORDER = ["eligible", "need_info", "if_applicable", "not_eligible"];

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const state = { lang: "en", text: "", overrides: {}, result: null, fields: {}, health: null };
  try { state.lang = localStorage.getItem("ym-lang") || "en"; } catch (_) {}

  const t = (k, ...a) => { const v = (I18N[state.lang] || I18N.en)[k] ?? I18N.en[k] ?? k; return typeof v === "function" ? v(...a) : v; };
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fieldLabel = (f) => (state.fields[f] && (state.fields[f][state.lang] || state.fields[f].en)) || f;
  const valueLabel = (v) => {
    if (Array.isArray(v)) return v.map(valueLabel).join(", ");
    if (v === true || v === "true") return t("yes");
    if (v === false || v === "false") return t("no");
    if (typeof v === "number" && v >= 1000) return "₹" + v.toLocaleString("en-IN");
    return (VALUE_LABELS[state.lang] || {})[String(v)] || String(v).replace(/_/g, " ");
  };

  async function api(path, body) {
    const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  }

  /* ---------- i18n ---------- */
  function applyLang() {
    document.documentElement.lang = state.lang;
    $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $$("[data-i18n-ph]").forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
    $$(".lang button").forEach((b) => b.classList.toggle("on", b.dataset.lang === state.lang));
    renderStatus();
    if (state.result) rerun();
  }
  $$(".lang button").forEach((b) => b.addEventListener("click", () => {
    state.lang = b.dataset.lang;
    try { localStorage.setItem("ym-lang", state.lang); } catch (_) {}
    applyLang();
  }));

  function renderStatus() {
    const h = state.health; if (!h) return;
    const on = h.llm.enabled;
    $("#status").innerHTML = `<span class="dot ${on ? "on" : ""}"></span>${esc(on ? t("aiOn") : t("aiOff"))} · ${esc(h.graph.backend.split(" ")[0])} · ${h.knowledge_base.schemes} schemes`;
    $("#status").title = `Graph: ${h.graph.backend}\nLLM: ${on ? h.llm.provider + " / " + h.llm.model : "off (rule-based fallback)"}\nKnowledge base reviewed ${h.knowledge_base.last_reviewed}`;
  }

  /* ---------- voice input (Web Speech API) ---------- */
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  let rec = null;
  $("#mic").addEventListener("click", () => {
    if (!SR) { $("#mic-hint").textContent = "Voice input needs Chrome or Edge."; return; }
    if (rec) { rec.stop(); return; }
    rec = new SR();
    rec.lang = SPEECH_LANG[state.lang]; rec.interimResults = true; rec.continuous = true;
    const base = $("#desc").value ? $("#desc").value.trim() + " " : "";
    rec.onresult = (e) => { $("#desc").value = base + [...e.results].map((r) => r[0].transcript).join(" "); };
    rec.onend = () => { $("#mic").classList.remove("rec"); $("#mic-hint").textContent = ""; rec = null; };
    rec.onerror = (e) => { $("#mic-hint").textContent = e.error === "not-allowed" ? "Microphone permission denied." : ""; };
    rec.start(); $("#mic").classList.add("rec"); $("#mic-hint").textContent = t("listening");
  });

  /* ---------- search ---------- */
  $$(".ex").forEach((b) => b.addEventListener("click", () => { $("#desc").value = b.dataset.ex; $("#ask-form").requestSubmit(); }));
  $("#ask-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const desc = $("#desc");
    if (desc.value.trim().length < 3) {
      desc.setCustomValidity(t("emptyMsg")); desc.reportValidity(); desc.focus();
      desc.addEventListener("input", () => desc.setCustomValidity(""), { once: true });
      return;
    }
    state.text = desc.value.trim(); state.overrides = {};
    $("#qa-log").innerHTML = "";
    rerun(true);
  });
  $("#desc").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) $("#ask-form").requestSubmit(); });

  async function rerun(scroll) {
    const btn = $("#go"); btn.disabled = true;
    const label = btn.innerHTML; btn.innerHTML = `<span class="spinner"></span>`;
    try {
      state.result = await api("/api/match", { text: state.text, profile: state.overrides, lang: state.lang });
      render();
      if (scroll) $("#results").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      console.error(err); alert(t("errorMsg"));
    } finally { btn.disabled = false; btn.innerHTML = label; $$("[data-i18n]", btn).forEach((el) => { el.textContent = t(el.dataset.i18n); }); }
  }

  /* ---------- rendering ---------- */
  function render() {
    const r = state.result;
    $("#results").classList.remove("hidden");
    renderProfile(r);
    renderFollowups(r.followups);
    const counts = Object.fromEntries(ORDER.map((k) => [k, r[k].length]));
    const fi = r.focus_info || {};
    const topic = (fi.topics || [])[0];
    const focusLabel = topic ? fi.labels[topic][state.lang] || fi.labels[topic].en : "";
    const chips = [["eligible", "chipEligible"], ["need_info", "chipNeed"], ["if_applicable", "chipMaybe"]]
      .filter(([k]) => counts[k]).map(([k, key]) => `<button class="stat" data-jump="${k}">${esc(t(key, counts[k]))}</button>`).join("");
    const sub = topic ? t(fi.reason === "student" ? "focusStudent" : "focusAsked", focusLabel) : t(counts.eligible ? "sub" : "subNone");
    $("#celebrate").innerHTML = `<div class="big">${esc(counts.eligible ? t("bigYes", counts.eligible) : t("bigNone"))}</div>
      <div class="sub">${esc(sub)}</div><div class="stats">${chips}</div>`;
    $$("#celebrate .stat").forEach((b) => b.addEventListener("click", () => {
      const g = $(`#g-${b.dataset.jump}`) || $(`#g-other_${b.dataset.jump === "eligible" ? "eligible" : "need"}`);
      if (!g) return;
      g.classList.remove("collapsed"); $(".toggle", g).textContent = t("hide"); g.scrollIntoView({ behavior: "smooth" });
    }));
    const groups = $("#groups"); groups.innerHTML = "";
    // Sections: what they asked for first, everything else after (collapsed when there is a focus).
    const sections = [];
    if (topic) {
      sections.push(["eligible", r.eligible.filter((m) => m.in_focus), t("focusEligible", focusLabel), false, "eligible"]);
      sections.push(["need_info", r.need_info.filter((m) => m.in_focus), t("focusNeed", focusLabel), false, "need_info"]);
      sections.push(["other_eligible", r.eligible.filter((m) => !m.in_focus), t("otherEligible"), true, "eligible"]);
      sections.push(["other_need", r.need_info.filter((m) => !m.in_focus), t("otherNeed"), true, "need_info"]);
    } else {
      sections.push(["eligible", r.eligible, t("eligible"), false, "eligible"]);
      sections.push(["need_info", r.need_info, t("need_info"), false, "need_info"]);
    }
    sections.push(["if_applicable", r.if_applicable, t("if_applicable"), r.if_applicable.length > 3 || !!topic, "if_applicable"]);
    sections.push(["not_eligible", r.not_eligible, t("not_eligible"), true, "not_eligible"]);
    for (const [k, items, title, collapsed, hintKey] of sections) {
      if (k.startsWith("other") && !items.length) continue;
      const sec = document.createElement("section");
      sec.className = "group" + (collapsed ? " collapsed" : "") + (k.startsWith("other") ? " other" : "")
        + (k === "not_eligible" || k === "if_applicable" ? " dim" : "");
      sec.id = `g-${k}`;
      sec.innerHTML = `<div class="group-head"><h2>${esc(title)}<span class="count">${items.length}</span></h2><span class="hint">${esc(t(hintKey + "Hint"))}</span>
        <button class="toggle"></button></div><div class="group-list"></div>`;
      const tog = $(".toggle", sec);
      const setTog = () => { tog.textContent = sec.classList.contains("collapsed") ? t("show") : t("hide"); };
      tog.addEventListener("click", () => { sec.classList.toggle("collapsed"); setTog(); }); setTog();
      const list = $(".group-list", sec);
      if (!items.length) list.innerHTML = `<div class="empty">${esc(t("nothingFound"))}</div>`;
      items.forEach((m, i) => { const c = card(m); c.style.setProperty("--i", Math.min(i, 12)); list.appendChild(c); });
      groups.appendChild(sec);
    }
  }

  function card(m) {
    const node = $("#tpl-card").content.firstElementChild.cloneNode(true);
    node.classList.add(m.status);
    const catLabel = (CATEGORY_LABELS[state.lang] || CATEGORY_LABELS.en)[m.category] || m.category.replace(/_/g, " ");
    const [icon, tile] = CATEGORY_ICON[m.category] || ["✨", "#efeaff"];
    const ic = $(".ic", node); ic.textContent = icon; ic.style.setProperty("--tile", tile);
    const st = m.status === "eligible" || m.status === "need_info" ? `<span class="badge status-${m.status}">${esc(t("st_" + m.status))}</span>` : "";
    $(".badges", node).innerHTML = `${st}<span class="badge ${m.level}">${esc(t(m.level))}</span><span class="badge">${esc(catLabel)}</span>`;
    $(".s-name", node).textContent = m.name_local;
    $(".s-alt", node).textContent = m.name_local !== m.name ? m.name : "";
    $(".amount", node).textContent = m.amount;
    $(".s-summary", node).textContent = m.summary;
    const crit = [
      ...m.met.map((x) => `<li class="met">✓ ${esc(x)}</li>`),
      ...m.to_confirm.map((x) => `<li class="confirm">❔ ${esc(x)}</li>`),
      ...m.unknown.map((x) => `<li class="unknown">? ${esc(x)}</li>`),
      ...m.not_met.map((x) => `<li class="notmet">✗ ${esc(x)}</li>`),
    ];
    $(".crit", node).innerHTML = crit.join("");
    $(".why-sum", node).innerHTML = [
      m.met.length && t("whyMet", m.met.length), m.to_confirm.length && t("whyConfirm", m.to_confirm.length),
      m.unknown.length && t("whyMissing", m.unknown.length), m.not_met.length && t("whyNot", m.not_met.length),
    ].filter(Boolean).join("<span style='color:var(--line)'>•</span>");
    if (m.status === "need_info") $(".why", node).open = true;
    const btn = $(".explain-btn", node); btn.textContent = t("explain");
    const box = $(".explain", node);
    btn.addEventListener("click", async () => {
      if (!box.classList.contains("hidden")) { box.classList.add("hidden"); node.classList.remove("wide"); btn.textContent = t("explain"); return; }
      box.classList.remove("hidden"); node.classList.add("wide"); btn.textContent = t("hideExplain");
      if (box.dataset.loaded === state.lang) return;
      box.innerHTML = `<span class="spinner"></span>`;
      try {
        const res = await api("/api/explain", { scheme_id: m.scheme_id, profile: state.result.profile, match: m, lang: state.lang });
        box.innerHTML = md(res.answer, res.contexts) + contextsHtml(res.contexts) +
          `<div class="sources">${esc(t("sources"))}: ${res.sources.map((s) => `<a href="${esc(s)}" target="_blank" rel="noopener">${esc(s.replace(/^https?:\/\//, "").slice(0, 70))}</a>`).join(" · ")}</div>`;
        box.dataset.loaded = state.lang;
      } catch (err) { console.error(err); box.textContent = t("errorMsg"); }
    });
    const a = $(".portal", node);
    if (m.portal) { a.href = m.portal; a.textContent = t("portal"); } else a.remove();
    return node;
  }

  function contextsHtml(ctx) {
    if (!ctx || !ctx.length) return "";
    return `<div class="ctx"><details><summary>${esc(t("passages"))} (${ctx.length})</summary>${ctx.map((c, i) =>
      `<p><b>[${i + 1}]</b> <i>${esc(c.title)} · ${esc(c.section)}</i>: ${esc(c.text)}</p>`).join("")}</details></div>`;
  }

  /* Minimal, safe Markdown → HTML (escape first, then format). */
  function md(src, ctx) {
    // Pull URLs out first so later rules (italics, citation tooltips) can never touch them.
    const inline = (s) => {
      const links = [];
      let h = esc(s).replace(/https?:\/\/[^\s<)"']+/g, (u) => {
        const trail = (u.match(/[.,;:]+$/) || [""])[0];
        const url = trail ? u.slice(0, -trail.length) : u;
        links.push(`<a href="${url}" target="_blank" rel="noopener">${url.replace(/^https?:\/\//, "")}</a>`);
        return `\u0000${links.length - 1}\u0000${trail}`;
      });
      h = inlineFmt(h);
      return h.replace(/\u0000(\d+)\u0000/g, (_, i) => links[+i]);
    };
    const inlineFmt = (h) => h
      .replace(/\*\*(.+?)\*\*/g, "<b>$1</b>")
      .replace(/(^|[^*])\*(?!\s)(.+?)\*/g, "$1<i>$2</i>")
      .replace(/_(.+?)_/g, "<i>$1</i>")
      .replace(/\[(\d+(?:\s*,\s*\d+)*)\]/g, (_, nums) => nums.split(/\s*,\s*/).map((n) => {
        const c = ctx && ctx[+n - 1];
        return `<span class="cite" title="${c ? esc(c.title + " – " + c.section + ": " + c.text.slice(0, 240).replace(/https?:\/\/\S+/g, "")) : ""}">${n}</span>`;
      }).join(""));
    const out = []; let list = null;
    const close = () => { if (list) { out.push(`</${list}>`); list = null; } };
    for (const raw of src.split(/\r?\n/)) {
      const line = raw.trimEnd();
      let m;
      if ((m = line.match(/^#{1,6}\s+(.*)/))) { close(); out.push(`<h4>${inline(m[1])}</h4>`); }
      else if ((m = line.match(/^\s*[-*•]\s+(.*)/))) { if (list !== "ul") { close(); out.push("<ul>"); list = "ul"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if ((m = line.match(/^\s*\d+[.)]\s+(.*)/))) { if (list !== "ol") { close(); out.push("<ol>"); list = "ol"; } out.push(`<li>${inline(m[1])}</li>`); }
      else if (!line.trim()) { close(); }
      else { close(); out.push(`<p>${inline(line)}</p>`); }
    }
    close();
    return out.join("");
  }

  function renderProfile(r) {
    const ex = r.extraction || {};
    $("#method").textContent = t("method_" + (ex.method || "rules"));
    $("#assumptions").innerHTML = [...(ex.assumptions || []), ...(ex.notes || [])].map((a) => `<div class="notice">${esc(a)}</div>`).join("");
    const p = r.profile;
    const chips = Object.entries(p).filter(([, v]) => v !== null && !(Array.isArray(v) && !v.length))
      .map(([k, v]) => `<span class="pchip"><b>${esc(fieldLabel(k))}</b>${esc(valueLabel(v))}</span>`);
    $("#profile-chips").innerHTML = chips.join("") || `<span class="hint">—</span>`;
    buildForm(p);
  }

  $("#edit-toggle").addEventListener("click", () => {
    const f = $("#profile-form"); f.classList.toggle("hidden");
    $("#edit-toggle").textContent = f.classList.contains("hidden") ? t("edit") : t("done");
  });

  function buildForm(p) {
    const f = $("#profile-form");
    const parts = [];
    for (const [k, meta] of Object.entries(state.fields)) {
      const v = p[k];
      const lab = esc(meta[state.lang] || meta.en);
      if (meta.type === "multi") {
        parts.push(`<label class="wide">${lab}<div class="multi">${meta.options.map((o) =>
          `<label><input type="checkbox" name="${k}" value="${o}" ${Array.isArray(v) && v.includes(o) ? "checked" : ""}>${esc(valueLabel(o))}</label>`).join("")}</div></label>`);
      } else if (meta.type === "enum" || meta.type === "bool") {
        const opts = meta.type === "bool" ? ["true", "false"] : meta.options;
        parts.push(`<label>${lab}<select name="${k}"><option value="">—</option>${opts.map((o) =>
          `<option value="${o}" ${String(v) === o ? "selected" : ""}>${esc(valueLabel(o))}</option>`).join("")}</select></label>`);
      } else {
        const type = meta.type === "text" ? "text" : "number";
        parts.push(`<label>${lab}<input name="${k}" type="${type}" ${meta.type === "float" ? 'step="0.01"' : ""} value="${esc(v ?? "")}"></label>`);
      }
    }
    parts.push(`<div class="actions"><button class="primary small" type="submit">${esc(t("update"))}</button></div>`);
    f.innerHTML = parts.join("");
  }

  $("#profile-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const f = e.target; const o = {};
    for (const [k, meta] of Object.entries(state.fields)) {
      if (meta.type === "multi") { o[k] = $$(`input[name="${k}"]:checked`, f).map((i) => i.value); continue; }
      const el = f.elements[k]; if (!el || el.value === "") continue;
      o[k] = meta.type === "bool" ? el.value === "true" : meta.type === "int" ? parseInt(el.value, 10)
        : meta.type === "float" ? parseFloat(el.value) : el.value;
    }
    state.overrides = o; rerun();
  });

  function renderFollowups(fus) {
    const card = $("#followups-card"); const box = $("#followups");
    if (!fus || !fus.length) { card.classList.add("hidden"); return; }
    card.classList.remove("hidden");
    box.innerHTML = fus.map((q, i) => {
      let ctl;
      if (q.type === "bool") ctl = `<button data-v="true">${esc(t("yes"))}</button><button data-v="false">${esc(t("no"))}</button>`;
      else if (q.type === "enum" || q.type === "multi") ctl = q.options.map((o) => `<button data-v="${o}">${esc(valueLabel(o))}</button>`).join("");
      else ctl = `<input type="${q.type === "text" ? "text" : "number"}" data-input><button data-save>${esc(t("save"))}</button>`;
      return `<div class="fq" data-i="${i}"><div class="fq-q">${esc(q.question)}<small>${esc(t("unlocks", q.unlocks))}</small></div><div class="fq-a">${ctl}</div></div>`;
    }).join("");
    $$(".fq", box).forEach((el) => {
      const q = fus[+el.dataset.i];
      const set = (v) => { state.overrides = { ...state.overrides, [q.field]: v }; rerun(); };
      $$("button[data-v]", el).forEach((b) => b.addEventListener("click", () => {
        const v = b.dataset.v;
        if (q.type === "bool") set(v === "true");
        else if (q.type === "multi") set([...new Set([...(state.result.profile[q.field] || []), v])]);
        else set(v);
      }));
      const save = $("button[data-save]", el);
      if (save) {
        const inp = $("[data-input]", el);
        const go = () => { if (inp.value === "") return; set(q.type === "text" ? inp.value : q.type === "float" ? parseFloat(inp.value) : parseInt(inp.value, 10)); };
        save.addEventListener("click", go); inp.addEventListener("keydown", (e) => { if (e.key === "Enter") go(); });
      }
    });
  }

  /* ---------- Q&A ---------- */
  $("#qa-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = $("#qa-input").value.trim(); if (!q) return;
    $("#qa-input").value = "";
    const log = $("#qa-log");
    log.insertAdjacentHTML("beforeend", `<div class="qa-q">${esc(q)}</div>`);
    const a = document.createElement("div"); a.className = "qa-a"; a.innerHTML = `<span class="spinner"></span>`; log.appendChild(a);
    try {
      const r = state.result;
      const ids = r ? [...r.eligible, ...r.need_info].map((m) => m.scheme_id) : null;
      const res = await api("/api/ask", { question: q, scheme_ids: null, profile: r ? r.profile : null, lang: state.lang, _hint: ids });
      a.innerHTML = md(res.answer, res.contexts) + contextsHtml(res.contexts);
    } catch (err) { console.error(err); a.textContent = t("errorMsg"); }
  });

  /* ---------- boot ---------- */
  (async () => {
    try {
      [state.fields, state.health] = await Promise.all([api("/api/fields"), api("/api/health")]);
    } catch (err) { console.error(err); }
    applyLang();
  })();
})();
