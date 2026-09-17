// Run fixture server first, then PLAYWRIGHT_MODULE=/path/to/playwright node tests/browser_review.cjs URL [screenshot-dir]
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
(async () => {
  const base = process.argv[2];
  assert(base, 'Pass the BROWSER_URL printed by browser_fixture.py');
  const output = process.argv[3] || '/tmp/audit-browser-review';
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({headless:true});
  const errors=[];
  try {
    for (const width of [1440,390]) {
      const page=await browser.newPage({viewport:{width,height:1000}});
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(base);
      await page.waitForSelector('#rows tr');
      await page.waitForFunction(()=>document.querySelector('#semantic-state').textContent.includes('coverage'));
      const fits=async()=>assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), 'Page-level horizontal overflow');
      await fits();
      await page.screenshot({path:path.join(output,`overview-${width}.png`)});
      await page.locator('#query').fill('strategic advisory');
      await page.getByRole('button',{name:'Find similar transactions',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#semantic-results').textContent.includes('A1'));
      const row=page.locator('#rows tr').filter({has:page.getByRole('button',{name:'Investigate',exact:true})}).first();
      await row.getByRole('button',{name:'Investigate',exact:true}).click();
      await page.waitForSelector('#investigation h3');
      assert.match(await page.locator('#investigation').innerText(),/semantic_account_mismatch/);
      for(const heading of ['Why flagged','Normal peers','Alternative matches','Related population','Other signals','Suggested evidence to inspect']) {
        assert.equal(await page.getByRole('heading',{name:heading,exact:true}).count(),1);
      }
      await page.locator('#investigate-id').fill('10');
      await page.getByRole('button',{name:'Investigate line',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#investigation h3')?.textContent.includes('A1'));
      await fits();
      await page.locator('#investigation h3').scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,`investigation-${width}.png`)});
      await page.getByRole('heading',{name:'Normal peers',exact:true}).scrollIntoViewIfNeeded();
      await page.screenshot({path:path.join(output,`peers-${width}.png`)});
      await page.locator('#rows details').first().locator('summary').click();
      await fits();
      await page.locator('#analysis-run').fill('999');
      await page.getByRole('button',{name:'Filter queue',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#rows').children.length===0);
      await page.locator('#analysis-run').fill('1');
      await page.getByRole('button',{name:'Filter queue',exact:true}).click();
      await page.waitForSelector('#rows tr');
      // Synthetic error and empty states; response shape remains the application's API contract.
      await page.route('**/api/semantic-profile',route=>route.fulfill({status:404,contentType:'application/json',body:JSON.stringify({error:'semantic run not found'})}));
      await page.getByRole('button',{name:'Load latest',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#semantic-state').textContent==='semantic run not found');
      await page.unroute('**/api/semantic-profile');
      await page.getByRole('button',{name:'Load latest',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#semantic-state').textContent.includes('coverage'));
      await page.route('**/api/semantic-investigation?*',async route=>{
        const response=await route.fetch();const body=await response.json();body.stale=true;body.entry.entry_id='<img src=x onerror="window.injected=true">';
        await route.fulfill({response,json:body});
      });
      await page.getByRole('button',{name:'Investigate line',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#investigation').textContent.includes('Historical snapshot'));
      assert.equal(await page.locator('#investigation img').count(),0);
      assert.equal(await page.evaluate(()=>window.injected),undefined);
      await fits();
      console.log(JSON.stringify({width,pageWidth:await page.evaluate(()=>document.documentElement.scrollWidth),flows:'overview/search/queue-investigate/manual-investigate/peers/filter/empty/error/stale/escaping',errors}));
      await page.close();
    }
    assert.deepEqual(errors,[]);
    console.log('Browser checks passed. Screenshots: '+output);
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
