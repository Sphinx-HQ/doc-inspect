# Security

Please report vulnerabilities to security@sphinxhq.com. Do not open a public
GitHub issue for a vulnerability.

We aim to acknowledge a report within a few business days and to coordinate
disclosure. A 90-day window from the first report is a reasonable default
unless we agree otherwise.

## Scope

- The `watchdoc` package runs locally. It does not send files anywhere unless
  you call `Client.check`.
- The demo UI in `demo/` is a local development app. It is not hardened for
  public hosting and is not in scope as a production service.
