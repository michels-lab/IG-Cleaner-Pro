'use strict';
/* Regression: the owner requested TWO actual WINDOWS, not two accounts in
 * each app sidebar. Protect the real single-account layout from reappearing. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const src=fs.readFileSync(path.join(__dirname,'..','desktop',
  'ig_cleaner_pro_v120_27_synced_companion.html'),'utf8');
const rail=src.indexOf('class="igc-instagram-rail"');
const bottom=src.indexOf('class="igc-rail-bottom"',rail);
assert(rail>=0&&bottom>rail,'Primary Instagram profile picker remains in the rail');
const section=src.slice(rail,bottom);
assert(section.includes('id="igcInstagramIdentity"'),'One active account selector remains');
for(const removed of ['igcDualSecondary','igcDualAdvanced','igcDualRobotTarget',
  'igcDualStatus','igc-dual-workspace','openOtherWorkspace','startDualReadOnlyRobotLanes',
  'stopDualReadOnlyRobotLanes','IGC_WINDOW_PROFILE_KEY']){
 assert(!src.includes(removed), 'Rejected same-window dual-account feature returned: '+removed);
}
assert(src.includes('igcRawProfileStorage.setItem(IGC_INSTAGRAM_PROFILE_KEY,key)'),
 'Switching the ONE active Instagram profile still persists safely');
for(const area of ['Analysis','Actions','Review','History']){
 assert(src.includes('id="igcAutomationTab'+area+'"'),
  'Automations must have a clearly labeled '+area+' view');
}
assert(src.includes("section.append(drawer);drawer.open=true"),
 'Review must reuse original saved-exception drawer, never clone it');
console.log('GRANADA: single-account sidebar and four clear Automations sections PASS');
