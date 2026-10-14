'use strict';
const $=s=>document.querySelector(s);
const sources={
 itinerary:['Danska itinerariet · Uppslagsverket Finland','https://www.uppslagsverket.fi/sv/view-170045-DanskaItinerariet'],
 eckeroRoute:['Eckerölinjen · Mariehamns stads historia','https://bibliotek.mariehamn.ax/fulltext/MariehamnsHistoria_1961-1986.pdf?dl=0'],
 postalEnd:['Postvägens sista år · Postmuseum','https://www.postmuseum.se/bocker/1966/1966_5-19-52_Naucl%C3%A9r.pdf'],
 shipRoutes:['Färjetrafikens början · Viking Line','https://www.vikingline.com/globalassets/documents/market_specific/corporate/group/the_ships_2026.pdf'],
 earlyMap:['Karta öfver Åland · cirka 1800 · Uppsala universitetsbibliotek / Alvin','https://www.alvin-portal.org/alvin/imageViewer.jsf?dsId=ATTACHMENT-0001&pid=alvin-record%3A82661'],
 cityMuseum:['Mariehamn på 1920-talet · Nybyggarne','https://mpf.spfpension.fi/verksamhet/nybyggarne/mariehamn/'],
 cityPlan:['Mariehamns första stadsplan · Mariehamns stad','https://www.mariehamn.ax/sites/default/files/attachments/guidedocument/generalplan_del2_03_plan.pdf'],
 bomarsundPlan:['Bomarsunds översiktsskiss · Fredriks betraktelser','https://mskfredrik.blogspot.com/2009/08/fastningen-bomarsund-pa-aland.html'],
 wrecks:['Maritimt kulturarv · Ålands landskapsregering','https://www.arcgis.com/home/item.html?id=0ff2d4f3d8024d878ec17375e94206e1'],
 postal:['Postkarta · C. J. Carlsson / Postmuseum','https://digitaltmuseum.se/011024626117/karta'],
 atlas:['Åland 1894 · Wikimedia Commons','https://commons.wikimedia.org/wiki/Atlas_of_%C3%85land'],
 photo:['Flygfoton · Mariehamns stad','https://karta.mariehamn.ax/IMS/'],
 heritage:['Ålands landskapsregering · kulturarvsregister','https://kartor.regeringen.ax/arcgis/rest/services/Kulturarv/Fornminnen/MapServer'],
 ancient:['Ålands forntid · Visit Åland','https://visitaland.com/upplev/historia/alands-forntid/'],
 church:['Jomala kyrka · Jomala församling','https://www.jomala.evl.ax/kyrka-och-lokaler/jomala-kyrka'],
 castle:['Kastelholm, Vita Björn och Jan Karlsgården · Ålands museum','https://www.museum.ax/sites/default/files/attachments/page/22-0092%20Museer%20pa%CC%8A%20A%CC%8Aland_SVE.pdf'],
 fortress:['Huvudfästet · Ålands museum','https://www.museum.ax/vara-museer-och-sevardheter/bomarsunds-fastningsruin/sevardheter/huvudfastet'],
 ruin:['Bomarsunds besökscenter · Ålands museum','https://www.museum.ax/museer-sevardheter/bomarsunds-fastningsruin/bomarsunds-besokscenter'],
 city:['Maritima Mariehamn · Ålands Sjöfartsmuseum','https://sjofartsmuseum.ax/segelsjofarten-2-2-2-3/'],
 library:['Stadsbibliotekets historia · Mariehamns stad','https://www.mariehamn.ax/kultur-och-bibliotek/stadsbibliotekets-historia/'],
 shore:['Strandlinjemodell · maannousu.info / Glare 2.2','https://maannousu.info/index_sv'],
 cityGrid:['Gatunät · OpenStreetMap','https://www.openstreetmap.org/copyright'],
 historicCity:['Mariehamns byggnadsarv · Mariehamns stad','https://www.mariehamn.ax/kultur-och-bibliotek/kulturarv/kmarkta-byggnader'],
 uplift:['Landhöjning · Lantmäteriet','https://www.lantmateriet.se/sv/geodata/gps-geodesi-och-swepos/Referenssystem/Landhojning/']};
const eras=[
 {y:-12000,title:'Under isen',tag:'Istiden',text:'Här finns ännu inga hus. Ett tjockt täcke av is tynger ner landet. När isen smälter kan marken sakta resa sig igen.',q:'Hur tror du att ett så tungt istäcke påverkar marken?',more:'Det vita istäcket är en illustration, inte en daterad karta över iskanten.',src:'uplift'},
 {y:-8000,title:'De första öarna',tag:'Landet stiger',text:'Små bergstoppar tittar upp ur vattnet. Det som en dag blir Åland börjar synas!',q:'Kan du hitta de första små öarna?',more:'De högsta delarna började komma upp ur havet för ungefär 10 000 år sedan.',src:'ancient'},
 {y:-4000,title:'Stenålderns boplatser',tag:'Stenåldern',text:'Människor fiskar, jagar och tillverkar redskap. Arkeologerna hittar spår efter deras bostäder och eldstäder i norra Saltvik.',q:'Vad skulle du ta med dig till en ö utan affärer?',more:'Kända boplatser har olika dateringar. Läs registeruppgifterna för varje fyndplats. Hyddan med streckad ram är en rekonstruktion.',src:'ancient'},
 {y:-1500,title:'Hem vid havet',tag:'Bronsåldern',text:'Öarna växer. Människor lever nära vattnet. Spår från den här tiden finns kvar, bland annat gravar byggda av sten.',q:'Var skulle du vilja bygga ett hus?',more:'Bronsåldern dateras här ungefär 1500–400 f.Kr. Husets form och placering är en rekonstruktion.',src:'ancient'},
 {y:800,title:'Gårdar och sjöresor',tag:'Vikingatiden',text:'På gårdarna arbetar människor och tar hand om djur. Havet binder ihop öarna med platser långt borta.',q:'Hur kunde man resa långt innan det fanns bilar?',more:'Fynd från järnåldern visar kontakter med omvärlden. Gården är ett pedagogiskt exempel, inte en utgrävd byggnad.',src:'ancient'},
 {y:1280,title:'Kyrkor av sten',tag:'Medeltiden',text:'En stor kyrka byggs i Jomala. Stenhus kan stå kvar länge. Den här kyrkan finns fortfarande!',q:'Vad är annorlunda med att bygga i sten och i trä?',more:'Analyser daterar Jomala kyrkas torn till 1280-talet. Årtalet på reglaget är ungefärligt.',src:'church'},
 {y:1388,title:'Ett slott vid vattnet',tag:'Medeltiden',text:'Kastelholm blir en viktig borg. Innanför de tjocka murarna finns rum, förråd och en gård.',q:'Varför kan det vara bra att ha ett slott nära vattnet?',more:'Slottet grundades på 1380-talet. Kartans punkt visar platsen, inte slottets form vid ett visst år.',src:'castle'},
 {y:1784,title:'Gårdar och ett häkte',tag:'1700-talet',text:'På gårdarna behövs flera hus: ett att bo i och andra för djur och mat. Vid Kastelholm byggs häktet Vita Björn.',q:'Varför hade man många små hus på en gård?',more:'Vita Björn uppfördes 1784. Den visade bondgården är en rekonstruktion.',src:'castle'},
 {y:1800,earlyMap:true,title:'Vägar mellan byar och kyrkor',tag:'Åland kring 1800',text:'På den gamla kartan slingrar sig vägar mellan byar, kyrkor och vatten. Förstora och leta efter namn ni känner igen!',q:'Vilken väg skulle ni följa mellan Jomala och Kastelholm?',more:'Uppsala universitetsbibliotek daterar den handritade, delvis färglagda kartan till cirka 1800. Årtalet är ungefärligt. Bilden täcker främst fasta Åland och delar av skärgården. Kartarkivet låter er jämföra den med 1894 års karta.',src:'earlyMap'},
 {y:1832,title:'En fästning växer fram',tag:'1800-talet',text:'Vid Bomarsund börjar ett enormt hus av sten ta form. Här ska soldater bo och arbeta.',q:'Hur många olika rum kan ett så stort hus behöva?',more:'Huvudfästet byggdes 1832–1843. Delar togs i bruk från 1839.',src:'fortress'},
 {y:1854,title:'Fästningen blir ruin',tag:'En stor förändring',text:'Det blir krig vid Bomarsund. Fästningen förstörs. Murarnas rester finns kvar och hjälper oss att förstå vad som hände.',q:'Vad kan en gammal mur berätta?',more:'Bomarsund förstördes 1854. Platsens berättelse övergår till ruinen vid denna hållpunkt.',src:'ruin'},
 {y:1860,cityPlan:true,title:'En stad på ritbordet',tag:'Mariehamns stadsplan',text:'Innan staden byggs ritar arkitekten gator, torg och parker. Här finns plats för en kyrka, en skola och ett sjukhus. Öppna planen och leta tillsammans!',q:'Vad skulle du rita in om du fick planera en ny stad?',more:'G. Th. Chiewitz ritade planen 1859; den första stadsplanen är från 1860. Mariehamn grundades 1861. Ritningen visar avsikter, inte färdiga byggnader. Planen ändrades när staden växte fram. De breda esplanaderna och rutnätet blev viktiga delar av staden.',src:'cityPlan'},
 {y:1861,title:'En stad blir till',tag:'Mariehamn grundas',text:'Mariehamn grundas. Gator och hus ska ge plats åt en ny stad vid havet.',q:'Vad tycker du behövs i en helt ny stad?',more:'Mariehamn grundades 1861 och utvecklades som sjöfartsstad. Trähuset är ett exempel, inte en viss byggnad från grundläggningsåret.',src:'city'},
 {y:1920,cityMuseum:true,title:'Hus och gårdar i trästaden',tag:'Mariehamn på 1920-talet',text:'Trästaden har fått ett rutnät av gator, gröna esplanader och gårdar med många små hus. Utforska kvarteren på kartan och jämför med stadsplanen från 1860.',q:'Vilka små hus ligger inne på gårdarna?',more:'1920 är tidslinjens hållpunkt för 1920-talet. Kartan hör till Nybyggarnes modellstad och visar inte ett exakt läge under ett enda år. Läs husbeskrivningarna för närmare dateringar.',src:'cityMuseum'},
 {y:1939,title:'Plats för staden',tag:'1900-talet',text:'I Mariehamn finns ett nytt stadshus. Även bibliotekets böcker får plats där.',q:'Vilka hus använder vi tillsammans?',more:'Biblioteket flyttade in i stadshuset 1939. Symbolerna visar utvalda byggnader, inte hela bebyggelsen.',src:'library'},
 {y:1989,title:'Ett hus fullt av böcker',tag:'Nära vår egen tid',text:'Biblioteket flyttar till sitt nya hus. Här kan små och stora hitta berättelser och lära sig nya saker.',q:'Vilken bok skulle du vilja låna om Åland?',more:'Dagens biblioteksbyggnad togs i bruk 1989.',src:'library'},
 {y:2026,title:'Ditt Åland',tag:'Idag',text:'Gamla och nya hus finns sida vid sida. Landet fortsätter att stiga, långsamt. Historien finns runt omkring oss.',q:'Vilken av platserna vill ni besöka tillsammans?',more:'Utforska tusentals nutida byggnadskonturer och vägsegment i hela Åland, eller sök i fornlämningsregistret. Äldre strandlinjer hämtas från Glare 2.2. Vald tid och modellens år visas var för sig. Ålands kust och nutidsdetaljer kommer från OSM 2026.',src:'uplift'}
];
// Linked OSM IDs and interior anchor points use the checked 2026 extract.
// The link identifies a place; it never dates today's footprint back into history.
const buildings=[
 {id:'hut',name:'Ett skydd på stenåldern',loc:'Saltvik · exempel',lat:60.345,lon:20.08,start:-4000,end:-1501,type:'hut',recon:true,text:'Ett enkelt skydd håller vinden borta. Tänk dig att du sitter här efter en dag vid havet.',more:'Boplatser är kända i norra Saltvik. Den här symbolens form och plats är en fri rekonstruktion, inte en dokumenterad hydda.',q:'Hur håller du värmen utan element?',src:'ancient'},
 {id:'bronze',name:'Ett hem under bronsåldern',loc:'Norra Åland · exempel',lat:60.32,lon:20.08,start:-1500,end:799,type:'house',recon:true,text:'Här visar vi ett tänkt hem. Familjens vardag följer ljuset, vädret och årstiderna.',more:'Huset illustrerar boende under förhistorien. Form, placering och visningstid är pedagogiska val.',q:'Hur lyser du upp ett hus utan elektricitet?',src:'ancient'},
 {id:'farm',name:'En gård under vikingatiden',loc:'Saltvik · exempel',lat:60.286,lon:20.045,start:800,end:1279,type:'farm',recon:true,text:'På en gård finns plats för människor, djur och förråd. Många sysslor måste göras varje dag.',more:'Detta är en typbild av en gård, inte ett återgivet arkeologiskt fynd.',q:'Vad skulle du vilja hjälpa till med på gården?',src:'ancient'},
 {id:'jomala',name:'Jomala kyrka',loc:'Jomala',lat:60.1525,lon:19.951,start:1280,type:'church',text:'En kyrka av sten, med ett högt torn. Den har byggts om, men delar är mycket gamla.',more:'Tornets datering pekar på 1280-talet. Kyrkans form har förändrats; platsmarkören visar inte byggnadsfaserna.',q:'Hur tror du att man fick upp stenarna så högt?',src:'church'},
 {id:'kastelholm',name:'Kastelholms slott',loc:'Sund',lat:60.2328629,lon:20.0806707,osmId:'way/230385754',start:1380,type:'castle',text:'Tjocka stenmurar omger slottets gård. Här har både kungligheter och människor som arbetade åt dem vistats.',more:'Slottet grundades på 1380-talet och har senare förfallit och restaurerats. Platsmarkören visar läget, inte byggnadens form under varje fas.',q:'Vilket rum tror du var varmast i ett slott?',src:'castle'},
 {id:'rural',name:'En åländsk bondgård',loc:'Sund · exempel',lat:60.254,lon:20.114,start:1500,type:'farm',recon:true,text:'Bostad, lada och uthus hör ihop. På gården förvaras mat för både människor och djur.',more:'En tänkt gård inspirerad av åländsk byggnadskultur. Den representerar inte samma verkliga gård under alla år.',q:'Var skulle du förvara mat över vintern?',src:'castle'},
 {id:'vita',name:'Vita Björn',loc:'Kastelholm',lat:60.2314068,lon:20.0828216,osmId:'way/231687786',start:1784,type:'house',text:'Det här lilla huset var ett häkte och ett fängelse. Idag är det ett museum.',more:'Byggt 1784 och använt som häkte och fängelse till 1975. Funktionen ändras genom tiden.',q:'Hur kan ett museum hjälpa oss att förstå förr i tiden?',src:'castle'},
 {id:'bomarsund',name:'Bomarsunds huvudfäste',loc:'Sund',lat:60.2125,lon:20.238,start:1832,type:'fortress',text:'En jättestor byggnad med plats för bostäder, bageri och verkstäder.',more:'Huvudfästet byggdes 1832–1843, togs delvis i bruk 1839 och förstördes 1854. Därefter beskriver berättelsen ruinen.',q:'Varför behövde fästningen ett eget bageri?',src:'fortress'},
 {id:'townhouse',name:'Ett trähus i Mariehamn',loc:'Mariehamn · exempel',lat:60.100,lon:19.94,start:1861,type:'house',recon:true,text:'Staden behöver bostäder. Ett trähus kan vara både hem och plats för arbete.',more:'Detta är ett exempel på en bostad i staden, inte en utpekad historisk fastighet. Exakt form och byggår är inte dokumenterade.',q:'Vad skulle du se från fönstret i en ny stad?',src:'city'},
 {id:'library',name:'Mariehamns stadsbibliotek',loc:'Mariehamn',lat:60.101842,lon:19.9433614,osmId:'way/165435017',start:1989,type:'civic',text:'Ett hus där berättelser väntar på att bli upptäckta. Här finns böcker för både barn och vuxna.',more:'Nuvarande biblioteksbyggnad togs i bruk 1989.',q:'Vilken berättelse skulle du vilja skriva själv?',src:'library'}
];
eras.push(
 {y:-5000,title:'Tidiga spår i Saltvik',tag:'De första boplatserna',text:'Små stenbitar och eldstäder berättar att människor har bott här. I Bertby finns en av de tidiga boplatserna.',q:'Vad kan en liten stenbit berätta?',more:'Registret anger omkring 5000 f.Kr. för Bertby. Dateringar är ungefärliga och kan omprövas.',src:'heritage'},
 {y:1750,title:'Brev över land och hav',tag:'Postvägen',text:'Brev färdas från Sverige över Åland till Finland. Postförarna går, rider och ror mellan Grisslehamn, Eckerö, Vårdö, Kumlinge, Brändö och den finska kusten.',q:'Hur skulle du skicka ett brev utan bilar och flygplan?',more:'Postförbindelsen över Åland inrättades 1638 och användes sista gången vintern 1910–1911. Linjen går från Grisslehamn via Signilskär och Åland till Vartsala och Tuomois i Töfsala. Den är schematisk och bygger på Carlssons 1700-talskarta. Från 1756 visas den nya hamnen i Grisslehamn. Den större förbindelsen gick mellan Stockholm och Åbo; dessa landsträckor ligger utanför vårt ruttutsnitt. Kartlagret dateras inte tillbaka till grundandet. Sveriges kust är en förenklad nutida referens, inte en daterad strandlinje.',src:'postal'},
 {y:1894,title:'Åland på en gammal karta',tag:'Åland 1894',text:'På en gammal karta kan du känna igen öar och ortnamn. Vad är annorlunda jämfört med idag?',q:'Kan du hitta en plats som du känner igen?',more:'Originalkartan från 1894 finns i kartarkivet, via British Library och Wikimedia Commons.',src:'atlas'},
 {y:1942,title:'Mariehamn från luften',tag:'Flygfoto 1942',text:'Flygfotot visar en stad som växer längs sina infarter. Följ gatorna i vårt omritade stadsnät och jämför med 1920-talets kvarter.',q:'Vilka gator och hus känner du igen?',more:'Mariehamns stads flygfoto togs den 25 juli 1942. Vi daterar inte dagens byggnader bakåt utifrån deras nutida konturer.',src:'photo'},
 {y:2021,title:'En stad att jämföra',tag:'Flygfoto 2021',text:'Staden har vuxit. Jämför flygfotot från 2021 med bilden från 1942 och leta efter hus, gator och stränder som förändrats.',q:'Var har det kommit flest nya hus?',more:'Mariehamns stads flygfoto togs den 6 juni 2021. Gatunätet här använder arkiverade OpenStreetMap-data från 2021. Mariehamns huslager använder separata, daterade OSM-uttag från 2014, 2021 och 2025 samt nutida konturer.',src:'photo'}
);
eras.push({y:2014,title:'Ett större gatunät',tag:'Mariehamn 2014',text:'Staden har vuxit långt utanför de första kvarteren. Följ de nya gatorna norrut och söderut.',q:'Var slutar den gamla rutnätsstaden och var börjar nya områden?',more:'Gatorna kommer från ett arkiverat OpenStreetMap-underlag från 2014. Det visar vad som var kartlagt då, inte varje gatas byggår. Kvartersytorna har härletts mellan gatorna.',src:'cityGrid'},{y:2025,title:'Gator nära vår egen tid',tag:'Mariehamn 2025',text:'Känn igen stadens äldre rutnät bland de nyare gatorna. Vilken väg skulle ni ta genom staden?',q:'Vilka delar av stadsplanen känner ni fortfarande igen?',more:'Detta steg använder OpenStreetMap-data från 2025. Skillnader mot 2021 kan bero på både förändringar i staden och bättre kartläggning. Huslagret använder kartlagda konturer från 2025, med daterade berättelser om namngivna hus.',src:'cityGrid'});
Object.assign(buildings.find(b=>b.id==='bomarsund'),window.BOMARSUND_PLACES[0]);
buildings.push(...window.BOMARSUND_PLACES.slice(1));
eras.push({y:1853,title:'Ett helt samhälle vid fästningen',tag:'Bomarsund före förstörelsen',text:'Huvudfästet, tornen, butikerna och sjukhuset hörde ihop. Utforska området som det såg ut före förstörelsen. Några stora byggen hann aldrig bli färdiga.',q:'Vilka platser behövde människorna i Bomarsund varje dag?',more:'1853 är översiktens jämförelseår, inte alla byggnaders byggår. Kartan är en tolkad plan, med ungefärliga lägen och former. Den 1854-hållpunkt som följer visar läget efter förstörelsen.',src:'bomarsundPlan'});
eras.push({y:1959,routeId:'viking-1959',title:'Bilarna följer med över havet',tag:'Bilfärjan Viking',text:'Viking börjar segla mellan Gräddö, Mariehamn och Galtby. Nu kan resenärerna ta med bilen på färjan.',q:'Vad behöver en hamn ha för att bilar ska kunna köra ombord?',more:'Premiärturen gick den 1 juni 1959. År 1960 flyttade Vikinglinjen från Gräddö till Kapellskär. Linjen på kartan visar 1959 års hamnförbindelse.',src:'shipRoutes'},{y:1961,routeId:'eckero-1961',title:'En färjeförbindelse till Eckerö',tag:'Eckerö Linjen',text:'Eckerö Linjen börjar trafikera mellan Grisslehamn och Eckerö. Havet binder ihop orterna på varsin sida.',q:'Vilka saker skulle ni ta med på en färjeresa?',more:'Eckerö Linjens förbindelse är belagd från 1961 och trafikeras fortfarande 2026. Läs ruttens källor för mer om trafiken.',src:'eckeroRoute'});
eras.push({y:1300,routeId:'danska-itinerariet',title:'En vägbeskrivning över havet',tag:'Danska itinerariet',text:'En medeltida text beskriver en sjöväg genom Ålands skärgård. Sjöfarare hittar fram med hjälp av öar, sund och platser att gå i land på.',q:'Hur hittar man vägen över havet utan en telefon?',more:'Hållpunkten ligger ungefär kring 1300. Beskrivningens datering varierar mellan källorna: 1200-tal eller tidigt 1300-tal. Den kallas också Kung Valdemars segelled. Här kan ni följa Ålandsdelen från Arholma till Aspö. Linjen är en schematisk tolkning, inte en säker historisk farled.',src:'itinerary'});
eras.push(...WreckTimeline.events(window.WRECKS));
Object.assign(sources,window.OFREDEN.sources);
eras.push(...window.OFREDEN.events);buildings.push(...window.OFREDEN.places);
eras.sort((a,b)=>a.y-b.y);buildings.push(...window.EXTRA_PLACES,...window.WRECKS);
const LAST=eras.length-1,MAX_TIME=LAST*100;
let cityJourney=false,cityPlaybackYear=1860;
const cityStops=[1860,1861,1876,1900,1920,1939,1942,1957,1989,2014,2021,2025,2026];
let selectedFeature=null;
let pos=MAX_TIME,year=2026,era=LAST,selected=null,playing=false,timer,lastTick=0,meta;
let zoom=1,panX=0,panY=0,W=0,H=0,fit=1,hits=[],pointers=new Map(),gesture=null,dragged=false;
const canvas=$('#map'),ctx=canvas.getContext('2d');
const explorer=new ExplorerLayers(()=>{if(meta)explorer.prepare(project);draw()},selectFeature);
explorer.storyPlaces=window.OFREDEN.places;explorer.flags.ofreden=true;
const shorelines=new ShorelineModel(draw,$('#detailStatus'));
const historicalOverlay=new HistoricalOverlay(draw);
const historicalRoads=new HistoricalRoads(draw);
const cityGrid=new CityGrid(draw);
const cityBuildings=new CityBuildings(draw);explorer.cityBuildings=cityBuildings;explorer.cityLibrary=buildings.find(b=>b.id==='library');
let shipRouteHits=[];
function date(y){return y<0?`${Math.abs(y).toLocaleString('sv-SE')} f.Kr.`:y===2026?'2026 · idag':`${y} e.Kr.`}
function visible(){return buildings.filter(b=>(typeof cityJourney==='undefined'||!cityJourney||b.id!=='townhouse')&&(b.category!=='ofreden'||$('#layerOfreden').checked)&&(b.category!=='fortress'||BomarsundPlan.visible(b,year,$('#layerFortress').checked,$('#layerTraces').checked))&&(b.category!=='wreck'||WreckTimeline.visible(b,year,$('#layerWrecks').checked))&&year>=b.start&&year<=(b.end??9999)&&(!b.recon||$('#layerRecon').checked)&&(!(b.category==='marine')||$('#layerMarine').checked)&&(b.recordType!=='marine'||explorer.available(b,year)))}
// Only explicitly enabled reconstructions use illustrative house shapes.
function symbol(type,recon=false){if(type.startsWith('ofred-'))return ofredenSymbol(type);if(type==='wreck')return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><path d="M18 3Q8 11 9 27L13 32H23L27 27Q28 11 18 3Z" fill="#376778" stroke="#faf7e8" stroke-width="2"/><path d="M18 9V27M12 19H24" fill="none" stroke="#faf7e8" stroke-width="1.5"/></svg>';if(!recon)return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><circle cx="18" cy="18" r="5" fill="${type==='pilot'?'#406b76':'#886b51'}" stroke="#faf7e8" stroke-width="2"/></svg>`;
 const common='fill="#b9a271" stroke="#5b5946" stroke-width="1.5"';const shape=type==='farm'?`<rect x="3" y="4" width="11" height="26" ${common}/><rect x="21" y="5" width="11" height="9" ${common}/><rect x="21" y="21" width="11" height="9" ${common}/>`:type==='hut'?`<ellipse cx="18" cy="18" rx="13" ry="10" ${common}/><path d="M6 18H30" stroke="#79633e"/>`:`<rect x="4" y="8" width="28" height="20" ${common}/><path d="M4 18H32" stroke="#79634e"/>`;
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><rect x="1" y="1" width="34" height="34" rx="3" fill="none" stroke="#806640" stroke-dasharray="3 3"/>${shape}</svg>`;
}
const iconCache=new Map();function iconFor(b){const key=b.type+b.recon;if(!iconCache.has(key)){const im=new Image();im.onload=draw;im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(symbol(b.type,b.recon));iconCache.set(key,im)}return iconCache.get(key)}
function storyMarkerMode(b){
 if(explorer.cityBuildings&&b.id==='library')return 'city-building';
 if(b.category==='ofreden')return 'ofreden';
 if(b.category==='fortress')return 'site-plan';
 if(b.category==='wreck')return 'wreck';
 if(b.recon)return 'reconstruction';
 const f=explorer.modernById?.get(b.osmId),mpp=meta?Math.cos(60.1*Math.PI/180)*40075016.7/meta.world/(fit*zoom):Infinity;
 return year>=2026&&explorer.flags.modern&&explorer.prepared&&f&&explorer.modernVisible(f,mpp)?'footprint':'point';
}
function drawStoryPlaces(){hits=[];for(const b of visible()){
 const mode=storyMarkerMode(b);if(mode==='footprint'||mode==='site-plan'||mode==='city-building')continue;
 const[x,y]=screen(b.lon,b.lat),size=mode==='ofreden'?30:mode==='wreck'?26:mode==='reconstruction'?Math.min(48,25+zoom*2):12;if(x<-40||x>W+40||y<-40||y>H+40)continue;
 ctx.save();if(selected===b.id){ctx.fillStyle='#faf8eaca';ctx.beginPath();ctx.arc(x,y,size*.8,0,7);ctx.fill();ctx.strokeStyle='#6c8660';ctx.lineWidth=2;ctx.stroke()}
 if(mode==='reconstruction'||mode==='wreck'||mode==='ofreden'){const im=iconFor(b);if(im.complete)ctx.drawImage(im,x-size/2,y-size/2,size,size)}else{ctx.beginPath();ctx.arc(x,y,4.5,0,7);ctx.fillStyle=b.category==='marine'?'#406b76':'#886b51';ctx.fill();ctx.strokeStyle='#faf7e8';ctx.lineWidth=1.5;ctx.stroke()}
 if(selected===b.id||(mode==='ofreden'&&zoom>3)||(mode==='reconstruction'&&zoom>2)){ctx.font='11px -apple-system,sans-serif';ctx.textAlign='center';const name=b.id==='bomarsund'&&year>=1854?'Bomarsunds ruiner':b.name,m=ctx.measureText(name);ctx.fillStyle='#f8f7f1ee';ctx.fillRect(x-m.width/2-5,y+size/2+2,m.width+10,18);ctx.fillStyle='#354d40';ctx.fillText(name,x,y+size/2+15)}ctx.restore();hits.push({id:b.id,x,y,size});
}}
function sourceLink(k){return `<a href="${sources[k][1]}" target="_blank" rel="noreferrer">${sources[k][0]} ↗</a>`}
// Article titles checked against Swedish Wikipedia; Ofreden additions 2026-10-14.
// Reconstructed homes link to background reading, never to a fictitious building.
const buildingWikipedia={
 hut:'Ålands historia',bronze:'Ålands historia',farm:'Ålands historia',
 jomala:'Jomala kyrka',kastelholm:'Kastelholms slott',rural:'Ålands historia',
 vita:'Vita Björn',bomarsund:'Bomarsunds fästning',townhouse:'Mariehamn',
 library:'Mariehamns stadsbibliotek'
};
const eraWikipedia={
 '1714':'Stora ofreden','1718':'Ålandskongressen','1719':'Stora ofreden','1720':'Slaget vid Föglöfjärden','1721':'Ålands historia','1742':'Ålands historia','1743':'Ålands historia',
 '-5000':'Ålands historia','1750':'Ålands historia','1800':'Åland','1894':'Åland','1942':'Mariehamn','2021':'Mariehamn',
 '-12000':'Istid','-8000':'Landhöjning','-4000':'Ålands historia',
 '-1500':'Ålands historia','800':'Ålands historia','1280':'Jomala kyrka',
 '1300':'Kung Valdemars segelled','1388':'Kastelholms slott','1784':'Vita Björn','1832':'Bomarsunds fästning',
 '1854':'Bomarsunds fästning','1860':'Mariehamn','1861':'Mariehamn','1920':'Mariehamn','1939':'Mariehamns stadshus',
 '1989':'Mariehamns stadsbibliotek','2026':'Ålands historia'
};
function wikipediaLink(building,period){
 if(building?.wiki)return `<p class="wikipedia-link"><a href="${safeURL(building.wiki)}" target="_blank" rel="noopener noreferrer">Wikipedia: ${htmlEscape(building.name)}${building.wikiLanguage?' ('+htmlEscape(building.wikiLanguage)+')':''} ↗</a></p>`;
 const title=building?buildingWikipedia[building.id]:eraWikipedia[period.y];
 if(!title)return '';
 const href='https://sv.wikipedia.org/wiki/'+encodeURIComponent(title.replaceAll(' ','_'));
 return `<p class="wikipedia-link"><a href="${href}" target="_blank" rel="noopener noreferrer" aria-label="${building?.recon?'Bakgrund på Wikipedia':'Wikipedia'}: ${title} (öppnas i ny flik)">${building?.recon?'Bakgrund på Wikipedia':'Wikipedia'}: ${title} ↗</a></p>`;
}
function updateUI(){let e=cityJourney?cityPeriod(year):eras[era],b=buildings.find(b=>b.id===selected&&visible().includes(b));if(!b)selected=null;$('.maparea').classList.toggle('fortress-view',b?.category==='fortress');$('.maparea').classList.toggle('ship-route-view',selectedFeature?.recordType==='shipRoute');$('#eraTitle').textContent=b?.category==='fortress'?'Bomarsund':selectedFeature?.recordType==='shipRoute'?'Fartygsrutter':e.tag;$('#mapDate').textContent=date(year);$('#yearLabel').textContent=date(year);$('#eraIndex').textContent=`${era+1} / ${eras.length}`;
const body=b?{...b,title:b.name,tag:b.category==='ofreden'?'Händelseplats · '+b.dateLabel:b.category==='fortress'?BomarsundPlan.tag(b,year):b.category==='wreck'?WreckTimeline.tag(b,year):b.category==='marine'?(EvidenceTime.state(b,year)==='trace'?'Tidigare lots- eller fyrplats':'Lots- eller fyrplats'):b.recon?'Rekonstruktion':b.id==='bomarsund'&&year>=1854?'Ruin sedan 1854':b.id==='bomarsund'&&year<1843?'Under byggnad':'Historisk byggnad'}:e;
const wreck=wreckForStory(b,e);
if(b?.category==='wreck')body.text=WreckTimeline.text(b,year);
if(b?.category==='fortress'){body.text=year>=1854?b.ruinText:b.text;body.title=year>=1854&&b.kind!=='cemetery'?b.name+' · äldre plats':b.name}
$('#story').innerHTML=`${b?'<button class="back" id="back">← Till tidsperioden</button><br>':''}<span class="storytag">${body.tag}</span><h2>${body.title}</h2><p>${body.text}</p>${wikipediaLink(b||wreck,e)}${b?.category==='ofreden'?ofredenDetails(b):''}${!b&&e.ofredenPlace?'<button id=focusOfredenEvent>Visa platsen på kartan</button>':''}${!b&&e.cityPlan?cityPlanControls():''}${!b&&e.cityMuseum?cityMuseumControls():''}${!b&&e.earlyMap?earlyMapControls():''}${!b&&e.routeId?'<button id=focusRouteEvent>Visa fartygsrutten</button>':''}${b?.category==='fortress'?`<div class="dating"><p>${htmlEscape(b.dateNote)}</p><small>${htmlEscape(b.geometrySource)} · Lägen och former är ungefärliga.</small></div>`:''}${b?.category==='fortress'||[1832,1853,1854].includes(e.y)?fortressControls():''}${wreck?wreckDetails(wreck):''}${wreck&&!b?`<button id="focusWreckEvent">Visa ${htmlEscape(wreck.name)} på kartan</button>`:''}${b?.temporal?`<p class="evidence-badge">${EvidenceTime.label(EvidenceTime.state(b,year))}</p><p class="asidehint">${htmlEscape(EvidenceTime.phase(b,year)?.label||b.temporal.dateLabel)}</p>`:''}<div class="question"><strong>Fundera tillsammans</strong>${body.q}</div><details><summary>Läs mer tillsammans</summary><p>${body.more}</p>${body.sourceUrl?`<a href="${safeURL(body.sourceUrl)}" target="_blank" rel="noreferrer">Ålands landskapsregering · platsens registeruppgifter ↗</a>`:sourceLink(body.src)}${b?.category==='fortress'?b.links.map(([label,url])=>`<p><a href="${safeURL(url)}" target="_blank" rel="noreferrer">${htmlEscape(label)} ↗</a></p>`).join(''):''}${(body.links||[]).map(([label,url])=>`<p><a href="${safeURL(url)}" target="_blank" rel="noopener noreferrer">${htmlEscape(label)} ↗</a></p>`).join('')}${wreck?wreck.links.map(([label,url])=>`<p><a href="${safeURL(url)}" target="_blank" rel="noreferrer">${htmlEscape(label)} ↗</a></p>`).join(''):''}</details>`;
$('#story').querySelectorAll('[data-city-plan]').forEach(el=>el.onclick=()=>el.dataset.cityPlan==='original'?window.openCityPlanArchive():window.openCityPlan(Number(el.dataset.cityPlan)));
$('#story').querySelectorAll('[data-city-museum]').forEach(el=>el.onclick=()=>el.dataset.cityMuseum==='original'?window.openCityMapArchive('1920'):window.openCityMap('1920',Number(el.dataset.cityMuseum)));
$('#story').querySelectorAll('[data-early-map]').forEach(el=>el.onclick=()=>window.openEarlyMapArchive(el.dataset.earlyMap==='compare'));
if($('#focusOfredenEvent'))$('#focusOfredenEvent').onclick=()=>openOfreden(e.y,true);
if($('#focusRouteEvent'))$('#focusRouteEvent').onclick=()=>openShipRoute(e.routeId);
if(!b&&e.y===1750){$('#story details').insertAdjacentHTML('beforeend','<p>'+sourceLink('postalEnd')+'</p><p><a href="https://www.sjofartsmuseet.se/Postrodden/Postroddens-historia.html" target="_blank" rel="noopener noreferrer">Roslagens sjöfartsmuseum · flytten 1756 ↗</a></p><p><a href="https://visitkustavi.fi/en/kohde/suuri-postitie/" target="_blank" rel="noopener noreferrer">Gustavs · postvägen till Vartsala ↗</a></p>');$('#story').insertAdjacentHTML('beforeend','<button id="showPostalRoute">Visa postvägen Sverige–Finland</button>');$('#showPostalRoute').onclick=()=>{explorer.flags.postal=true;$('#layerPostal').checked=true;focusPostalRoute();window.MapUI?.showMap()}}
if(!b&&year>=1860){$('#story').insertAdjacentHTML('beforeend',`<p id="cityBuildingNote" class="asidehint">${htmlEscape(cityBuildings.status(year,cityBuildings.records(year,explorer,cityGrid,explorer.cityLibrary)))}</p><p id="cityStageNote" class="asidehint">${htmlEscape(cityGrid.status(year))}</p>${e.cityPlan||e.cityMuseum?'':`<button data-city-grid-year="${year}">Utforska Mariehamns stadsnät</button>`}`);bindCityGridButtons()}
updateRouteList();
if($('#fortressClose'))$('#fortressClose').onclick=()=>{const main=window.BOMARSUND_PLACES[0];focusMap(main.lon,main.lat,100);selectBuilding(main.id,false)};
$('#story').querySelectorAll('[data-fortress-year]').forEach(el=>el.onclick=()=>openBomarsund(Number(el.dataset.fortressYear)));
if($('#focusWreckEvent'))$('#focusWreckEvent').onclick=()=>openWreck(wreck, e.y);
if($('#back'))$('#back').onclick=()=>{selected=null;explorer.selected=null;updateUI();draw()};
$('#placeCount').textContent=visible().length;$('#places').innerHTML=visible().map(b=>`<button class="place ${b.id===selected?'active':''}" data-id="${b.id}"><span class="icon">${symbol(b.type,b.recon)}</span><span>${b.id==='bomarsund'&&year>=1854?'Bomarsunds ruiner':b.name}<small>${b.loc}${b.recon?' · rekonstruktion':''}</small></span><span class="arrow">›</span></button>`).join('')||'<p class="asidehint">Inga utvalda platser visas under den här perioden. Följ hur landet förändras.</p>';
$('#places').querySelectorAll('button').forEach(el=>el.onclick=()=>selectBuilding(el.dataset.id,true));$('#previous').disabled=cityJourney?year<=1860:pos<=0;$('#next').disabled=pos>=MAX_TIME;if(selectedFeature)showFeatureStory();window.MapUI?.refreshStory();
}
function yearAtPosition(p){const i=Math.min(LAST-1,Math.floor(p/100)),t=(p-i*100)/100;return Math.round(eras[i].y+(eras[i+1].y-eras[i].y)*t)||1}
function setTime(p){if(cityJourney&&yearAtPosition(Number(p))<1860)setCityJourney(false);selected=null;selectedFeature=null;explorer.selected=null;pos=Math.max(0,Math.min(MAX_TIME,Number(p)));year=yearAtPosition(pos);era=Math.max(0,eras.findLastIndex(e=>year>=e.y));$('#jumpYear').value=year;$('#time').value=cityJourney?year:pos;$('#time').setAttribute('aria-valuetext',date(year));updateUI();draw();window.MapUI?.timeChanged({era,year,date:date(year),title:cityJourney?cityPeriod(year).title:eras[era].title,playing,atStop:Math.abs(pos/100-Math.round(pos/100))<.001})}
function project(lon,lat){return [(lon+180)/360*meta.world-meta.x0,(1-Math.asinh(Math.tan(lat*Math.PI/180))/Math.PI)/2*meta.world-meta.y0]}
function screen(lon,lat){let [x,y]=project(lon,lat);return[(x-meta.width/2)*fit*zoom+W/2+panX,(y-meta.height/2)*fit*zoom+H/2+panY]}
function draw(){if(!meta)return;ctx.clearRect(0,0,W,H);let s=fit*zoom;const view={width:W,height:H,zoom,scale:s,panX,panY,meta,year,routeGroup:$('#routeGroup').value,onlyRoute:$('#onlyRoute').checked};shorelines.draw(ctx,view);view.overlay=historicalOverlay;view.historicalRoads=historicalRoads;view.cityGrid=cityGrid;view.cityBuildings=cityBuildings;cityBuildings.selected=selected;cityGrid.selected=selectedFeature?.recordType==='cityGrid'?selectedFeature.id:null;historicalRoads.selected=selectedFeature?.recordType==='historicalRoad'?selectedFeature.id:null;
const fortressCenter=screen(20.238,60.215);view.fortressDetail=$('#layerFortress').checked&&year>=1832&&zoom>=12&&fortressCenter[0]>=0&&fortressCenter[0]<=W&&fortressCenter[1]>=0&&fortressCenter[1]<=H;
explorer.prepare(project);explorer.render(ctx,view);shipRouteHits=TransportRoutes.draw(ctx,view,screen,$('#layerShipRoutes').checked,selectedFeature?.recordType==='shipRoute'?selectedFeature.id:null);
ctx.save();ctx.fillStyle='#54797c';ctx.font='italic 17px Georgia';ctx.textAlign='center';[['Ålands hav',19.42,60.08],['Skärgårdshavet',20.95,60.32]].forEach(([n,x,y])=>{let p=screen(x,y);ctx.fillText(n,...p)});ctx.restore();
if(year>=-4000){ctx.font='10px -apple-system,sans-serif';ctx.textAlign='center';ctx.fillStyle='#65775c';[['GETA',19.84,60.38],['SALT VIK',20.12,60.34],['ECKERÖ',19.57,60.22],['JOMALA',19.90,60.18],['FÖGLÖ',20.46,60.02],['KUMLINGE',20.75,60.25],['KÖKAR',20.90,59.91],['BRÄNDÖ',21.03,60.42]].forEach(([n,x,y])=>{let p=screen(x,y);ctx.fillText(n==='SALT VIK'?'SALTVIK':n,...p)})}
drawStoryPlaces();hits.push(...BomarsundPlan.draw(ctx,visible().filter(b=>b.category==='fortress'),screen,year,zoom,selected,W,H));let mpp=Math.cos(60.2*Math.PI/180)*40075016.7/meta.world/s;$('#scale').textContent=mpp*60<1000?Math.round(mpp*60/10)*10+' m':(mpp*60/1000).toFixed(zoom>5?1:0)+' km';$('#scale').style.width='60px'}
function resize(){let r=canvas.getBoundingClientRect();W=r.width;H=r.height;let d=window.devicePixelRatio||1;canvas.width=Math.round(W*d);canvas.height=Math.round(H*d);ctx.setTransform(d,0,0,d,0,0);if(meta){const oldFit=fit;fit=Math.min(W/meta.width,H/meta.height)*1.28;panX*=fit/oldFit;panY*=fit/oldFit}draw()}
function zoomAt(f,x=W/2,y=H/2){let old=zoom;zoom=Math.max(.3,Math.min(256,zoom*f));panX=x-W/2-(x-W/2-panX)*zoom/old;panY=y-H/2-(y-H/2-panY)*zoom/old;draw()}
function selectBuilding(id,focus){selectedFeature=null;explorer.selected=null;selected=id;const b=buildings.find(x=>x.id===id);explorer.selected=b.osmId||null;if(focus&&b.category==='fortress'){fitBomarsund();focus=false}if(focus&&meta){zoom=Math.max(zoom,5);let [x,y]=project(b.lon,b.lat);panX=-(x-meta.width/2)*fit*zoom;panY=-(y-meta.height/2)*fit*zoom}pause();updateUI();draw();window.MapUI?.showStory(true)}
function pause(){const wasPlaying=playing;playing=false;cancelAnimationFrame(timer);$('#play').innerHTML='▶ <span>Spela</span>';$('#play').setAttribute('aria-label','Spela tidsresan');if(wasPlaying)window.MapUI?.playbackStopped()}
function playbackFrame(now){
 if(!playing)return;
 if(typeof cityJourney!=='undefined'&&cityJourney){cityPlaybackFrame(now);return}
 // A slow download or a busy/background tab must never cause a jump through time.
 const elapsed=Math.min(100,Math.max(0,now-lastTick));
 if(elapsed<32){timer=requestAnimationFrame(playbackFrame);return}lastTick=now;
 const stop=(Math.floor(pos/100)+1)*100;
 const nextPos=Math.min(MAX_TIME,$('#autostop').checked?stop:MAX_TIME,pos+elapsed/60);
 if(shorelines.prepare(yearAtPosition(nextPos))){
  if(yearAtPosition(nextPos)!==year)setTime(nextPos);
  else{pos=nextPos;$('#time').value=pos}
  if(pos>=MAX_TIME||($('#autostop').checked&&pos>=stop)){pause();return}
 }
 timer=requestAnimationFrame(playbackFrame);
}
$('#play').onclick=()=>{if(playing){pause();return}if(pos>=MAX_TIME){if(cityJourney)goToYear(1860);else setTime(0)}cityPlaybackYear=year;playing=true;window.MapUI?.playbackStarted();$('#play').innerHTML='Ⅱ <span>Pausa</span>';$('#play').setAttribute('aria-label','Pausa tidsresan');lastTick=performance.now();shorelines.prepare(year);timer=requestAnimationFrame(playbackFrame)};
$('#time').oninput=e=>{pause();if(cityJourney)goToYear(Number(e.target.value));else setTime(e.target.value)};$('#previous').onclick=()=>{pause();if(cityJourney){goToYear(cityStops.filter(y=>y<year).at(-1)??1860);return}setTime(Math.max(0,Math.ceil(pos/100)-1)*100)};$('#next').onclick=()=>{pause();if(cityJourney){goToYear(cityStops.find(y=>y>year)??2026);return}setTime(Math.min(LAST,Math.floor(pos/100)+1)*100)};document.querySelectorAll('[data-year]').forEach(b=>{b.style.left=(positionForYear(Number(b.dataset.year))/MAX_TIME*100)+'%';b.onclick=()=>{pause();setCityJourney(false);selected=null;goToYear(Number(b.dataset.year))}});
$('#zoomIn').onclick=()=>zoomAt(1.6);$('#zoomOut').onclick=()=>zoomAt(1/1.6);$('#reset').onclick=()=>{setCityJourney(false);zoom=1;panX=panY=0;draw()};canvas.addEventListener('wheel',e=>{e.preventDefault();const r=canvas.getBoundingClientRect();zoomAt(e.deltaY>0?.88:1.14,e.clientX-r.left,e.clientY-r.top)},{passive:false});
function cancelMapGesture(){pointers.clear();gesture=null;dragged=false}
canvas.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0)return;canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});gesture={x:e.clientX,y:e.clientY,panX,panY};dragged=false;if(pointers.size===2){let [a,b]=[...pointers.values()];gesture={distance:Math.hypot(a.x-b.x,a.y-b.y),cx:(a.x+b.x)/2,cy:(a.y+b.y)/2};dragged=true}});
canvas.addEventListener('pointermove',e=>{if(e.pointerType==='mouse'&&e.buttons===0){cancelMapGesture();return}if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===2){let [a,b]=[...pointers.values()],r=canvas.getBoundingClientRect();const distance=Math.hypot(a.x-b.x,a.y-b.y),cx=(a.x+b.x)/2,cy=(a.y+b.y)/2;if(gesture?.distance>0){panX+=cx-gesture.cx;panY+=cy-gesture.cy;zoomAt(distance/gesture.distance,cx-r.left,cy-r.top)}gesture={distance,cx,cy};return}if(!gesture||gesture.distance)return;let dx=e.clientX-gesture.x,dy=e.clientY-gesture.y;if(Math.abs(dx)+Math.abs(dy)>5)dragged=true;if(!dragged)return;panX=gesture.panX+dx;panY=gesture.panY+dy;draw()});
canvas.addEventListener('pointerup',e=>{if(!dragged&&pointers.size===1){let r=canvas.getBoundingClientRect(),x=e.clientX-r.left,y=e.clientY-r.top,h=hits.filter(h=>storyHit(h,x,y)).sort((a,b)=>Math.hypot(x-a.x,y-a.y)-Math.hypot(x-b.x,y-b.y))[0];if(h)selectBuilding(h.id,false);else{const f=cityBuildings.hit(x,y,ctx)||explorer.hit(x,y,ctx)||cityGrid.hit(x,y,ctx)||historicalRoads.hit(x,y,ctx)||TransportRoutes.hit(shipRouteHits,x,y);if(f?.cluster){const lon=f.cluster.reduce((s,f)=>s+f.lon,0)/f.cluster.length,lat=f.cluster.reduce((s,f)=>s+f.lat,0)/f.cluster.length;focusMap(lon,lat,Math.min(256,zoom*2))}else if(f)selectFeature(f,false)}}pointers.delete(e.pointerId);gesture=null;if(pointers.size===1){let a=[...pointers.values()][0];gesture={x:a.x,y:a.y,panX,panY};dragged=true}});canvas.addEventListener('pointercancel',cancelMapGesture);
canvas.addEventListener('lostpointercapture',e=>{if(pointers.has(e.pointerId))cancelMapGesture()});
window.addEventListener('blur',cancelMapGesture);
canvas.addEventListener('keydown',e=>{if(['+','=','-','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Home'].includes(e.key)){e.preventDefault();if(e.key==='+'||e.key==='=')zoomAt(1.5);if(e.key==='-')zoomAt(1/1.5);if(e.key==='ArrowUp')panY+=50;if(e.key==='ArrowDown')panY-=50;if(e.key==='ArrowLeft')panX+=50;if(e.key==='ArrowRight')panX-=50;if(e.key==='Home'){zoom=1;panX=panY=0}draw()}});
$('#sources').innerHTML=Object.keys(sources).map(k=>`<li>${sourceLink(k)}</li>`).join('');$('#about').onclick=()=>{pause();$('#info').showModal()};$('#closeInfo').onclick=()=>$('#info').close();new ResizeObserver(resize).observe(canvas);document.addEventListener('visibilitychange',()=>{if(document.hidden)pause()});
function positionForYear(y){let i=Math.max(0,eras.findLastIndex(e=>y>=e.y));if(i>=LAST)return MAX_TIME;return i*100+(y-eras[i].y)/(eras[i+1].y-eras[i].y)*100}
function goToYear(y){setTime(positionForYear(Math.max(-12000,Math.min(2026,y))))}
function focusMap(lon,lat,targetZoom=24){if(!meta)return;zoom=targetZoom;let[x,y]=project(lon,lat);panX=-(x-meta.width/2)*fit*zoom;panY=-(y-meta.height/2)*fit*zoom;draw()}
function focusPostalRoute(){
 if(!meta)return;
 const points=window.postalRouteForYear(year).map(p=>project(p.lon,p.lat));if(!points.length)return;
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);
 // Fit both endpoints even on narrow phones; labels face into the viewport.
 zoom=Math.max(.3,Math.min(2,(W-64)/((right-left)*fit),(H-100)/((bottom-top)*fit)));
 panX=-((left+right)/2-meta.width/2)*fit*zoom;panY=-((top+bottom)/2-meta.height/2)*fit*zoom;draw();
}
function showFeatureStory(){$('#story').innerHTML=selectedFeature.recordType==='cityBuilding'?cityBuildings.story(selectedFeature):selectedFeature.recordType==='cityGrid'?cityGrid.story(selectedFeature):selectedFeature.recordType==='shipRoute'?TransportRoutes.story(selectedFeature):selectedFeature.recordType==='historicalRoad'?historicalRoads.story(selectedFeature):explorer.story(selectedFeature);$('#backFeature').onclick=()=>{selectedFeature=null;explorer.selected=null;updateUI();draw()};bindCityGridButtons();window.MapUI?.refreshStory()}
function selectFeature(f,focus){if(f.recordType==='shipRoute'){openShipRoute(f.id,focus);return}const story=visible().find(b=>b.id===f.id||b.osmId===f.id);if(story){selectBuilding(story.id,focus);return}pause();selected=null;selectedFeature=f;explorer.selected=f.id;if(focus&&!f.kind)focusMap(f.lon,f.lat,Math.max(zoom,16));showFeatureStory();draw();window.MapUI?.showStory(true)}
$('#time').max=MAX_TIME;
function applyYearInput(){const input=$('#jumpYear');if(input.value.trim()===''||!Number.isFinite(Number(input.value)))return;pause();goToYear(Number(input.value))}
$('#jumpYear').onchange=applyYearInput;$('#jumpYear').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();applyYearInput()}};
function clearSearch(){$('#placeSearch').value='';explorer.search('');$('#registerStatus').textContent=explorer.heritage.length.toLocaleString('sv-SE')+' registerposter · Ålands landskapsregering'}
$('#modernPlace').onchange=e=>{if(e.target.value==='')return;const p=explorer.modernPlaces[Number(e.target.value)];if(!p)return;pause();clearSearch();explorer.flags.modern=true;$('#layerModern').checked=true;goToYear(2026);focusMap(p.lon,p.lat,28);e.target.value=''};
$('#focusMariehamn').onclick=()=>{pause();clearSearch();goToYear(2026);focusMap(19.941,60.103,28)};
$('#focusStone').onclick=()=>{pause();clearSearch();goToYear(-4000);focusMap(20.130,60.316,16)};
$('#focusFortress').onclick=()=>openBomarsund(1853);
$('#layerFortress').onchange=()=>{updateUI();draw()};
$('#focusPostal').onclick=()=>{pause();$('#layerPostal').checked=true;explorer.flags.postal=true;goToYear(1750);focusPostalRoute()};
for(const[id,key]of [['layerHeritage','heritage'],['layerUndated','undated'],['layerModern','modern'],['layerPostal','postal'],['layerUncertain','uncertain'],['layerTraces','traces'],['layerHistoric','historic'],['layerBoundaries','boundaries']])$("#"+id).onchange=e=>{explorer.flags[key]=e.target.checked;explorer.listKey=null;selectedFeature=null;updateUI();draw()};
$('#categoryFilter').onchange=e=>{explorer.category=e.target.value;explorer.listKey=null;draw()};
$('#layerRecon').onchange=()=>{updateUI();draw()};
$('#layerCoverageGaps').onchange=e=>{shorelines.showCoverageGaps=e.target.checked;draw()};
function chooseMapBackground(value,focus=true){
 const cityMap=['1860','1920'].includes(value);$('.maparea').classList.toggle('city-plan-view',cityMap);historicalOverlay.enabled=value!=='model';historicalOverlay.mode=value;historicalOverlay.loadCityPlan();historicalOverlay.loadMuseumMap();$('#mapBackground').value=value;
 $('#cityPlanActions').hidden=!cityMap;$('#overlayControls').hidden=!historicalOverlay.enabled;$('#overlayBadge').hidden=!historicalOverlay.enabled;
 $('#overlayBadge').textContent=value==='1860'?'Stadsplan 1860 · planerade byggnader · ungefärlig inpassning':value==='1920'?'1920-talet · museikarta · ungefärlig inpassning':'Kartöverlägg 1894 · ungefärlig inpassning';
 if(focus&&historicalOverlay.enabled){if(cityMap)focusCityPlan();else focusMap(20.1,60.25,1.4)}draw();
}
$('#mapBackground').onchange=e=>chooseMapBackground(e.target.value);
$('#overlayOpacity').oninput=e=>{historicalOverlay.opacity=Number(e.target.value)/100;$('#opacityValue').textContent=e.target.value+' %';draw()};
$('#layerWrecks').onchange=()=>{updateUI();draw()};
$('#wreckChoice').innerHTML='<option value="">Välj ett fartyg…</option>'+window.WRECKS.map(w=>`<option value="${w.id}">${w.name} · ${w.sinkingYear??w.discoveryYear}${w.sinkingYear==null?' (hittas)':''}</option>`).join('');
$('#wreckChoice').onchange=e=>{const w=window.WRECKS.find(w=>w.id===e.target.value);if(w)openWreck(w);e.target.value=''};
$('#ofredenYear').innerHTML='<option value="">Välj en berättelse…</option>'+window.OFREDEN.events.map(e=>`<option value="${e.y}">${e.y} · ${htmlEscape(e.title)}</option>`).join('');
$('#ofredenYear').onchange=e=>{if(e.target.value)openOfreden(Number(e.target.value));e.target.value=''};
$('#layerOfreden').onchange=e=>{explorer.flags.ofreden=e.target.checked;explorer.listKey=null;updateUI();draw()};
$('#layerMarine').onchange=()=>{updateUI();draw()};
$('#placeSearch').oninput=e=>explorer.search(e.target.value);
function jumpToSearch(){const query=$('#placeSearch').value.trim().toLocaleLowerCase('sv'),wreck=query&&window.WRECKS.find(w=>w.name.toLocaleLowerCase('sv').includes(query)||w.registryCode.toLocaleLowerCase('sv')===query);if(wreck){openWreck(wreck);return}const ofreden=query&&window.OFREDEN?.places.find(p=>[p.name,p.loc,...p.registryCodes].join(' ').toLocaleLowerCase('sv').includes(query));if(ofreden){openOfreden(ofreden.start,true);return}const found=explorer.search($('#placeSearch').value),q=explorer.query;const rank=f=>f.name.toLocaleLowerCase('sv')===q||f.code.toLocaleLowerCase('sv')===q?0:f.name.toLocaleLowerCase('sv').startsWith(q)?1:2;found.sort((a,b)=>rank(a)-rank(b));const f=found[0];if(f){$('#registerStatus').textContent=found.length+' sökträffar i hela registret';if(!explorer.available(f,year)){if(EvidenceTime.firstYear(f)!=null){explorer.flags.uncertain=true;$('#layerUncertain').checked=true;goToYear(EvidenceTime.firstYear(f))}else{$('#layerUndated').checked=true;explorer.flags.undated=true}}explorer.flags.heritage=true;$('#layerHeritage').checked=true;explorer.flags.historic=true;$('#layerHistoric').checked=true;explorer.category='all';$('#categoryFilter').value='all';selectFeature(f,true)}else $('#registerStatus').textContent='Inga fyndplatser matchar sökningen.'}
$('#searchPlace').onclick=jumpToSearch;$('#placeSearch').onkeydown=e=>{if(e.key==='Enter')jumpToSearch()};
if(matchMedia('(max-width:800px)').matches)$('.layers').open=false;
setTime(MAX_TIME);explorer.load();shorelines.load();historicalOverlay.load();historicalRoads.load();cityGrid.load();cityBuildings.load();
(async()=>{try{const res=await fetch('assets/terrain.json?v=b67087802576');if(!res.ok)throw Error('metadata');meta=await res.json();$('#mapStatus').textContent='';resize();focusMap(19.941,60.103,28)}catch(e){$('#mapStatus').textContent='Kartan kunde inte laddas. Ladda om sidan för att försöka igen. Berättelserna går fortfarande att läsa.';console.error(e)}})();
window.currentMapContext=()=>{if(!meta)return {year,lon:19.941,lat:60.103};const x=meta.x0+meta.width/2-panX/(fit*zoom),y=meta.y0+meta.height/2-panY/(fit*zoom);return{year,lon:x/meta.world*360-180,lat:Math.atan(Math.sinh(Math.PI*(1-2*y/meta.world)))*180/Math.PI,zoom}};

function openWreck(wreck, eventYear=wreck.sinkingYear??wreck.discoveryYear){
 pause();clearSearch();goToYear(eventYear);focusMap(wreck.lon,wreck.lat,5);selectBuilding(wreck.id,false);
}
function wreckDetails(wreck){
 const dates=[wreck.sinkingYear?`Förlisning: ${wreck.sinkingYear}`:'Förlisning: osäkert år',...(wreck.discoveryYear?[`Upptäckt: ${wreck.discoveryYear}${wreck.id==='wreck-hindenburg'?' enligt vrakregistret':''}`]:[])];
 return `<div class="dating"><strong>${dates.join(' · ')}</strong>${wreck.uncertainty?`<p>${htmlEscape(wreck.uncertainty)}</p>`:''}<small>${htmlEscape(wreck.registryCode)} · Registerpunkt med varierande lägesnoggrannhet. Symbolen visar inte vrakets form, storlek eller riktning.</small></div>`;
}

$('#cityJourney').onchange=e=>{pause();if(e.target.checked)openCityGrid(Math.max(1860,year));else{setCityJourney(false);setTime(pos)}};
document.querySelectorAll('[data-city-stop]').forEach(b=>b.onclick=()=>{pause();goToYear(Number(b.dataset.cityStop))});

$('#cityGridYear').onchange=e=>{if(e.target.value)openCityGrid(Number(e.target.value));e.target.value=''};
$('#layerCityGrid').onchange=e=>{cityGrid.enabled=e.target.checked;if(selectedFeature?.recordType==='cityGrid')selectedFeature=null;updateUI();draw()};

$('#layerRoadHistory').onchange=e=>{historicalRoads.enabled=e.target.checked;if(selectedFeature?.recordType==='historicalRoad')selectedFeature=null;updateUI();draw()};
$('#roadYear').onchange=e=>{if(!e.target.value)return;const y=Number(e.target.value);pause();clearSearch();historicalRoads.enabled=true;$('#layerRoadHistory').checked=true;if(y===2026){explorer.flags.modern=true;$('#layerModern').checked=true}goToYear(y);if(y===1920||y===1942)focusMap(19.937, y===1920?60.0968:60.115,y===1920?28:10);else focusMap(20.02,60.22,1.6);e.target.value='';window.MapUI?.showMap()};
$('#roadsMariehamn').onclick=()=>{pause();clearSearch();focusMap(19.937,60.098,28);window.MapUI?.showMap()};
$('#routeChoice').innerHTML='<option value="">Välj en sjörutt…</option>'+Object.entries(TransportRoutes.groups).map(([group,label])=>`<optgroup label="${label}">${TransportRoutes.routes.filter(r=>r.group===group).map(r=>`<option value="${r.id}">${htmlEscape(r.name)} · ${htmlEscape(r.dateLabel)}</option>`).join('')}</optgroup>`).join('');
$('#routeChoice').onchange=e=>{if(e.target.value)openShipRoute(e.target.value);e.target.value=''};
$('#routeGroup').onchange=()=>{if(selectedFeature?.recordType==='shipRoute'&&$('#routeGroup').value!=='all'&&selectedFeature.group!==$('#routeGroup').value){selectedFeature=null;explorer.selected=null}updateUI();draw()};
$('#onlyRoute').onchange=()=>{updateUI();draw()};
$('#routeOverview').onclick=()=>{pause();clearSearch();selected=null;selectedFeature=null;$('#layerShipRoutes').checked=true;$('#routeGroup').value='all';goToYear(2026);focusMap(20.35,60.23,1.1);window.MapUI?.showMap()};
$('#layerShipRoutes').onchange=()=>{if(!$('#layerShipRoutes').checked&&selectedFeature?.recordType==='shipRoute'){selectedFeature=null;explorer.selected=null}updateUI();draw()};
window.openEarlyMapYear=()=>{pause();clearSearch();selected=null;chooseMapBackground('model',false);goToYear(1800);focusMap(20.02,60.23,2);window.MapUI?.showMap()};
window.openCityMap=(mode,y)=>{pause();clearSearch();selected=null;goToYear(y);chooseMapBackground(mode);$('.layers').open=true;window.MapUI?.showMap()};
window.openCityPlan=y=>window.openCityMap('1860',y);
$('#overlayOriginal').onclick=()=>window.openCityMapArchive(historicalOverlay.mode);
$('#overlayPlanYear').onclick=()=>window.openCityPlan(1860);
$('#overlayMuseumYear').onclick=()=>window.openCityMap('1920',1920);
$('#overlayToday').onclick=()=>window.openCityMap(historicalOverlay.mode,2026);

function wreckForStory(building,period){return building?(building.category==='wreck'?building:null):window.WRECKS.find(w=>w.id===period.wreckId)}

function fortressControls(){return '<div class="fortress-controls" aria-label="Jämför Bomarsund"><button data-fortress-year="1853">Före · 1853</button><button data-fortress-year="1854">Efter · 1854</button><button data-fortress-year="2026">Idag</button><button id="fortressClose">Zooma in huvudfästet</button></div><p class="layernote">Tolkad plan · fylld brun: byggnad · streckad gul: påbörjat bygge · grå: tidigare utbredning. Streckade områden anger bebyggelse eller begravningsplats. År 1854 visar läget efter förstörelsen. Äldre bebyggelseområden visas därefter med ”Visa även äldre spår och belägg”.</p>'}
function fitBomarsund(){
 if(!meta)return;const a=project(20.202,60.224),b=project(20.276,60.205);const z=Math.min((W-170)/((b[0]-a[0])*fit),(H-125)/((b[1]-a[1])*fit));focusMap(20.239,60.2145,Math.max(12,Math.min(80,z)));
}
function openBomarsund(y){pause();clearSearch();$('#layerFortress').checked=true;goToYear(y);fitBomarsund();selectBuilding('bomarsund',false);}
function storyHit(h,x,y){if(h.labelRect){const r=h.labelRect;return x>=r.x&&x<=r.x+r.w&&y>=r.y&&y<=r.y+r.h}return h.rings?.some(r=>BomarsundPlan.contains(r,x,y))||Math.hypot(x-h.x,y-h.y)<Math.max(22,h.size)}

function cityPlanControls(){return '<div class="fortress-controls"><button data-city-grid-year="1860">Utforska stadsplanens gatunät</button><button data-city-plan="original">Se originalplanen</button></div><p class="layernote">Streckade gator och kvarter är planerade, inte färdig bebyggelse.</p>'}
function focusCityPlan(){
 if(!meta)return;
 if(historicalOverlay.mode==='1920'){
  const map=HistoricalOverlay.museum,m=HistoricalOverlay.affine(map.anchors,project);
  const corners=[[0,0],[map.width,0],[map.width,map.height],[0,map.height]].map(([x,y])=>[m[0]*x+m[2]*y+m[4],m[1]*x+m[3]*y+m[5]]);
  const xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]),left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);
  zoom=Math.max(.65,Math.min(100,Math.min((W-80)/((right-left)*fit),(H-100)/((bottom-top)*fit))));
  panX=-((left+right)/2-meta.width/2)*fit*zoom;panY=-((top+bottom)/2-meta.height/2)*fit*zoom+20;draw();return;
 }
const a=project(19.923,60.103),b=project(19.949,60.092);
 focusMap(19.936,60.0975,Math.max(12,Math.min(100,Math.min((W-80)/((b[0]-a[0])*fit),(H-85)/((b[1]-a[1])*fit)))));
}

function cityMuseumControls(){return '<div class="fortress-controls"><button data-city-grid-year="1920">Utforska gator, kvarter och hus</button><button data-city-museum="original">Se museikartan och husens berättelser</button></div>'}

function earlyMapControls(){return '<div class="fortress-controls"><button data-early-map="original">Förstora kartan från cirka 1800</button><button data-early-map="compare">Jämför med 1894</button></div><p class="layernote">Daterad cirka 1800 · kartbilden finns i kartarkivet. Huvudkartans strandlinjer kommer från en separat modell.</p>'}

function updateRouteList(){
 const selectedRoute=selectedFeature?.recordType==='shipRoute'?selectedFeature.id:null;
 $('#onlyRoute').disabled=!selectedRoute;if(!selectedRoute)$('#onlyRoute').checked=false;
 const active=TransportRoutes.active(year,$('#layerShipRoutes').checked,$('#routeGroup').value,$('#onlyRoute').checked?selectedRoute:null);
 $('#routeStatus').textContent=!$('#layerShipRoutes').checked?'Fartygslagret är avstängt.':active.length?active.length+(active.length===1?' daterad rutt visas under valt år.':' daterade rutter visas under valt år.'):'Inga rutter i detta urval är belagda för valt år. Välj en rutt ovan för att besöka dess tid.';
 $('#activeRoutes').innerHTML=active.map(r=>`<button class="register-place" data-route="${r.id}">${htmlEscape(r.name)}<small>${htmlEscape(r.dateLabel)}</small></button>`).join('');
 $('#activeRoutes').querySelectorAll('[data-route]').forEach(b=>b.onclick=()=>openShipRoute(b.dataset.route));
}
function openShipRoute(id,focus=true){
 const route=TransportRoutes.routes.find(r=>r.id===id);if(!route)return;
 pause();clearSearch();$('#layerShipRoutes').checked=true;
 if($('#routeGroup').value!=='all')$('#routeGroup').value=route.group;
 if(!TransportRoutes.visible(route,year))goToYear(route.focusYear??route.from);
 selected=null;selectedFeature=route;explorer.selected=null;updateUI();
 if(focus&&meta){const pts=route.path.map(p=>project(...p)),xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]),left=Math.min(...xs),right=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);zoom=Math.max(.65,Math.min(100,Math.min((W-Math.min(240,W*.3))/((right-left)*fit),(H-Math.min(220,H*.45))/((bottom-top)*fit))));panX=-((left+right)/2-meta.width/2)*fit*zoom;panY=-((top+bottom)/2-meta.height/2)*fit*zoom}
 draw();window.MapUI?.showStory(true);
}

function bindCityGridButtons(){document.querySelectorAll('[data-city-grid-year]').forEach(el=>el.onclick=()=>openCityGrid(Number(el.dataset.cityGridYear)))}
function openCityGrid(targetYear){
 setCityJourney(true);
 pause();clearSearch();explorer.flags.historic=true;$('#layerHistoric').checked=true;cityGrid.enabled=true;$('#layerCityGrid').checked=true;historicalRoads.enabled=true;$('#layerRoadHistory').checked=true;explorer.flags.modern=true;$('#layerModern').checked=true;
 chooseMapBackground('model',false);goToYear(targetYear);
 if(meta){const a=project(19.922,60.103),b=project(19.951,60.090);zoom=Math.max(8,Math.min(70,(W-48)/((b[0]-a[0])*fit),(H-50)/((b[1]-a[1])*fit)));panX=-((a[0]+b[0])/2-meta.width/2)*fit*zoom;panY=-((a[1]+b[1])/2-meta.height/2)*fit*zoom;draw()}
 window.MapUI?.showMap();
}


// Event symbols stay the same size on screen; they are not building footprints.
function ofredenSymbol(type){
 const shapes={
  'ofred-congress':'<path d="M9 10H17L19 12H27V25H19L17 23H9Z M18 12V24"/>',
  'ofred-fleet':'<path d="M8 23H28L24 28H12Z M18 8V23 M18 10L26 20H18Z M8 31Q13 28 18 31T28 31"/>',
  'ofred-battle':'<path d="M8 22H26L22 27H12Z M17 8V22 M17 10L25 19H17Z M7 30Q12 28 17 30T28 30 M27 6V12 M24 9H30"/>',
  'ofred-skans':'<path d="M8 26V14H12V10H16V14H20V10H24V14H28V26 M8 26H28 M16 26V20H20V26"/>'
 };
 return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36"><circle cx="18" cy="18" r="17" fill="#faf7e8" stroke="#8b6954" stroke-dasharray="3 2"/><g fill="none" stroke="#72533f" stroke-width="1.5" stroke-linejoin="round">${shapes[type]||shapes['ofred-congress']}</g></svg>`;
}
function ofredenDetails(place){
 return `<p class="asidehint">${htmlEscape(place.precision)} Symbolen visar typen av plats, inte dess form eller storlek.</p>${(place.details||[]).map(d=>`<details><summary>${htmlEscape(d.title)}</summary><p>${htmlEscape(d.text)}</p></details>`).join('')}`;
}
function openOfreden(targetYear,selectPlace=false){setCityJourney(false);
 const event=window.OFREDEN.events.find(e=>e.y===targetYear);if(!event)return;
 pause();clearSearch();$('#layerOfreden').checked=true;explorer.flags.ofreden=true;explorer.listKey=null;
 chooseMapBackground('model',false);goToYear(targetYear);
 const place=window.OFREDEN.places.find(p=>p.id===event.ofredenPlace);
 if(place){focusMap(place.lon,place.lat,8);if(W<600){panY-=H*.25;draw()}if(selectPlace){selectBuilding(place.id,false);return}}
 else focusMap(20.12,60.19,1.4);
 window.MapUI?.showStory(true);
}

function cityPeriod(y){
 const stop=cityStops.filter(n=>n<=y).at(-1)??1860;
 const extra={1876:{title:'Hus vid stadens gator',text:'Gamla rådhuset är byggt. Vid gatorna finns allt fler hus och gårdar. Tryck på ett hus för att upptäcka dess historia.',more:'Gamla rådhuset dateras till 1876. Kartan visar bara de husplatser vi har daterade uppgifter om; den är inte en fullständig inventering.',src:'historicCity'},1900:{title:'Trähus och gårdar',text:'Fler hus har fått plats i staden. Bostäder, gårdshus och offentliga byggnader hör ihop med gatorna runt dem.',more:'Namngivna hus visas från sina källbelagda år. Ett streckat hus anger ett känt läge där den historiska konturen saknas.',src:'historicCity'},1957:{title:'Staden får nya hus',text:'På Badhusberget står det nuvarande vattentornet. I staden finns både äldre trähus och nyare byggnader.',more:'Det nuvarande vattentornet är från 1957. Tidigare och senare byggnadsfaser beskrivs när du trycker på ett namngivet hus.',src:'historicCity'}};
 const source=extra[stop]||eras.find(e=>e.y===stop)||eras.find(e=>e.y===1861);
 return {...source,y:stop,tag:'Mariehamn · '+date(y),q:source.q||'Vilka hus finns kvar när du går framåt i tiden?'};
}
function setCityJourney(enabled){
 cityJourney=enabled;$('#cityJourney').checked=enabled;$('#time').min=enabled?1860:0;$('#time').max=enabled?2026:MAX_TIME;$('#time').value=enabled?Math.max(1860,year):pos;
 document.querySelector('footer').classList.toggle('city-journey',enabled);$('#cityTimeTicks').hidden=!enabled;
}
function cityPlaybackFrame(now){
 const elapsed=Math.min(100,Math.max(0,now-lastTick));if(elapsed<32){timer=requestAnimationFrame(playbackFrame);return}lastTick=now;
 const stop=cityStops.find(y=>y>year)??2026,next=Math.min(2026,$('#autostop').checked?stop:2026,cityPlaybackYear+elapsed/500);
 if(shorelines.prepare(Math.floor(next))){cityPlaybackYear=next;if(Math.floor(next)!==year)goToYear(Math.floor(next));if(next>=2026||($('#autostop').checked&&next>=stop)){pause();return}}
 timer=requestAnimationFrame(playbackFrame);
}
