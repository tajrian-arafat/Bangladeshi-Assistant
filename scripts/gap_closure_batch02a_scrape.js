#!/usr/bin/env node
/**
 * Batch 2A gap closure — browser-rendered official source capture.
 * Uses system Chrome via puppeteer-core. Does not bypass auth.
 */
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const OUT_DIR = path.join(__dirname, '../data/research/verification/batch-02a-passport-gap-closure/source_snapshots');
const CHROME = process.env.CHROME_PATH || '/usr/local/bin/google-chrome';

const TARGETS = [
  { id: 'epassport_fees', url: 'https://www.epassport.gov.bd/instructions/passport-fees', waitMs: 12000 },
  { id: 'epassport_fees_nwww', url: 'https://epassport.gov.bd/instructions/passport-fees', waitMs: 12000 },
  { id: 'epassport_landing', url: 'https://epassport.gov.bd/landing', waitMs: 8000 },
  { id: 'epassport_status', url: 'https://www.epassport.gov.bd/application-status', waitMs: 10000 },
  { id: 'epassport_onboarding', url: 'https://www.epassport.gov.bd/onboarding', waitMs: 10000 },
  { id: 'epassport_instructions', url: 'https://www.epassport.gov.bd/instructions/instructions', waitMs: 12000 },
  { id: 'abudhabi_mission', url: 'https://abudhabi.mofa.gov.bd/', waitMs: 10000 },
  { id: 'abudhabi_epassport', url: 'https://abudhabi.mofa.gov.bd/en/site/page/E-passport', waitMs: 10000 },
  { id: 'singapore_mission', url: 'https://singapore.mofa.gov.bd/', waitMs: 10000 },
  { id: 'singapore_epassport_alt', url: 'https://singapore.mofa.gov.bd/en/site/page/e-passport', waitMs: 10000 },
  { id: 'mrp_home', url: 'http://passport.gov.bd/', waitMs: 8000 },
  { id: 'mrp_status', url: 'http://passport.gov.bd/OnlineStatus.aspx', waitMs: 8000 },
  { id: 'dip_home', url: 'https://www.dip.gov.bd/', waitMs: 8000 },
  { id: 'police_charter', url: 'https://www.police.gov.bd/en/citizen_charter', waitMs: 8000 },
  { id: 'police_charter_bn', url: 'https://www.police.gov.bd/citizen_charter', waitMs: 8000 },
];

async function scrapeTarget(page, target, networkLog) {
  const result = {
    id: target.id,
    url: target.url,
    http_status: null,
    retrieval_method: 'puppeteer_headless_chrome',
    retrieved_at: new Date().toISOString(),
    title: null,
    visible_text: null,
    inner_text_length: 0,
    api_calls: [],
    error: null,
  };

  try {
    const response = await page.goto(target.url, {
      waitUntil: 'networkidle2',
      timeout: 60000,
    });
    result.http_status = response ? response.status() : null;
    await new Promise((r) => setTimeout(r, target.waitMs));
    result.title = await page.title();
    result.visible_text = await page.evaluate(() => document.body?.innerText || '');
    result.inner_text_length = result.visible_text.length;
    result.api_calls = networkLog.filter((n) =>
      /epassport|passport|fee|payment|api/i.test(n.url)
    ).slice(0, 50);
  } catch (err) {
    result.error = String(err.message || err);
  }

  const html = await page.content().catch(() => '');
  fs.writeFileSync(path.join(OUT_DIR, `${target.id}.html`), html, 'utf8');
  fs.writeFileSync(path.join(OUT_DIR, `${target.id}.txt`), result.visible_text || '', 'utf8');
  return result;
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--window-size=1280,900',
    ],
  });

  const results = [];
  for (const target of TARGETS) {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );
    const networkLog = [];
    page.on('response', async (resp) => {
      try {
        const url = resp.url();
        const ct = resp.headers()['content-type'] || '';
        if (/json|text\/plain|javascript/i.test(ct) || /api|fee|passport/i.test(url)) {
          let bodyPreview = null;
          if (/json/i.test(ct)) {
            try {
              const txt = await resp.text();
              bodyPreview = txt.slice(0, 4000);
            } catch (_) {}
          }
          networkLog.push({ url, status: resp.status(), content_type: ct, body_preview: bodyPreview });
        }
      } catch (_) {}
    });

    console.log(`Scraping ${target.id} ...`);
    const result = await scrapeTarget(page, target, networkLog);
    results.push(result);
    await page.close();
  }

  await browser.close();
  fs.writeFileSync(
    path.join(OUT_DIR, 'scrape_results.json'),
    JSON.stringify(results, null, 2),
    'utf8'
  );
  console.log(JSON.stringify(results.map((r) => ({
    id: r.id,
    status: r.http_status,
    text_len: r.inner_text_length,
    error: r.error,
    api_count: r.api_calls.length,
  })), null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
