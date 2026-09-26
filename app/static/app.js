const $ = selector => document.querySelector(selector);
const safe = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let chart = null, input = null, mode = 'simple', group = 'current', page = 0;
const pad = n => String(n).padStart(2, '0');
const now = new Date();
$('#queryDate').value = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
$('#queryTime').value = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
const bazi = value => ['year','month','day','time'].map(k => value?.[k] || '').join(' ');
const item = (name, value) => `<div><span>${name}</span><strong>${safe(value)}</strong></div>`;
const empty = value => value === '' || value === null || value === undefined ? '—' : value;

function showChart(data) {
  chart = data; mode = 'simple'; group = 'current'; page = 0;
  $('.mode-switch [data-mode="simple"]').click();
  const info = data.basic_info, n = data.basic_chart;
  $('#infoCard').innerHTML = `<div class="section-head"><div><span class="eyebrow">BIRTH / QUERY</span><h3>命盘信息</h3></div><span class="badge">${safe(info.gender)}命</span></div><div class="info-grid">${item('阳历出生', info.birth_datetime)}${item('农历出生', info.birth_lunar + (info.birth_is_leap ? ' · 闰月' : ''))}${item('出生八字', bazi(info.birth_bazi))}${item('求测时间', info.query_datetime)}${item('求测八字', bazi(info.query_bazi))}</div><p class="subtle">显示时间遵循原程序的晚子时处理；原输入：${safe(info.birth_datetime_input)} / ${safe(info.query_datetime_input)}</p>`;
  $('#numberCard').innerHTML = `<div class="section-head"><div><span class="eyebrow">CORE / NUMBERS</span><h3>核心命数</h3></div></div><div class="numbers-grid">${[['先天命数',n.cong_num],['五音命数',n.tone_num],['日命数',n.day_life],['时运数',n.time_luck],['考刻',n.moment],['本命数',n.main_num],['十二辟卦',n.hexagram],['后天命数',n.later_num]].map(([label,value])=>`<div><span>${label}</span><strong>${safe(value)}</strong></div>`).join('')}</div><p class="pro-only calc-note">${safe(n.cong_calc)} · ${safe(n.day_life_calc)} · ${safe(n.moment_calc)} · ${safe(n.main_calc)}<br>${safe(n.later_calc)}</p>`;
  $('#destinyCard').innerHTML = `<div class="section-head"><div><span class="eyebrow">DESTINY / ARTICLES</span><h3>本命条文</h3></div><span>${data.destiny_articles.length} 条</span></div>${data.destiny_articles.length ? `<div class="destiny-list">${data.destiny_articles.map(a=>`<article><div class="destiny-title"><span>${safe(a.item)}</span><strong>条文 ${safe(a.number)}</strong></div><p>${safe(a.duanyu === '未找到断语' ? '暂未找到匹配条文' : empty(a.duanyu))}</p><div class="pro-only minor">${safe(a.formula)} · ${safe(a.source)}${a.duanyu_age ? ` · 断语年龄 ${safe(a.duanyu_age)}` : ''}</div></article>`).join('')}</div>` : `<div class="empty-state">暂未找到匹配条文<span>原项目的 14-10 表对这组卦名、考刻与先天数无对应记录。</span></div>`}`;
  const virtualAge = Number(info.query_datetime.slice(0,4)) - Number(info.birth_datetime.slice(0,4)) + 1;
  $('#result').dataset.virtualAge = String(virtualAge);
  if (virtualAge < 1) group = '1';
  else if (virtualAge > 100) group = '81';
  $('#result').hidden = false;
  renderAnnual();
  if (location.pathname !== '/result') history.pushState({}, '', '/result');
  $('#result').scrollIntoView({behavior:'smooth', block:'start'});
}

function filtered() {
  if (!chart) return [];
  const age = Number($('#result').dataset.virtualAge);
  if (group === 'current') return chart.annual_fortunes.filter(x => x.age >= age-2 && x.age <= age+2);
  const min = Number(group);
  return chart.annual_fortunes.filter(x => x.age >= min && x.age <= Math.min(min+19,100));
}

function annualCard(x) {
  const detail = [
    ['四声',x.sound],['标记',x.marker],['字母',x.letter],['校正数字母',x.corrected_letter],
    ['校正数',x.original_correction],['校正后校正数',x.corrected_correction],
    ['计算公式',x.formula],['原条文',x.original_fortune],['原断语',x.original_duanyu],
    ['原断语年龄',x.original_duanyu_age],['校正后条文',x.corrected_fortune],
    ['校正后断语',x.corrected_duanyu],['校正后断语年龄',x.corrected_duanyu_age],
  ];
  return `<article class="year-card ${x.age === Number($('#result').dataset.virtualAge) ? 'near-current' : ''}"><div class="year-top"><span class="year-age">${x.age} 岁 <small>· ${safe(x.year)}</small></span>${x.age === Number($('#result').dataset.virtualAge) ? '<span class="badge">参考虚岁</span>' : ''}</div><div class="year-fortune"><span>校正后条文 ${safe(empty(x.corrected_fortune))}</span><p>${safe(x.corrected_duanyu || '暂无匹配断语')}</p></div><details ${mode === 'pro' ? 'open' : ''}><summary>查看计算过程</summary><div class="detail-grid">${detail.map(([label,value])=>item(label,empty(value))).join('')}</div><p class="data-source">数据来源：原项目 14-11 至 14-14、铁板神数-条文断词.csv</p></details></article>`;
}

function renderAnnual() {
  if (!chart) return;
  const age = Number($('#result').dataset.virtualAge);
  const choices = [['current',`当前年龄附近${age >= 1 && age <= 100 ? ` · ${age}岁` : ''}`],['1','1–20'],['21','21–40'],['41','41–60'],['61','61–80'],['81','81–100']];
  $('#ageFilters').innerHTML = choices.map(([key,label])=>`<button type="button" class="${group === key ? 'active' : ''}" data-group="${key}">${safe(label)}</button>`).join('');
  const list = filtered(), pages = Math.max(1,Math.ceil(list.length/10));
  if (page >= pages) page = 0;
  $('#annualCount').textContent = `${chart.annual_fortunes.length} 岁完整数据`;
  $('#annualList').innerHTML = list.length ? list.slice(page*10,(page+1)*10).map(annualCard).join('') : '<div class="empty-state">所选求测年对应的年龄超出原项目的 1–100 岁范围。<span>可选择下方其他年龄段查看完整流年。</span></div>';
  $('#pageLabel').textContent = list.length ? `${page+1} / ${pages}` : '';
  $('#prevPage').disabled = page === 0;
  $('#nextPage').disabled = page >= pages-1;
  $('.pagination').hidden = pages === 1;
}

$('#chartForm').addEventListener('submit', async event => {
  event.preventDefault();
  const birth = `${$('#birthDate').value} ${$('#birthTime').value}`;
  const query = `${$('#queryDate').value} ${$('#queryTime').value}`;
  $('#error').textContent = '';
  if (birth > query) { $('#error').textContent = '出生时间不能晚于求测时间'; return; }
  input = {gender: document.querySelector('input[name="gender"]:checked').value, birth_datetime: birth, query_datetime: query};
  const button = $('#submitBtn'); button.disabled = true; button.innerHTML = '正在排盘…';
  const controller = new AbortController(), timer = setTimeout(()=>controller.abort(),20000);
  try {
    const response = await fetch('/api/v1/chart',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input),signal:controller.signal});
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.error?.message || '排盘失败，请稍后重试');
    showChart(result.data);
  } catch (err) { $('#error').textContent = err.name === 'AbortError' ? '请求超时，请稍后重试' : err.message; }
  finally { clearTimeout(timer); button.disabled = false; button.innerHTML = '开始排盘 <span aria-hidden="true">↗</span>'; }
});

$('.mode-switch').addEventListener('click', event => {
  const button = event.target.closest('button[data-mode]'); if (!button) return;
  mode = button.dataset.mode; $('#result').classList.toggle('pro',mode === 'pro');
  document.querySelectorAll('.mode-switch button').forEach(b => { b.classList.toggle('active',b === button); b.setAttribute('aria-pressed',String(b === button)); });
  renderAnnual();
});
$('#ageFilters').addEventListener('click', event => { const b=event.target.closest('button[data-group]');if (b) { group=b.dataset.group;page=0;renderAnnual(); } });
$('#prevPage').addEventListener('click',()=>{if(page>0){page--;renderAnnual();}});
$('#nextPage').addEventListener('click',()=>{page++;renderAnnual();});
$('#printBtn').addEventListener('click',()=>{
  if(!chart)return;
  $('#annualList').innerHTML=chart.annual_fortunes.map(annualCard).join('');
  window.print();
  setTimeout(renderAnnual,1000);
});
window.addEventListener('afterprint',renderAnnual);
$('#copyBtn').addEventListener('click',async()=>{
  if(!chart) return;
  const n=chart.basic_chart,b=chart.basic_info;
  const lines=[`铁板神数排盘 · ${b.gender}`,`出生 ${b.birth_datetime} · ${b.birth_lunar}`,`八字 ${bazi(b.birth_bazi)}`,`先天命数 ${n.cong_num} · 五音命数 ${n.tone_num} · 日命数 ${n.day_life} · 时运数 ${n.time_luck}`,`考刻 ${n.moment} · 本命数 ${n.main_num} · 十二辟卦 ${n.hexagram}`,`本命条文：${chart.destiny_articles.length ? chart.destiny_articles.map(a=>`${a.item} ${a.number} ${a.duanyu}`).join('；'):'暂未找到匹配条文'}`,...chart.annual_fortunes.map(x=>`${x.age}岁 ${x.year} 校正后条文 ${x.corrected_fortune||'—'} ${x.corrected_duanyu||''}`)];
  try { await navigator.clipboard.writeText(lines.join('\n'));$('#copyBtn').textContent='已复制';setTimeout(()=>$('#copyBtn').textContent='复制结果',1800); }
  catch { $('#error').textContent='复制失败，请使用 Markdown 下载'; }
});
$('#markdownBtn').addEventListener('click',async()=>{
  if(!input)return;
  try { const response=await fetch('/api/v1/report.md',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});if(!response.ok){const err=await response.json();throw new Error(err.error?.message||'导出失败');}const blob=await response.blob();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`铁板排盘_${input.birth_datetime.slice(0,10)}_${input.query_datetime.slice(0,10)}.md`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),5000); }
  catch(err){$('#error').textContent=err.message;}
});
