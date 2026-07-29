#!/usr/bin/env python3
import json
import os
import urllib.request
import urllib.error

API_KEY = os.environ.get('LEOLAN_N8N_API_KEY', '')
BASE = 'https://n8n.leolan.net/api/v1'
PORTAL_WORKFLOW_ID = 'zmjsS7oWl89aAVH7'
STRIPE_WEBHOOK_ID = 'EGdns4krCtz7s7Cf'
STRIPE_SECRET = os.environ.get('LEOLAN_STRIPE_SECRET', '')
BREVO_KEY = os.environ.get('LEOLAN_BREVO_KEY', '')


ADDON_HANDLER_CODE = r'''
const DEFAULT_CUSTOMERS = {
  TEST01: {
    code: 'TEST01',
    name: 'Test Restaurant',
    restaurantName: 'Test Restaurant',
    slug: 'test-restaurant',
    plan: 'starter',
    msgLimit: 500,
    msgCount: { '2026-04-01': 32, '2026-04-02': 28, '2026-04-08': 41, '2026-04-10': 53, '2026-04-11': 17 },
    customerEmail: 'restaurant@example.com',
    activeAddons: [],
    warned80: false,
    warned100: false,
  },
};

const ADDON_CONFIG = {
  starter_to_pro: { amount: 14900, label: 'Starter → Pro Upgrade', description: 'Upgrade von Starter auf Pro', category: 'plan', plan: 'pro', msgLimit: 2000 },
  messages_s: { amount: 49900, label: 'Nachrichten S', description: '1.000 Nachrichten / Monat', category: 'messages', msgLimit: 1000 },
  messages_m: { amount: 59900, label: 'Nachrichten M', description: '2.000 Nachrichten / Monat', category: 'messages', msgLimit: 2000 },
  messages_l: { amount: 69900, label: 'Nachrichten L', description: 'Bis zu 20.000 Nachrichten / Monat', category: 'messages', msgLimit: 20000 },
  instagram_autoposts: { amount: 8900, label: 'Instagram Auto-Posts', description: 'Täglich KI-Posts', category: 'social' },
  facebook_autoposts: { amount: 5900, label: 'Facebook Auto-Posts', description: 'Täglich KI-Posts', category: 'social' },
  review_management: { amount: 8900, label: 'Bewertungsmanagement', description: 'KI antwortet auf Reviews', category: 'reputation' },
  google_business: { amount: 7900, label: 'Google Business', description: 'Profil automatisch', category: 'visibility' },
  dashboard: { amount: 3900, label: 'Dashboard', description: 'Statistiken', category: 'analytics' },
  email_monitor: { amount: 5900, label: 'E-Mail Monitor', description: 'Wichtige E-Mails', category: 'monitoring' },
  reels_ai_videos: { amount: 14900, label: 'Reels KI-Videos', description: 'Automatische Reels', category: 'content' },
};

function initCustomers(staticData) {
  if (!staticData.customers) staticData.customers = JSON.parse(JSON.stringify(DEFAULT_CUSTOMERS));
  for (const [code, customer] of Object.entries(DEFAULT_CUSTOMERS)) {
    if (!staticData.customers[code]) staticData.customers[code] = JSON.parse(JSON.stringify(customer));
  }
  for (const customer of Object.values(staticData.customers)) {
    if (!Array.isArray(customer.activeAddons)) customer.activeAddons = [];
    if (!customer.plan) customer.plan = 'starter';
    if (!customer.msgLimit) customer.msgLimit = 500;
  }
  return staticData.customers;
}

function normalizeCode(value) {
  return String(value || '').trim().toUpperCase();
}

function getCustomerByCode(staticData, code) {
  const customers = initCustomers(staticData);
  return customers[normalizeCode(code)] || null;
}

function monthUsage(msgCount = {}) {
  const now = new Date();
  const monthKey = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  return Object.entries(msgCount).reduce((sum, [day, count]) => day.startsWith(monthKey) ? sum + Number(count || 0) : sum, 0);
}

function weekUsage(msgCount = {}) {
  const now = new Date();
  const start = new Date(now);
  start.setDate(now.getDate() - 6);
  start.setHours(0, 0, 0, 0);
  return Object.entries(msgCount).reduce((sum, [day, count]) => {
    const date = new Date(`${day}T00:00:00`);
    return date >= start && date <= now ? sum + Number(count || 0) : sum;
  }, 0);
}

const staticData = $getWorkflowStaticData('global');
const customers = initCustomers(staticData);
if (!staticData.priceIds) staticData.priceIds = {};

function toFormBody(form) {
  return Object.entries(form)
    .filter(([, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
    .join('&');
}

async function stripeRequest(method, path, form) {
  const body = toFormBody(form);
  return await this.helpers.httpRequest({
    method,
    url: `https://api.stripe.com/v1/${path}`,
    headers: {
      Authorization: 'Bearer __STRIPE_SECRET__',
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body,
    json: true,
  });
}

async function ensureRecurringPrice(key, config) {
  if (staticData.priceIds[key]) return staticData.priceIds[key];
  const product = await stripeRequest('POST', 'products', {
    name: `LeoLan Digital · ${config.label}`,
    description: config.description || config.label,
    'metadata[addonType]': key,
  });
  const price = await stripeRequest('POST', 'prices', {
    product: product.id,
    unit_amount: String(config.amount),
    currency: 'eur',
    'recurring[interval]': 'month',
    'metadata[addonType]': key,
  });
  staticData.priceIds[key] = price.id;
  return price.id;
}

async function warmupPrices() {
  for (const [key, config] of Object.entries(ADDON_CONFIG)) {
    await ensureRecurringPrice(key, config);
  }
}

const payload = { ...($json || {}), ...($json.query || {}), ...($json.params || {}), ...($json.body || {}) };
const customer = getCustomerByCode(staticData, payload.code);
if (!customer) {
  return [{ json: { success: false, error: 'Ungültiger Kunden-Code.' } }];
}

await warmupPrices();

const addonType = String(payload.addonType || '').trim();
if (!addonType) {
  return [{
    json: {
      success: true,
      slug: customer.slug,
      restaurantName: customer.restaurantName,
      plan: customer.plan || 'starter',
      msgLimit: Number(customer.msgLimit || 500),
      weekUsage: weekUsage(customer.msgCount || {}),
      monthUsage: monthUsage(customer.msgCount || {}),
      activeAddons: customer.activeAddons || [],
      priceIds: staticData.priceIds,
    },
  }];
}

const config = ADDON_CONFIG[addonType];
if (!config) {
  return [{ json: { success: false, error: 'Unbekanntes Add-On.' } }];
}
if (addonType === 'starter_to_pro' && String(customer.plan || 'starter') === 'pro') {
  return [{ json: { success: false, error: 'Pro ist bereits aktiv.' } }];
}
if ((customer.activeAddons || []).includes(addonType)) {
  return [{ json: { success: false, error: 'Dieses Add-On ist bereits aktiv.' } }];
}

const priceId = await ensureRecurringPrice(addonType, config);
const successUrl = 'https://ki.leolan.net/portal/?checkout=success';
const cancelUrl = 'https://ki.leolan.net/portal/?checkout=cancel';
const session = await stripeRequest('POST', 'checkout/sessions', {
  mode: 'subscription',
  success_url: successUrl,
  cancel_url: cancelUrl,
  'line_items[0][price]': priceId,
  'line_items[0][quantity]': '1',
  customer_email: customer.customerEmail || '',
  'metadata[purchaseCategory]': 'addon',
  'metadata[code]': customer.code,
  'metadata[slug]': customer.slug,
  'metadata[addonType]': addonType,
  'metadata[addonLabel]': config.label,
  'metadata[addonAmount]': String(config.amount / 100),
  'metadata[restaurantName]': customer.restaurantName || customer.name || '',
  'subscription_data[metadata][purchaseCategory]': 'addon',
  'subscription_data[metadata][code]': customer.code,
  'subscription_data[metadata][slug]': customer.slug,
  'subscription_data[metadata][addonType]': addonType,
  'subscription_data[metadata][addonLabel]': config.label,
  'subscription_data[metadata][addonAmount]': String(config.amount / 100),
  'subscription_data[metadata][restaurantName]': customer.restaurantName || customer.name || '',
});

return [{
  json: {
    success: true,
    checkoutUrl: session.url,
    addonType,
    addonLabel: config.label,
    plan: customer.plan || 'starter',
    msgLimit: customer.msgLimit || 500,
  },
}];
'''

BUILD_INVOICE_CODE = r'''
const event = $input.first().json.body || $input.first().json || {};
if ((event.type || '') !== 'checkout.session.completed') {
  return [{ json: { success: true, ignored: true, type: event.type || 'unknown' } }];
}

const payload = event.data?.object || {};
const meta = payload.metadata || {};
const purchaseCategory = meta.purchaseCategory || (meta.addonType ? 'addon' : 'core');
const customerEmail = payload.customer_details?.email || payload.customer_email || meta.email || '';
if (!customerEmail) return [{ json: { success: false, error: 'customer_email_missing' } }];

const addr = payload.customer_details?.address || {};
const addrParts = [
  addr.line1,
  addr.line2,
  [addr.postal_code, addr.city].filter(Boolean).join(' '),
  addr.country
].filter(Boolean);
const customerAddress = (meta.customerAddress || addrParts.join('\n') || '');
const customerPhone = meta.phone || payload.customer_details?.phone || '';
const customerWebsite = meta.website || '';
const customerVatId = meta.vatId || '';
const whatsappNumber = meta.whatsappNumber || '';
const currency = (payload.currency || 'eur').toUpperCase();

if (purchaseCategory === 'addon') {
  const addonType = String(meta.addonType || '').trim();
  const addonLabel = meta.addonLabel || addonType || 'Add-On';
  const addonAmount = parseFloat(meta.addonAmount) || 0;
  const code = String(meta.code || '').trim().toUpperCase();
  const slug = String(meta.slug || '').trim();
  const restaurantName = meta.restaurantName || payload.customer_details?.name || customerEmail.split('@')[0] || 'Kunde';

  const N8N_API_KEY = os.environ.get('LEOLAN_N8N_API_KEY', '');
  const BASE = 'https://n8n.leolan.net/api/v1';
  const PORTAL_WORKFLOW_ID = 'zmjsS7oWl89aAVH7';

  async function n8nApi(method, path, body) {
    return await this.helpers.httpRequest({
      method,
      url: `${BASE}${path}`,
      headers: {
        'X-N8N-API-KEY': N8N_API_KEY,
        'Content-Type': 'application/json',
      },
      body,
      json: true,
    });
  }

  function ensureCustomer(staticData) {
    if (!staticData.global) staticData.global = {};
    if (!staticData.global.customers) staticData.global.customers = {};
    if (!staticData.global.customers[code]) {
      staticData.global.customers[code] = {
        code,
        name: restaurantName,
        restaurantName,
        slug: slug || code.toLowerCase(),
        plan: 'starter',
        msgLimit: 500,
        msgCount: {},
        customerEmail,
        activeAddons: [],
        warned80: false,
        warned100: false,
      };
    }
    const customer = staticData.global.customers[code];
    if (!Array.isArray(customer.activeAddons)) customer.activeAddons = [];
    customer.customerEmail = customerEmail || customer.customerEmail || '';
    customer.restaurantName = customer.restaurantName || restaurantName;
    customer.slug = customer.slug || slug || code.toLowerCase();
    if (addonType === 'starter_to_pro') {
      customer.plan = 'pro';
      customer.msgLimit = Math.max(Number(customer.msgLimit || 0), 2000);
    } else {
      if (!customer.activeAddons.includes(addonType)) customer.activeAddons.push(addonType);
      if (addonType === 'messages_s') customer.msgLimit = Math.max(Number(customer.msgLimit || 0), 1000);
      if (addonType === 'messages_m') customer.msgLimit = Math.max(Number(customer.msgLimit || 0), 2000);
      if (addonType === 'messages_l') customer.msgLimit = Math.max(Number(customer.msgLimit || 0), 20000);
    }
    customer.lastAddonPurchase = {
      addonType,
      addonLabel,
      amount: addonAmount,
      stripeSessionId: payload.id || '',
      purchasedAt: new Date().toISOString(),
    };
    customer.warned80 = false;
    customer.warned100 = false;
  }

  try {
    const workflow = await n8nApi('GET', `/workflows/${PORTAL_WORKFLOW_ID}`);
    const staticData = workflow.staticData || {};
    ensureCustomer(staticData);
    await n8nApi('PUT', `/workflows/${PORTAL_WORKFLOW_ID}`, {
      name: workflow.name,
      nodes: workflow.nodes,
      connections: workflow.connections,
      settings: workflow.settings,
      staticData,
    });
    await n8nApi('POST', `/workflows/${PORTAL_WORKFLOW_ID}/activate`, {});
  } catch (error) {
    console.log('portal staticData update failed:', error.message);
  }

  return [{ json: {
    success: true,
    purchaseCategory: 'addon',
    customerEmail,
    email: customerEmail,
    companyName: restaurantName,
    restaurantName,
    modules: addonLabel,
    amount: addonAmount.toFixed(2).replace('.', ',') + ' ' + currency,
    monthlyNetTotal: addonAmount,
    setupFeeAmount: 0,
    vatAmount: 0,
    grossTotal: addonAmount,
    currency,
    customerAddress,
    customerPhone,
    customerWebsite,
    customerVatId,
    whatsappNumber,
    addonType,
    addonLabel,
    code,
    slug,
  }}];
}

const companyName = meta.companyName || payload.customer_details?.name || customerEmail.split('@')[0] || 'Kunde';
const modules = meta.modules || 'LeoLan Digital Paket';
const monthlyNetTotal = parseFloat(meta.monthlyNetTotal) || 0;
const setupFeeAmount = parseFloat(meta.setupFeeAmount) || 349;
const vatAmount = 0;
const netTotal = monthlyNetTotal + setupFeeAmount;
const grossTotal = netTotal;
const amount = grossTotal.toFixed(2).replace('.', ',') + ' ' + currency;

return [{ json: {
  success: true,
  purchaseCategory: 'core',
  email: customerEmail,
  customerEmail,
  companyName,
  modules,
  amount,
  monthlyNetTotal,
  setupFeeAmount,
  vatAmount,
  grossTotal,
  whatsappNumber,
  currency,
  customerAddress,
  customerPhone,
  customerWebsite,
  customerVatId
}}];
'''

BREVO_PAYLOAD_CODE = r'''
const data = $input.first().json;
const customerEmail = data.email || data.customerEmail || '';
const companyName = data.companyName || customerEmail;
const purchaseCategory = data.purchaseCategory || 'core';
const modulesRaw = data.modules;
const modules = Array.isArray(modulesRaw) ? modulesRaw.map(m => m.name || String(m)).join(', ') : (modulesRaw ? String(modulesRaw) : 'Ihre Module');
const monthlyNet = parseFloat(data.monthlyNetTotal) || 0;
const setupFee = parseFloat(data.setupFeeAmount) || 0;
const vatAmount = parseFloat(data.vatAmount) || 0;
const grossTotal = parseFloat(data.grossTotal) || 0;
const dateStr = new Date().toLocaleDateString('de-DE');
if (!customerEmail) return [{ json: { skipped: true } }];

const staticData = $getWorkflowStaticData('global');
if (!staticData.invoiceCounter || staticData.invoiceCounter < 33) {
  staticData.invoiceCounter = 33;
}

let invoiceNr = null;
if (purchaseCategory !== 'addon') {
  staticData.invoiceCounter += 1;
  invoiceNr = 'LD-' + new Date().getFullYear() + '-' + String(staticData.invoiceCounter).padStart(4, '0');
}

return [{ json: {
  ...data,
  _brevo_to: customerEmail,
  _brevo_name: companyName,
  _brevo_subject: purchaseCategory === 'addon'
    ? '✅ Add-On erfolgreich gebucht — LeoLan Digital'
    : ('✅ Kaufbestätigung & Rechnung — LeoLan Digital (' + invoiceNr + ')'),
  invoiceNr,
  dateStr,
  modules,
  monthlyNetTotal: monthlyNet,
  setupFeeAmount: setupFee,
  vatAmount,
  grossTotal
} }];
'''

GENERATE_PDF_CODE = r'''
const data = $input.first().json;
if ((data.purchaseCategory || 'core') === 'addon') {
  return [{ json: { ...data, pdfBase64: null, pdfFilename: null } }];
}

let pdfBase64 = null;
try {
  const invoicePayload = JSON.stringify({
    invoice_nr: data.invoiceNr || 'LD-0000',
    date_str: data.dateStr || new Date().toLocaleDateString('de-DE'),
    company_name: data.companyName || data._brevo_name || data.customerEmail || 'Kunde',
    customer_email: data._brevo_to || data.customerEmail || '',
    modules: data.modules || '',
    monthly_net: parseFloat(data.monthlyNetTotal) || 0,
    setup_fee: parseFloat(data.setupFeeAmount) || 349,
    vat_amount: 0,
    gross_total: (parseFloat(data.monthlyNetTotal) || 0) + (parseFloat(data.setupFeeAmount) || 349),
    customer_address: data.customerAddress || '',
    customer_phone: data.customerPhone || '',
    customer_website: data.customerWebsite || '',
    customer_vat_id: data.customerVatId || '',
    service_period: data.servicePeriod || '',
    payment_terms: 'Zahlbar sofort, rein netto.'
  });

  const resp = await this.helpers.request({
    method: 'POST',
    uri: 'http://172.18.0.1:5050/generate-invoice',
    headers: { 'Content-Type': 'application/json' },
    body: invoicePayload
  });

  const result = typeof resp === 'string' ? JSON.parse(resp) : resp;
  if (result && result.pdf) {
    pdfBase64 = result.pdf;
  }
} catch (e) {
  console.log('PDF error:', e.message);
}

return [{ json: {
  ...data,
  vatAmount: 0,
  grossTotal: (parseFloat(data.monthlyNetTotal) || 0) + (parseFloat(data.setupFeeAmount) || 349),
  pdfBase64,
  pdfFilename: 'Rechnung_' + (data.invoiceNr || 'LD-0000') + '.pdf'
} }];
'''

BREVO_EMAIL_CODE = r'''
const data = $input.first().json;
const customerEmail = data._brevo_to || data.email || data.customerEmail || '';
const companyName = data.companyName || data._brevo_name || customerEmail;
const subject = data._brevo_subject || 'Kaufbestätigung LeoLan Digital';
const purchaseCategory = data.purchaseCategory || 'core';
const invoiceNr = data.invoiceNr || 'LD-0000';
const dateStr = new Date().toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
const monthlyNet = parseFloat(data.monthlyNetTotal) || 0;
const setupFee = parseFloat(data.setupFeeAmount) || 0;
const pdfBase64 = data.pdfBase64 || null;
const pdfFilename = data.pdfFilename || ('Rechnung_' + invoiceNr + '.pdf');

if (!customerEmail) return [{ json: { skipped: true } }];

let html = '';
if (purchaseCategory === 'addon') {
  const addonLabel = data.addonLabel || data.modules || 'Ihr Add-On';
  const amount = monthlyNet.toFixed(2).replace('.', ',') + ' € / Monat';
  html = `<!DOCTYPE html><html lang="de"><body style="margin:0;padding:0;background:#0d1526;font-family:Arial,sans-serif;color:#ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0d1526;padding:24px 12px;">
    <tr><td align="center">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;">
        <tr><td style="background:#f5a623;padding:16px 28px;border-radius:12px 12px 0 0;">
          <p style="margin:0;color:#1a2744;font-weight:900;font-size:13px;text-transform:uppercase;letter-spacing:2px;">Add-On aktiviert</p>
        </td></tr>
        <tr><td style="background:#1a2744;padding:34px 28px 30px;border-radius:0 0 12px 12px;">
          <h1 style="margin:0 0 10px;color:#fff;font-size:28px;line-height:1.25;">${addonLabel} erfolgreich gebucht</h1>
          <p style="margin:0 0 18px;color:#8a9bbf;font-size:15px;line-height:1.7;">Hallo <strong>${companyName}</strong>, Ihr neues Modul wurde erfolgreich über Stripe aktiviert.</p>
          <div style="background:#0d1526;border:1px solid #253655;border-radius:14px;padding:18px 20px;margin-bottom:22px;">
            <p style="margin:0 0 8px;color:#8a9bbf;font-size:12px;text-transform:uppercase;letter-spacing:1.5px;">Gebuchtes Modul</p>
            <p style="margin:0 0 4px;color:#fff;font-size:20px;font-weight:900;">${addonLabel}</p>
            <p style="margin:0;color:#f5a623;font-size:16px;font-weight:900;">${amount}</p>
          </div>
          <p style="margin:0 0 8px;color:#8ab89a;font-size:14px;line-height:1.7;">• Das Add-On ist jetzt in Ihrem Kundenkonto hinterlegt.</p>
          <p style="margin:0 0 8px;color:#8ab89a;font-size:14px;line-height:1.7;">• Abrechnung läuft automatisch über Stripe.</p>
          <p style="margin:0 0 24px;color:#8ab89a;font-size:14px;line-height:1.7;">• Bei Fragen antworten Sie einfach auf diese E-Mail.</p>
          <a href="https://ki.leolan.net/portal/" style="display:inline-block;background:#f5a623;color:#1a2744;text-decoration:none;font-weight:900;padding:14px 28px;border-radius:10px;font-size:15px;">Zum Kunden-Portal →</a>
        </td></tr>
      </table>
    </td></tr>
  </table>
  </body></html>`;
} else {
  let leistungsRows = '';
  if (monthlyNet > 0) {
    leistungsRows += `<tr style="background:#0d1526;"><td style="padding:12px 16px;color:#fff;font-size:14px;border-top:1px solid #1e2e4a;">${data.modules || 'KI-Paket'}</td><td style="padding:12px 16px;color:#8a9bbf;font-size:13px;text-align:right;border-top:1px solid #1e2e4a;">monatlich</td></tr>`;
  }
  if (setupFee > 0) {
    leistungsRows += `<tr style="background:#111d30;"><td style="padding:12px 16px;color:#fff;font-size:14px;border-top:1px solid #1e2e4a;">Setup-Gebühr (einmalig)</td><td style="padding:12px 16px;color:#8a9bbf;font-size:13px;text-align:right;border-top:1px solid #1e2e4a;">einmalig</td></tr>`;
  }

  let betragLine = '';
  if (setupFee > 0 && monthlyNet > 0) {
    betragLine = `Setup: ${setupFee.toFixed(2).replace('.', ',')} € • Monatlich: ${monthlyNet.toFixed(2).replace('.', ',')} €`;
  } else if (setupFee > 0) {
    betragLine = `Setup: ${setupFee.toFixed(2).replace('.', ',')} €`;
  } else {
    betragLine = `Monatlich: ${monthlyNet.toFixed(2).replace('.', ',')} €`;
  }

  html = `<!DOCTYPE html><html lang="de" style="background:#0d1526;"><head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta name="color-scheme" content="only light"/>
    <title>Kaufbestätigung LeoLan Digital</title>
  </head>
  <body style="margin:0;padding:0;background:#0d1526;font-family:Arial,sans-serif;color:#ffffff;" bgcolor="#0d1526">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#0d1526;padding:24px 12px;">
  <tr><td align="center">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;">
  <tr><td align="center" style="padding:32px 0 20px;">
    <img src="https://ki.leolan.net/leolan-logo.png" width="100" height="100" style="display:block;border-radius:20px;border:0;" alt="LeoLan"/>
  </td></tr>
  <tr><td style="background:#f5a623;padding:14px 28px;border-radius:8px 8px 0 0;">
    <p style="margin:0;color:#1a2744;font-weight:900;font-size:13px;text-transform:uppercase;letter-spacing:2px;">✓ KAUFBESTÄTIGUNG & RECHNUNG</p>
  </td></tr>
  <tr><td style="background:#1a2744;padding:32px 28px 24px;">
    <h1 style="margin:0 0 6px;color:#fff;font-size:26px;line-height:1.3;font-weight:900;">Vielen Dank für Ihre Bestellung!</h1>
    <p style="margin:0 0 24px;color:#8a9bbf;font-size:14px;">LeoLan Digital · KI-Automatisierung für Gastronomie & Hotellerie</p>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:28px;">
    <tr>
      <td style="width:33%;padding-right:8px;border-right:1px solid #2d3e60;">
        <p style="margin:0 0 4px;color:#8a9bbf;font-size:10px;text-transform:uppercase;letter-spacing:1px;">Rechnungsnr.</p>
        <p style="margin:0;color:#f5a623;font-size:14px;font-weight:900;">${invoiceNr}</p>
      </td>
      <td style="width:33%;padding:0 8px;border-right:1px solid #2d3e60;">
        <p style="margin:0 0 4px;color:#8a9bbf;font-size:10px;text-transform:uppercase;letter-spacing:1px;">Datum</p>
        <p style="margin:0;color:#fff;font-size:14px;font-weight:700;">${dateStr}</p>
      </td>
      <td style="width:33%;padding-left:8px;">
        <p style="margin:0 0 4px;color:#8a9bbf;font-size:10px;text-transform:uppercase;letter-spacing:1px;">Status</p>
        <p style="margin:0;color:#2dd881;font-size:14px;font-weight:900;">✓ Bezahlt</p>
      </td>
    </tr>
    </table>
    <p style="margin:0 0 8px;color:#fff;font-size:15px;">Hallo <strong>${companyName}</strong>,</p>
    <p style="margin:0 0 6px;color:#8a9bbf;font-size:14px;line-height:1.7;">Ihre Bestellung wurde erfolgreich aufgenommen. Wir richten Ihr System innerhalb von <strong style="color:#f5a623;">48 Stunden</strong> ein.</p>
    <p style="margin:0 0 28px;color:#8a9bbf;font-size:14px;line-height:1.7;">Sie erhalten Ihre Zugangsdaten und alle weiteren Informationen automatisch per E-Mail.</p>
    <p style="margin:0 0 10px;color:#8a9bbf;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;">Gebuchte Leistungen</p>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:24px;border-radius:10px;overflow:hidden;">
      <tr style="background:#243250;">
        <td style="padding:10px 16px;color:#f5a623;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:1.5px;width:70%;">Leistung</td>
        <td style="padding:10px 16px;color:#f5a623;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:1.5px;text-align:right;">Info</td>
      </tr>
      ${leistungsRows}
    </table>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom:24px;">
    <tr><td style="background:#0d1526;border-radius:10px;padding:14px 18px;">
      <p style="margin:0 0 4px;color:#8a9bbf;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;">Gesamtbetrag</p>
      <p style="margin:0;color:#f5a623;font-size:16px;font-weight:900;">${betragLine}</p>
    </td></tr>
    </table>
    <div style="background:#0d2a1a;border:1px solid #1a5c35;border-radius:10px;padding:18px 20px;margin-bottom:24px;">
      <p style="margin:0 0 12px;color:#2dd881;font-size:15px;font-weight:900;">Wie geht es weiter?</p>
      <p style="margin:0 0 6px;color:#8ab89a;font-size:13px;line-height:1.7;">1. Wir richten Ihren WhatsApp-Bot innerhalb von 48 Stunden ein.</p>
      <p style="margin:0 0 6px;color:#8ab89a;font-size:13px;line-height:1.7;">2. Sie erhalten Login-Daten für Ihr persönliches Dashboard.</p>
      <p style="margin:0;color:#8ab89a;font-size:13px;line-height:1.7;">3. Unser Team begleitet Sie durch den Start — bei Fragen sind wir sofort da.</p>
    </div>
    <a href="https://ki.leolan.net" style="display:inline-block;background:#f5a623;color:#1a2744;text-decoration:none;font-weight:900;padding:14px 28px;border-radius:10px;font-size:15px;">Zu Ihrem Dashboard →</a>
  </td></tr>
  <tr><td style="background:#0a1020;padding:18px 28px;border-radius:0 0 8px 8px;">
    <p style="margin:0 0 4px;color:#fff;font-size:13px;font-weight:700;">LeoLan Digital</p>
    <p style="margin:0;color:#56677f;font-size:12px;line-height:1.7;">Kamaleddin Nazari · Reicker Straße 132 · 01237 Dresden<br/>business@leolan.net · ki.leolan.net<br/>Steuernr.: 203/252/14709 · USt-IdNr.: DE351138587</p>
  </td></tr>
  </table>
  </td></tr>
  </table>
  </body></html>`;
}

const emailPayload = {
  sender: { name: 'LeoLan Digital', email: 'business@leolan.net' },
  to: [{ email: customerEmail, name: companyName }],
  bcc: [{ email: 'business@leolan.net' }],
  subject,
  htmlContent: html,
};

if (pdfBase64) {
  emailPayload.attachment = [{ name: pdfFilename, content: pdfBase64 }];
}

const resp = await this.helpers.request({
  method: 'POST',
  uri: 'https://api.brevo.com/v3/smtp/email',
  headers: {
    'api-key': '__BREVO_KEY__',
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(emailPayload),
});

const result = typeof resp === 'string' ? JSON.parse(resp) : resp;
return [{ json: { ...data, brevoSent: true, messageId: result.messageId, pdfAttached: !!pdfBase64 } }];
'''


ADDON_HANDLER_CODE = ADDON_HANDLER_CODE.replace('__STRIPE_SECRET__', STRIPE_SECRET)
BUILD_INVOICE_CODE = BUILD_INVOICE_CODE.replace('__N8N_API_KEY__', API_KEY)
BREVO_EMAIL_CODE = BREVO_EMAIL_CODE.replace('__BREVO_KEY__', BREVO_KEY)


def api(path, method='GET', payload=None):
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={
            'X-N8N-API-KEY': API_KEY,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode('utf-8')
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'{method} {path} failed: {e.code} {body}')


def update_portal_workflow():
    wf = api(f'/workflows/{PORTAL_WORKFLOW_ID}')
    wf['name'] = 'Portal Add-On Checkout'
    for node in wf['nodes']:
        if node['id'] == 'ug1':
            node['name'] = 'Portal Add-On Webhook'
            node['parameters']['path'] = 'portal-addon'
        elif node['id'] == 'ug2':
            node['name'] = 'Portal Add-On Status Webhook'
            node['parameters']['path'] = 'portal-addon-status'
        elif node['id'] == 'ug3':
            node['name'] = 'Portal Add-On Stripe Legacy'
            node['parameters']['path'] = 'portal-addon-stripe'
        elif node['id'] == 'ug4':
            node['name'] = 'Handle Add-On Checkout'
            node['parameters']['jsCode'] = ADDON_HANDLER_CODE
        elif node['id'] == 'ug5':
            node['name'] = 'Portal Add-On Response'
    wf['connections'] = {
        'Portal Add-On Webhook': {'main': [[{'node': 'Handle Add-On Checkout', 'type': 'main', 'index': 0}]]},
        'Portal Add-On Status Webhook': {'main': [[{'node': 'Handle Add-On Checkout', 'type': 'main', 'index': 0}]]},
        'Portal Add-On Stripe Legacy': {'main': [[{'node': 'Handle Add-On Checkout', 'type': 'main', 'index': 0}]]},
        'Handle Add-On Checkout': {'main': [[{'node': 'Portal Add-On Response', 'type': 'main', 'index': 0}]]},
    }
    payload = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': wf['settings'],
        'staticData': wf.get('staticData'),
    }
    api(f'/workflows/{PORTAL_WORKFLOW_ID}', 'PUT', payload)
    api(f'/workflows/{PORTAL_WORKFLOW_ID}/activate', 'POST', {})


def update_stripe_webhook():
    wf = api(f'/workflows/{STRIPE_WEBHOOK_ID}')
    for node in wf['nodes']:
        if node['name'] == 'Build Invoice':
            node['parameters']['jsCode'] = BUILD_INVOICE_CODE
        elif node['name'] == 'Brevo Payload vorbereiten':
            node['parameters']['jsCode'] = BREVO_PAYLOAD_CODE
        elif node['name'] == 'Generate PDF':
            node['parameters']['jsCode'] = GENERATE_PDF_CODE
        elif node['name'] == 'Brevo Email Code':
            node['parameters']['jsCode'] = BREVO_EMAIL_CODE
    payload = {
        'name': wf['name'],
        'nodes': wf['nodes'],
        'connections': wf['connections'],
        'settings': wf['settings'],
        'staticData': wf.get('staticData'),
    }
    api(f'/workflows/{STRIPE_WEBHOOK_ID}', 'PUT', payload)
    api(f'/workflows/{STRIPE_WEBHOOK_ID}/activate', 'POST', {})


if __name__ == '__main__':
    if not all([API_KEY, STRIPE_SECRET, BREVO_KEY]):
        raise SystemExit('Bitte LEOLAN_N8N_API_KEY, LEOLAN_STRIPE_SECRET und LEOLAN_BREVO_KEY setzen.')
    update_portal_workflow()
    update_stripe_webhook()
    print('OK: Portal Add-On Checkout + Stripe Webhook aktualisiert')
