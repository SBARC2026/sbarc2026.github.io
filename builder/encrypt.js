// node encrypt.js <payload.json> <password> <out.json>          portal data (JSON in, JSON out)
// node encrypt.js --bin <file> <password> <out.bin>              any file, e.g. a PDF (binary out)
// AES-256-CBC with a PBKDF2-SHA256 key. The plaintext starts with "SBARC1:" so a wrong password is detected.
// Salt and IV are derived from the content, so unchanged figures give an identical file (no needless redeploys).
// Binary layout: "SBP1" | salt (16) | iv (16) | iterations (uint32 BE) | ciphertext
const fs = require('fs');
const crypto = require('crypto');
const args = process.argv.slice(2);
const bin = args[0] === '--bin';
const [inPath, password, outPath] = bin ? args.slice(1) : args;
const ITER = 120000;
const body = bin ? fs.readFileSync(inPath) : Buffer.from(fs.readFileSync(inPath, 'utf8'), 'utf8');
const plain = Buffer.concat([Buffer.from('SBARC1:', 'utf8'), body]);
const h = (tag) => crypto.createHash('sha256').update(tag).update(password).update(plain).digest().subarray(0, 16);
const salt = h('salt');
const iv = h('iv');
const key = crypto.pbkdf2Sync(Buffer.from(password, 'utf8'), salt, ITER, 32, 'sha256');
const c = crypto.createCipheriv('aes-256-cbc', key, iv);
const ct = Buffer.concat([c.update(plain), c.final()]);
if (bin) {
  const it = Buffer.alloc(4); it.writeUInt32BE(ITER);
  fs.writeFileSync(outPath, Buffer.concat([Buffer.from('SBP1'), salt, iv, it, ct]));
} else {
  fs.writeFileSync(outPath, JSON.stringify({ salt: salt.toString('base64'), iv: iv.toString('base64'), iter: ITER, ct: ct.toString('base64') }));
}
console.log('encrypted', plain.length, 'bytes');
