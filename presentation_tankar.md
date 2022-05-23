# Tankar kring presentationens upplägg

Upplägg
- Introduktion
    - Context (PR dev)
    - Förklara problemet, vad vi undersöker — automatisk kategorisering
    - Varför viktigt? — underlätta för utvecklare, byggsten för mer forskning NL-PL
    - capture interest
- Outline (sammanfattning)
- Previous work
    - DeepRelease (fastText, dataset)
- Gold Standard Dataset
    - DR baseline
    - (low IAA)
- Theory
    - Transformers, BERT — intuition
    - Classification, metrics — f1
    - Transfer learning
    - freezing layers, thawing
- Titles only classifier
    - Dataset DR
    - our models perform better
- Extended text classifier
    - Dataset scraped texts
    - DistilBERT
- Code diffs classifier
    - Dataset scraped code diffs
    - Interesting results
- Ensemble classifier
    - theory
    - Combined features
    - best results
- Conclusion & Last words
    - More research needed on PL-understanding
    - Hoppas vi kan bidra till mer forskning samt Docks produkten på Backtick


- Börja med en kort introduktion, förklara PR, problemet och vad vi försöker automatisera, samt varför det är viktigt
- Sen skulle vi kunna ge en outline för resten av presentationen
- Vi kan berätta om DeepRelease (fastText, dataset) och att vi testar den på vårt eget annoterade dataset
- Sen lite teori för att förstå BERT, kanske nämna de 4 modellerna vi använder (tränade på kod, text)
- Första experiment med titlar, jämförbart med DR baseline, sätter ny baseline för kommande experiment
- Andra experiment med extended text (scraping kan nämnas här också)
- Tredje experiment med code diffs
- Sista experiment med ensemble classifier, förklara hur det går till
- Conclusion, last words


Hur mycket teori behöver vi gå in på?