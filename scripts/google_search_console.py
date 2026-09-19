#!/usr/bin/env python3
"""Small stdlib-only helper for Google Site Verification + Search Console APIs.

Authentication: set GOOGLE_ACCESS_TOKEN to a user OAuth access token with suitable
siteverification and webmasters scopes. This script never stores the token.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import urllib.error


def token():
    t = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not t:
        raise SystemExit("GOOGLE_ACCESS_TOKEN is required")
    return t


def request(method, url, body=None):
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": "AgentWebFactory/0.10",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        raise SystemExit(f"Google API HTTP {e.code}: {raw}")


def verify_token(domain):
    body = {
        "site": {"type": "INET_DOMAIN", "identifier": domain},
        "verificationMethod": "DNS_TXT",
    }
    return request("POST", "https://www.googleapis.com/siteVerification/v1/token", body)


def verify_domain(domain):
    body = {"site": {"type": "INET_DOMAIN", "identifier": domain}}
    url = "https://www.googleapis.com/siteVerification/v1/webResource?verificationMethod=DNS_TXT"
    return request("POST", url, body)


def add_property(domain):
    site = urllib.parse.quote(f"sc-domain:{domain}", safe="")
    return request("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{site}")


def submit_sitemap(domain, sitemap):
    site = urllib.parse.quote(f"sc-domain:{domain}", safe="")
    feed = urllib.parse.quote(sitemap, safe="")
    return request("PUT", f"https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}")


def inspect_url(domain, url):
    body = {"inspectionUrl": url, "siteUrl": f"sc-domain:{domain}", "languageCode": "en-US"}
    return request("POST", "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect", body)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("get-dns-token")
    a.add_argument("domain")

    a = sub.add_parser("verify-domain")
    a.add_argument("domain")

    a = sub.add_parser("add-property")
    a.add_argument("domain")

    a = sub.add_parser("submit-sitemap")
    a.add_argument("domain")
    a.add_argument("sitemap")

    a = sub.add_parser("inspect-url")
    a.add_argument("domain")
    a.add_argument("url")

    args = ap.parse_args()
    if args.cmd == "get-dns-token":
        out = verify_token(args.domain)
    elif args.cmd == "verify-domain":
        out = verify_domain(args.domain)
    elif args.cmd == "add-property":
        out = add_property(args.domain)
    elif args.cmd == "submit-sitemap":
        out = submit_sitemap(args.domain, args.sitemap)
    else:
        out = inspect_url(args.domain, args.url)

    print(json.dumps({"http_status": out[0], "data": out[1]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
