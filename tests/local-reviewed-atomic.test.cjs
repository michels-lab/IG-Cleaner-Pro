"use strict";
// Real production saveReviewedState: a failed second localStorage write must
// never turn into persisted Reviewed with missing relationship metadata.
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const start=html.indexOf("function saveReviewedState(){");
const end=html.indexOf("function clearHiddenSelection(){",start);
assert(start>0&&end>start,"Production saveReviewedState is required");
const saved=new Map([["done",'["old"]'],["meta",'{"old":{"reviewedAt":11}}']]);
const doneSet=new Set(["old","new"]),reviewedMeta={old:{reviewedAt:11},new:{reviewedAt:22}};
let writes=0,failAt=2,syncs=0;
const ctx={JSON,String,Error,Set,Object,console,LS_DONE:"done",LS_REVIEW_META:"meta",doneSet,reviewedMeta,
 window:{igcQueueStateSync(){syncs++}},
 localStorage:{
  getItem:k=>saved.has(k)?saved.get(k):null,
  setItem(k,v){
    writes++;
    if(writes===failAt){const e=Error("QuotaExceededError");e.name="QuotaExceededError";throw e}
    saved.set(k,String(v));
  },
  removeItem:k=>saved.delete(k)
 }
};
vm.createContext(ctx);vm.runInContext(html.slice(start,end),ctx);
assert.throws(()=>ctx.saveReviewedState(),/No se guardó la revisión/,
 "Second write failure must be visible and not counted as confirmation");
assert.equal(saved.get("done"),'["old"]',"Durable DONE must roll back");
assert.equal(saved.get("meta"),'{"old":{"reviewedAt":11}}',"Prior review metadata survives");
assert.deepEqual([...doneSet],["old"],"In-memory DONE must recover prior state");
assert.deepEqual(Object.keys(reviewedMeta),["old"],"In-memory meta must not advertise fake confirmation");
assert.equal(syncs,0,"Failed review must NEVER enqueue cloud write");
writes=0;failAt=0;
doneSet.add("new");reviewedMeta.new={reviewedAt:22};
assert.doesNotThrow(()=>ctx.saveReviewedState());
assert.deepEqual(JSON.parse(saved.get("done")).sort(),["new","old"]);
assert.equal(JSON.parse(saved.get("meta")).new.reviewedAt,22);
assert.equal(syncs,1,"Cloud publication only after both writes succeed");
console.log("PASS: quota failure rolls back both Reviewed keys and memory; successful retry syncs once");
