# Åland genom tiderna

En interaktiv karta på svenska för att upptäcka Ålands historia tillsammans med barn, från istiden till idag. Utforska hur land, bosättningar, byggnader, vägar och sjörutter förändras längs tidslinjen.

**[Öppna kartan på åland.erikedin.com](https://xn--land-poa.erikedin.com/)**

## Kör lokalt

Webbplatsen är statisk HTML, CSS och JavaScript. Färdiga kartdata finns i repot; du behöver inte installera npm-paket eller bygga om data för att köra den.

```sh
git clone https://github.com/321k/aland-tidsresan.git
cd aland-tidsresan
python3 -m http.server 4173 --directory dist
```

Öppna [localhost:4173](http://localhost:4173/). Använd en lokal webbserver eftersom kartan hämtar data med `fetch`.

## Innehåll

- Zoom- och flyttbar karta med tidslinje, uppspelning och berättelser.
- Historiska strandlinjer, bosättningar, fornlämningar och byggnader med tidsstyrd synlighet.
- Mariehamns stadsnät från stadsplanen 1860, museikartan över 1920-talet, flygfotot 1942 och senare OpenStreetMap-utdrag.
- Stora och lilla ofreden: Lövös fredskongress, Flaka flottbas, sjöslaget vid Flisö/Ledsund, Degerby skans samt flykt och återkomst.
- Historiska landsvägar, postvägen mellan Sverige och Finland, färjerutter och andra sjöleder.
- Källhänvisningar, historiska kartbilder och länkar för vidare läsning.

## Projektstruktur

| Sökväg | Innehåll |
| --- | --- |
| `dist/` | Webbplatsen som körs och publiceras, inklusive kartmoduler och tillgångar |
| `data/` | Källdata, manuella karttolkningar och dokumentation om ursprung och osäkerhet |
| `scripts/` | Import och bearbetning av geografiska data samt uppdatering av cacheversioner |
| `tests/` | Automatiserade tester av tidsgränser, geometri och kartbeteende |
| `wrangler.jsonc` | Cloudflare-konfiguration för den publika webbplatsen |
| `DEPLOYMENT.md` | Instruktioner för publicering |

## Kontrollera ändringar

JavaScript-testerna använder Nodes inbyggda testverktyg och inga externa testpaket. Använd Node.js 20 eller senare.

```sh
node --test tests/*.test.cjs
```

Efter ändringar i webbplatsens filer eller genererade kartdata, uppdatera cacheversionerna:

```sh
python3 scripts/cache_versions.py
```

Kontrollera också kartan i webbläsaren, särskilt berörda årtal, zoomnivåer och mobilvy.

## Uppdatera kartdata

Redigera källdata i `data/` och kör motsvarande skript i `scripts/`. För Mariehamns stadsnät ligger de manuella tolkningarna i `data/mariehamn-city-traces.json`; historiska landsvägar finns i `data/historical-road-traces.json`.

Exempel för dessa två datalager:

```sh
python3 -m venv .venv-geo
.venv-geo/bin/python -m pip install numpy scipy pyproj shapely
.venv-geo/bin/python scripts/build_city_grid.py
.venv-geo/bin/python scripts/build_historical_roads.py
python3 scripts/cache_versions.py
node --test tests/*.test.cjs
```

Ofredernas berättelser och källor redigeras i `data/ofreden.json` och paketeras med `python3 scripts/build_ofreden.py`. Registerdateringar ligger separat i `data/temporal-enrichment.json` och uppdateras med `python3 scripts/build_heritage.py`.

Andra importskript kan behöva fler bibliotek, externa källdata eller nätåtkomst. Läs respektive skript innan det körs; en fullständig nyimport behövs inte för vanliga ändringar.

## Historisk tolkning och källor

Kartan är ett pedagogiskt projekt och innehåller förenklade rekonstruktioner. Källornas årtal är inte automatiskt byggnadsår:

- Stadsplanen 1860 visas som en **plan**, inte som bevis för färdigbyggda gator och hus.
- Museikartan beskriver **1920-talet**. Hussymbolerna är förenklade och visas tillsammans med den källan; när de försvinner vid nästa kartsteg betyder det inte att husen revs då.
- Flygfotot 1942 ger ett urval tolkade gator, inte en fullständig byggnadsinventering.
- Kvarter som beräknas mellan gator är inte fastighetsgränser.
- Skillnader mellan OpenStreetMap-utdrag kan bero både på verkliga förändringar och på förbättrad kartläggning.
- Historiska kartor och strandlinjemodeller har osäkerheter i läge och datering.

Ursprung, länkar, metoder och begränsningar finns i `data/*provenance.json` och i webbplatsens källinformation. Behåll dessa uppgifter vid ändringar.

Kartdata, arkivbilder och inkluderade bibliotek har sina respektive rättigheter och villkor. OpenStreetMap-material kommer från [OpenStreetMaps bidragsgivare och omfattas av ODbL](https://www.openstreetmap.org/copyright). Bibliotekslicenser finns i `dist/vendor/`. Att repot är offentligt innebär inte att alla ingående kartbilder och data har samma licens; kontrollera respektive källa före återanvändning.

## Publicering

Webbplatsen publiceras på Cloudflare Workers Static Assets. Se [DEPLOYMENT.md](DEPLOYMENT.md) för kommandon och efterkontroll. GitHub-repot är inte kopplat till automatisk publicering.
