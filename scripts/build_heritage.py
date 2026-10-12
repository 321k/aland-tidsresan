import json
from pathlib import Path
r=json.loads(Path('data/heritage-joined.json').read_text());curated=json.loads(Path('data/curated-places.json').read_text())['places'];by_code={p['registryId']:p for p in curated if p['category']=='archaeology'}
features=[];seen=set()
for f in r['features']:
 if f['id'] in seen:continue
 seen.add(f['id'])
 p=by_code.get(f['id']);periods=[dict(label=d['periodLabel'],from_=d['minYear'],to=d['maxYear']) for d in f['dating']]
 periods=[{'from':d.pop('from_'),**d} for d in periods]
 features.append(dict(id='registry:'+f['id'],code=f['id'],name=p['name'] if p else f['name'],lon=f['coordinates'][0],lat=f['coordinates'][1],description=f['description'],childText=p['description'] if p else None,datingNote=p['datingNote'] if p else 'Datering inom en bred period; inte ett exakt startår. Äldre platser visas också som historiska spår.',earliestYear=p['fromYear'] if p else None,dateLabel=p['dateLabel'] if p else None,village=f['village'],municipality=f['municipality'],status=f['status'],sourceUrl=f['sourceUrl'],periods=periods,periodLabels=f['periodLabels'],topography=f['topography'],wiki=p['wikipedia'] if p else None))
Path('dist/assets/heritage.json').write_text(json.dumps({'attribution':r['attribution'],'license':'CC BY 4.0','source':r['source'],'features':features},ensure_ascii=False,separators=(',',':')))
places=[]
for p in curated:
 if p['category']=='archaeology':continue
 places.append(dict(id=p['id'],name=p['name'],loc=p['registryId']+' · sjöfart',lat=p['lat'],lon=p['lon'],start=p['fromYear'],type='pilot',category='marine',text=p['description'],more=p['dateLabel']+'. '+p['datingNote']+' Platsmarkören anger ett registerområde, inte byggnadens uppmätta läge.',dateLabel=p['dateLabel'],q='Hur tror du att en lots lärde sig var grunden finns?',src='heritage',sourceUrl=p['sources'][0]['url'],wiki=p['wikipedia']))
Path('dist/places-data.js').write_text('window.EXTRA_PLACES='+json.dumps(places,ensure_ascii=False,separators=(',',':'))+';\n')
Path('data/heritage-provenance.json').write_text(json.dumps({k:v for k,v in r.items() if k!='features'},ensure_ascii=False,indent=2))
print(len(features),'registry places;',len(places),'maritime places')
