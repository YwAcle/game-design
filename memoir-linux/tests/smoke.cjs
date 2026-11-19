const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const url = pathToFileURL(path.join(root, 'index.html')).href;
const storageKey = 'hogwarts-always-v1';
const errors = [];
let checks = 0;
function check(condition, message) { assert.ok(condition, message); checks++; console.log('PASS', message); }

async function fillStory(page, body = '那个等我一起上课的人，我还记得你。\n<img src=x onerror=alert(1)>') {
  await page.locator('#author-input').fill('小巫师');
  await page.locator('[name=title]').fill('那个等我上线的人');
  await page.locator('#memory-body').fill(body);
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    const remoteRequests = [];
    page.on('request', request => { if (/^https?:/.test(request.url())) remoteRequests.push(request.url()); });
    await page.goto(url);
    await page.waitForTimeout(600);
    check(await page.title() === '魔法留声 · Hogwarts, Always', 'file:// opens without a server');
    check(await page.locator('a[href="explore.html"]').count() === 0, 'no map entrance remains in the memoir');
    check(await page.locator('.hero-buttons .button-gold').getAttribute('href') === '#memories', 'primary action opens the memoir');
    await page.locator('.hero-buttons [data-open-write]').click();
    check(await page.locator('#write-dialog').isVisible(), 'hero write action opens the memory editor');
    await page.keyboard.press('Escape');
    check(await page.locator('.memory-card').count() === 3, 'three clearly labeled inspiration stories render');
    check(remoteRequests.length === 0, 'the app loads without remote requests');
    check(await page.evaluate(() => document.documentElement.scrollWidth === innerWidth), 'desktop has no horizontal overflow');
    console.log('RENDERER', await page.locator('#render-note').textContent());
    check((await page.locator('#render-note').textContent()).includes('WebGL'), 'WebGL particle renderer initializes');
    await page.mouse.move(940, 280);
    await page.waitForTimeout(200);
    check(await page.locator('#magic-canvas').evaluate(canvas => canvas.width === 1440 && canvas.height === 1000), 'render surface matches viewport');
    await page.screenshot({ path: path.join(root, 'preview-desktop.png'), fullPage: true });

    await page.locator('[data-scene="1"]').click();
    check(await page.locator('#scene-name').textContent() === '廊桥 · 再等一场日落', 'scene thumbnail changes the scene and caption');
    check(await page.locator('[data-scene="1"]').getAttribute('aria-pressed') === 'true', 'scene selection exposes its state');
    await page.locator('#lumos-toggle').click();
    check(await page.locator('body').evaluate(body => body.classList.contains('lumos')), 'Lumos lights the scene');
    await page.locator('#snitch').click({ force: true });
    check(await page.locator('#snitch').evaluate(node => node.classList.contains('caught')), 'golden snitch can be caught');
    await page.locator('#sound-toggle').click();
    check(await page.locator('#sound-toggle').getAttribute('aria-pressed') === 'true', 'sound starts only after interaction');
    await page.locator('#sound-toggle').click();

    await page.locator('[data-house="ravenclaw"]').click();
    check((await page.locator('#house-message').textContent()).includes('拉文克劳'), 'house choice updates the welcome');
    await page.locator('[data-open-write]').first().click();
    check(await page.locator('#house-input').inputValue() === 'ravenclaw', 'letter inherits the selected house');
    await fillStory(page, '   ');
    await page.locator('.submit-memory').click();
    check(await page.locator('#form-error').isVisible(), 'whitespace-only stories are rejected');
    await fillStory(page);
    await page.keyboard.press('Escape');
    await page.locator('[data-open-write]').first().click();
    check((await page.locator('#memory-body').inputValue()).includes('我还记得你'), 'closing the dialog preserves the draft');
    await page.locator('.submit-memory').click();
    check(!await page.locator('#write-dialog').isVisible(), 'valid story saves and closes the editor');
    check(await page.locator('.memory-card').count() === 1, 'new story appears under my stories');
    check(await page.locator('.memory-title').textContent() === '那个等我上线的人', 'saved title renders');
    check(await page.locator('.memory-excerpt img').count() === 0, 'user content is rendered as text, not HTML');
    await page.locator('.favorite-button').click();
    await page.reload();
    check(await page.locator('[data-house="ravenclaw"]').getAttribute('aria-pressed') === 'true', 'house persists after reload');
    check(await page.locator('.memory-card').count() === 4, 'story persists after reload');
    await page.locator('[data-filter="favorites"]').click();
    check(await page.locator('.memory-card').count() === 1, 'favorite persists and filters correctly');
    await page.locator('.memory-open').click();
    check((await page.locator('#detail-body').textContent()).includes('<img src=x'), 'detail preserves literal punctuation and markup');
    const pngPromise = page.waitForEvent('download');
    await page.locator('#postcard-button').click();
    const png = await pngPromise;
    const pngData = await fs.readFile(await png.path());
    check(pngData.subarray(1, 4).toString() === 'PNG' && pngData.readUInt32BE(16) === 1080, 'PNG keepsake exports from file:// at full resolution');
    await png.saveAs(path.join(require('node:os').tmpdir(), 'hogwarts-test-keepsake.png'));
    await page.keyboard.press('Escape');
    const backupPromise = page.waitForEvent('download');
    await page.locator('#backup-button').click();
    const backup = await backupPromise;
    const saved = JSON.parse(await fs.readFile(await backup.path(), 'utf8'));
    check(saved.memories.length === 1 && saved.house === 'ravenclaw' && saved.favorites.length === 1, 'JSON export contains the actual story, house and favorite');

    await page.locator('.memory-open').click();
    await page.locator('#delete-memory').click();
    check(await page.locator('#detail-dialog').isVisible(), 'first delete click requests confirmation');
    await page.locator('#delete-memory').click();
    check(await page.locator('#empty-state').isVisible(), 'confirmed deletion updates the filtered empty state');
    await page.reload();
    check(await page.locator('.memory-card').count() === 3, 'deleted story stays deleted');
    await context.close();

    const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, reducedMotion: 'reduce' });
    const mobilePage = await mobile.newPage();
    mobilePage.on('pageerror', error => errors.push(error.message));
    await mobilePage.goto(url);
    check(await mobilePage.locator('body').evaluate(body => body.classList.contains('reduced-motion')), 'system reduced-motion preference is honored');
    check(await mobilePage.evaluate(() => document.documentElement.scrollWidth === innerWidth), 'mobile has no horizontal overflow');
    const heroBox = await mobilePage.locator('.hero-content').boundingBox();
    const scenesBox = await mobilePage.locator('.scene-bottom').boundingBox();
    check(heroBox.y + heroBox.height < scenesBox.y, 'mobile hero text does not overlap scene controls');
    await mobilePage.screenshot({ path: path.join(root, 'preview-mobile.png'), fullPage: true });
    await mobilePage.locator('[data-open-write]').first().click();
    check(await mobilePage.locator('#write-dialog').evaluate(node => node.scrollWidth <= node.clientWidth), 'mobile editor fits the viewport');
    await mobilePage.screenshot({ path: path.join(root, 'preview-letter.png') });
    await mobile.close();

    const blocked = await browser.newContext();
    await blocked.addInitScript(() => { Storage.prototype.setItem = () => { throw new DOMException('Full', 'QuotaExceededError'); }; });
    const blockedPage = await blocked.newPage();
    blockedPage.on('pageerror', error => errors.push(error.message));
    await blockedPage.goto(url);
    await blockedPage.locator('[data-open-write]').first().click();
    await fillStory(blockedPage);
    await blockedPage.locator('.submit-memory').click();
    check(await blockedPage.locator('#write-dialog').isVisible() && await blockedPage.locator('#form-error').isVisible(), 'storage failure keeps the draft and reports the error');
    check(await blockedPage.locator('.memory-card').count() === 3, 'storage failure never reports a phantom saved story');
    await blocked.close();

    const corrupt = await browser.newContext();
    await corrupt.addInitScript(key => localStorage.setItem(key, '{broken-but-precious'), storageKey);
    const corruptPage = await corrupt.newPage();
    corruptPage.on('pageerror', error => errors.push(error.message));
    await corruptPage.goto(url);
    await corruptPage.locator('[data-house="gryffindor"]').click();
    check(await corruptPage.evaluate(key => localStorage.getItem(key), storageKey) === '{broken-but-precious', 'corrupted existing storage is preserved instead of overwritten');
    await corrupt.close();
    check(errors.length === 0, `no unhandled browser errors (${errors.join('; ')})`);
    console.log(`\n${checks} checks passed.`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
