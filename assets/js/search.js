const root=document.querySelector('[data-note-search]');
if(root){
  const form=root.querySelector('form'),input=form.elements.q,type=form.elements.type,tag=form.elements.tag,year=form.elements.year,month=form.elements.month;
  const status=root.querySelector('.search-status'),results=root.querySelector('.search-results');
  const base=root.dataset.base,lang=document.documentElement.lang;
  type.value=root.dataset.defaultType;
  const tagLabels=JSON.parse(root.querySelector('[data-note-tag-labels]').textContent);
  let apiPromise,sequence=0,timer,availableMonths=[];
  const placeholders=new Map([tag,year,month].map(select=>[select,select.options[0].text]));
  function populate(select,entries){
    const previous=select.value;
    select.replaceChildren(new Option(placeholders.get(select),''));
    for(const [value,label] of entries)select.add(new Option(label,value));
    select.value=entries.some(([value])=>value===previous)?previous:'';
  }
  function updateMonths(){
    const formatter=new Intl.DateTimeFormat(lang,{year:'numeric',month:'short'});
    populate(month,availableMonths.filter(value=>!year.value||value.startsWith(year.value+'-')).map(value=>{
      const [y,m]=value.split('-').map(Number);
      return [value,formatter.format(new Date(y,m-1,1))];
    }));
  }
  async function api(){
    if(!apiPromise)apiPromise=(async()=>{
      const response=await fetch(`${base}pagefind/status.json`,{cache:'no-store'});
      if(!response.ok)throw new Error('Search manifest unavailable');
      const manifest=await response.json();
      if(!manifest.languages?.[lang])return null;
      const pf=await import(`${base}pagefind/pagefind.js`);
      await pf.options({baseUrl:base});
      const filters=await pf.filters();
      populate(tag,Object.entries(tagLabels).filter(([id])=>id in (filters.tag||{})));
      populate(year,Object.keys(filters.year||{}).filter(value=>/^\d{4}$/.test(value)).sort().reverse().map(value=>[value,value]));
      availableMonths=Object.keys(filters.month||{}).filter(value=>/^\d{4}-(0[1-9]|1[0-2])$/.test(value)).sort().reverse();
      updateMonths();
      return pf;
    })().catch(error=>{apiPromise=undefined;throw error;});
    return apiPromise;
  }
  function snippet(value){
    const parsed=new DOMParser().parseFromString(value,'text/html');const fragment=document.createDocumentFragment();
    function append(node,parent){
      if(node.nodeType===Node.TEXT_NODE){parent.append(document.createTextNode(node.textContent));return;}
      if(node.nodeType!==Node.ELEMENT_NODE)return;
      const next=node.tagName==='MARK'?document.createElement('mark'):parent;
      for(const child of node.childNodes)append(child,next);
      if(next!==parent)parent.append(next);
    }
    for(const node of parsed.body.childNodes)append(node,fragment);
    return fragment;
  }
  async function findItems(pf,query,filters){
    const response=await pf.search(query||null,{filters});
    let items=await Promise.all(response.results.map(r=>r.data()));
    // Browser ICU and the index's Chinese dictionary can split technical words
    // differently, including partial result sets. For Han-text queries check the same filtered,
    // language-specific public index; never fetch unpublished source content.
    if(lang.startsWith('zh') && /^[\p{Script=Han}\s]{2,}$/u.test(query)){
      const candidates=await pf.search(null,{filters});
      const terms=query.trim().split(/\s+/);
      const escape=value=>{const span=document.createElement('span');span.textContent=value;return span.innerHTML;};
      const literal=(await Promise.all(candidates.results.map(r=>r.data()))).flatMap(item=>{
        const text=(item.content||'').replace(/\u200b/g,'');
        if(!terms.every(term=>text.includes(term)))return [];
        const at=text.indexOf(terms[0]),start=Math.max(0,at-45),end=at+terms[0].length;
        return [{...item,excerpt:(start?'…':'')+escape(text.slice(start,at))+'<mark>'+escape(terms[0])+'</mark>'+escape(text.slice(end,end+100))+(end+100<text.length?'…':'')}];
      });
      const present=new Set(items.map(item=>item.url));
      items.push(...literal.filter(item=>!present.has(item.url)));
    }
    return items;
  }
  function updateFilterCount(){
    const count=[tag,year,month].filter(select=>select.value).length+(type.value!==root.dataset.defaultType?1:0);
    const badge=root.querySelector('[data-active-filters]');
    if(badge){badge.hidden=count===0;badge.textContent=`${count} ${root.dataset.activeLabel}`;}
  }
  async function search(){
    updateFilterCount();
    const token=++sequence;results.replaceChildren();status.textContent=root.dataset.loading;
    try{
      const pf=await api();if(token!==sequence)return;
      if(!pf){status.textContent=root.dataset.empty;return;}
      const filters={};if(type.value)filters.type=type.value;if(tag.value)filters.tag=tag.value;if(year.value)filters.year=year.value;if(month.value)filters.month=month.value;
      const items=await findItems(pf,input.value.trim(),filters);if(token!==sequence)return;
      status.textContent=items.length?`${items.length} ${root.dataset.count}`:root.dataset.noResults;
      for(const item of items){
        const address=new URL(item.url,location.origin);if(address.origin!==location.origin)continue;
        const li=document.createElement('li'),heading=document.createElement('h3'),a=document.createElement('a'),p=document.createElement('p');
        a.href=address.pathname+address.search+address.hash;a.textContent=item.meta.title||item.url;heading.append(a);
        p.append(snippet(item.excerpt||''));li.append(heading,p);results.append(li);
      }
    }catch(error){if(token===sequence)status.textContent=root.dataset.error;}
  }
  form.addEventListener('submit',e=>{e.preventDefault();search();});
  input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(search,180);});
  type.addEventListener('change',search);tag.addEventListener('change',search);
  year.addEventListener('change',()=>{updateMonths();search();});
  month.addEventListener('change',search);
  root.querySelector('[data-search-clear]').addEventListener('click',()=>{input.value='';type.value=root.dataset.defaultType;tag.value='';year.value='';updateMonths();month.value='';clearTimeout(timer);search();input.focus();});
  // Load filter values without presenting duplicate archive entries on initial visit.
  api().then(pf=>{if(!pf && !root.dataset.defaultType)status.textContent=root.dataset.empty;}).catch(()=>{status.textContent=root.dataset.error;});
}
