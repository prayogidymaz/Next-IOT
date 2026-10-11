import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { ACCESS_TOKEN_COOKIE } from "@/lib/auth/constants";
import { isAccessTokenUsable } from "@/lib/auth/session";
import { roleFromAccessToken } from "@/lib/auth/token-role";

const PROTECTED_PREFIXES = ["/dashboard", "/tenants", "/billing", "/system"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));
  if (!isProtected) return NextResponse.next();

  const token = request.cookies.get(ACCESS_TOKEN_COOKIE)?.value;
  if (!isAccessTokenUsable(token)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }
  if (roleFromAccessToken(token) !== "super_admin") {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("error", "super_admin_required");
    return NextResponse.redirect(loginUrl);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/tenants/:path*", "/billing/:path*", "/system/:path*"],
};
