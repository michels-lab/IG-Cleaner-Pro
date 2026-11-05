"use strict";
/* GRANADA ZIP integrity: standard local stored/deflated Instagram archives.
 * Synthetic requests only. No network, user accounts or mutation. */
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const zlib=require("node:zlib");
const html=fs.readFileSync(path.join(__dirname,
  "../desktop/ig_cleaner_pro_v120_27_synced_companion.html"),"utf8");
const start=html.indexOf("function decodeZipName(bytes,utf8=true){");
const end=html.indexOf("function makeVirtualFile(entry,bytes){",start);
assert(start>=0&&end>start,"Use production ZIP reader, not a test-only reimplementation");
const ctx={Uint8Array,Uint32Array,DataView,TextDecoder,
  DecompressionStream,Blob,Response,Math,Error,Array};
vm.createContext(ctx);
vm.runInContext(html.slice(start,end),ctx,{timeout:5000});
assert.equal(ctx.zipCrc32(Buffer.from("123456789")),0xcbf43926,
  "Standard IEEE ZIP CRC32 known-answer vector");

// Deliberately independent bitwise generator, not the production lookup table.
function crcRef(buffer){
 let v=0xffffffff;
 for(const byte of buffer){
  v^=byte;
  for(let i=0;i<8;i++)v=(v>>>1)^((v&1)?0xedb88320:0);
 }
 return (v^0xffffffff)>>>0;
}
function archive(files){
 const local=[],directory=[];let offset=0;
 for(const {name,body,method=0} of files){
  const label=Buffer.from(name,"utf8"),raw=Buffer.from(body);
  const compressed=method===8?zlib.deflateRawSync(raw):raw;
  const crc=crcRef(raw);
  const lh=Buffer.alloc(30);
  lh.writeUInt32LE(0x04034b50,0);lh.writeUInt16LE(20,4);
  lh.writeUInt16LE(0x0800,6);lh.writeUInt16LE(method,8);
  lh.writeUInt32LE(crc,14);lh.writeUInt32LE(compressed.length,18);
  lh.writeUInt32LE(raw.length,22);lh.writeUInt16LE(label.length,26);
  const ch=Buffer.alloc(46);
  ch.writeUInt32LE(0x02014b50,0);ch.writeUInt16LE(20,4);
  ch.writeUInt16LE(20,6);ch.writeUInt16LE(0x0800,8);
  ch.writeUInt16LE(method,10);ch.writeUInt32LE(crc,16);
  ch.writeUInt32LE(compressed.length,20);ch.writeUInt32LE(raw.length,24);
  ch.writeUInt16LE(label.length,28);ch.writeUInt32LE(offset,42);
  local.push(lh,label,compressed);directory.push(ch,label);
  offset+=lh.length+label.length+compressed.length;
 }
 const central=Buffer.concat(directory),footer=Buffer.alloc(22);
 footer.writeUInt32LE(0x06054b50,0);footer.writeUInt16LE(files.length,8);
 footer.writeUInt16LE(files.length,10);
 footer.writeUInt32LE(central.length,12);footer.writeUInt32LE(offset,16);
 return {bytes:Buffer.concat([...local,central,footer]),centralOffset:offset,
   entryCount:files.length};
}
const pending=JSON.stringify({relationships_follow_requests_sent:[
 {title:"alpha.pending",string_list_data:[{value:"alpha.pending",timestamp:1700000000}]},
 {title:"beta.pending",string_list_data:[{value:"beta.pending",timestamp:1700000100}]}
]});
const following=JSON.stringify({relationships_following:[
 {title:"account.following",string_list_data:[{value:"account.following"}]}]});
const bundle=archive([
 {name:"connections/followers_and_following/pending_follow_requests.json",body:pending},
 {name:"connections/followers_and_following/following.json",body:following,method:8}
]);
const file=buf=>({arrayBuffer:async()=>Uint8Array.from(buf).buffer});
(async()=>{
 const zip=await ctx.readZipEntries(file(bundle.bytes));
 assert.equal(zip.entries.length,2);
 assert.equal(zip.entries[0].crc32,crcRef(Buffer.from(pending)));
 assert.equal(Buffer.from(await zip.extract(zip.entries[0])).toString(),pending);
 assert.equal(Buffer.from(await zip.extract(zip.entries[1])).toString(),following,
  "Deflated ZIP entries are also checked after decompression");

 const changed=Buffer.from(bundle.bytes),location=changed.indexOf("alpha.pending");
 assert(location>0,"Fixture must include cleartext target in stored ZIP data");
 changed[location+1]="z".charCodeAt(0);
 const altered=await ctx.readZipEntries(file(changed));
 await assert.rejects(()=>altered.extract(altered.entries[0]),/CRC|dañado|modificado/,
  "JSON that remains syntactically valid must not pass a forged/stale ZIP CRC");

 const wrongCrc=Buffer.from(bundle.bytes);
 wrongCrc.writeUInt32LE(0,bundle.centralOffset+16);
 const checksum=await ctx.readZipEntries(file(wrongCrc));
 await assert.rejects(()=>checksum.extract(checksum.entries[0]),/CRC/,
   "Reader must trust central-directory CRC, not local-header data");

 const wrongSize=Buffer.from(bundle.bytes);
 wrongSize.writeUInt32LE(Buffer.byteLength(pending)+1,bundle.centralOffset+24);
 const size=await ctx.readZipEntries(file(wrongSize));
 await assert.rejects(()=>size.extract(size.entries[0]),/tamaño|CRC/,
   "Unexpected decompressed length must invalidate the import");

 const wrongDirectory=Buffer.from(bundle.bytes);
 wrongDirectory.writeUInt32LE(0xffffffff,wrongDirectory.length-22+12);
 await assert.rejects(()=>ctx.readZipEntries(file(wrongDirectory)),/ZIP64/,
   "Unsupported ZIP64 must reject rather than report misleading empty requests");

 const truncated=Buffer.from(bundle.bytes);
 truncated.writeUInt32LE(bundle.bytes.length,bundle.bytes.length-22+16);
 await assert.rejects(()=>ctx.readZipEntries(file(truncated)),/Directorio central ZIP/,
   "Out-of-bounds directory cannot be interpreted as an empty ZIP");

 console.log("PASS: standard stored + deflate ZIP, known CRC32, changed parseable JSON, forged CRC/length and truncated directory rejected before import");
})().catch(e=>{console.error(e);process.exitCode=1});