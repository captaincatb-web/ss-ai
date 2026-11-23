global.document={createElement:()=>({}),head:{appendChild(){}}};global.window={};require('./episodes.js');
const o={};for(const [k,v] of Object.entries(window.EPISODES))o[k]={intro:!!v.intro,segs:v.segs,groups:v.scenes.map(s=>s.segs)};
require('fs').writeFileSync('/tmp/mg_eps.json',JSON.stringify(o));console.log('eps',Object.keys(o).length);
