'use strict';
// Regression: optional second-account robot controls must not bury primary navigation.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const src=fs.readFileSync(path.resolve(process.argv[2]||path.join(__dirname,'../desktop/ig_cleaner_pro_v120_27_synced_companion.html')),'utf8');
const home=src.indexOf('id="tab-moduleDashboard"'),health=src.indexOf('id="tab-diag"');
const panel=src.indexOf('<div class="igc-dual-workspace"'),foot=src.indexOf('<div class="igc-rail-bottom"');
assert(home>=0&&health>home&&panel>health&&foot>panel,'Secondary-account tools must appear AFTER all navigation');
const advancedStart=src.indexOf('<details id="igcDualAdvanced"',panel);
const quick=src.slice(panel,advancedStart),advanced=src.slice(advancedStart,foot);
assert(quick.includes('id="igcDualSecondary"')&&quick.includes('openOtherWorkspace(false)')&&quick.includes('openOtherWorkspace(true)'),'Profile selection and quick tab/window launch must remain visible');
assert(advanced.startsWith('<details')&&!advanced.startsWith('<details open'),'Advanced robot controls must be collapsed by default');
for(const item of ['id="igcDualRobotTarget"','id="igcDualRobotStatus"','id="igcDualStatus"','startDualReadOnlyRobotLanes()','refreshDualReadOnlyRobotLanes()','stopOneDualReadOnlyRobotLane()','restartOneDualReadOnlyRobotLane()','stopDualReadOnlyRobotLanes()','openTwoChromeSessions()'])
 assert(advanced.includes(item),'Missing protected dual robot control: '+item);
console.log('GRANADA sidebar structure: nav-first, compact and complete PASS');
