// node encrypt.js <payload.json> <password> <out.json>
// AES-256-CBC with a PBKDF2-SHA256 key. The plaintext starts with "SBARC1:" so a wrong password is detected.
// Salt and IV are derived from the content, so unchanged figures give an identical file (no needless redeploys).
const fs = require('fs');
const crypto = require('crypto');
const [, , inPath, password, outPath] = process.argv;
const ITER = 120000;
const plain = Buffer.from('SBARC1:' + fs.readFileSync(inPath, 'utf8'), 'utf8');
const h = (tag) => crypto.createHash('sha256').update(tag).update(password).update(plain).digest().subarray(0, 16);
const salt = h('salt');
const iv = h('iv');
const key = crypto.pbkdf2Sync(Buffer.from(password, 'utf8'), salt, ITER, 32, 'sha256');
const c = crypto.createCipheriv('aes-256-cbc', key, iv);
const ct = Buffer.concat([c.update(plain), c.final()]);
fs.writeFileSync(outPath, JSON.stringify({ salt: salt.toString('base64'), iv: iv.toString('base64'), iter: ITER, ct: ct.toString('base64') }));
console.log('encrypted', plain.length, 'bytes');
