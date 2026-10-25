(()=>{'use strict';
const $=s=>document.querySelector(s),pages=[...document.querySelectorAll('.page')],key='solomon-reader:'+location.pathname;
let state={};try{state=JSON.parse(localStorage.getItem(key)||'{}')||{}}catch{}
let index=0,restoring=false,timer;
const persist=()=>{try{localStorage.setItem(key,JSON.stringify(state))}catch{}};
const apply=()=>{document.body.classList.toggle('dark',state.dark===true);document.documentElement.style.setProperty('--size',Math.max(16,Math.min(30,Number(state.size)||21))+'px')};
function close(){ $('#contents').hidden=true;$('#contents-button').setAttribute('aria-expanded','false') }
function show(n,y=0){clearTimeout(timer);if(index===2){state.section='essay';state.y=scrollY;persist()}index=Math.max(0,Math.min(pages.length-1,n));restoring=true;pages.forEach((p,i)=>p.hidden=i!==index);$('#previous').disabled=index===0;$('#next').disabled=index===pages.length-1;$('#page-count').textContent=pages[index].dataset.label;history.replaceState(null,'','#'+pages[index].id);close();$('#reading').focus({preventScroll:true});requestAnimationFrame(()=>{window.scrollTo(0,y);requestAnimationFrame(()=>{restoring=false})});}
function addLink(label,id,index){const a=document.createElement('a');a.href='#'+id;a.textContent=label;a.onclick=e=>{e.preventDefault();show(index);if(id!==pages[index].id){history.replaceState(null,'','#'+id);requestAnimationFrame(()=>requestAnimationFrame(()=>document.getElementById(id).scrollIntoView()))}};$('#contents').append(a)}
pages.forEach((p,i)=>{addLink(p.dataset.label,p.id,i);if(p.id==='essay')p.querySelectorAll('h2,h3').forEach(h=>addLink(h.textContent,h.id,i));const cover=p.querySelector('.cover');if(cover)cover.style.backgroundImage='url("cover.webp")'});
$('#previous').onclick=()=>show(index-1);$('#next').onclick=()=>show(index+1);
$('#contents-button').onclick=()=>{const open=$('#contents').hidden;$('#contents').hidden=!open;$('#contents-button').setAttribute('aria-expanded',String(open));if(open)$('#contents a').focus()};
$('#smaller').onclick=()=>{state.size=Math.max(16,(Number(state.size)||21)-1);apply();persist()};$('#larger').onclick=()=>{state.size=Math.min(30,(Number(state.size)||21)+1);apply();persist()};$('#theme').onclick=()=>{state.dark=!state.dark;apply();persist()};
$('#share').onclick=async()=>{const url=document.querySelector('[rel=canonical]').href;try{if(navigator.share)await navigator.share({title:document.title,url});else{await navigator.clipboard.writeText(url);$('#status').textContent='Link copied'}}catch(e){if(e.name!=='AbortError')$('#status').textContent='Copy the address from your browser to share.'}};
if(state.section==='essay'){$('#resume').hidden=false;$('#resume').onclick=()=>show(2,Number(state.y)||0)}
window.addEventListener('scroll',()=>{if(restoring||index!==2)return;clearTimeout(timer);timer=setTimeout(()=>{state.section='essay';state.y=scrollY;persist()},150)},{passive:true});
window.addEventListener('keydown',e=>{if(e.key==='Escape'){close();$('#contents-button').focus()}});
function fromHash(){const id=location.hash.slice(1),target=document.getElementById(id);const n=pages.findIndex(p=>p===target||p.contains(target));show(n>=0?n:0);if(target&&target!==pages[n])requestAnimationFrame(()=>{history.replaceState(null,'','#'+id);target.scrollIntoView()})}
window.addEventListener('hashchange',fromHash);apply();fromHash();
})();
