global.document={createElement:()=>({}),head:{appendChild(){}}};global.window={};require('./episodes.js');
const o={};for(const [k,v] of Object.entries(window.EPISODES))o[k]={intro:!!v.intro,voice:v.voice||null,caps:v.caps||[],tag:v.tag||''};
require('fs').writeFileSync('/tmp/eps.json',JSON.stringify(o));console.log(Object.keys(o).length);
