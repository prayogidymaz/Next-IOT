import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { isAccessTokenUsable } from "@/lib/auth/session";

export function middleware(request: NextRequest) {
  const token = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  if (!isAccessTokenUsable(token)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/control-center/:path*",
    "/cyberdeck/:path*",
    "/settings/:path*",
    "/developer/:path*",
    "/studio/:path*",
  ],
};
