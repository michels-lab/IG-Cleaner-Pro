"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const html=fs.readFileSync(path.join(__dirname,"../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const from=html.indexOf("function igcFocusStorageDiagnostic(");
const to=html.indexOf("function setActiveFocusBatch(",from);
assert(from>=0&&to>from,"Missing storage diagnostic implementation");
const localStorage={
 length:2,
 key:i=>["private_auth_token","ig_reviewed_history"][i],
 getItem:key=>key==="private_auth_token"?"very_secret_value":"reviewed-profile-123"
};
const ctx={
 localStorage,JSON,String,Math,Number,
 igcEncodeActiveFocusBatch:batch=>batch
};
vm.createContext(ctx);vm.runInContext(html.slice(from,to),ctx);
const text=ctx.igcFocusStorageDiagnostic({name:"QuotaExceededError"},{rows:[
 {username:"private_username",href:"https://instagram.com/private_username/"}
]});
assert.match(text,/QuotaExceededError/);
assert.match(text,/tamaño de tanda/);
assert.match(text,/almacenamiento usado/);
for(const secret of ["private_username","private_auth_token","very_secret_value","reviewed-profile-123"]){
 assert(!text.includes(secret),"Diagnostic must redact storage keys, values and profile identities");
}
ctx.localStorage={get length(){throw Error("SecurityError")}};
assert.doesNotThrow(()=>ctx.igcFocusStorageDiagnostic({name:"SecurityError"},{rows:[]}));
console.log("PASS: redacted Focus storage diagnostics under quota and blocked storage");
