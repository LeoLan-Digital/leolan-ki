# LeoLan Website SEO + Build Plan

> Coding/implementation owner: GLM-5.1. Hermes coordinates, audits, reviews and verifies. No git push or deploy without Leo's explicit approval.

**Repo:** `/Users/leo/LeoLan-Digital`  
**Remote:** `https://github.com/LeoLan-Digital/leolan-ki.git`  
**Live canonical domain:** `https://ki.leolan.net/`  
**Problem discovered:** `https://leolan.net/` currently returns Shopify/402 and robots `Disallow: /`, while `ki.leolan.net` is live and indexable.

---

## Current audit snapshot

### Good
- `ki.leolan.net` live: home, robots, sitemap, llms.txt, pricing.md all return 200.
- `robots.txt` allows normal crawlers and AI bots: GPTBot, ChatGPT-User, PerplexityBot, ClaudeBot, anthropic-ai, Google-Extended, Bingbot.
- `llms.txt` exists and describes LeoLan for AI search.
- `pricing.md` exists and is parseable for AI agents.
- Homepage has one H1, meta description, OG/Twitter tags, 7 JSON-LD blocks, image alt text.
- Sitemap exists and includes hreflang for main DE pages.

### Critical issues
1. **Main domain problem:** `https://leolan.net/` is unavailable/Shopify `402 Payment Required` and robots says `Disallow: /`.
   - Impact: brand domain can look dead or blocked to Google/users/AI.
   - Fix: decide whether `leolan.net` should 301 redirect to `https://ki.leolan.net/` or serve the same site.

2. **Sitemap/AI files incomplete:** `llms.txt` and `pricing.md` are not listed in `sitemap.xml`.
   - Impact: AI/search discovery weaker.
   - Fix: add both files to sitemap as canonical resources.

3. **Hreflang reciprocity incomplete:** sitemap has hreflang alternates on DE parent URLs, but locale URLs mostly have no reciprocal alternates.
   - Impact: Google can ignore hreflang clusters.
   - Fix: add reciprocal hreflang blocks for all locale URLs or simplify locales until complete.

4. **Onboarding/Enterprise schema missing:** key conversion pages have no JSON-LD.
   - Impact: weaker AI/Google understanding for offer/pricing/service pages.
   - Fix: add Product/Service/Offer/FAQ schema where appropriate.

5. **Homepage title too long:** 83 chars.
   - Impact: SERP truncation.
   - Fix: shorten to ~55-60 chars.

---

## Build direction

### Phase 1 — SEO foundation fixes

#### Task 1: Main domain decision
- Decide with Leo: `leolan.net` should likely redirect to `ki.leolan.net`.
- No DNS/Cloudflare/Shopify change without explicit approval.
- Prepare redirect plan only.

#### Task 2: Sitemap upgrade
Files:
- Modify: `sitemap.xml`

Add:
- `https://ki.leolan.net/llms.txt`
- `https://ki.leolan.net/pricing.md`

Verify:
```bash
curl -I https://ki.leolan.net/llms.txt
curl -I https://ki.leolan.net/pricing.md
```

#### Task 3: Hreflang repair
Files:
- Modify: `sitemap.xml`
- Potentially locale HTML files under `en/`, `tr/`, `ru/`, `id/`, `th/`

Approach:
- Each locale URL should list itself and every equivalent alternate.
- Include `x-default`.
- Ensure canonical URL appears in same hreflang set.

#### Task 4: Metadata cleanup
Files:
- Modify: `index.html`
- Modify: `onboarding.html`
- Modify: `enterprise/index.html`
- Modify: `ueber-uns.html`

Fixes:
- Shorten homepage title.
- Add meta description where missing/weak.
- Fix visible copy spacing bugs like `echteProbleme`, `—weil`, `verpasst,geht`.

### Phase 2 — AI SEO / structured data

#### Task 5: Add schema to key pages
Files:
- `onboarding.html`: Service + OfferCatalog + FAQPage
- `enterprise/index.html`: Service + Offer + FAQPage
- `ueber-uns.html`: Person/Organization/AboutPage
- `alternatives/index.html`: Comparison/FAQ schema if not already sufficient

Verify with rendered DOM, not only static curl:
```js
document.querySelectorAll('script[type="application/ld+json"]').length
```

#### Task 6: Upgrade llms.txt
Files:
- Modify: `llms.txt`

Add direct links:
- Homepage
- Pricing markdown
- Onboarding
- Alternatives
- Enterprise
- App Store link
- Contact/onboarding CTA

### Phase 3 — Build pages that can rank

Recommended new/expanded SEO pages:

1. `/whatsapp-bot-restaurant/`
   - Keyword: WhatsApp Bot Restaurant
   - Intent: buyer/problem aware

2. `/ki-restaurant/`
   - Keyword: KI Restaurant / KI für Restaurants
   - Intent: education + conversion

3. `/restaurant-reservierung-automatisieren/`
   - Keyword: Restaurant Reservierung automatisieren
   - Intent: direct pain point

4. `/google-bewertungen-restaurant-automatisieren/`
   - Keyword: Google Bewertungen Restaurant automatisch beantworten
   - Intent: service-specific

5. `/speisekarte-qr-code-restaurant/`
   - Keyword: QR Code Speisekarte Restaurant
   - Intent: lead magnet / entry offer

Each page should include:
- 1 clear H1
- 50-60 char title
- 145-160 char meta description
- direct answer block in first 60 words
- FAQ section
- Service/FAQ schema
- internal links to `/onboarding/`, `/pricing.md`, `/alternatives/`

### Phase 4 — Verification

Run locally:
```bash
cd /Users/leo/LeoLan-Digital
python3 -m http.server 8088
curl -I http://127.0.0.1:8088/
curl -I http://127.0.0.1:8088/sitemap.xml
curl -I http://127.0.0.1:8088/llms.txt
curl -I http://127.0.0.1:8088/pricing.md
```

Run checks:
- HTML parses without missing closing major tags.
- All canonical URLs use `https://ki.leolan.net/...`.
- All sitemap URLs return 200 on live after deployment.
- No new page is orphaned.
- No git push/deploy until Leo says explicitly.

---

## GLM-5.1 execution handoff

Prompt for GLM-5.1:

```text
You are GLM-5.1 coding agent. Work in /Users/leo/LeoLan-Digital. Implement Phase 1 and Phase 2 only from docs/plans/2026-05-18-leolan-website-seo-build-plan.md. Do not git push, deploy, edit DNS, or touch external services. Make local file changes only. Preserve existing design. After changes, run local verification commands and report changed files, test output, and any remaining risks.
```

---

## Explicit approval needed from Leo

Before any of these:
- Git push
- Deploy / Cloudflare Pages / hosting publish
- DNS/Cloudflare/Shopify redirect for `leolan.net`
- App/build/submission actions
