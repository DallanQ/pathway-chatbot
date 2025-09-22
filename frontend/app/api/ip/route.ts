import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const ip = request.headers.get('x-forwarded-for') || request.ip;

  if (!ip) {
    return new NextResponse('IP address not found', { status: 400 });
  }

  return new NextResponse(ip, { status: 200 });
}
