// ═══════════════════════════════════════════════
//  SHARED UTILITIES — included in every page
// ═══════════════════════════════════════════════

// ── AUTH / STATE ──────────────────────────────
function getUser(){
  try{ return JSON.parse(localStorage.getItem('cg_user')||'null'); }catch{ return null; }
}
function setUser(u){ localStorage.setItem('cg_user', JSON.stringify(u)); }
function clearUser(){ localStorage.removeItem('cg_user'); localStorage.removeItem('cg_state'); }
function getState(){
  try{ return JSON.parse(localStorage.getItem('cg_state')||'{}'); }catch{ return {}; }
}
function setState(patch){
  var s=getState(); Object.assign(s,patch);
  localStorage.setItem('cg_state',JSON.stringify(s));
}
function requireAuth(){
  if(!getUser()){ window.location.href='landing.html'; return false; }
  return true;
}

// ── WATCHED / RATINGS ─────────────────────────
function getSessWatched(){ return new Set((getState().sessWatched||[]).map(Number)); }
function addWatched(mid){
  var s=getState(); var w=s.sessWatched||[];
  if(w.indexOf(+mid)===-1) w.push(+mid);
  setState({sessWatched:w});
  apiMarkWatched(mid, getSessRatings()[+mid]||null);
}
function removeWatched(mid){
  var s=getState(); s.sessWatched=(s.sessWatched||[]).filter(function(m){return m!==+mid;});
  setState(s);
}
function getSessRatings(){ return getState().sessRatings||{}; }
function setRating(mid,r){ var sr=getSessRatings(); sr[+mid]=r; setState({sessRatings:sr}); }
function getSessReviews(){ return getState().sessReviews||{}; }
function addReview(mid,obj){
  var rv=getSessReviews(); if(!rv[+mid]) rv[+mid]=[];
  rv[+mid].unshift(obj); setState({sessReviews:rv});
}
function getSaved(){ return new Set((getState().sessSaved||[]).map(Number)); }
function toggleSaved(mid){
  var s=getState(); var sv=s.sessSaved||[]; var i=sv.indexOf(+mid);
  if(i===-1) sv.push(+mid); else sv.splice(i,1);
  setState({sessSaved:sv}); return i===-1;
}
function allW(){
  var u=getUser(); if(!u) return new Set();
  var base=(typeof DB!=='undefined'&&DB.userWatched)?(DB.userWatched[String(u.dbId||1)]||[]).map(Number):[];
  return new Set([...base,...getSessWatched()]);
}
function isW(mid){ return allW().has(+mid); }
function myR(mid){
  var sr=getSessRatings(); if(sr[+mid]) return sr[+mid];
  var u=getUser(); if(!u||typeof DB==='undefined') return 0;
  var ur=(DB.userRatings||{})[String(u.dbId||1)]||{};
  return ur[String(mid)]||0;
}
function minfo(mid){
  if(typeof DB==='undefined') return null;
  return DB.movies[mid]||DB.movies[String(mid)];
}

// ── HELPERS ───────────────────────────────────
var EMOJIS={Action:'💥',Adventure:'🗺️',Animation:'🎨',Comedy:'😄',Crime:'🕵️',
  Documentary:'📹',Drama:'🎭',Fantasy:'🧙',Horror:'👻',Musical:'🎵',
  Mystery:'🔍',Romance:'💕','Sci-Fi':'🚀',Thriller:'⚡',War:'⚔️',
  Western:'🤠',Children:'🧸',IMAX:'🎬','Film-Noir':'🎩'};
function emo(g){ if(!g)return'🎬'; for(var k in EMOJIS)if(g.indexOf(k)!==-1)return EMOJIS[k]; return'🎬'; }
function gcls(g){ if(!g)return'gdf'; var p=g.split('|')[0].replace(/[^a-zA-Z-]/g,''); return'g'+p; }
function cleanT(t){ return t.replace(/^(.+),\s(The|A|An)\s(\(\d{4}\))$/,'$2 $1 $3').replace(/\s\(\d{4}\)$/,''); }
function getYear(t){ var m=t.match(/\((\d{4})\)/); return m?m[1]:'—'; }
function starsStr(r){ var n=Math.round((r||0)*2)/2,s=''; for(var i=1;i<=5;i++)s+=i<=n?'★':'☆'; return s; }

// ── CARD FACTORY ──────────────────────────────
function makeCard(movieId, score, reason, delay){
  delay=delay||0;
  var info=minfo(movieId); if(!info){var d=document.createElement('div');return d;}
  var title=info[0],genres=info[1],avgR=info[2],rCnt=info[3];
  var clean=cleanT(title),gClass=gcls(genres),em=emo(genres);
  var gtags=(genres||'').split('|').slice(0,2).map(function(g){return'<span class="gtag">'+g+'</span>';}).join('');
  var watched2=isW(movieId);
  var div=document.createElement('div');
  div.className='mc'; div.style.animationDelay=(delay*38)+'ms';
  div.innerHTML=
    '<div class="mc-poster '+gClass+'"><div class="mc-pbg"></div><span class="mc-em">'+em+'</span>'+
    (score?'<div class="mc-score">↑'+score+'</div>':'')+
    (watched2?'<div class="mc-seen">✓ Seen</div>':'')+
    '</div><div class="mc-body"><div class="mc-title">'+clean+'</div>'+
    '<div class="mc-meta">'+(avgR>0?'<span class="mc-stars">'+starsStr(avgR)+'</span><span class="mc-rtxt">'+avgR+'</span>':'')+
    '</div><div class="mc-tags">'+gtags+(rCnt>0?'<span class="gtag">'+rCnt+' ratings</span>':'')+
    '</div>'+(reason?'<div class="mc-reason">'+reason+'</div>':'')+
    '</div>';
  div.addEventListener('click',function(){window.location.href='movie.html?id='+movieId;});
  return div;
}

// ── NAV ───────────────────────────────────────
function buildNav(active){
  var u=getUser();
  var el=document.getElementById('nav-root');
  if(!el) return;
  el.innerHTML=
    '<a class="logo" href="'+(u?'index.html':'landing.html')+'">Cine<span>Graph</span></a>'+
    (u?
      '<a class="nl'+(active==='home'?' on':'')+'" href="index.html">Discover</a>'+
      '<a class="nl'+(active==='search'?' on':'')+'" href="search.html">Search</a>'+
      '<a class="nl'+(active==='watched'?' on':'')+'" href="watched.html">Watched</a>'+
      '<a class="nl'+(active==='graph'?' on':'')+'" href="graph.html">Graph</a>'+
      '<a class="nl'+(active==='profile'?' on':'')+'" href="profile.html">Profile</a>'+
      '<div class="user-chip" onclick="doLogout()"><div class="dot"></div><span>'+u.name+'</span></div>'
    :
      '<a class="nl" href="landing.html#login">Log in</a>'+
      '<a class="nl cta-nav" href="landing.html#signup">Sign up</a>'
    );
}
function doLogout(){ clearUser(); window.location.href='landing.html'; }

// ── TOAST ─────────────────────────────────────
var _tt;
function toast(msg,type){
  var el=document.getElementById('toast'); if(!el)return;
  el.textContent=msg; el.className='toast show '+(type||'');
  clearTimeout(_tt); _tt=setTimeout(function(){el.classList.remove('show');},2400);
}

// ── BACKEND BRIDGE ────────────────────────────
var API='http://localhost:8000';
function apiMarkWatched(mid,rating){
  var u=getUser(); if(!u) return;
  var dbId=u.dbId||1;
  fetch(API+'/users/'+dbId+'/watched',{
    method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({movie_id:+mid,rating:rating||null})
  }).catch(function(){});
}
function apiGetRecs(cb){
  var u=getUser(); if(!u){cb(null);return;}
  fetch(API+'/users/'+(u.dbId||1)+'/recommendations')
    .then(function(r){return r.json();}).then(cb).catch(function(){cb(null);});
}

// ── INPUT VALIDATION ──────────────────────────
function validateEmail(e){ return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e); }
function validatePassword(p){ return p && p.length>=6; }
function validateName(n){ return n && n.trim().length>=2; }
function showFieldError(id, msg){
  var el=document.getElementById(id); if(!el)return;
  el.style.borderColor='var(--red)';
  var err=el.parentElement.querySelector('.field-err');
  if(!err){err=document.createElement('div');err.className='field-err';el.parentElement.appendChild(err);}
  err.textContent=msg;
}
function clearFieldError(id){
  var el=document.getElementById(id); if(!el)return;
  el.style.borderColor='';
  var err=el.parentElement.querySelector('.field-err'); if(err)err.textContent='';
}
