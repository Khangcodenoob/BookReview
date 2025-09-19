(function(){
  // Simple chat widget logic that calls /api/chat/suggest
  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const form = document.getElementById('chat-widget-form');
  const input = document.getElementById('chat-widget-input');
  const messages = document.getElementById('chat-messages');

  if(!toggle || !panel || !form || !input || !messages) return;

  function append(who, html){
    const el = document.createElement('div');
    el.className = 'cw-message ' + (who === 'bot' ? 'bot' : 'user');
    el.innerHTML = '<strong>' + (who==='bot'? 'Bot' : 'Bạn') + ':</strong> ' + html;
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
  }

  function setProcessing(on){
    if(on){
      const p = document.createElement('div'); p.className='cw-processing'; p.textContent='Đang xử lý...'; messages.appendChild(p);
      messages.scrollTop = messages.scrollHeight;
      return p;
    }
    return null;
  }

  toggle.addEventListener('click', ()=>{
    const open = !panel.hasAttribute('hidden');
    if(open){
      panel.setAttribute('hidden','');
    }else{
      panel.removeAttribute('hidden');
      // focus input
      setTimeout(()=>input.focus(), 120);
    }
  });
  closeBtn.addEventListener('click', ()=>{
    panel.setAttribute('hidden','');
    toggle.focus();
  });

  // close on Escape when panel is open
  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape'){
      if(!panel.hasAttribute('hidden')){
        panel.setAttribute('hidden','');
        toggle.focus();
      }
    }
  });

  async function sendQuery(q, seed){
    if(!q) return;
    append('user', q);
    const proc = setProcessing(true);
    try{
      const body = {q};
      if(seed) body.seed_book_id = seed;
      const res = await fetch('/api/chat/suggest', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
      const j = await res.json();
      if(proc) proc.remove();
      if(j && j.ok && Array.isArray(j.suggestions)){
        // render suggestion cards
        const container = document.createElement('div');
        container.className = 'cw-suggestions';
        j.suggestions.forEach(s=>{
          const card = document.createElement('a');
          card.className = 'cw-card';
          card.href = s.url;
          card.innerHTML = `<div style="display:flex;gap:8px;align-items:center"><img src="${s.cover_url||'/static/placeholder.jpg'}" style="width:46px;height:64px;object-fit:cover;border-radius:6px;border:1px solid rgba(0,0,0,0.06)"><div style="flex:1"><strong>${s.title}</strong><div class='muted' style='font-size:13px'>${s.author}</div><div class='muted' style='font-size:13px;margin-top:6px'>${s.short}</div></div></div>`;
          card.target = '_blank';
          container.appendChild(card);
        });
        append('bot', container.outerHTML);
      } else if(j && j.error){
        append('bot', 'Lỗi: ' + (j.error || 'Không xác định'));
      } else {
        append('bot', 'Không có đề xuất.');
      }
    }catch(err){
      if(proc) proc.remove();
      append('bot', 'Lỗi kết nối.');
    }
  }

  form.addEventListener('submit', (e)=>{e.preventDefault(); const q=input.value&&input.value.trim(); if(!q) return; input.value=''; sendQuery(q, window.__chat_seed_book_id || null);} );

  // keyboard: Ctrl+Enter sends
  input.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)){
      e.preventDefault(); form.requestSubmit();
    }
  });
})();
