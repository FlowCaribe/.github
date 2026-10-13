/* Local visual QA. Requires marked and playwright; never uploads README content. */
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { marked } = require('marked');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const output = path.resolve(process.env.PROFILE_PREVIEW_DIR || path.join(root, '.preview'));
fs.mkdirSync(output, { recursive: true });
const cssPath = path.join(root, '.preview', 'github-markdown.css');
if (!fs.existsSync(cssPath)) throw new Error('Place github-markdown.css in .preview/; see maintenance.md.');
const css = fs.readFileSync(cssPath, 'utf8');
const expectedTeamCount = JSON.parse(fs.readFileSync(path.join(root, 'profile', 'profile.json'), 'utf8')).developers.length;
const rendered = marked.parse(fs.readFileSync(path.join(root, 'README.md'), 'utf8'), { gfm: true });
const shell = `<!doctype html><html lang="es"><head><meta charset="utf-8"><base href="../"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Flow Caribe RP · README preview</title><style>${css}
body{margin:0;background:#fff}@media(prefers-color-scheme:dark){body{background:#0d1117}}.markdown-body{box-sizing:border-box;max-width:1012px;margin:32px auto;padding:32px;border:1px solid var(--borderColor-default,#d1d9e0);border-radius:12px}a:focus-visible{outline:2px solid #A775EA;outline-offset:4px}img{vertical-align:top}@media(max-width:767px){.markdown-body{margin:0;padding:24px;border:0;border-radius:0}}@media(max-width:360px){.markdown-body{padding:16px}}
</style></head><body><article class="markdown-body">${rendered}</article></body></html>`;
fs.writeFileSync(path.join(output, 'index.html'), shell);
const types = { '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.html': 'text/html; charset=utf-8' };
const server = http.createServer((request, response) => {
  const requested = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
  if (requested === '/') { response.setHeader('Content-Type', types['.html']); response.end(shell); return; }
  const target = path.resolve(root, '.' + requested);
  if (!target.startsWith(root + path.sep) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
    response.writeHead(404); response.end('Not found'); return;
  }
  response.setHeader('Content-Type', types[path.extname(target)] || 'application/octet-stream');
  fs.createReadStream(target).pipe(response);
});

function filesIn(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const item = path.join(dir, entry.name);
    return entry.isDirectory() ? filesIn(item) : [item];
  });
}

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({ headless: true, ...(process.env.PROFILE_CHROMIUM_PATH ? { executablePath: process.env.PROFILE_CHROMIUM_PATH } : {}) });
  try {
    const report = { renderer: 'marked (GFM) + local GitHub Markdown CSS', browser: browser.version(), viewports: [], textOverflow: [] };
    const page = await browser.newPage({ deviceScaleFactor: 1 });
    for (const theme of ['dark', 'light']) {
      await page.emulateMedia({ colorScheme: theme, reducedMotion: 'reduce' });
      for (const width of [1440, 900, 390, 320]) {
        await page.setViewportSize({ width, height: 1000 });
        await page.goto(base, { waitUntil: 'networkidle' });
        const metrics = await page.evaluate(() => ({
          overflow: document.documentElement.scrollWidth > innerWidth,
          images: [...document.images].map(img => ({ src: new URL(img.currentSrc).pathname, loaded: img.complete && img.naturalWidth > 0, width: img.getBoundingClientRect().width, height: img.getBoundingClientRect().height, top:img.getBoundingClientRect().top, bottom:img.getBoundingClientRect().bottom })),
          links: document.querySelectorAll('a').length,
          tables: document.querySelectorAll('table').length,
        }));
        if (metrics.overflow || metrics.images.some(img => !img.loaded)) throw new Error(`Failed layout or image at ${width}px/${theme}`);
        const team = metrics.images.filter(img => img.src.includes('/team/'));
        if (team.length !== expectedTeamCount || team.some(card => Math.abs(team[0].width-card.width)>1 || Math.abs(team[0].height-card.height)>1)) throw new Error('Unequal developer cards');
        if (team.some((card,index)=>index>0 && card.top<team[index-1].bottom)) throw new Error('Discord cards must be stacked vertically');
        await page.screenshot({ path: path.join(output, `${theme}-${width}.png`), fullPage: true });
        report.viewports.push({ theme, width, ...metrics });
      }
    }
    for (const file of filesIn(path.join(root, 'profile', 'assets')).filter(file => file.endsWith('.svg'))) {
      const relative = path.relative(root, file).split(path.sep).join('/');
      await page.goto(`${base}/${relative}`);
      const issues = await page.evaluate(() => {
        const box = document.documentElement.viewBox.baseVal;
        return [...document.querySelectorAll('text')].flatMap(text => {
          const b = text.getBBox();
          return b.x < -1 || b.y < -1 || b.x + b.width > box.width + 1 || b.y + b.height > box.height + 1 ? [{ text: text.textContent, x: b.x, y: b.y, width: b.width, height: b.height }] : [];
        });
      });
      report.textOverflow.push(...issues.map(issue => ({ file: relative, ...issue })));
    }
    fs.writeFileSync(path.join(output, 'qa.json'), JSON.stringify(report, null, 2));
    if (report.textOverflow.length) throw new Error(`Text overflow in ${report.textOverflow.length} SVG labels; see qa.json.`);
    console.log(`Verified 8 viewport/theme combinations, ${filesIn(path.join(root, 'profile', 'assets')).filter(file => file.endsWith('.svg')).length} SVG text bounds, ${expectedTeamCount} equal team cards and loaded assets. Screenshots: ${output}`);
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); server.close(); process.exitCode = 1; });
