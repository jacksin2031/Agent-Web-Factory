#!/usr/bin/env python3
import argparse
import json
import re
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree

UA = "AgentWebFactoryValidator/0.10"
NOT_FOUND_PROBE = "__agent_web_factory_404_probe__"


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag.lower() == "title":
            self.in_title = True
        elif tag.lower() == "meta":
            self.meta.append(attrs)
        elif tag.lower() == "link":
            self.links.append(attrs)

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read(2_000_000)
            return response.status, response.geturl(), dict(response.headers), body
    except urllib.error.HTTPError as exc:
        body = exc.read(2_000_000)
        return exc.code, exc.geturl(), dict(exc.headers), body


def check_robots(body):
    text = body.decode("utf-8", "replace")
    # Conservative check for a global production block. This is not a full robots parser.
    blocks = re.split(r"(?im)^\s*user-agent\s*:\s*", text)
    blocked = False
    for block in blocks[1:]:
        lines = block.splitlines()
        if not lines:
            continue
        agent = lines[0].strip()
        if agent == "*" and re.search(r"(?im)^\s*disallow\s*:\s*/\s*(?:#.*)?$", "\n".join(lines[1:])):
            blocked = True
            break
    return {"pass": not blocked, "globally_blocked": blocked, "bytes": len(body)}


def check_sitemap(body):
    try:
        root = ElementTree.fromstring(body)
        local_name = root.tag.rsplit("}", 1)[-1]
        if local_name not in {"urlset", "sitemapindex"}:
            return {"pass": False, "root": local_name, "error": "Unexpected sitemap root element"}
        locs = [node.text.strip() for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "loc" and node.text and node.text.strip()]
        return {"pass": bool(locs), "root": local_name, "loc_count": len(locs), "bytes": len(body)}
    except ElementTree.ParseError as exc:
        return {"pass": False, "error": f"Invalid XML: {exc}", "bytes": len(body)}


def header_value(headers, name):
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return ""


def meta_content(meta, *, name=None, prop=None):
    for item in meta:
        if name is not None and item.get("name", "").lower() == name.lower():
            return item.get("content")
        if prop is not None and item.get("property", "").lower() == prop.lower():
            return item.get("content")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--allow-http", action="store_true", help="Allow HTTP for local validator tests only")
    args = ap.parse_args()
    base = args.url if args.url.startswith("http") else "https://" + args.url
    if not base.endswith("/"):
        base += "/"

    result = {"url": base, "checks": {}, "pass": True}

    try:
        status, final_url, headers, body = fetch(base)
        text = body.decode("utf-8", "replace")
        parser = HeadParser()
        parser.feed(text)

        final = urlparse(final_url)
        content_type = headers.get("Content-Type", "")
        desc = meta_content(parser.meta, name="description")
        robots_meta = meta_content(parser.meta, name="robots") or ""
        viewport = meta_content(parser.meta, name="viewport")
        og_title = meta_content(parser.meta, prop="og:title")
        xcto = header_value(headers, "X-Content-Type-Options")
        referrer = header_value(headers, "Referrer-Policy")
        hsts = header_value(headers, "Strict-Transport-Security")
        csp = header_value(headers, "Content-Security-Policy")
        xfo = header_value(headers, "X-Frame-Options")
        canonical = next(
            (
                l.get("href")
                for l in parser.links
                if "canonical" in str(l.get("rel", "")).lower().split()
            ),
            None,
        )
        canonical_parsed = urlparse(canonical) if canonical else None

        result["checks"]["homepage"] = {"pass": 200 <= status < 300, "status": status, "final_url": final_url}
        result["checks"]["https"] = {
            "pass": args.allow_http or final.scheme == "https",
            "scheme": final.scheme,
        }
        result["checks"]["content_type"] = {"pass": "text/html" in content_type.lower(), "value": content_type}
        result["checks"]["title"] = {"pass": bool(parser.title.strip()), "value": parser.title.strip()}
        result["checks"]["description"] = {"pass": bool(desc), "value": desc}
        result["checks"]["viewport"] = {"pass": bool(viewport), "value": viewport}
        result["checks"]["open_graph"] = {"pass": bool(og_title), "og:title": og_title}
        result["checks"]["x_content_type_options"] = {
            "pass": xcto.lower().strip() == "nosniff", "value": xcto
        }
        result["checks"]["referrer_policy"] = {"pass": bool(referrer.strip()), "value": referrer}
        result["checks"]["hsts"] = {
            "pass": args.allow_http or bool(hsts.strip()), "value": hsts, "skipped_for_http_fixture": args.allow_http
        }
        result["checks"]["frame_protection"] = {
            "pass": "frame-ancestors" in csp.lower() or bool(xfo.strip()),
            "content_security_policy": csp,
            "x_frame_options": xfo,
        }
        result["checks"]["canonical"] = {
            "pass": bool(
                canonical
                and canonical_parsed.scheme in ({"http", "https"} if args.allow_http else {"https"})
                and canonical_parsed.netloc == final.netloc
            ),
            "value": canonical,
        }
        result["checks"]["noindex"] = {"pass": "noindex" not in robots_meta.lower(), "value": robots_meta}

        robots_url = urljoin(final_url, "robots.txt")
        rs, rfu, rh, rb = fetch(robots_url)
        robots_check = check_robots(rb)
        robots_check.update({"status": rs, "url": rfu})
        robots_check["pass"] = robots_check["pass"] and 200 <= rs < 300
        result["checks"]["robots.txt"] = robots_check

        sitemap_url = urljoin(final_url, "sitemap.xml")
        ss, sfu, sh, sb = fetch(sitemap_url)
        sitemap_check = check_sitemap(sb)
        sitemap_check.update({"status": ss, "url": sfu})
        sitemap_check["pass"] = sitemap_check["pass"] and 200 <= ss < 300
        result["checks"]["sitemap.xml"] = sitemap_check

        probe_url = urljoin(final_url, NOT_FOUND_PROBE)
        ns, nfu, nh, nb = fetch(probe_url)
        result["checks"]["404"] = {"pass": ns in {404, 410}, "status": ns, "url": nfu}

        for value in result["checks"].values():
            if isinstance(value, dict) and value.get("pass") is False:
                result["pass"] = False
    except Exception as exc:
        result["pass"] = False
        result["error"] = f"{exc.__class__.__name__}: {exc}"

    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
