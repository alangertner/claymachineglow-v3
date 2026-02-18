const http = require('http');
const fs = require('fs');
const WebSocket = require('ws');

const CDP_PORT = 18800;

async function getCookies(targetId) {
  // Get list of targets
  const targets = await new Promise((resolve, reject) => {
    http.get(`http://127.0.0.1:${CDP_PORT}/json`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(JSON.parse(data)));
    }).on('error', reject);
  });
  
  const target = targets.find(t => t.id === targetId) || targets[0];
  const wsUrl = target.webSocketDebuggerUrl;
  
  const ws = new WebSocket(wsUrl);
  await new Promise(r => ws.on('open', r));
  
  let id = 1;
  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      ws.send(JSON.stringify({id: msgId, method, params}));
      const handler = (msg) => {
        const data = JSON.parse(msg);
        if (data.id === msgId) {
          ws.removeListener('message', handler);
          if (data.error) reject(data.error);
          else resolve(data.result);
        }
      };
      ws.on('message', handler);
    });
  }
  
  const {cookies} = await send('Network.getCookies', {urls: ['https://x.com', 'https://ton.x.com']});
  ws.close();
  return cookies;
}

async function downloadWithCookies(url, outputPath, cookies) {
  const cookieHeader = cookies.map(c => `${c.name}=${c.value}`).join('; ');
  
  const urlObj = new URL(url);
  const options = {
    hostname: urlObj.hostname,
    path: urlObj.pathname,
    headers: {
      'Cookie': cookieHeader,
      'User-Agent': 'Mozilla/5.0'
    }
  };
  
  return new Promise((resolve, reject) => {
    const proto = urlObj.protocol === 'https:' ? require('https') : http;
    proto.get(options, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        // Follow redirect
        downloadWithCookies(res.headers.location, outputPath, cookies).then(resolve).catch(reject);
        return;
      }
      const stream = fs.createWriteStream(outputPath);
      res.pipe(stream);
      stream.on('finish', () => {
        stream.close();
        resolve(fs.statSync(outputPath).size);
      });
    }).on('error', reject);
  });
}

async function main() {
  const url = process.argv[2];
  const output = process.argv[3];
  const targetId = process.argv[4] || '';
  
  const cookies = await getCookies(targetId);
  const size = await downloadWithCookies(url, output, cookies);
  console.log(`Downloaded ${size} bytes to ${output}`);
}

main().catch(console.error);
