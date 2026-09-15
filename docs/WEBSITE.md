# Website and app links

Canonical website: **https://finemenot.xyz/**. Sources, privacy and support are sections on this one barebones page: `#sources`, `#privacy`, `#support`. `App/AppLinks.swift` owns the app’s website and database base URLs.

Cloudflare provides DNS. GitHub Pages hosts `Site/` and `Data/Published/`, deployed by the existing `data.yml` GitHub Action through `Scripts/stage_site.py`. No separate Worker, proxy, new hosting subscription or Codex automation is required.

DNS records are DNS-only CNAMEs, with automatic TTL:

| Name | Target |
|---|---|
| `finemenot.xyz` | `aindaco1.github.io` |
| `www.finemenot.xyz` | `aindaco1.github.io` |

Cloudflare flattens the apex CNAME. GitHub Pages is configured with `finemenot.xyz` as its custom domain. GitHub must finish certificate provisioning before HTTPS enforcement is enabled. A green deployment does not establish DNS or HTTPS availability.

Release checks: verify authoritative and public DNS; valid TLS without bypassing certificate checks; the page and its three section anchors; `/data/manifest.json`; the manifest’s immutable snapshot and SHA-256; and Update now in the new app build. TestFlight marketing/privacy URLs use the new domain. The owner explicitly requested no compatibility work for older test builds.

DNS is managed in Cloudflare; the website and data continue to deploy from GitHub Actions on the existing schedule. Do not remove the GitHub custom domain or rewrite app URLs independently of this contract.

`verify-website.yml` is a **manual-only**, read-only GitHub Action for migrations. It waits for GitHub's certificate and checks the canonical page, three section anchors, immutable snapshot digest/version/count and public database agreement. It has a bounded 65-minute job timeout and does not add a recurring schedule. Run `python3 Scripts/check_site.py` for the same delivery check without waiting. HTTPS enforcement is an administrator's Pages setting; the verification workflow does not receive an administrator credential.

Activation snapshot, September 14, 2026 at 22:43 Mountain: Cloudflare DNS records and GitHub's origin are correct; parent `.xyz` DNS is still NXDOMAIN and GitHub's certificate is not yet available. [Cloudflare documents that a newly registered domain's parent-TLD propagation can take up to 24 hours](https://developers.cloudflare.com/dns/zone-setups/troubleshooting/pending-nameservers/). This is a pending external deployment check, not a verified-live HTTPS site. See the [manual verification run](https://github.com/aindaco1/fine-me-not/actions/runs/34929772047) for its eventual result.
