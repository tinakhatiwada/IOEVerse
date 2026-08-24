/**
 * IOEverse Global AI Chat Widget
 * Include via: <script src="/static/js/chat-widget.js"></script>
 * Optionally set window.CHAT_SUBJECT before including to filter answers.
 */
(function () {
  // --- Inject CSS ---
  const style = document.createElement('style');
  style.textContent = `
    #ioe-fab{position:fixed;bottom:28px;right:28px;z-index:9000;width:52px;height:52px;border-radius:50%;background:#6366f1;border:none;cursor:pointer;box-shadow:0 4px 20px rgba(99,102,241,.5);display:flex;align-items:center;justify-content:center;transition:transform .2s,box-shadow .2s;font-family:'Inter',sans-serif;}
    #ioe-fab:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(99,102,241,.65);}
    #ioe-fab svg{width:22px;height:22px;fill:#fff;pointer-events:none;}
    #ioe-panel{position:fixed;bottom:90px;right:28px;z-index:8999;width:360px;border-radius:18px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,.18);border:1px solid #e5e7eb;flex-direction:column;display:none;font-family:'Inter',sans-serif;}
    #ioe-panel.open{display:flex;animation:ioeSlide .22s ease;}
    @keyframes ioeSlide{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    .ioe-head{background:#0f1f3d;padding:15px 18px;display:flex;align-items:center;gap:10px;flex-shrink:0;}
    .ioe-av{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#6366f1,#818cf8);display:grid;place-items:center;flex-shrink:0;}
    .ioe-av svg{width:16px;height:16px;fill:#fff;}
    .ioe-hi strong{display:block;color:#fff;font-size:13px;font-weight:700;}
    .ioe-hi small{color:rgba(255,255,255,.45);font-size:11px;}
    .ioe-dot{width:7px;height:7px;border-radius:50%;background:#10b981;margin-left:auto;animation:ioePulse 2s infinite;}
    @keyframes ioePulse{0%,100%{opacity:1}50%{opacity:.35}}
    .ioe-subj{background:rgba(99,102,241,.07);border-bottom:1px solid #e5e7eb;padding:5px 16px;font-size:11px;color:#6366f1;font-weight:600;display:none;}
    .ioe-msgs{height:290px;overflow-y:auto;padding:14px;background:#f9fafb;display:flex;flex-direction:column;gap:9px;}
    .ioe-m{max-width:88%;padding:9px 13px;border-radius:12px;font-size:13px;line-height:1.55;word-break:break-word;}
    .ioe-m.ai{background:#fff;color:#0f1f3d;border:1px solid #e5e7eb;align-self:flex-start;border-radius:4px 12px 12px 12px;}
    .ioe-m.user{background:#6366f1;color:#fff;align-self:flex-end;border-radius:12px 4px 12px 12px;}
    .ioe-m.thinking{color:#9ca3af;font-style:italic;background:#fff;border:1px solid #e5e7eb;align-self:flex-start;border-radius:4px 12px 12px 12px;}
    .ioe-m.err{background:#fef2f2;color:#dc2626;border:1px solid #fecaca;align-self:flex-start;border-radius:4px 12px 12px 12px;}
    .ioe-foot{padding:10px 14px;border-top:1px solid #e5e7eb;display:flex;gap:8px;background:#fff;flex-shrink:0;}
    .ioe-inp{flex:1;border:1.5px solid #e5e7eb;border-radius:8px;padding:9px 12px;font-size:13px;font-family:'Inter',sans-serif;outline:none;color:#0f1f3d;transition:border-color .2s;}
    .ioe-inp:focus{border-color:#6366f1;}
    .ioe-btn{background:#6366f1;border:none;border-radius:8px;padding:9px 13px;cursor:pointer;transition:background .2s;flex-shrink:0;}
    .ioe-btn:hover{background:#4f46e5;}
    .ioe-btn:disabled{background:#d1d5db;cursor:not-allowed;}
    .ioe-btn svg{width:15px;height:15px;fill:#fff;display:block;}
    @media(max-width:480px){#ioe-panel{width:calc(100vw - 24px);right:12px;bottom:78px;}#ioe-fab{right:16px;bottom:16px;}}
  `;
  document.head.appendChild(style);

  // --- Inject HTML ---
  const wrap = document.createElement('div');
  wrap.innerHTML = `
    <button id="ioe-fab" aria-label="AI Chat">
      <svg id="ioe-icon-chat" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
      <svg id="ioe-icon-close" viewBox="0 0 24 24" style="display:none"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
    </button>
    <div id="ioe-panel">
      <div class="ioe-head">
        <div class="ioe-av"><svg viewBox="0 0 24 24"><path d="M12 3C7 3 3 7 3 12s4 9 9 9 9-4 9-9-4-9-9-9zm-1 13v-5l-1-.6V9l4 2.4V13l-1 .6V16h-2z"/></svg></div>
        <div class="ioe-hi"><strong>AI Study Assistant</strong><small>IOEverse RAG</small></div>
        <div class="ioe-dot"></div>
      </div>
      <div class="ioe-subj" id="ioe-subj-bar"></div>
      <div class="ioe-msgs" id="ioe-msgs">
        <div class="ioe-m ai">Hello! I am your AI study assistant. Ask me anything about your IOE syllabus and I will answer based on your course materials.</div>
      </div>
      <div class="ioe-foot">
        <input type="text" class="ioe-inp" id="ioe-inp" placeholder="Ask any question..." autocomplete="off" />
        <button class="ioe-btn" id="ioe-send" aria-label="Send">
          <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(wrap);

  // --- Logic ---
  const fab    = document.getElementById('ioe-fab');
  const panel  = document.getElementById('ioe-panel');
  const msgs   = document.getElementById('ioe-msgs');
  const inp    = document.getElementById('ioe-inp');
  const sendBtn = document.getElementById('ioe-send');
  const iconChat  = document.getElementById('ioe-icon-chat');
  const iconClose = document.getElementById('ioe-icon-close');
  const subjBar   = document.getElementById('ioe-subj-bar');

  let isOpen = false;

  function toggleChat() {
    isOpen = !isOpen;
    panel.classList.toggle('open', isOpen);
    iconChat.style.display  = isOpen ? 'none'  : 'block';
    iconClose.style.display = isOpen ? 'block' : 'none';

    // Show subject filter if set
    const subj = window.CHAT_SUBJECT || null;
    if (subj) {
      subjBar.style.display = 'block';
      subjBar.textContent = 'Filtered to: ' + subj;
    }

    if (isOpen) inp.focus();
  }

  function addMsg(text, cls) {
    const d = document.createElement('div');
    d.className = 'ioe-m ' + cls;
    d.textContent = text;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }

  async function sendMessage() {
    const q = inp.value.trim();
    if (!q) return;

    addMsg(q, 'user');
    inp.value = '';
    sendBtn.disabled = true;

    const thinking = addMsg('Thinking...', 'thinking');

    try {
      const body = { question: q };
      if (window.CHAT_SUBJECT)  body.subject = window.CHAT_SUBJECT;
      if (window.CHAT_CHAPTER)  body.chapter = window.CHAT_CHAPTER;

      const res  = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      thinking.remove();

      if (data.answer) {
        addMsg(data.answer, 'ai');
      } else {
        addMsg(data.error || 'No relevant answer found. Try a more specific question.', 'err');
      }
    } catch (e) {
      thinking.remove();
      addMsg('Connection error. Please try again.', 'err');
    }

    sendBtn.disabled = false;
    inp.focus();
  }

  fab.addEventListener('click', toggleChat);
  sendBtn.addEventListener('click', sendMessage);
  inp.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });
})();
