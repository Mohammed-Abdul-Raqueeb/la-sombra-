# La Sombra — concept site

A fourteen-room coastal estate. Eight pages, no build step required to view,
no dependencies, no framework.

## Open it

Unzip the whole folder first, then open `index.html`.
`index.html` on its own will render unstyled — the stylesheet, script, fonts
and video all live in the sibling `assets/` folder.

To serve it locally instead:

    python3 -m http.server 8000

then visit http://localhost:8000

## Pages

| file | what it is |
|---|---|
| `index.html` | home, full-bleed canopy video |
| `estate.html` | the land, materials, water, and the interactive shade study |
| `rooms.html` | six rooms, filterable by aspect |
| `table.html` | the kitchen and its three services |
| `hours.html` | the whole day, 05:40 to 22:30, with a live solar dial |
| `journal.html` | index of six pieces |
| `journal-shade.html` | one full long-form article |
| `visit.html` | rates, travel, FAQ, enquiry form |

## Rebuilding the HTML

The eight pages are generated from one template so the header, nav and footer
cannot drift apart. `build.py` holds both the template and all the copy.

    cd la-sombra
    python3 build.py

It rewrites the eight `.html` files **in this folder**, beside `assets/`, and
touches nothing inside `assets/`. It has to write here: every path in the pages
is relative, so HTML generated into a subfolder would load no CSS, JS, font or
video. If `assets/` is not next to `build.py` the script stops with an error
rather than producing pages that cannot find their own stylesheet.

## Assets

Every video is derived from a single supplied clip of a palm canopy:

| file | what it is |
|---|---|
| `canopy-1920.mp4` | hero loop, desktop |
| `canopy-1280.mp4` | hero loop, laptop and tablet |
| `canopy-mobile.mp4` | hero loop, purpose-built 4:5 portrait reframe |
| `shade-1600.mp4` | cold desaturated regrade, used as a dark band header |
| `*.webp` | posters and one bleached still |

All four loops are seamless: the tail is crossfaded over the head, because the
camera drifts and a hard cut would pop.

Fonts are self-hosted and subsetted. Fraunces is instanced with `opsz 96`,
`SOFT 12` and `WONK 1` pinned so only the weight axis ships.

## Opening it straight off disk

Everything works from `file://` — stylesheet, fonts, script, video. Your console
will show two CORS lines about the `.woff2` preloads on each page. That is
expected: a `file://` page has a null origin, so the browser refuses the
*preload*, while `@font-face` still fetches the same files and both typefaces
render. The preload is kept because it saves a round trip on the font path when
the site is actually hosted. Serving over `http://` removes the messages.

## Notes

La Sombra is fictional. The canopy footage is the single asset supplied with
the brief, regraded and reframed for each page.
