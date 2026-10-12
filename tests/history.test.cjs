const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const box={};vm.createContext(box);vm.runInContext(fs.readFileSync('dist/timeline-model.js','utf8')+';this.time=EvidenceTime',box);vm.runInContext(fs.readFileSync('dist/map-coordinates.js','utf8')+';this.grid=mariehamnGrid',box);
const time=box.time,heritage=JSON.parse(fs.readFileSync('dist/assets/heritage.json')).features,buildings=JSON.parse(fs.readFileSync('dist/assets/historic-buildings.json')).features.map(f=>({...f,recordType:'building'}));
test('a relocation does not place a building at its current address before arrival',()=>{
 const f=buildings.find(f=>f.id==='mh-history:strandnasgard');assert.equal(time.state(f,1760),'future');assert.equal(time.state(f,1899),'future');assert.equal(time.state(f,1900),'attested');
 const ass=buildings.find(f=>f.id==='mh-history:ass');assert.equal(time.state(ass,1896),'future');assert.equal(time.state(ass,1922),'attested');
});
test('demolition leaves a site marker without extending the physical building lifetime',()=>{
 const f=buildings.find(f=>f.id==='mh-history:tvargrand2');assert.equal(time.state(f,2003),'attested');assert.equal(time.state(f,2005),'trace');assert.equal(time.state(f,2026),'trace');
});
test('period boundaries and conflicting building dates never become exact evidence',()=>{
 assert.equal(time.state({periods:[{from:-5500,to:-1500}]},-5500),'possible');assert.equal(time.state({periods:[{from:-5500,to:-1500}]},2026),'trace');assert.equal(time.state({periods:[]},2026),'undated');
 assert.equal(time.state(buildings.find(f=>f.id==='mh-history:tullpackhuset'),1896),'possible');
});
test('a monument dates to its erection, not the event it commemorates',()=>{
 const f=heritage.find(f=>f.code==='Ku 3.6');assert.equal(time.state(f,1808),'future');assert.equal(time.state(f,1919),'future');assert.equal(time.state(f,1920),'attested');
});
test('prehistoric evidence does not imply uninterrupted occupation',()=>{
 const f=heritage.find(f=>f.code==='Sa 2.21');assert.equal(time.state(f,-5000),'possible');assert.equal(time.state(f,2026),'trace');
 const phased=heritage.find(f=>f.code==='Sa 20.7');assert.equal(time.state(phased,-3500),'possible');assert.equal(time.state(phased,-3200),'trace');assert.equal(time.state(phased,-3000),'possible');
});
test('every shoreline model year resolves to a real geometry asset; nearest model is explicit',()=>{
 const manifest=JSON.parse(fs.readFileSync('dist/assets/shorelines/manifest.json'));
 assert.ok(manifest.years.length>=68);assert.equal(time.modelYear(2026,manifest.years),1900);assert.equal(time.modelYear(-4100,manifest.years),-4000);
 for(const year of manifest.years){const data=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(`dist/assets/shorelines/${year}.json.gz`)));assert.equal(data.year,year);assert.ok(Array.isArray(data.classes.land));assert.ok(Array.isArray(data.classes.noData));}
});
test('archive map centre uses the official Finnish grid, within 1 metre of independent pyproj controls',()=>{
 for(const [lon,lat,n,e]of [[19.941,60.103,6665549.83998,20496718.03923],[19.9268313,60.0958139,6664749.99642,20495928.99855],[19.86,59.98,6651852.84582,20492183.28895],[20.12,60.15,6670790.90770,20506665.66258]]){const result=box.grid(lon,lat);assert.ok(Math.abs(result[0]-n)<1);assert.ok(Math.abs(result[1]-e)<1);}
});
test('historical building records have usable attribution and preserve official multi-area boundaries',()=>{
 assert.equal(buildings.length,28);assert.equal(new Set(buildings.map(f=>f.id)).size,28);for(const f of buildings){assert.ok(f.sources.length);assert.ok(f.sources.every(s=>s.url.startsWith('https://')));assert.ok(f.precision);assert.ok(f.phases.length);}
 const polygons=JSON.parse(fs.readFileSync('dist/assets/heritage-boundaries.geojson')).features;assert.equal(polygons.length,1870);assert.ok(new Set(polygons.map(f=>f.properties.code)).size<polygons.length);
});
