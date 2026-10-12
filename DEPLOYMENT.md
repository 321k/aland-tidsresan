# Publicering på Cloudflare

Kartan publiceras offentligt på https://åland.erikedin.com/ med Cloudflare Workers Static Assets.
Domänens DNS-form är `xn--land-poa.erikedin.com`.

`wrangler.jsonc` anger Cloudflare-kontot, domänen och `dist/` som publiceringskatalog.
Ingen serverkod eller byggprocess behövs. Endast filerna i `dist/` publiceras.

Kör från projektkatalogen med en behörig Cloudflare-inloggning:

```sh
python3 scripts/cache_versions.py
node --test tests/*.test.cjs
npx --yes wrangler@4.149.0 deploy --dry-run
npx --yes wrangler@4.149.0 deploy
```

Kontrollera efter publicering att startsidan och komprimerade kartfiler laddas över HTTPS,
att nutidskusten visas och att äldre fynd döljs i nutidsvyn.

Publicering sker med Wrangler från denna katalog. Automatisk publicering från GitHub
är ännu inte konfigurerad. Den tidigare Sites-adressen är en separat, äldre publicering;
`.openai/hosting.json` finns kvar som referens och styr inte Cloudflare-publiceringen.
