let book,currentIndex=0,contentPackage=null,packagePromise=null;
const $=s=>document.querySelector(s);
const stateKey='solomon-reader:fingerprint-of-reality';
const packageParts=8;
function save(extra={}){if(!book)return;const prev=JSON.parse(localStorage.getItem(stateKey)||'{}');localStorage.setItem(stateKey,JSON.stringify({...prev,section:book.sections[currentIndex].id,scrollY:window.scrollY,...extra}));}
function loadState(){return JSON.parse(localStorage.getItem(stateKey)||'{}')}
function buildToc(){const nav=$('#tocList');nav.innerHTML='';book.sections.filter(s=>s.toc).forEach(s=>{const a=document.createElement('a');a.href='#'+s.id;a.textContent=s.label;a.dataset.id=s.id;a.onclick=e=>{e.preventDefault();goToId(s.id);closeToc()};nav.appendChild(a)})}
async function loadContentPackage(){
  if(contentPackage)return contentPackage;
  if(packagePromise)return packagePromise;
  packagePromise=(async()=>{
    const parts=await Promise.all(Array.from({length:packageParts},(_,i)=>fetch(`content.gz.b64.${i}`,{cache:'force-cache'}).then(r=>{if(!r.ok)throw new Error(`package part ${i} missing`);return r.text()})));
    const b64=parts.join('').replace(/\s+/g,'');
    const binary=atob(b64);
    const bytes=new Uint8Array(binary.length);
    for(let i=0;i<binary.length;i++)bytes[i]=binary.charCodeAt(i);
    if(!('DecompressionStream' in window))throw new Error('This browser does not support the required reader decompression feature.');
    const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));
    const text=await new Response(stream).text();
    contentPackage=JSON.parse(text);
    return contentPackage;
  })();
  return packagePromise;
}
async function getSectionHtml(s){
  if(s.special==='front-cover')return `<div class="cover-page"><img src="${book.cover}" alt="Front cover of ${escapeHtml(book.title)} by ${escapeHtml(book.author)}"></div>`;
  if(s.special==='back-cover')return `<div class="cover-page"><img src="${book.backCover}" alt="Back cover of ${escapeHtml(book.title)} by ${escapeHtml(book.author)}"></div>`;
  try{const direct=await fetch(s.file,{cache:'no-store'});if(direct.ok)return await direct.text()}catch(e){}
  const pkg=await loadContentPackage();
  const key=s.file.split('/').pop();
  if(pkg&&typeof pkg[key]==='string')return pkg[key];
  throw new Error(`Section ${key} not found in publication package.`);
}
function setSectionUrl(id){history.replaceState(null,'',`${location.pathname}${location.search}#${id}`)}
function scrollToSectionStart(){
  document.documentElement.scrollTop=0;
  document.body.scrollTop=0;
  window.scrollTo({top:0,left:0,behavior:'auto'});
}
async function loadSection(i,restoreScroll=false){
  currentIndex=Math.max(0,Math.min(i,book.sections.length-1));
  const s=book.sections[currentIndex];
  setSectionUrl(s.id);
  $('#content').setAttribute('aria-busy','true');
  $('#content').innerHTML=`<div class="placeholder"><h1>${escapeHtml(s.label)}</h1><p class="no-indent">Loading…</p></div>`;
  if(!restoreScroll)scrollToSectionStart();
  let html='';
  try{html=await getSectionHtml(s)}catch(e){html=`<div class="placeholder"><h1>${escapeHtml(s.label)}</h1><p class="no-indent">This section could not be loaded. Please return to Solomon Christian Publishing and try again.</p></div>`;console.error(e)}
  $('#content').innerHTML=html;
  $('#content').removeAttribute('aria-busy');
  $('#content').focus({preventScroll:true});
  $('#prevBtn').disabled=currentIndex===0;
  $('#nextBtn').disabled=currentIndex===book.sections.length-1;
  document.querySelectorAll('.toc a').forEach(a=>a.classList.toggle('active',a.dataset.id===s.id));
  if(restoreScroll){
    const st=loadState();
    requestAnimationFrame(()=>window.scrollTo({top:st.scrollY||0,left:0,behavior:'auto'}));
  }else{
    save({scrollY:0});
    requestAnimationFrame(()=>{scrollToSectionStart();requestAnimationFrame(scrollToSectionStart)});
  }
  updateProgress();
}
function escapeHtml(v){return String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function goToId(id){const i=book.sections.findIndex(s=>s.id===id);if(i>=0)loadSection(i)}
function updateProgress(){if(!book)return;const max=document.documentElement.scrollHeight-innerHeight;const within=max>0?scrollY/max:0;const overall=(currentIndex+within)/book.sections.length;$('#progressBar').style.width=(overall*100)+'%'}
function openToc(){$('#toc').classList.add('open');$('#scrim').classList.add('open');$('#toc').setAttribute('aria-hidden','false')}
function closeToc(){$('#toc').classList.remove('open');$('#scrim').classList.remove('open');$('#toc').setAttribute('aria-hidden','true')}
function changeFont(delta){const st=loadState();let n=st.fontSize||parseInt(getComputedStyle(document.documentElement).getPropertyValue('--size'))||20;n=Math.min(26,Math.max(16,n+delta));document.documentElement.style.setProperty('--size',n+'px');save({fontSize:n})}
(async()=>{
  try{
    book=await fetch('book.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error('book manifest unavailable');return r.json()});
    $('#bookTitle').textContent=book.title;
    buildToc();
    const st=loadState();
    if(st.theme==='dark')document.body.classList.add('dark');
    if(st.fontSize)document.documentElement.style.setProperty('--size',st.fontSize+'px');
    const hash=location.hash.slice(1);
    const hasReadingHistory=Boolean(st.section);
    const id=hash||st.section||(hasReadingHistory?'prologue':'front-cover');
    const i=book.sections.findIndex(s=>s.id===id);
    await loadSection(i>=0?i:0,!hash&&hasReadingHistory);
    $('#tocBtn').onclick=openToc;$('#tocClose').onclick=closeToc;$('#scrim').onclick=closeToc;
    $('#prevBtn').onclick=()=>loadSection(currentIndex-1);$('#nextBtn').onclick=()=>loadSection(currentIndex+1);
    $('#themeBtn').onclick=()=>{document.body.classList.toggle('dark');save({theme:document.body.classList.contains('dark')?'dark':'light'})};
    $('#fontUp').onclick=()=>changeFont(1);$('#fontDown').onclick=()=>changeFont(-1);
    $('#search').oninput=e=>{const q=e.target.value.toLowerCase();document.querySelectorAll('.toc a').forEach(a=>a.style.display=a.textContent.toLowerCase().includes(q)?'block':'none')};
    window.addEventListener('scroll',()=>{updateProgress();save()},{passive:true});
    window.addEventListener('keydown',e=>{if(e.key==='Escape')closeToc()});
  }catch(e){$('#content').innerHTML='<div class="placeholder"><h1>Reader unavailable</h1><p class="no-indent">The book reader could not initialize. Please refresh the page.</p></div>';console.error(e)}
})();
