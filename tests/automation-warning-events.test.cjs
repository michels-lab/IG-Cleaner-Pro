'use strict';
/* Read-only canonical Automations event counters: a later OK must not erase an
 * earlier Review warning. No browser, Instagram login or external service. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

process.env.TZ = 'America/Monterrey';
const src = fs.readFileSync(path.join(__dirname, '../tools/automation_activity_ui.py'), 'utf8');
const begin = src.indexOf('function dateValue(value){');
const end = src.indexOf('async function readHistory(account,task){', begin);
assert(begin >= 0 && end > begin, 'Use real production period and summary functions');
const sessionStart = Date.parse('2026-11-09T05:50:00Z');
const context = {Date, Number, Math, String, Object, Set, sessionStart,
 HANDLE:/^[a-z0-9._]{1,30}$/i};
const fns = vm.runInNewContext(src.slice(begin,end) + '\n({summarize,cutoff})', context, {timeout:2500});
const now = new Date('2026-11-09T06:15:00Z'); // 00:15 Nov 9 Monterrey

const current = {
 task:'unfollow',username:'example.user',status:'ok',origin:'robot',
 at:'2026-11-09T06:05:00Z', // 00:05 Nov 9
 warning_events:[
   {status:'review',at:'2026-11-09T05:45:00Z',origin:'robot'}, // yesterday 23:45
   {status:'review',at:'2026-11-09T05:45:00Z',origin:'robot'}, // duplicate persisted snapshot
   {status:'error',at:'2026-11-08T06:10:00Z',origin:'unknown'},
   {status:'blocked',at:'2099-01-01T01:00:00Z',origin:'robot'}, // future = never
   {status:'ok',at:'2026-11-09T05:30:00Z',origin:'robot'}, // not warning
 ]
};
const resolved = {task:'cancel',username:'already.ok',status:'already_not_requested',
                  origin:'robot',at:'2026-11-09T06:10:00Z',
                  warning_events:[]};
const rows=[current,{...current},resolved];
const today = fns.summarize(rows,'today',now);
assert.equal(today.verified,1,'Later OK is counted exactly once');
assert.equal(today.unfollow,1);
assert.equal(today.cancel,0);
assert.equal(today.warning,0,'Prior calendar-day warning is not counted in Hoy');
assert.equal(today.no_action,1,'Already-not-requested is not a successful cancellation');
const hour=fns.summarize(rows,'h1',now);
assert.equal(hour.verified,1);
assert.equal(hour.warning,1,'Old Review remains visible at its own time');
const trailing=fns.summarize(rows,'h24',now);
assert.equal(trailing.warning,1);
assert.equal(fns.summarize(rows,'session',now).warning,0,
  'A warning from before this app session is not invented for this session');
assert.equal(fns.summarize(rows,'d7',now).warning,2,
  'Older saved error remains an independent warning event in 7-day history');
// The current warning itself must not double-count with an identical archived event.
const pending={task:'cancel',username:'in.review',status:'review',
  origin:'robot',at:'2026-11-09T06:08:00Z',
  warning_events:[{status:'review',at:'2026-11-09T06:08:00Z',origin:'robot'}]};
assert.equal(fns.summarize([pending],'h1',now).warning,1);
console.log('Automations: warning event history, exact timestamps, no-click, duplicate + local-midnight parity PASS');
