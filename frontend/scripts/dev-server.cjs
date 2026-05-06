const path = require('path');
const net = require('net');

const projectRoot = path.resolve(__dirname, '..');
const startServerPath = path.join(
  projectRoot,
  'node_modules',
  'next',
  'dist',
  'server',
  'lib',
  'start-server.js'
);

const { startServer } = require(startServerPath);

const requestedPort = Number(process.env.PORT || '3000');
const host = process.env.HOST || '127.0.0.1';

process.chdir(projectRoot);

function canBindPort(port) {
  return new Promise((resolve) => {
    const server = net.createServer();
    const finish = (value) => {
      server.removeAllListeners();
      resolve(value);
    };

    server.once('error', () => finish(false));
    server.listen(port, host, () => {
      server.close(() => finish(true));
    });
  });
}

async function selectPort() {
  for (let port = requestedPort; port < requestedPort + 10; port += 1) {
    if (await canBindPort(port)) {
      return port;
    }
  }

  return requestedPort;
}

(async () => {
  const port = await selectPort();
  await startServer({
    dir: projectRoot,
    port,
    allowRetry: true,
    isDev: true,
    hostname: host,
  });
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
