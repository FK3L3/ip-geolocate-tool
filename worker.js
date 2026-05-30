// Cloudflare Worker — AbuseIPDB CORS proxy for ip/geolocate
// Deploy at https://dash.cloudflare.com/?to=/:account/workers
//
// The worker accepts:
//   GET /?ip=<address>   with header  X-Abuse-Key: <your-key>
// and proxies to AbuseIPDB, adding CORS headers so the browser accepts it.

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'X-Abuse-Key, Accept',
};

export default {
  async fetch(request) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);
    const ip  = url.searchParams.get('ip')  || '';
    const key = request.headers.get('X-Abuse-Key') || '';

    if (!ip || !key) {
      return json({ error: 'Missing ip or X-Abuse-Key header' }, 400);
    }

    const upstream = `https://api.abuseipdb.com/api/v2/check?ipAddress=${encodeURIComponent(ip)}&maxAgeInDays=90`;
    const resp = await fetch(upstream, {
      headers: { Key: key, Accept: 'application/json' },
    });

    const body = await resp.text();
    return new Response(body, {
      status: resp.status,
      headers: { 'Content-Type': 'application/json', ...CORS },
    });
  },
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}
