# Publicering av Saltvik-piloten

Publicerad 2026-11-10 på https://xn--land-poa.erikedin.com efter användarens uttryckliga publiceringsbesked. Version `42001622-199e-4ed8-9ca1-b19f6c0ff891` betjänar 100 % av trafiken. Föregående version: `1baae6c6-0228-4794-bd63-263d99ad7f50`.

En isolerad kopia av den föregående produktionsversionen användes. Endast pilotens 13 redan befintliga objekt ersattes med deras kompilerade granskningsresultat och 52 observationspunkter lades till. Alla 13 får konservativ visningsstart 1968, inte fastställt byggår. Befintliga geometrier och övriga katalogposter bevarades. 164 andra lokala objekt och övriga lokala katalogändringar ingår inte i publiceringen. Worker-koden behölls. Sju publika filer ändrades; alla 276 publika filer har hämtats över HTTPS och checksummejämförts både före och efter publiceringen.

143 riktade JavaScript-tester och Wrangler dry-run passerade. Den ursprungliga granskningsrapportens befintliga Python-/kartvalideringsfel kvarstår dokumenterade och har inte kringgåtts genom källändringar. Visuell webbläsarkontroll var inte tillgänglig eftersom lokal webbläsaranvändning är avstängd i Work-inställningarna. Kontroll mot livekatalogen bekräftar samtliga 13 dateringar.

Se [kvitto](receipt.json), [avgränsning](release-scope.json), [livekontroll](live-verification.log), [testutdata](javascript-tests.log) och [publiceringslogg](deploy.log). Granskningsbatchens tidigare `not-published` beskriver granskningsögonblicket; detta separata kvitto dokumenterar den efterföljande publiceringen. Ingen push eller sammanslagning har gjorts. Inga fler kartblad har granskats.
