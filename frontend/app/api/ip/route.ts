import { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') || request.ip;

  if (!ip) {
    return new Response('IP address not found', { status: 400 });
  }

  return new Response(ip, { status: 200 });
}
