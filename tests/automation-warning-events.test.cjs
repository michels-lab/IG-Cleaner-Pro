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
const fns = vm.runInNewContext(src.slice(begin,end) + '\n({summarize,cutoff,reconciledOutcomes})', context, {timeout:2500});
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
// Regression: legacy journals may have both "Example.User" and "example.user"
// keys. Insertion order must never decide whether a real later OK is visible.
const earlierCase={task:'unfollow',username:'Example.User',status:'review',
  origin:'robot',at:'2026-11-09T06:01:00Z',
  warning_events:[{status:'blocked',at:'2026-11-09T06:00:00Z',origin:'robot'}]};
const newerCase={task:'unfollow',username:'example.user',status:'ok',
  origin:'robot',at:'2026-11-09T06:10:00Z',
  warning_events:[{status:'blocked',at:'2026-11-09T06:00:00Z',origin:'robot'}]};
for(const records of [[earlierCase,newerCase],[newerCase,earlierCase],
  [earlierCase,newerCase,earlierCase,newerCase]]){
 const actual=fns.summarize(records,'h1',now);
 assert.equal(actual.verified,1,'Newest verified outcome wins regardless of saved key order');
 assert.equal(actual.unfollow,1,'Do not double-count case variants as separate users');
 assert.equal(actual.warning,2,'Prior Review and shared blocked event remain distinct');
}
const latestReview={...earlierCase,status:'review',at:'2026-11-09T06:12:00Z'};
assert.equal(fns.summarize([newerCase,latestReview],'h1',now).verified,0,
  'A newer Review supersedes an older positive outcome');
const newest=fns.reconciledOutcomes([earlierCase,newerCase,earlierCase]);
assert.equal(newest.length,1,'The timeline displays one row per casefolded Instagram identity');
assert.equal(newest[0].record.status,'ok','The activity timeline uses the latest outcome');
assert.equal(newest[0].at,Date.parse(newerCase.at));
const conflicting={...newerCase,origin:'unknown'};
for(const pair of [[newerCase,conflicting],[conflicting,newerCase]]){
 const actual=fns.summarize(pair,'h1',now);
 assert.equal(actual.verified,0,'Equal-time contradictory provenance must fail closed');
 assert.equal(actual.legacy_unknown,0,'Do not arbitrarily select a conflicting saved row');
}
const collision=fns.reconciledOutcomes([newerCase,conflicting]);
assert.equal(collision.length,1);
assert.equal(collision[0].conflict,true,'History must visibly flag contradictory latest proof');
const sameHandleOtherTask={...newerCase,task:'cancel'};
const multiTask=fns.summarize([earlierCase,newerCase,sameHandleOtherTask],'today',now);
assert.equal(multiTask.verified,2,'Separate Unfollow and Cancel journals stay independent');
assert.equal(multiTask.unfollow,1);
assert.equal(multiTask.cancel,1);
assert.equal(multiTask.warning,3,'Separate Unfollow and Cancel warnings each count by exact task and timestamp');

// GRANADA regression: toggling robot/unknown provenance is not allowed to
// inflate successes, relabel legacy OK as robot or erase warnings by origin.
const oldUnknown={...newerCase,username:'old.history',origin:'unknown'};
const unknownWarning={...newerCase,username:'unknown.warning',
 status:'review',origin:'unknown',at:'2026-11-09T06:11:00Z',
 warning_events:[{status:'blocked',at:'2026-11-09T06:00:00Z',origin:'unknown'}]};
const scopedOrigins=[newerCase,oldUnknown,unknownWarning];
const allOrigins=fns.summarize(scopedOrigins,'h1',now,'all');
assert.equal(allOrigins.verified,1);
assert.equal(allOrigins.legacy_unknown,1);
assert.equal(allOrigins.warning,2);
const robotOnly=fns.summarize(scopedOrigins,'h1',now,'robot');
assert.equal(robotOnly.verified,1);
assert.equal(robotOnly.legacy_unknown,0,'Legacy unknown origin cannot be claimed as robot');
assert.equal(robotOnly.warning,0,'Unknown warning events cannot be called robot warnings');
const unknownOnly=fns.summarize(scopedOrigins,'h1',now,'unknown');
assert.equal(unknownOnly.verified,0,'Unknown historical OK cannot be counted as confirmed robot');
assert.equal(unknownOnly.legacy_unknown,1);
assert.equal(unknownOnly.warning,2);
// Crucial ordering: prove cross-origin conflicts on the FULL journal before
// applying the requested visible origin. Otherwise a robot-only filter could
// silently remove a same-time contradictory unknown result and invent an OK.
const crossOriginConflict=[newerCase,{...newerCase,origin:'unknown'}];
assert.equal(fns.summarize(crossOriginConflict,'h1',now,'robot').verified,0);
assert.equal(fns.summarize(crossOriginConflict,'h1',now,'unknown').legacy_unknown,0);
assert.equal(fns.reconciledOutcomes(crossOriginConflict)[0].conflict,true);
const oldWarningOnRobot={...newerCase,username:'mixed.warnings',
 warning_events:[{status:'review',at:'2026-11-09T06:00:00Z',origin:'unknown'}]};
assert.equal(fns.summarize([oldWarningOnRobot],'h1',now,'robot').warning,0);
assert.equal(fns.summarize([oldWarningOnRobot],'h1',now,'unknown').warning,1,
 'Historical warning provenance is preserved separately from current action origin');
assert(src.includes("origin.id='igcActOrigin'"),
 'Production Windows activity panel must expose a working origin selector');
assert(src.includes("origin.addEventListener('change',()=>render(latest))"),
 'Origin selector must recompute period tiles and journal without a reload');

console.log('Automations: warning event history, exact timestamps, no-click, duplicate casefold + local-midnight parity + provenance-filter fail-closed PASS');
