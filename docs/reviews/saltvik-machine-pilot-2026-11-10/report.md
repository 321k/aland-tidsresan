# Saltvik 102107: pilot för maskinföreslagna byggnadsbelägg

Granskad 2026-11-10. Endast blad 102107; inget publicerat, pushat eller sammanslaget.

## Urval och resultat

De första **24** tidigare obehandlade kandidaterna i den levererade filens ordning har granskats. Urvalet kräver `symbol` på minst två utgåvor av 102107 och utesluter objekt i tidigare byggnadsbeslut och granskningsomgångar, inklusive väntande beslut. Ingen av de 24 förekom i något annat befintligt JSON-beslut i `data/`. Efter denna avgränsning finns 641 kandidater; återstående 617 har inte granskats i piloten. Alla 24 valda hade fyra maskinträffar. Ordningen inom denna fyrträffsgrupp följer indatafilen och är inte en separat kvalitetspoäng.

**13 accepterade, 11 uppskjutna, 0 förkastade.** 52 av 96 föreslagna träffar (54,2 %) har bekräftats som rimliga motsvarigheter till samma byggnad. Resterande 44 träffar gäller verkliga byggnadssymboler men osäker identitet: de är inte bevisade felträffar. En byggnadssymbol finns alltså i granskningsområdet för samtliga 96 träffar, men detta är inte 100 % korrekt objektmatchning. Andelen 54,2 % är en försiktig bekräftelseandel, inte ett skattat precisionsmått för hela bladet. 1978 är inte en oberoende byggnadsinventering.

Originalskanningarna har checksumme- och dimensionskontrollerats med `rural_map_candidates.scan`. Utsnitten omfattar 110 × 110 originalpixlar (cirka 187 × 187 m), förstorade tre gånger utan utjämning. Varje rad visar 1968, 1978, 1985 och 1993 från vänster till höger: först rå bild, sedan samma bild med den nutida kandidatkonturen i magenta och grannkonturer i blått. Utsnittens exakta originalkoordinater finns i [utsnittstabellen](crop-origins.md). Symbolcentrum för accepterade observationer har avlästs manuellt; detektorns avstånd används inte som ett beslut.

Besluten använder oförändrat format i `rural-map-review.json`: `objectId`, `input`, `referenceGeometryId`, `basis`, `maxSymbolDistanceMeters`, `observations`, `reviewedAt` och `reviewBatch`. Fingeravtrycket beräknas med `museum_reconstruction.fingerprint`. Omgången sparas i `rural-map-batches.json`; uppskjutna fall ligger i dess befintliga `pending`-lista. Ingen ny evidensklass eller automatisk import har införts.

## Datering och katalogeffekt

**13 befintliga byggnader får visningsstart 1968 i stället för 2026.** Övriga startår: 0 ändringar. Inga objekt skapas, flyttas, avslutas eller dubbleras. Samma moderna referenskontur används även före 2026. Alla äldre objektuppgifter och geometrier ska vara bevarade.

1968 är en konservativ visningsgräns och ett senast-belägg, inte ett byggår; tillkomstens nedre gräns är okänd. Kartläggningen 1964, 1985 års revidering 1981–1983 och 1993 års underlag 1990–1991 blir inte byggdatum. 1993 års blad trycktes 1994. 1978 återger äldre byggnadsunderlag med vägkomplettering. Kontinuitet och användning av nutida takform anges uttryckligen som tolkning. Ingen maskinklass `none`, `ink` eller `built-up-tint` används för att fördröja eller avsluta ett hus.

## Individuell granskning

Samtliga fall nedan har inspekterats i **1968, 1978, 1985 och 1993**. Tabellen redovisar alla 13 accepterade (därmed fler än de begärda tio), alla 11 uppskjutna och samtliga förkastade (inga). `Index` är det nollbaserade indexet i maskinfilens kandidatlista.

| Nr / index | Objekt-id | Beslut | Iakttagelse i de fyra utgåvorna | Utsnitt |
| --- | --- | --- | --- | --- |
| 1 / 1587 | `building:osm:way-306475879` | Uppskjuten | Flera små fyllda och ihåliga hussymboler samt en gårdsväg ligger inom dagens stora sammansatta kontur. Den moderna byggnaden kan inte identifieras med något enskilt äldre hus; möjlig föregångarbebyggelse. Uppskjuten. | [Bild 01](page-01.jpg) |
| 2 / 1588 | `building:osm:way-451942586` | Accepterad | En liten fylld, ungefär nord–sydlig hussymbol ligger vid åkerns södra hörn, öster om gårdsvägen och norr om ett separat ihåligt uthus. Läget, riktningen och gårdssambandet återkommer i alla fyra utgåvor och stämmer med den lilla nutida konturen. | [Bild 01](page-01.jpg) |
| 3 / 1589 | `building:osm:way-453608881` | Accepterad | Den södra av två fyllda, ungefär öst–västliga hussymboler ligger längs åkerkanten, väster om gårdsvägen. Den norra grannen och det ihåliga uthuset på östra sidan skiljs tydligt från kandidaten. Samma ordning, riktning och rimliga symbolstorlek finns i alla fyra utgåvor. | [Bild 02](page-02.jpg) |
| 4 / 1590 | `building:osm:way-453609548` | Uppskjuten | 1968, 1978 och 1985 visar en oregelbunden mindre byggnadsfigur intill vägen; 1993 visar en betydligt större rektangel närmare dagens kontur. Ombyggnad, tillbyggnad eller ersättningshus kan inte skiljas åt. Dagens hela hus backdateras inte. Uppskjuten. | [Bild 02](page-02.jpg) |
| 5 / 1591 | `building:osm:way-455336255` | Accepterad | Den stora fyllda T-formade skolbyggnaden har samma tvärgående huvuddel och nordliga flygel i alla fyra utgåvor. Det separata långsmala huset söderut och gårdsinfarten återkommer. T-formens läge, storlek och riktning motsvarar dagens byggnad. | [Bild 03](page-03.jpg) |
| 6 / 1592 | `building:osm:way-577587968` | Accepterad | Den mellersta fristående byggnaden i gruppen vid karttexten Sjukhuset/Sjukhus har en snedställd långsmal huvudkropp med mindre utsprång. Den ligger mellan det västra rektangulära huset och det östra vinkelhuset i alla fyra utgåvor. Form, storlek, riktning och gårdsvägar stöder samma identitet. | [Bild 03](page-03.jpg) |
| 7 / 1593 | `building:osm:way-577587969` | Accepterad | Det västra av sjukhusgruppens hus är en fristående långsmal rektangel i nordväst–sydostlig riktning, närmast stranden. Samma form och läge i förhållande till strand, gårdsväg och de två östra grannhusen syns i alla fyra utgåvor. | [Bild 04](page-04.jpg) |
| 8 / 1594 | `building:osm:way-577587970` | Accepterad | Sjukhusgruppens östra byggnad har en tydlig vinkel med en indragen sydsida i alla fyra utgåvor. Storlek och riktning motsvarar den nutida vinkelkonturen; västgrannen och de små husen söderut är separata. | [Bild 04](page-04.jpg) |
| 9 / 1595 | `building:osm:way-614782662` | Uppskjuten | De tre äldre utgåvorna visar en markant längre och bredare fylld byggnad vid vägkröken än den nutida konturen. 1993 års symbol är mindre. Samma plats och riktning räcker inte för att avgöra generalisering, ändring eller ersättningshus. Uppskjuten. | [Bild 05](page-05.jpg) |
| 10 / 1596 | `building:osm:way-614782681` | Accepterad | En liten fylld nord–sydlig hussymbol står öster om det större västliga huset och omedelbart nordost om ett separat ihåligt uthus. Alla fyra utgåvor behåller samma gårdsordning och ungefärliga storlek och riktning som dagens smala kontur. | [Bild 05](page-05.jpg) |
| 11 / 1597 | `building:osm:way-626785243` | Uppskjuten | Alla fyra utgåvor visar en mindre U-liknande skolbyggnad. Dagens betydligt större sammansatta kontur sträcker sig långt åt nordväst utanför symbolen och har annan form. Tillbyggnader eller ersättningshus behöver utredas före backdatering. Uppskjuten. | [Bild 06](page-06.jpg) |
| 12 / 1598 | `building:osm:way-844736909` | Uppskjuten | Den fyllda, närmast kvadratiska symbolen ligger vid södra delen av dagens längre kontur intill stranden i alla fyra utgåvor. Den nordliga delen saknar motsvarande form. Äldre hus, senare tillbyggnad och ersättningshus kan inte skiljas åt. Uppskjuten. | [Bild 06](page-06.jpg) |
| 13 / 1599 | `building:osm:way-1030562627` | Uppskjuten | 1968 och 1978 visar en långsmal snedställd symbol förskjuten norr om den lilla nutida vinkelkonturen; 1985 är symbolen större och förskjuten åt öster. 1993 ligger en mindre symbol närmare dagens läge. Riktning och form ger inte tillräckligt säker kontinuitet. Uppskjuten. | [Bild 07](page-07.jpg) |
| 14 / 1600 | `building:osm:way-1030562631` | Accepterad | En liten fylld snedställd hussymbol ligger i gårdens sydöstra del, omedelbart norr om den diagonala tillfarten. Det större huset åt nordväst och uthusen vid östra vägen skiljer platsen från grannarna. Samma läge och förenliga storlek och riktning återkommer i alla fyra utgåvor. | [Bild 07](page-07.jpg) |
| 15 / 1601 | `building:osm:way-1030562633` | Uppskjuten | 1968, 1978 och 1985 visar en fylld hussymbol söder om landsvägen. 1993 är symbolen mindre och ligger vid den nutida konturens västra kant, nära ett separat ihåligt uthus. Källgeneralisering och identitetsbyte kan inte säkert skiljas åt. Uppskjuten. | [Bild 08](page-08.jpg) |
| 16 / 1602 | `building:osm:way-1041618518` | Uppskjuten | En fylld symbol återkommer söder om gårdsgruppen, men de äldre symbolerna är förskjutna åt sydväst och 1993 motsvarar främst den nutida konturens sydliga del. Den nordliga delen och kontinuiteten är otillräckligt belagda. Uppskjuten. | [Bild 08](page-08.jpg) |
| 17 / 1603 | `building:osm:way-1284291122` | Accepterad | En fristående fylld rektangel i nordväst–sydostlig riktning ligger norr om landsvägen, längs samma gårdsstig och väster om ett separat hus. Storlek, riktning och grannordning stämmer i alla fyra utgåvor. De äldre kartornas mindre lägesförskjutningar följer gårdssambandet. | [Bild 09](page-09.jpg) |
| 18 / 1604 | `building:osm:way-1328629401` | Accepterad | Gårdens södra huvudbyggnad är en fylld långsmal rektangel i västnordväst–ostsydostlig riktning. Den ligger söder om uthusen, väster om landsvägen och inom samma åkerkant i alla fyra utgåvor. Formen och storleken är förenliga med dagens kontur. | [Bild 09](page-09.jpg) |
| 19 / 1605 | `building:osm:way-1436669815` | Accepterad | Ett separat långsmalt nord–sydligt hus ligger direkt söder om den T-formade skolan och väster om den prickade gårdsgången. Symbolens storlek, riktning och placering mellan skola och södra tillfart överensstämmer i alla fyra utgåvor. | [Bild 10](page-10.jpg) |
| 20 / 1606 | `building:osm:way-1469019854` | Uppskjuten | Alla fyra utgåvor visar en fylld symbol vid gårdens västra kant, men den är avsevärt större än den mycket lilla nutida konturen; 1985 framträder en tydligare vinkel. Symbolgeneralisering, föregångare och del av större hus kan inte avgöras. Uppskjuten. | [Bild 10](page-10.jpg) |
| 21 / 1607 | `building:osm:way-1475060919` | Accepterad | En fristående fylld långsmal symbol i nordnordost–sydsydvästlig riktning ligger öster om det smala stråket och norr om den större gårdsbyggnaden. Alla fyra utgåvor visar samma riktning, rimliga storlek och grannordning utan konkurrerande hus på kandidatens plats. | [Bild 11](page-11.jpg) |
| 22 / 1608 | `building:osm:way-1475201387` | Uppskjuten | Den fyllda symbolen intill landsvägen sammanfaller med två tätt liggande nutida konturer, kandidaten och grannen direkt söderut. I 1993 års utgåva är figuren dessutom större och oregelbunden. Ingen enskild beständig byggnad kan säkert väljas. Uppskjuten. | [Bild 11](page-11.jpg) |
| 23 / 1609 | `building:osm:way-1475202137` | Accepterad | En liten fylld ungefär öst–västlig byggnad ligger längst in i den smala gårdsfickan öster om tillfarten. Samma åkeromslutning och västliga grannläge syns i alla fyra utgåvor; symbolens mindre lägesförskjutning byter inte gårdsplats. Storlek och riktning är förenliga med dagens lilla kontur. | [Bild 12](page-12.jpg) |
| 24 / 1610 | `building:osm:way-1476347301` | Uppskjuten | Den äldre fyllda byggnadssymbolen är större än kandidaten och ligger nära mellanrummet mot den lilla nutida grannen norrut; förskjutningen ändras mellan utgåvorna. Kartsymbolens byggnadsägare och en eventuell förändring av byggnaden kan inte säkerställas. Uppskjuten. | [Bild 12](page-12.jpg) |

## Avlästa symbolcentrum

Koordinaterna nedan är originalskanningens pixlar, i ordningen 1968 / 1978 / 1985 / 1993. De är generaliserade symbolcentrum, inte inmätta takkonturer.

| Objekt-id | 1968 | 1978 | 1985 | 1993 |
| --- | --- | --- | --- | --- |
| `building:osm:way-451942586` | [1747, 3106] | [1714, 3124] | [3838, 2995] | [2922, 2733] |
| `building:osm:way-453608881` | [2959, 759] | [2925, 777] | [5052, 649] | [4186, 416] |
| `building:osm:way-455336255` | [5564, 3264] | [5531, 3280] | [7664, 3150] | [6758, 2967] |
| `building:osm:way-577587968` | [2233, 6116] | [2199, 6131] | [4329, 6007] | [3356, 5752] |
| `building:osm:way-577587969` | [2216, 6130] | [2182, 6146] | [4314, 6022] | [3339, 5766] |
| `building:osm:way-577587970` | [2264, 6115] | [2232, 6131] | [4362, 6006] | [3388, 5752] |
| `building:osm:way-614782681` | [5455, 4246] | [5422, 4263] | [7555, 4135] | [6629, 3949] |
| `building:osm:way-1030562631` | [5251, 5729] | [5219, 5745] | [7355, 5620] | [6398, 5423] |
| `building:osm:way-1284291122` | [1180, 4251] | [1147, 4269] | [3269, 4145] | [2332, 3865] |
| `building:osm:way-1328629401` | [5269, 3688] | [5236, 3705] | [7368, 3579] | [6453, 3388] |
| `building:osm:way-1436669815` | [5550, 3288] | [5517, 3304] | [7652, 3174] | [6743, 2991] |
| `building:osm:way-1475060919` | [3426, 3276] | [3393, 3293] | [5525, 3166] | [4609, 2940] |
| `building:osm:way-1475202137` | [2921, 3172] | [2888, 3189] | [5013, 3062] | [4105, 2825] |

## Spårbarhet

Indata är skrivskyddad arbetskälla: `../map-timeline/out/aland-sheet-evidence/`. Inget där har ändrats. Statusen `machine-proposals-unreviewed` gäller fortfarande maskinfilen.

`building-backdating-candidates.json` SHA-256: `e8f7e89a12a6e1f4b7d1ac100e031bd74a2f77ecd8e997e7981067e7e15bc200`.

| Källa | Skanning SHA-256 | Registrering och dateringspolicy |
| --- | --- | --- |
| [nls:102107:1968](https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/1/1021/102107/102107_1968.jpg) | `f02b6721ec8ed07de3c7eb1e9f7878092238116fe2ee3c813bec5ce0a1c37e27` | printed-grid-affine; Utgivningsår används som konservativ visningsgräns. Kartläggningsår och flygfotografering anger underlagets ålder, inte byggår. |
| [nls:102107:1978](https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/1/1021/102107/102107_1978.jpg) | `eb2b1239926f0c4092c2012a5f033fc02ef23cf87cae2a24eb173c807e401c1d` | printed-grid-affine; Vägnätet kompletterades 1978 med rött övertryck. Byggnadernas grundunderlag är äldre och utgåvan är inte en ny byggnadsinventering. Källår är inte byggår. |
| [nls:102107:1985](https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/1/1021/102107/102107_1985.jpg) | `ecc5f343ea06666ae2ca3dce8f04928d117a5d37bfe3add00d9ee5a031dfbd07` | printed-grid-affine; Utgivningsår används som konservativ visningsgräns. Kartläggningsår och flygfotografering anger underlagets ålder, inte byggår. |
| [nls:102107:1993](https://vanhatpainetutkartat.maanmittauslaitos.fi/mml_vanhat_kartat/Painetut_kartat/21_Peruskartta_20k/1/1021/102107/102107_1993.jpg) | `1cae50900ad1499124d5b2ee87500f14d2fb279e4f6f15a265614cf7c8958704` | printed-grid-mesh; Utgåvan anges som 1993, tryckt 1994; flygfotografering 1990 och terrängkomplettering 1991. Utgåvans år används som konservativ visningsgräns, inte byggår. |

Bildrättigheter: © Lantmäteriverket, CC BY 4.0. Utsnitt ur originalskanningar med nutida konturöverlägg; se källposternas attribution och licens i granskningsregistret. Nutida konturer: © OpenStreetMap contributors, ODbL. Fullständiga råa och överlagrade separatutsknitt finns lokalt i `data/map-scan-cache/review/102107/machine-pilot-2026-11-10/`.

## Systematiska begränsningar och rekommendation

- Fyra utgåvoträffar kan återge samma äldre underlag; särskilt 1978 tillför ingen oberoende byggnadsinventering. Räkna undersöknings-/revideringsgenerationer separat från publiceringsutgåvor.
- Stora eller sammansatta moderna konturer kan få träff på små föregångare eller flera hus inne i samma kontur (nr 1, 4 och 11). Symbolträff är inte identitetsbevis.
- Små konturer och täta grannar är känsliga för generaliserade symbolstorlekar och lokala förskjutningar (bland annat nr 13, 20, 22 och 24). Närmaste symbol räcker inte.
- Urvalet innehåller bara den starkaste fyrträffsgruppen och flera närliggande skol-/sjukhusbyggnader. Det är inget slumpmässigt kvalitetsurval och säger lite om tvåträffsfall, missade symboler eller andra blad.

Fortsätt gärna med ytterligare en begränsad, manuellt granskad omgång efter uttryckligt klartecken. Behåll råa och överlagrade utsnitt, separata utgåvor, grannkonturer, manuella pixelcentrum, fingeravtryck och individuella svenska motiveringar. Flagga stora form-/areaskillnader och flera möjliga byggnader före rangordning. Dela upp maskinträffens symbolriktighet och byggnadsidentitet i rapporteringen; använd aldrig negativa maskinresultat som frånvarobelägg. Ingen massimport rekommenderas. **Inga ytterligare blad har behandlats.**

## Validering och tester

Byggning och cacheversionering har körts med projektets `.venv-geo/bin/python`. De fullständiga testerna efter ändringen kördes i en isolerad kopia så att förtesterna kan avslutas mot orörda indata. Kopian innehöll före den slutliga batchkopplingsrättningen exakt samma källor, tester och byggda filer som det integrerade arbetsflödet, verifierat genom bytejämförelse. Slutliga riktade kontroller har körts direkt i arbetsrepot. Kartvalideraren har dessutom körts direkt i arbetsrepot.

| Kontroll | Resultat | Oförkortad utdata |
| --- | --- | --- |
| `scripts/build_temporal_objects.py` | PASS — 35 976 objekt, 45 509 geometrier | [bygglogg](logs/build.log) |
| `scripts/cache_versions.py` | PASS | [cachelogg](logs/cache.log) |
| `scripts/build_rural_sectors.py` | PASS — bara Saltviks objektslista ändrad | [liggarlogg](logs/sectors-build.log) |
| `scripts/build_rural_coverage_page.py` | PASS | [sidlogg](logs/coverage-page-build.log) |
| `node --test tests/*.test.cjs` före piloten | PASS — 423/423 | [förtest](logs/baseline-node.log) |
| `node --test tests/*.test.cjs` efter piloten | PASS — 423/423 | [slutlig omkörning i arbetsrepot](logs/final-node.log) |
| `python -m unittest discover -s tests -p 'test_*.py'` före piloten | FAIL — 347 körda, 12 failures, 5 errors | [fullständig förtestlogg](logs/baseline-python.log) |
| Fullständig Python-körning efter pilotbesluten, före rättad batchkoppling | FAIL — 340 körda, 12 failures, 5 errors, 2 skips | [oförkortad eftertestlogg](logs/post-python.log) |
| Slutlig riktad omkörning: sektorer och QGIS-kontroller | PASS — 14 tester, inga skips | [slutlogg](logs/final-focused.log) |
| Slutlig katalogtestmodul | PASS — 6 tester | [slutlogg](logs/final-catalogue-tests.log) |
| `scripts/review_historical_maps.py` före piloten | FAIL — redan gammal byggd katalog | [förtestlogg](logs/baseline-validation.log) |
| `scripts/review_historical_maps.py` efter ombyggnad | FAIL — redan saknat `symbolCount` i stadsfaser | [fullständig logg](logs/validation.log) |
| Avgränsad katalogjämförelse mot nykompilerad baslinje | PASS | [audit](audit.log) |
| Källpatch mot kopia av exakt arbetsbaslinje | PASS | [patchkontroll](patch-verification.log) |

Kartvaliderarens fel efter ombyggnaden, ordagrant:

```text
Traceback (most recent call last):
  File "/Users/erikedin/Documents/ChatGPT/Åland history/aland-tidsresan/scripts/review_historical_maps.py", line 34, in <module>
    print(json.dumps(check(), ensure_ascii=False, indent=2))
                     ~~~~~^^
  File "/Users/erikedin/Documents/ChatGPT/Åland history/aland-tidsresan/scripts/review_historical_maps.py", line 20, in check
    'postwarStages': [{k: s[k] for k in ['id', 'from', 'through', 'counts', 'symbolCount']} for s in catalog['cityStages']],
                          ~^^^
KeyError: 'symbolCount'
```

De sju stadsfaser som redan i den nykompilerade förbaslinjen saknar `symbolCount` är 1860, 1861, 1871, 1920, 1927, 1942 och 1952. Samtliga stadsfaser är oförändrade av piloten. Kontrollprogrammet har inte ändrats eller kringgåtts. Förtestets gamla katalog hade samma objektuppgifter men äldre geometrinoteringar för regionala vägar och annan listordning; den ordinarie ombyggnaden uppdaterar även detta befintliga byggresultat. Pilotens effekt räknas därför mot den nykompilerade baslinjen.

Den fullständiga efterkörningen hittade ett pilotfel: de nya besluten saknade den befintliga `reviewBatch`-kopplingen. Detta är nu rättat och sektortestet passerar med det uppdaterade förväntade antalet. Den gamla katalogjämförelsen passerar efter ombyggnaden. Övriga elva failures och fem errors har samma testnamn som i förbaslinjen och har inte ändrats eller kringgåtts. Hela Python-sviten har inte körts om efter metadatafixen; relevanta sektor- och katalogtester har körts om separat.

De två skips i den isolerade körningen berodde på lokalt genererade QGIS-filer som saknades i kopian: Hammarlands granskningsdatabas (sju tester) och Saltviks registrerade raster (ett test). De har därefter körts i arbetsrepot och passerar utan skips, tillsammans med de sex sektortesterna. Därför körde isoleringen 340 tester jämfört med förbaslinjens 347; ett helt klassförtest räknades som skip, medan dess sju testmetoder inte kördes.

Sektorliggaren och dess publiceringskopia har byggts om. Endast sektorn 102107 får fler granskade byggnader; status, första-genomgångsstatus och prioriteringskö är oförändrade. Översiktssidan visar 759 i stället för 746 byggnader totalt och 246 i stället för 233 på Saltvikbladet. Sidans redan gamla vägantal uppdateras samtidigt från dess befintliga liggare (98 → 733 totalt och 92 → 727 för Hammarland); inga vägobjekt eller väggranskningar ändras.

Tre befintliga förväntade antal i landsbygdstesterna har ökats med 13: byggnadsbeslut 569 → 582, och visade generiska hus per årgrupp 472/537/543/567 → 485/550/556/580 samt batchkopplade beslut 724 → 737. Inga testvillkor, toleranser eller valideringar har försvagats.

## Leverans och bevarande av pågående arbete

Arbetsgrenen är `review/saltvik-machine-evidence-pilot`. Registren, den byggda katalogen och flera beroenden var redan ospårade när arbetet började. För att inte stagea eller checka in annans pågående innehåll omfattar pilotens commit endast denna nya rapportmapp, granskningsbilderna, loggarna och [källpatchen](pilot.patch). De integrerade ändringarna ligger kvar i arbetskatalogen, ostageade. Patchen innehåller endast tilläggen till de två befintliga registren och de tre antaljusteringarna i testerna. [Kontrollsummorna](file-hashes.md) beskriver exakt arbetsbaslinje och resultat för alla tretton ändrade filer.

Patchen är **redan applicerad i den aktuella arbetskatalogen** och ska inte appliceras en andra gång. I en separat kopia av samma förbaslinje kan man använda:

```sh
git apply --check docs/reviews/saltvik-machine-pilot-2026-11-10/pilot.patch
git apply docs/reviews/saltvik-machine-pilot-2026-11-10/pilot.patch
.venv-geo/bin/python scripts/build_rural_sectors.py
.venv-geo/bin/python scripts/build_rural_coverage_page.py
.venv-geo/bin/python scripts/build_temporal_objects.py
.venv-geo/bin/python scripts/cache_versions.py
```

Alla tidigare beslut och källposter är oförändrade. Samtliga tidigare geometrier och belägg är bevarade; de 52 nya geometrierna är enbart avlästa kartsymbolpunkter. De 11 uppskjutna objektens katalogposter är exakt oförändrade. Katalogens övergripande äldre `recordedAt` har inte använts för att omdatera tidigare beslut; varje nytt beslut och granskningsomgång har uttryckligt `reviewedAt: 2026-11-10`.

Ingen ändring har gjorts i `map-timeline/`, `DEPLOYMENT.md` eller `wrangler.jsonc`. Ingen publicering, push eller merge har utförts.

