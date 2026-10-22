const el=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const source=seconds=>seconds?.length?`<a href="https://www.youtube.com/watch?v=o3mkGBcPkrI&t=${seconds[0]}s" target="_blank" rel="noreferrer">视频 ${Math.floor(seconds[0]/60)}:${String(seconds[0]%60).padStart(2,'0')} ↗</a>`:'';
const article=a=>`<div class="verse"><span class="number">${a.number}</span>${a.sentence?` · ${esc(a.sentence)}`:' · 条文待补'}${a.range_adjustment?`<small>（原数${a.arithmetic_number}，范围调整${a.range_adjustment}）</small>`:''}</div>`;
const statuses={requires_basis_number:'选一个基数，继续往下算。',requires_benming_gua_number:'请先选择演算基数。',requires_middle_five_rule:'此分支遇后天中五，寄卦规则待补。',unresolved_pair_boundary:'此基数的配卦边界待补。',four_stem_fallback:'遇5或10，改用四柱天干取数。'};
for(const id of ['father-animal','mother-animal'])for(const animal of '鼠牛虎兔龙蛇马羊猴鸡狗猪'){const option=document.createElement('option');option.value=animal;option.textContent=animal;el(id).append(option);}
function mode(){el('date-inputs').hidden=el('input-mode').value!=='date';el('pillar-inputs').hidden=el('input-mode').value!=='pillars';}
el('input-mode').onchange=mode;
el('video-example').onclick=()=>{
  el('input-mode').value='pillars';mode();
  for(const [key,value] of Object.entries({year:'乙巳',month:'辛巳',day:'甲申',time:'丙子'}))el(key).value=value;
  el('father-animal').value='鼠';el('mother-animal').value='牛';
  el('basis-number').value=9003;el('fortune-pillar').value='壬午';
  el('video-form').requestSubmit();
};
function branch(title,r){
  if(!r)return'';
  const steps=(r.pillar_steps||[]).map(p=>`<p>${esc(p.pillar)}：${p.values.join('＋')}＝${p.sum}；除8余${p.remainder_mod8}，取${p.trigram_number}。</p>`).join('');
  return `<h4>${title}</h4>${statuses[r.status]?`<p>${statuses[r.status]}</p>`:''}${r.pair_sums?`<p>${r.input_number} → 两组相加 ${r.pair_sums.join('、')}${r.upper?` → ${r.upper}上、${r.lower}下`:''}</p>`:''}${r.line_values_top_down?`<p>${r.line_values_top_down.join('＋')}＝${r.line_sum}</p>`:''}${steps}${r.combination!==undefined?`<p class="math">${r.combination} ＋ ${r.benming_gua_number??'待定'} ＝ ${r.base??'待定'}</p>`:''}${r.number!==undefined&&r.number!==null?`<p class="math">所得数：${r.number}</p>`:''}${r.articles?.map(article).join('')||''}${r.article?article(r.article):''}${r.rule_basis?`<details><summary>取数依据</summary><p class="muted">${esc(r.rule_basis)}</p></details>`:''}${r.status==='untransformed_branch_only'?'<p class="muted">按视频未合化分支演算。</p>':''}${source(r.source_seconds)}`;
}
function render(r){
  const k=r.preliminary;
  el('video-summary').innerHTML=`<p>${['year','month','day','time'].map(key=>esc(r.bazi[key])).join('　')}</p><p>太玄合计 <strong>${k.sum}</strong> ÷ 时支序数 ${k.hour_divisor}，余 ${k.remainder}；暂取${k.next_shichen_candidate?'下一时辰':''}第${k.initial_ke_candidate}刻。</p><p>月${k.upper}上、年${k.lower}下；${k.thousands_rule}，组合得 <strong>${k.base_number}</strong>。</p>`;
  el('video-candidates').innerHTML=`<details><summary>1327考刻候选</summary>${k.secret_candidates.map(a=>`<p>原数＋1327×${a.multiplier}＝${a.number}${a.in_corpus?'':'（超出条文范围）'}</p>`).join('')}</details>`;
  el('video-parents').innerHTML=r.parent_candidates.map(p=>`<details><summary>${p.relation}属${p.animal} · 基条${p.base_number}</summary><p class="muted">核对已知事实，选择条号继续演算。</p>${p.year_candidates.map(a=>`${article(a)}${a.number<10000?`<button type="button" class="choice" data-basis="${a.number}">用${a.number}继续</button>`:''}`).join('')}</details>`).join('');
  el('video-articles').innerHTML=`<table><thead><tr><th>四柱</th><th>八卦加则</th><th>干支化数</th></tr></thead><tbody>${r.pillar_articles.map((row,i)=>`<tr><td>${['年','月','日','时'][i]} ${row.pillar}</td><td>${row.jiaze.number}<details><summary>过程</summary><p>${row.jiaze.upper}上、${row.jiaze.lower}下</p><p>${row.jiaze.line_values_top_down.join('＋')}＝${row.jiaze.line_sum}</p><p>${esc(row.jiaze_article.sentence)}</p></details></td><td>${row.stem_branch_sum_number}<details><summary>条文</summary><p>${esc(row.sum_article.sentence)}</p></details></td></tr>`).join('')}</tbody></table>`;
  el('video-next').innerHTML=branch('基数化卦',r.number_method)+branch('前卦 · 逐次加96',r.before_after.before)+branch('后卦 · 逐次减96',r.before_after.after)+branch('大运流年',r.annual)+(r.life_sequence?`<details><summary>逐加96轮转 · ${r.life_sequence.articles.length}条</summary>${r.life_sequence.articles.map(article).join('')}</details>`:'');
  el('video-tables').innerHTML=r.reference_tables.map(t=>`<h4>${esc(t.title)}</h4><p>${t.rows.map(row=>`${esc(row.key)}：${esc(Array.isArray(row.value)?row.value.join('/'):row.value)}`).join('；')}</p>${source(t.source_seconds)}`).join('');
  el('video-result').hidden=false;
}
el('video-parents').onclick=e=>{const number=e.target.dataset.basis;if(number){el('basis-number').value=number;el('video-form').requestSubmit();}};
el('video-form').onsubmit=async e=>{
  e.preventDefault();el('video-run').disabled=true;el('video-error').hidden=true;
  const data={known_parents:{}};
  if(el('input-mode').value==='pillars')data.bazi=Object.fromEntries(['year','month','day','time'].map(key=>[key,el(key).value.trim()]));
  else{data.birth_date=el('video-date').value;data.birth_time=el('video-time').value;}
  for(const [id,key] of [['father-animal','父亲'],['mother-animal','母亲']])if(el(id).value)data.known_parents[key]=el(id).value;
  if(el('basis-number').value)data.basis_number=Number(el('basis-number').value);
  if(el('fortune-pillar').value.trim())data.fortune_pillar=el('fortune-pillar').value.trim();
  try{
    const response=await fetch('/api/v1/video-chart',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
    const payload=await response.json();
    if(!response.ok||!payload.success)throw Error(payload.error?.message||'演算失败');
    render(payload.data);
  }catch(err){el('video-result').hidden=true;el('video-error').textContent=err.message;el('video-error').hidden=false;}
  finally{el('video-run').disabled=false;}
};
