// node decrypt.js <file.bin> <password> <out>   (inverse of encrypt.js --bin; used by build.py for builder/p6/p6.bin)
const fs = require('fs'); const crypto = require('crypto');
const [inPath, password, outPath] = process.argv.slice(2);
const b = fs.readFileSync(inPath);
if (b.subarray(0, 4).toString() !== 'SBP1') { console.error('not an SBP1 file'); process.exit(2); }
const salt = b.subarray(4, 20), iv = b.subarray(20, 36), iter = b.readUInt32BE(36), ct = b.subarray(40);
const key = crypto.pbkdf2Sync(Buffer.from(password, 'utf8'), salt, iter, 32, 'sha256');
let plain;
try { const d = crypto.createDecipheriv('aes-256-cbc', key, iv); plain = Buffer.concat([d.update(ct), d.final()]); } catch (e) { console.error('wrong password'); process.exit(3); }
if (plain.subarray(0, 7).toString() !== 'SBARC1:') { console.error('wrong password'); process.exit(3); }
fs.writeFileSync(outPath, plain.subarray(7));
