# Magnifiq Search

<img src="https://github.com/lez/magnifiq/blob/master/public/image/logo.png\?raw=true" alt="logo" width="500"/>

This is a Nostr search engine based on Nostr.
Its aim is to help discover Nostr apps, services, people, events and other stuff.

Use github issues to report bugs, feature requests, questions, suggestions.

## Setup

This app uses a special relay feature, filtering tags by AND operand. This is added in https://github.com/lez/nostr-rs-relay The feature adds a `"&t"` key in REQ filters, which return results if ALL of its values show up in the `tags` field of an event.

It also uses `kind:30077` trust events specified here: https://github.com/lez/nips/77.md

You must run the relay mentioned above with sqlite backend (default) on `localhost:8080`.
You also need to run `tagserver.py` on `localhost:4000`.

Run magnifiq in dev mode: `vite`.

More info coming soon!

Contact the developer if you feel like: npub1elta7cneng3w8p9y4dw633qzdjr4kyvaparuyuttyrx6e8xp7xnq32cume