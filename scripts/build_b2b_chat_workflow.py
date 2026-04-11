from pathlib import Path
import json

root = Path('/Users/leo/.openclaw/workspace/repos/leolan-ki')
portal_path = root / 'portal/index.html'
admin_path = root / 'admin-dashboard/index.html'

portal = portal_path.read_text()
portal = portal.replace("const CHAT_URL = 'https://n8n.leolan.net/webhook/portal-chat';", "const CHAT_URL = 'https://n8n.leolan.net/webhook/b2b-chat';")
portal = portal.replace("const CHAT_HISTORY_URL = 'https://n8n.leolan.net/webhook/portal-chat-history';", "const CHAT_HISTORY_URL = 'https://n8n.leolan.net/webhook/b2b-chat/history';")
portal = portal.replace("      try {\n        const url = `${CHAT_HISTORY_URL}?code=${encodeURIComponent(auth.code)}`;\n        const data = await apiJson(url, { method: 'GET' });\n", "      try {\n        const url = `${CHAT_HISTORY_URL}?customerCode=${encodeURIComponent(auth.code)}`;\n        const data = await apiJson(url, { method: 'GET' });\n")
portal = portal.replace("          body: JSON.stringify({\n            code: auth.code,\n            type: 'customer_to_admin',\n            message,\n            customerEmail: email,\n            restaurantName: auth.restaurantName,\n            slug: auth.slug\n          })\n", "          body: JSON.stringify({\n            action: 'send',\n            customerCode: auth.code,\n            message,\n            customerEmail: email,\n            customerName: auth.restaurantName || auth.name,\n            restaurantName: auth.restaurantName,\n            slug: auth.slug\n          })\n")
portal_path.write_text(portal)

admin = admin_path.read_text()
admin = admin.replace('.customer-row { grid-template-columns: minmax(0, 1.5fr) auto auto auto; }', '.customer-row { grid-template-columns: minmax(0, 1.5fr) auto auto; }')
admin = admin.replace('.customer-row, .idea-row, .sync-row, .feedback-row {', '.customer-row, .idea-row, .sync-row, .feedback-row, .chat-customer-row {')
admin = admin.replace('.customer-name, .idea-title, .sync-title, .feedback-title { font-weight: 700; line-height: 1.45; word-break: break-word; }', '.customer-name, .idea-title, .sync-title, .feedback-title, .chat-customer-name { font-weight: 700; line-height: 1.45; word-break: break-word; }')
admin = admin.replace('.customer-meta, .idea-meta, .sync-meta, .feedback-meta { color: var(--muted); font-size: 0.92rem; margin-top: 4px; line-height: 1.5; }', '.customer-meta, .idea-meta, .sync-meta, .feedback-meta, .chat-customer-meta { color: var(--muted); font-size: 0.92rem; margin-top: 4px; line-height: 1.5; }')
admin = admin.replace('.status-badge, .type-badge {\n      display: inline-flex; align-items: center; justify-content: center; padding: 10px 14px; border-radius: 999px; font-size: 0.9rem; font-weight: 800; min-width: 98px;\n    }', '.status-badge, .type-badge, .unread-badge {\n      display: inline-flex; align-items: center; justify-content: center; padding: 10px 14px; border-radius: 999px; font-size: 0.9rem; font-weight: 800; min-width: 98px;\n    }\n    .unread-badge { min-width: 74px; background: rgba(255,184,77,0.16); border: 1px solid rgba(255,184,77,0.24); color: #ffe0a8; }\n    .unread-badge.zero { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.08); color: var(--muted); }\n    .chat-customer-row { grid-template-columns: minmax(0, 1.4fr) auto auto; }')
admin = admin.replace('.customer-row, .idea-row, .sync-row, .feedback-row { grid-template-columns: 1fr; align-items: stretch; }', '.customer-row, .idea-row, .sync-row, .feedback-row, .chat-customer-row { grid-template-columns: 1fr; align-items: stretch; }')
admin = admin.replace('<button class="tab-button" data-tab="bot-feedback" type="button">📊 Bot-Feedback</button>\n        <button class="tab-button" data-tab="sync" type="button">🔄 Synchronisation</button>', '<button class="tab-button" data-tab="bot-feedback" type="button">📊 Bot-Feedback</button>\n        <button class="tab-button" data-tab="customer-chat" type="button">💬 Kunden-Chat</button>\n        <button class="tab-button" data-tab="sync" type="button">🔄 Synchronisation</button>')
admin = admin.replace('<section class="tab-panel" id="panel-sync">', '''<section class="tab-panel" id="panel-customer-chat">\n        <section class="grid">\n          <article class="panel span-3">\n            <div class="eyebrow">Chat-Kunden</div>\n            <div class="metric-number" id="chatCustomerCount">—</div>\n            <div class="metric-sub">Kunden mit Chatverlauf</div>\n          </article>\n          <article class="panel span-3">\n            <div class="eyebrow">Ungelesen</div>\n            <div class="metric-number warning" id="chatUnreadCount">—</div>\n            <div class="metric-sub">Offene Kunden-Nachrichten</div>\n          </article>\n          <article class="panel span-3">\n            <div class="eyebrow">Letzte Nachricht</div>\n            <div class="metric-number success" id="chatLastTime">—</div>\n            <div class="metric-sub">Neueste Aktivität im Kundenchat</div>\n          </article>\n          <article class="panel span-3">\n            <div class="eyebrow">Antwortkanal</div>\n            <div class="metric-number" style="font-size:1.2rem" id="chatReplyChannel">Brevo</div>\n            <div class="metric-sub">E-Mail + Verlauf in n8n</div>\n          </article>\n\n          <article class="panel span-12">\n            <div class="toolbar">\n              <div>\n                <h2>💬 B2B Kunden-Chat</h2>\n                <p style="color:var(--muted);margin-top:8px">Alle Restaurant- und Hotel-Kunden, die Leo geschrieben haben.</p>\n              </div>\n              <div class="toolbar-actions">\n                <button class="action-button primary" id="refreshChatCustomersButton" type="button">Chats neu laden</button>\n              </div>\n            </div>\n            <div class="status-line" id="chatCustomersStatus"></div>\n            <div class="list" id="chatCustomerList"></div>\n          </article>\n        </section>\n      </section>\n\n      <section class="tab-panel" id="panel-sync">''')
admin = admin.replace("<div style=\"margin-top:10px\"><strong>Chat POST:</strong> <code>https://n8n.leolan.net/webhook/portal-chat</code></div>\n              <div style=\"margin-top:10px\"><strong>Chat GET:</strong> <code>https://n8n.leolan.net/webhook/portal-chat-history</code></div>", "<div style=\"margin-top:10px\"><strong>Chat POST:</strong> <code>https://n8n.leolan.net/webhook/b2b-chat</code></div>\n              <div style=\"margin-top:10px\"><strong>Chat Verlauf:</strong> <code>https://n8n.leolan.net/webhook/b2b-chat/history</code></div>")
admin = admin.replace("    const CHAT_API = 'https://n8n.leolan.net/webhook/portal-chat';\n    const CHAT_HISTORY_API = 'https://n8n.leolan.net/webhook/portal-chat-history';", "    const CHAT_API = 'https://n8n.leolan.net/webhook/b2b-chat';\n    const CHAT_HISTORY_API = 'https://n8n.leolan.net/webhook/b2b-chat/history';")
admin = admin.replace("    const syncBotList = document.getElementById('syncBotList');\n    const syncStatus = document.getElementById('syncStatus');\n    const syncLog = document.getElementById('syncLog');\n    const syncAllButton = document.getElementById('syncAllButton');\n", "    const syncBotList = document.getElementById('syncBotList');\n    const syncStatus = document.getElementById('syncStatus');\n    const syncLog = document.getElementById('syncLog');\n    const syncAllButton = document.getElementById('syncAllButton');\n\n    const chatCustomerCount = document.getElementById('chatCustomerCount');\n    const chatUnreadCount = document.getElementById('chatUnreadCount');\n    const chatLastTime = document.getElementById('chatLastTime');\n    const chatReplyChannel = document.getElementById('chatReplyChannel');\n    const chatCustomerList = document.getElementById('chatCustomerList');\n    const chatCustomersStatus = document.getElementById('chatCustomersStatus');\n    const refreshChatCustomersButton = document.getElementById('refreshChatCustomersButton');\n")
admin = admin.replace("    let workflows = [];\n    let ideas = [];\n    let syncData = { syncLog: [], activeBots: 0, lastSyncAt: null };\n    let currentChat = null;\n", "    let workflows = [];\n    let ideas = [];\n    let syncData = { syncLog: [], activeBots: 0, lastSyncAt: null };\n    let chatCustomers = [];\n    let currentChat = null;\n")
admin = admin.replace("            <button class=\"chat-button\" type=\"button\" data-chat=\"${escapeHtml(slug)}\" data-name=\"${escapeHtml(item.restaurantName || extractRestaurantName(item.name))}\">Chat</button>\n", "")
admin = admin.replace("      customerList.querySelectorAll('.toggle-button').forEach(button => button.addEventListener('click', () => toggleWorkflow(button.dataset.id, button.dataset.action, button)));\n      customerList.querySelectorAll('.chat-button').forEach(button => button.addEventListener('click', () => openChat(button.dataset.chat, button.dataset.name)));\n", "      customerList.querySelectorAll('.toggle-button').forEach(button => button.addEventListener('click', () => toggleWorkflow(button.dataset.id, button.dataset.action, button)));\n")
admin = admin.replace("    async function loadAll() {\n      await Promise.all([loadDashboard(), loadIdeas()]);\n    }\n", "    function renderChatCustomerOverview(items) {\n      const totalUnread = items.reduce((sum, item) => sum + (Number(item.unreadCount) || 0), 0);\n      chatCustomerCount.textContent = items.length;\n      chatUnreadCount.textContent = totalUnread;\n      chatReplyChannel.textContent = 'Brevo';\n      chatLastTime.textContent = items[0]?.lastTimestamp ? formatTime(items[0].lastTimestamp) : '—';\n\n      if (!items.length) {\n        chatCustomerList.innerHTML = '<div class=\"empty-state\">Noch keine B2B-Kunden-Nachrichten vorhanden.</div>';\n        return;\n      }\n\n      chatCustomerList.innerHTML = items.map(item => `\n        <article class=\"chat-customer-row\">\n          <div>\n            <div class=\"chat-customer-name\">${escapeHtml(item.customerName || item.restaurantName || item.customerCode)}</div>\n            <div class=\"chat-customer-meta\">Code ${escapeHtml(item.customerCode)}${item.customerEmail ? ` · ${escapeHtml(item.customerEmail)}` : ''} · Letzte Nachricht ${formatDateTime(item.lastTimestamp)}</div>\n            <div class=\"chat-customer-meta\" style=\"margin-top:8px\">${escapeHtml(item.lastMessage || '—')}</div>\n          </div>\n          <div class=\"unread-badge ${Number(item.unreadCount) ? '' : 'zero'}\">${Number(item.unreadCount) ? `${escapeHtml(item.unreadCount)} neu` : 'gelesen'}</div>\n          <button class=\"chat-button\" type=\"button\" data-customer-code=\"${escapeHtml(item.customerCode)}\" data-customer-name=\"${escapeHtml(item.customerName || item.restaurantName || item.customerCode)}\" data-customer-email=\"${escapeHtml(item.customerEmail || '')}\">Öffnen</button>\n        </article>\n      `).join('');\n\n      chatCustomerList.querySelectorAll('.chat-button').forEach(button => button.addEventListener('click', () => openChat(button.dataset.customerCode, button.dataset.customerName, button.dataset.customerEmail)));\n    }\n\n    async function loadChatCustomers() {\n      chatCustomersStatus.textContent = 'Kunden-Chats werden geladen…';\n      refreshChatCustomersButton.disabled = true;\n      try {\n        const url = `${CHAT_HISTORY_API}?adminKey=${encodeURIComponent(getStoredSecret())}`;\n        const data = await apiJson(url, { method: 'GET' });\n        chatCustomers = Array.isArray(data.customers) ? data.customers : [];\n        renderChatCustomerOverview(chatCustomers);\n        chatCustomersStatus.textContent = chatCustomers.length ? `${chatCustomers.length} Chat-Kunden geladen.` : 'Noch keine Chat-Kunden vorhanden.';\n      } catch (error) {\n        chatCustomers = [];\n        renderChatCustomerOverview([]);\n        chatCustomersStatus.textContent = error.message || 'Kunden-Chats konnten nicht geladen werden.';\n      } finally {\n        refreshChatCustomersButton.disabled = false;\n      }\n    }\n\n    async function loadAll() {\n      await Promise.all([loadDashboard(), loadIdeas(), loadChatCustomers()]);\n    }\n")
admin = admin.replace("    async function openChat(slug, name) {\n      currentChat = { slug, name };\n      chatTitle.textContent = `Chat · ${name}`;\n      chatSubtitle.textContent = `Slug: ${slug}`;\n", "    async function openChat(customerCode, name, email = '') {\n      currentChat = { customerCode, name, email };\n      chatTitle.textContent = `Chat · ${name}`;\n      chatSubtitle.textContent = `Kunden-Code: ${customerCode}${email ? ` · ${email}` : ''}`;\n")
admin = admin.replace("        const url = `${CHAT_HISTORY_API}?slug=${encodeURIComponent(slug)}&adminKey=${encodeURIComponent(getStoredSecret())}`;\n        const data = await apiJson(url, { method: 'GET' });\n        renderChatMessages(Array.isArray(data.messages) ? data.messages : []);\n        chatStatus.textContent = data.customerEmail ? `Antwort geht an ${data.customerEmail}` : 'Keine Kunden-E-Mail hinterlegt.';\n", "        const url = `${CHAT_HISTORY_API}?customerCode=${encodeURIComponent(customerCode)}&adminKey=${encodeURIComponent(getStoredSecret())}`;\n        const data = await apiJson(url, { method: 'GET' });\n        renderChatMessages(Array.isArray(data.messages) ? data.messages : []);\n        chatStatus.textContent = data.customerEmail ? `Antwort geht an ${data.customerEmail}` : 'Keine Kunden-E-Mail hinterlegt.';\n        await loadChatCustomers();\n")
admin = admin.replace("          body: JSON.stringify({ slug: currentChat.slug, type: 'admin_to_customer', adminKey: getStoredSecret(), message })\n", "          body: JSON.stringify({ action: 'admin-reply', adminKey: getStoredSecret(), customerCode: currentChat.customerCode, message })\n")
admin = admin.replace("        renderChatMessages(Array.isArray(data.messages) ? data.messages : []);\n        chatReply.value = '';\n        chatStatus.textContent = data.customerEmail ? `Gesendet an ${data.customerEmail}` : 'Antwort gespeichert, aber keine Kunden-E-Mail vorhanden.';\n", "        renderChatMessages(Array.isArray(data.messages) ? data.messages : []);\n        chatReply.value = '';\n        chatStatus.textContent = data.customerEmail ? `Gesendet an ${data.customerEmail}` : 'Antwort gespeichert, aber keine Kunden-E-Mail vorhanden.';\n        await loadChatCustomers();\n")
admin = admin.replace("    refreshIdeasButton.addEventListener('click', loadIdeas);\n    syncAllButton.addEventListener('click', syncAllBots);\n", "    refreshIdeasButton.addEventListener('click', loadIdeas);\n    refreshChatCustomersButton.addEventListener('click', loadChatCustomers);\n    syncAllButton.addEventListener('click', syncAllBots);\n")
admin = admin.replace("      customerList.innerHTML = ideasList.innerHTML = feedbackFeed.innerHTML = syncBotList.innerHTML = syncLog.innerHTML = '';\n", "      customerList.innerHTML = ideasList.innerHTML = feedbackFeed.innerHTML = syncBotList.innerHTML = syncLog.innerHTML = chatCustomerList.innerHTML = '';\n")
admin = admin.replace("      positiveFeedbackCount.textContent = improvementCount.textContent = averageRating.textContent = trendThisWeek.textContent = trendLastWeek.textContent = complaintCount.textContent = feedbackTotalCount.textContent = '—';\n", "      positiveFeedbackCount.textContent = improvementCount.textContent = averageRating.textContent = trendThisWeek.textContent = trendLastWeek.textContent = complaintCount.textContent = feedbackTotalCount.textContent = '—';\n      chatCustomerCount.textContent = chatUnreadCount.textContent = chatLastTime.textContent = '—';\n")
admin_path.write_text(admin)

workflow_js = r'''const input = $input.first().json || {};
const body = input.body || {};
const query = input.query || {};
const payload = { ...query, ...body };
const action = String(payload.action || (Object.keys(query).length ? 'history' : '')).trim();
const adminKey = String(payload.adminKey || query.adminKey || body.adminKey || '');
const customerCode = String(payload.customerCode || payload.code || '').trim().toUpperCase();
const message = String(payload.message || '').trim();
const now = new Date().toISOString();
const ADMIN_KEY = 'SET_ADMIN_KEY_IN_N8N';
const BREVO_KEY = 'SET_BREVO_KEY_IN_N8N';
const ADMIN_EMAIL = 'business@leolan.net';

const staticData = $getWorkflowStaticData('global');
if (!staticData.b2b_chats) staticData.b2b_chats = {};
if (!staticData.b2b_customers) staticData.b2b_customers = {};

function ensureCustomer(code) {
  if (!code) throw new Error('customerCode fehlt.');
  if (!staticData.b2b_chats[code]) staticData.b2b_chats[code] = [];
  if (!staticData.b2b_customers[code]) staticData.b2b_customers[code] = { customerCode: code, customerEmail: '', customerName: '', restaurantName: '', slug: '', updatedAt: now };
  return staticData.b2b_customers[code];
}

function normalizeMessages(messages) {
  return (messages || []).map(item => ({
    from: item.from === 'admin' ? 'admin' : 'customer',
    message: String(item.message || ''),
    timestamp: item.timestamp || now,
    read: Boolean(item.read),
  })).sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
}

async function sendBrevoEmail({ toEmail, toName, subject, htmlContent, textContent }) {
  if (!toEmail) return null;
  return await this.helpers.httpRequest({
    method: 'POST',
    url: 'https://api.brevo.com/v3/smtp/email',
    headers: {
      'api-key': BREVO_KEY,
      'Content-Type': 'application/json',
      'accept': 'application/json',
    },
    body: {
      sender: { email: ADMIN_EMAIL, name: 'LeoLan Digital' },
      to: [{ email: toEmail, name: toName || toEmail }],
      subject,
      htmlContent,
      textContent,
    },
    json: true,
  });
}

if (action === 'send') {
  if (!customerCode) throw new Error('customerCode fehlt.');
  if (!message) throw new Error('message fehlt.');
  const customer = ensureCustomer(customerCode);
  customer.customerEmail = String(payload.customerEmail || customer.customerEmail || '').trim();
  customer.customerName = String(payload.customerName || customer.customerName || '').trim();
  customer.restaurantName = String(payload.restaurantName || customer.restaurantName || customer.customerName || '').trim();
  customer.slug = String(payload.slug || customer.slug || '').trim();
  customer.updatedAt = now;

  staticData.b2b_chats[customerCode].push({ from: 'customer', message, timestamp: now, read: false });

  const subject = `Neue B2B-Kundennachricht · ${customer.restaurantName || customer.customerName || customerCode}`;
  const preview = String(message).replace(/</g, '&lt;').replace(/>/g, '&gt;');
  await sendBrevoEmail({
    toEmail: ADMIN_EMAIL,
    toName: 'LeoLan Digital',
    subject,
    textContent: `Neue Nachricht von ${customer.restaurantName || customer.customerName || customerCode} (${customerCode})\n${customer.customerEmail ? 'E-Mail: ' + customer.customerEmail + '\n' : ''}\n${message}`,
    htmlContent: `<p><strong>Neue Nachricht von ${customer.restaurantName || customer.customerName || customerCode}</strong></p><p>Kunden-Code: ${customerCode}</p>${customer.customerEmail ? `<p>E-Mail: ${customer.customerEmail}</p>` : ''}<p style="white-space:pre-wrap">${preview}</p>`,
  });

  return [{ json: { success: true, customerCode, customerEmail: customer.customerEmail || '', messages: normalizeMessages(staticData.b2b_chats[customerCode]) } }];
}

if (action === 'admin-reply') {
  if (adminKey !== ADMIN_KEY) throw new Error('adminKey ungültig.');
  if (!customerCode) throw new Error('customerCode fehlt.');
  if (!message) throw new Error('message fehlt.');
  const customer = ensureCustomer(customerCode);
  staticData.b2b_chats[customerCode].push({ from: 'admin', message, timestamp: now, read: true });
  customer.updatedAt = now;

  if (customer.customerEmail) {
    const htmlMessage = String(message).replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
    await sendBrevoEmail({
      toEmail: customer.customerEmail,
      toName: customer.customerName || customer.restaurantName || customer.customerCode,
      subject: `Antwort von LeoLan Digital`,
      textContent: `Hallo ${customer.customerName || customer.restaurantName || customer.customerCode},\n\n${message}\n\nViele Grüße\nLeoLan Digital`,
      htmlContent: `<p>Hallo ${customer.customerName || customer.restaurantName || customer.customerCode},</p><p style="white-space:pre-wrap">${htmlMessage}</p><p>Viele Grüße<br>LeoLan Digital</p>`,
    });
  }

  return [{ json: { success: true, customerCode, customerEmail: customer.customerEmail || '', messages: normalizeMessages(staticData.b2b_chats[customerCode]) } }];
}

if (action === 'history') {
  if (adminKey) {
    if (adminKey !== ADMIN_KEY) throw new Error('adminKey ungültig.');
    if (customerCode) {
      const customer = ensureCustomer(customerCode);
      staticData.b2b_chats[customerCode] = normalizeMessages(staticData.b2b_chats[customerCode]).map(item => item.from === 'customer' ? { ...item, read: true } : item);
      return [{ json: { success: true, customerCode, customerEmail: customer.customerEmail || '', customerName: customer.customerName || customer.restaurantName || customerCode, messages: normalizeMessages(staticData.b2b_chats[customerCode]) } }];
    }

    const customers = Object.entries(staticData.b2b_chats)
      .map(([code, messages]) => {
        const customer = staticData.b2b_customers[code] || { customerCode: code };
        const normalized = normalizeMessages(messages);
        const last = normalized[normalized.length - 1] || {};
        return {
          customerCode: code,
          customerName: customer.customerName || customer.restaurantName || code,
          customerEmail: customer.customerEmail || '',
          restaurantName: customer.restaurantName || '',
          lastMessage: last.message || '',
          lastTimestamp: last.timestamp || customer.updatedAt || now,
          unreadCount: normalized.filter(item => item.from === 'customer' && !item.read).length,
        };
      })
      .sort((a, b) => new Date(b.lastTimestamp) - new Date(a.lastTimestamp));

    return [{ json: { success: true, customers } }];
  }

  if (!customerCode) throw new Error('customerCode fehlt.');
  const customer = ensureCustomer(customerCode);
  return [{ json: { success: true, customerCode, customerEmail: customer.customerEmail || '', messages: normalizeMessages(staticData.b2b_chats[customerCode]) } }];
}

throw new Error('Ungültige action. Erlaubt: send, admin-reply, history');'''

workflow = {
    "name": "B2B Customer Chat",
    "nodes": [
        {
            "id": "b2b-post",
            "name": "B2B Chat POST",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1.1,
            "position": [240, 280],
            "parameters": {
                "httpMethod": "POST",
                "path": "b2b-chat",
                "responseMode": "responseNode",
                "options": {}
            },
            "webhookId": "b2b-chat-post"
        },
        {
            "id": "b2b-history",
            "name": "B2B Chat History",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1.1,
            "position": [240, 480],
            "parameters": {
                "httpMethod": "GET",
                "path": "b2b-chat/history",
                "responseMode": "responseNode",
                "options": {}
            },
            "webhookId": "b2b-chat-history"
        },
        {
            "id": "b2b-code",
            "name": "Handle B2B Chat",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [520, 380],
            "parameters": {"jsCode": workflow_js}
        },
        {
            "id": "b2b-response",
            "name": "JSON Response",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1.1,
            "position": [800, 380],
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{ JSON.stringify($json) }}",
                "options": {
                    "responseCode": 200,
                    "responseHeaders": {
                        "entries": [
                            {"name": "Access-Control-Allow-Origin", "value": "*"},
                            {"name": "Access-Control-Allow-Headers", "value": "Content-Type"}
                        ]
                    }
                }
            }
        }
    ],
    "connections": {
        "B2B Chat POST": {"main": [[{"node": "Handle B2B Chat", "type": "main", "index": 0}]]},
        "B2B Chat History": {"main": [[{"node": "Handle B2B Chat", "type": "main", "index": 0}]]},
        "Handle B2B Chat": {"main": [[{"node": "JSON Response", "type": "main", "index": 0}]]}
    },
    "settings": {"executionOrder": "v1"}
}

(root / 'b2b-customer-chat.workflow.json').write_text(json.dumps(workflow, ensure_ascii=False, indent=2))
print('updated portal/admin and wrote workflow json')
