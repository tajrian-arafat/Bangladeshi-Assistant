#!/usr/bin/env node
/**
 * Batch 3C gap closure — browser-rendered BSP/BRTA official source capture.
 * Targets: fitness, tax token, route permit, advance income tax, vehicle modifications,
 * BSP hub/calculator/roadSafety, MV tax portal.
 */
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const OUT_DIR = path.join(
  __dirname,
  '../data/research/verification/batch-03c-brta-fitness-tax-permit-gap-closure/source_snapshots'
);
const CHROME = process.env.CHROME_PATH || '/usr/local/bin/google-chrome';

const TARGETS = [
  {
    id: 'brta_fitness',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922db91933eb65569e0af12',
    waitMs: 15000,
  },
  {
    id: 'brta_tax_token',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922e0ab933eb65569e281ad',
    waitMs: 15000,
  },
  {
    id: 'brta_route_permit',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922df7a933eb65569e2240e',
    waitMs: 15000,
  },
  {
    id: 'brta_advance_income_tax',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922e058933eb65569e269cd',
    waitMs: 15000,
  },
  {
    id: 'brta_color_change',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922dd3a933eb65569e14058',
    waitMs: 15000,
  },
  {
    id: 'brta_engine_change',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922dfbe933eb65569e23c89',
    waitMs: 15000,
  },
  {
    id: 'brta_tire_size_change',
    url: 'http://brta.portal.gov.bd/pages/static-pages/6922dcdf933eb65569e127ec',
    waitMs: 15000,
  },
  { id: 'bsp_fee_calculator', url: 'https://bsp.brta.gov.bd/feeCalculator', waitMs: 12000 },
  { id: 'bsp_home', url: 'https://bsp.brta.gov.bd/bsp/?lan=en', waitMs: 8000 },
  { id: 'bsp_road_safety', url: 'https://bsp.brta.gov.bd/roadSafety', waitMs: 8000 },
  { id: 'mv_tax_portal', url: 'https://brta.cnsbd.com/mvtax_brta', waitMs: 12000 },
];

function sha256(text) {
  return crypto.createHash('sha256').update(text || '', 'utf8').digest('hex');
}

async function scrapeTarget(page, target) {
  const result = {
    id: target.id,
    url: target.url,
    canonical_url: target.url,
    http_status: null,
    availability: 'UNKNOWN',
    retrieval_method: 'puppeteer_headless_chrome',
    retrieved_at: new Date().toISOString(),
    title: null,
    visible_text: '',
    inner_text_length: 0,
    content_hash: null,
    snapshot_html: `${target.id}.html`,
    snapshot_txt: `${target.id}.txt`,
    error: null,
    cms_body_empty: null,
    page_heading: null,
  };

  try {
    const response = await page.goto(target.url, { waitUntil: 'networkidle2', timeout: 90000 });
    result.http_status = response ? response.status() : null;
    await new Promise((r) => setTimeout(r, target.waitMs));
    result.title = await page.title();
    result.visible_text = await page.evaluate(() => document.body?.innerText || '');
    result.inner_text_length = result.visible_text.length;
    result.content_hash = sha256(result.visible_text);

    const meta = await page.evaluate(() => {
      const text = document.body?.innerText || '';
      const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
      const headingCandidates = lines.filter(
        (l) =>
          l.length > 2 &&
          l.length < 80 &&
          !/^(কন্টেন্ট|Content|বাংলাদেশ|অফিস|Office|Skip|Accessibility)/i.test(l)
      );
      const cmsEmpty =
        /(?:^|\n)(?:কন্টেন্ট:\s*পাতা|Content:\s*Pages?)(?:\n|$)/i.test(text) &&
        !/(?:ধাপ|step|required document|প্রয়োজনীয়)/i.test(text);
      return {
        cms_body_empty: cmsEmpty,
        page_heading: headingCandidates.length ? headingCandidates[headingCandidates.length - 1] : null,
      };
    });
    result.cms_body_empty = meta.cms_body_empty;
    result.page_heading = meta.page_heading;

    if (result.http_status === 404) {
      result.availability = 'TEMPORARILY_UNAVAILABLE';
    } else if (result.http_status >= 500) {
      result.availability = 'CURRENTLY_UNAVAILABLE';
    } else if (result.http_status >= 400) {
      result.availability = 'TEMPORARILY_UNAVAILABLE';
    } else if (result.inner_text_length < 120) {
      result.availability = 'JS_SHELL_ONLY';
    } else {
      result.availability = 'RENDERED';
    }
  } catch (err) {
    result.error = String(err.message || err);
    result.availability = 'FETCH_FAILED';
  }

  const html = await page.content().catch(() => '');
  fs.writeFileSync(path.join(OUT_DIR, result.snapshot_html), html, 'utf8');
  fs.writeFileSync(path.join(OUT_DIR, result.snapshot_txt), result.visible_text || '', 'utf8');
  result.content_hash_html = sha256(html);
  return result;
}

async function tryFeeCalculator(page) {
  const out = {
    id: 'bsp_fee_calculator_interaction',
    retrieval_method: 'puppeteer_interaction_probe',
    retrieved_at: new Date().toISOString(),
    captured: false,
    samples: [],
    note: null,
  };
  try {
    await page.goto('https://bsp.brta.gov.bd/feeCalculator', { waitUntil: 'networkidle2', timeout: 90000 });
    await new Promise((r) => setTimeout(r, 8000));
    const body = await page.evaluate(() => document.body?.innerText || '');
    if (/404|not found/i.test(body)) {
      out.note = 'Fee calculator returned 404 — BSP outside operating hours or path gated';
      return out;
    }
    const selects = await page.$$('select');
    out.select_count = selects.length;
    if (selects.length === 0) {
      out.note = 'No select elements found; calculator may require login or different UI';
      return out;
    }
    const probe = await page.evaluate(() => {
      const selects = Array.from(document.querySelectorAll('select'));
      return selects.map((s, i) => ({
        index: i,
        name: s.name || s.id || `select_${i}`,
        options: Array.from(s.options)
          .slice(0, 8)
          .map((o) => o.textContent?.trim())
          .filter(Boolean),
      }));
    });
    out.samples = probe;
    out.captured = probe.length > 0;
  } catch (err) {
    out.note = String(err.message || err);
  }
  return out;
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
      '--window-size=1400,1000',
    ],
  });

  const results = [];
  for (const target of TARGETS) {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    );
    console.log(`Scraping ${target.id} ...`);
    results.push(await scrapeTarget(page, target));
    await page.close();
  }

  const feePage = await browser.newPage();
  await feePage.setUserAgent(
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  );
  const feeProbe = await tryFeeCalculator(feePage);
  await feePage.close();
  await browser.close();

  const payload = { targets: results, fee_calculator_probe: feeProbe };
  fs.writeFileSync(path.join(OUT_DIR, 'scrape_results.json'), JSON.stringify(payload, null, 2), 'utf8');
  console.log(
    JSON.stringify(
      results.map((r) => ({
        id: r.id,
        status: r.http_status,
        availability: r.availability,
        text_len: r.inner_text_length,
        cms_body_empty: r.cms_body_empty,
        heading: r.page_heading?.slice(0, 60),
        title: r.title?.slice(0, 80),
      })),
      null,
      2
    )
  );
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
