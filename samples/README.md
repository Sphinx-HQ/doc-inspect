# Sample files

Synthetic documents for trying the toolkit. They are fictional Example Corp /
Example Bank content, not real customer documents.

Run local inspection first, then the hosted check on the same file:

```python
from watchdoc import inspect, Client

path = "samples/edited_statement.pdf"
print(inspect(path).to_json())
print(Client().check(path))  # needs WATCHDOC_API_KEY
```

This README does not describe how production detection works, and it does not
explain how to change a document so that production results change.

| File | What `inspect()` reports locally | WatchDoc |
| --- | --- | --- |
| `edited_statement.pdf` | PDF with Info dates that differ after a later save. | Run `Client.check` on this file to see WatchDoc's decision and flags. |
| `invoice-editor-producer.pdf` | Info `Creator` / `Producer` strings, creation vs modification dates that differ, and an XMP modify date that does not match Info. | Run `Client.check` on this file to see WatchDoc's decision and flags. |
| `statement-scrubbed.pdf` | No Info dictionary and no XMP packet. | Run `Client.check` on this file to see WatchDoc's decision and flags. |
| `receipt-photo.jpg` | JPEG with EXIF Make, Model, Software, and DateTimeOriginal. | Run `Client.check` on this file to see WatchDoc's decision and flags. |

Regenerate with `python samples/make_samples.py` (or `make samples`).
