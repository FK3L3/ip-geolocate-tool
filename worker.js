// Cloudflare Worker — AbuseIPDB CORS proxy for ip/geolocate
// Deploy via the Cloudflare dashboard drag-and-drop uploader (no wrangler needed).
//
// Accepts:  GET /?ip=<address>   +   header  X-Abuse-Key: <your-api-key>
// Returns:  AbuseIPDB JSON response with CORS headers added.

var CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'X-Abuse-Key, Accept',
};

addEventListener('fetch', function(event) {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: CORS });
  }

  var url = new URL(request.url);
  var ip  = url.searchParams.get('ip')  || '';
  var key = request.headers.get('X-Abuse-Key') || '';

  if (!ip || !key) {
    return jsonResponse({ error: 'Missing ip or X-Abuse-Key header' }, 400);
  }

  var upstream = 'https://api.abuseipdb.com/api/v2/check'
    + '?ipAddress=' + encodeURIComponent(ip)
    + '&maxAgeInDays=90';

  var resp = await fetch(upstream, {
    headers: { Key: key, Accept: 'application/json' },
  });

  var body = await resp.text();
  return new Response(body, {
    status: resp.status,
    headers: Object.assign({ 'Content-Type': 'application/json' }, CORS),
  });
}

function jsonResponse(data, status) {
  return new Response(JSON.stringify(data), {
    status: status || 200,
    headers: Object.assign({ 'Content-Type': 'application/json' }, CORS),
  });
}
