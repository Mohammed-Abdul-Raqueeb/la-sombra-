#!/usr/bin/env python3
"""La Sombra — static build. One shell, eight pages, no duplicated chrome."""
import os, re, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))
# Pages must land beside assets/, because every href in the shell is relative to
# them. Writing to a subfolder produces HTML that loads no CSS, JS, fonts or video.
OUT  = ROOT

SITE = {
    "name": "La Sombra",
    "tag": "A coastal estate on the Punta Aloe headland",
    "tel": "+34 971 000 000",
    "mail": "reservas@lasombra.example",
}

NAV = [("estate", "The Estate"), ("rooms", "Rooms"), ("table", "The Table"),
       ("hours", "Hours"), ("journal", "Journal"), ("visit", "Visit")]

# ── the estate's day, used by the dial, the hours page and the shade study ──
HOURS = [
    ("05:40", "First light", "The headland path is opened. Coffee and a thermos are left on the courtyard sill for anyone walking out early.", "sun"),
    ("07:00", "Breakfast begins", "Under the east arcade, which takes the low sun until nine and is out of it after. Bread from the wood oven, fruit from the terraces, eggs if you want them.", "sun"),
    ("09:15", "The gardeners move", "Watering finishes and the crew shifts to the north beds. The pool deck is quiet and already warm.", "sun"),
    ("11:00", "Sea hour", "The boat leaves the cove for the sea caves and returns before the wind turns. Six places, first asked.", "sun"),
    ("13:00", "The long table", "One sitting, one menu, four courses. It runs about two hours and nobody hurries it.", "sun"),
    ("14:30", "Siesta", "The whole estate goes quiet. Shutters are drawn on the west side. Nothing is served, nothing is scheduled.", "shade"),
    ("16:30", "Shade returns west", "The palms throw across the west terrace and it becomes the best seat on the property. Iced tea, cold almonds.", "shade"),
    ("18:20", "Golden hour", "The light comes in flat under the canopy. The bar opens on the lower terrace.", "sun"),
    ("19:45", "Sundown", "From the headland bench, which seats four and is worth walking to.", "sun"),
    ("20:30", "Dinner", "Small plates on the courtyard, or the full menu at the table. Both run until it is finished.", "shade"),
    ("22:30", "Lamps down", "Path lights drop to their lowest setting so the sky comes back. The bar stays open, quietly.", "shade"),
]

ROOMS = [
    dict(slug="arcada", name="Arcada", n="01", size=32, sleeps=2, aspect="East",
         shade="Shaded to 09:00, then again after 15:00", rate=280,
         copy="The original guest rooms, built into the east arcade. Deep reveals, a stone floor that stays cold, and a shuttered door onto the courtyard. Morning light, then out of it for the rest of the day.",
         detail=["Courtyard door", "Stone floor", "Ceiling fan, no air conditioning", "Bath with window"]),
    dict(slug="mirador", name="Mirador", n="02", size=44, sleeps=2, aspect="North-west",
         shade="Shaded to 13:00", rate=395,
         copy="Two rooms on the upper floor with the long view down the headland. They take the afternoon sun full on, which is either the reason to book them or the reason not to.",
         detail=["Headland view", "Private balcony", "Deep bath", "Writing desk"]),
    dict(slug="palmar", name="Palmar", n="03", size=38, sleeps=2, aspect="South",
         shade="Shaded all day by the old palms", rate=340,
         copy="Set among the forty-one palms that gave the estate its name. The canopy holds the sun off from morning to evening, so the room stays several degrees cooler than anything else here.",
         detail=["Under the canopy", "Outdoor shower", "Hammock terrace", "Coolest rooms on the estate"]),
    dict(slug="cisterna", name="Cisterna", n="04", size=52, sleeps=3, aspect="West",
         shade="Full sun to 16:30, shaded after", rate=460,
         copy="Built over the estate's original water cistern, which is why the walls are a metre thick and the ground floor never gets warm. A sitting room, a bedroom, and a small court of its own.",
         detail=["Two rooms", "Private court", "Metre-thick walls", "Sleeps three"]),
    dict(slug="huerta", name="Huerta", n="05", size=48, sleeps=4, aspect="East",
         shade="Shaded to 10:00 and after 14:00", rate=430,
         copy="At the top of the kitchen garden, away from the main house. Two bedrooms and a long table outside under a reed roof. The one to take if you are travelling with people you actually like.",
         detail=["Two bedrooms", "Reed-roof terrace", "Garden kitchen", "Sleeps four"]),
    dict(slug="casa-punta", name="Casa Punta", n="06", size=96, sleeps=6, aspect="All",
         shade="Shaded terraces at every hour", rate=980,
         copy="The far house on the point, ten minutes' walk from everything. Three bedrooms, a kitchen that works, and terraces on four sides so there is always one out of the sun. Booked whole.",
         detail=["Three bedrooms", "Full kitchen", "Terraces on four sides", "Ten minutes from the main house"]),
]

TABLE = [
    ("Breakfast", "07:00 – 10:30", "East arcade",
     "Bread from the wood oven, whatever the terraces gave up that morning, yoghurt, honey from the north beds. Eggs and jamón if you ask. No buffet and no menu card.",
     ["Wood-oven bread", "Terrace fruit", "Honey from the estate", "Coffee, properly made"]),
    ("The long table", "13:00, one sitting", "The courtyard",
     "Four courses, one menu, everyone at once. Rosa decides it on the morning of and writes it on the board by the kitchen door. Vegetables lead; fish arrives when the cove boats come in.",
     ["One sitting a day", "Menu set that morning", "Fish from the cove", "Around two hours"]),
    ("Dinner", "20:30 until it is finished", "Courtyard or the table",
     "Small plates outside if the evening is good, the full menu inside if it is not. The kitchen closes when the last table is done, not at a time printed somewhere.",
     ["Small plates or full menu", "Estate wine list", "Kitchen closes late", "Children welcome"]),
]

JOURNAL = [
    dict(slug="journal-shade", date="12 August", read="9 min", kicker="Building",
         title="Shade is architecture, not decoration",
         standfirst="Every wall on this estate was placed by watching where the palms already fell. That is a slower way to build and it is the only one that works here.",
         feature=True),
    dict(slug=None, date="28 July", read="4 min", kicker="The Table",
         title="Rosa will not tell you the menu in advance",
         standfirst="Twelve years of cooking here and she has never once written it down more than four hours ahead."),
    dict(slug=None, date="9 July", read="6 min", kicker="The Land",
         title="Forty-one palms and what they cost",
         standfirst="A count of every tree on the headland, what each one needs in water, and why we planted nine more this spring."),
    dict(slug=None, date="21 June", read="5 min", kicker="Water",
         title="The cistern still works",
         standfirst="The estate's 1890s rainwater system was never decommissioned. Last winter it took thirty per cent of our load."),
    dict(slug=None, date="3 June", read="7 min", kicker="The Sea",
         title="A short guide to the cove, and when not to swim in it",
         standfirst="The current turns about an hour after the wind does. Here is how to read it from the bench."),
    dict(slug=None, date="17 May", read="3 min", kicker="Rooms",
         title="Why there is no air conditioning",
         standfirst="Thick walls, cross draught, shutters and shade get us to twenty-four degrees in August. The plant would have cost more than the roof."),
]

FAQS = [
    ("When should we come?",
     "April to June and September to early November. July and August are hot enough that most of the day is spent under the canopy, which some people come specifically for and others find limiting. December to February is mild, green and very quiet."),
    ("Is there air conditioning?",
     "No. The walls are between sixty centimetres and a metre thick, every room has cross ventilation and shutters, and the planting is arranged to keep the sun off the building. Rooms sit around twenty-four degrees through August. There are ceiling fans in every room."),
    ("How do we get here?",
     "The nearest airport is fifty minutes by road. We will send a car if you tell us your flight, and it is the same price as a taxi. There is no public transport to the headland and the last two kilometres are a private track."),
    ("Can we bring children?",
     "Yes, and they are welcome at every service including the long table. Huerta and Casa Punta are the two houses that suit families. The cove is unsupervised and the current turns, so children swim with an adult."),
    ("Do you take single-night bookings?",
     "Not between May and October, when the minimum is three nights, or five over the August fortnight. Out of season we take single nights whenever there is a gap."),
    ("Is the estate accessible?",
     "Partly, and we would rather be straight about it. Arcada and Cisterna are step-free from the car court, and the courtyard, the arcade and the table are all level. The upper rooms, the headland path and the cove are not. Call us and we will tell you honestly whether it will work."),
]

RATES = [
    ("Arcada", "280", "340", "220"), ("Palmar", "340", "410", "270"),
    ("Mirador", "395", "480", "310"), ("Huerta", "430", "520", "340"),
    ("Cisterna", "460", "560", "365"), ("Casa Punta", "980", "1,180", "780"),
]

# ══════════════════════════════════════════════════════════════════════════
#  shell
# ══════════════════════════════════════════════════════════════════════════
def shell(slug, title, desc, body, extra_class="", scripts=""):
    nav = "".join(
        '<li><a href="%s.html"%s>%s</a></li>' % (s, ' aria-current="page"' if s == slug else "", l)
        for s, l in NAV)
    sheet = "".join(
        '<li><a href="%s.html"><span>%s</span></a></li>' % (s, l) for s, l in NAV)
    foot_nav = "".join('<li><a href="%s.html">%s</a></li>' % (s, l) for s, l in NAV)

    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{H.escape(title)} — {SITE['name']}</title>
<meta name="description" content="{H.escape(desc)}">
<meta name="theme-color" content="#F2EEE7">
<meta property="og:title" content="{H.escape(title)} — {SITE['name']}">
<meta property="og:description" content="{H.escape(desc)}">
<meta property="og:type" content="website">
<link rel="preload" href="assets/fonts/instrument-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/site.css">
<script>document.documentElement.className="js";</script>
</head>
<body class="{extra_class}" data-page="{slug}">
<a class="skip" href="#main">Skip to content</a>

<header class="bar" id="bar">
  <a class="mark" href="index.html" aria-label="{SITE['name']}, home">
    <svg class="mark__g" width="26" height="26" viewBox="0 0 26 26" aria-hidden="true" focusable="false">
      <circle cx="13" cy="13" r="5.4" fill="none" stroke="currentColor" stroke-width="1.3"/>
      <path d="M13 1.4v3.2M13 21.4v3.2M1.4 13h3.2M21.4 13h3.2M4.8 4.8l2.3 2.3M18.9 18.9l2.3 2.3M21.2 4.8l-2.3 2.3M7.1 18.9l-2.3 2.3"
            stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    <span class="mark__w">La&nbsp;Sombra</span>
  </a>

  <nav class="bar__nav" aria-label="Primary"><ul>{nav}</ul></nav>

  <a class="dial" href="hours.html" id="dial" title="The estate's day">
    <svg class="dial__arc" width="46" height="26" viewBox="0 0 46 26" aria-hidden="true" focusable="false">
      <path d="M3 23a20 20 0 0 1 40 0" fill="none" stroke="currentColor" stroke-width="1.1" opacity=".28"/>
      <path id="dialTrack" d="M3 23a20 20 0 0 1 40 0" fill="none" stroke="currentColor" stroke-width="1.3"/>
      <circle id="dialSun" cx="3" cy="23" r="3.1" fill="currentColor"/>
    </svg>
    <span class="dial__t"><b id="dialTime">—</b><i id="dialNow">the estate's day</i></span>
  </a>

  <a class="btn btn--sm" href="visit.html#enquire">Enquire</a>

  <button class="burger" id="burger" aria-expanded="false" aria-controls="sheet" aria-label="Open menu">
    <span></span><span></span>
  </button>
</header>

<div class="sheet" id="sheet" hidden>
  <nav aria-label="Mobile"><ul>{sheet}</ul></nav>
  <a class="btn btn--block" href="visit.html#enquire">Enquire</a>
  <p class="sheet__c">{SITE['tel']}<br>{SITE['mail']}</p>
</div>

<main id="main">
{body}
</main>

<footer class="foot">
  <div class="wrap foot__top">
    <div class="foot__brand">
      <p class="foot__mk">La Sombra</p>
      <p class="foot__tag">{SITE['tag']}. Fourteen rooms, forty-one palms,<br>one sitting at the long table.</p>
      <a class="btn btn--ghost" href="visit.html#enquire">Ask about a stay</a>
    </div>
    <div class="foot__cols">
      <div><h2>Visit</h2><ul>{foot_nav}</ul></div>
      <div><h2>Reach us</h2><ul>
        <li><a href="tel:{SITE['tel'].replace(' ','')}">{SITE['tel']}</a></li>
        <li><a href="mailto:{SITE['mail']}">{SITE['mail']}</a></li>
        <li><span>Punta Aloe headland</span></li>
        <li><span>Reception 08:00 – 22:00</span></li>
      </ul></div>
      <div><h2>The day</h2><ul>
        <li><span>Breakfast 07:00</span></li>
        <li><span>Long table 13:00</span></li>
        <li><span>Siesta 14:30</span></li>
        <li><span>Dinner 20:30</span></li>
      </ul></div>
    </div>
  </div>
  <div class="wrap foot__base">
    <p>© 2026 La Sombra</p>
    <p class="foot__fine">Concept site. La Sombra is a fictional estate; the canopy
      footage is the single asset supplied with the brief, regraded and reframed for each page.</p>
  </div>
</footer>

<script src="assets/js/site.js" defer></script>{scripts}
</body>
</html>
"""

# ── small builders ────────────────────────────────────────────────────────
def head_block(kind, eyebrow, title, lede, extra=""):
    """kind: light | shade | still"""
    media = ""
    if kind == "shade":
        media = ('<div class="phead__media"><video class="phead__v" muted loop playsinline '
                 'preload="none" data-src="assets/media/shade-1600.mp4" '
                 'poster="assets/media/poster-shade.webp" aria-hidden="true" tabindex="-1"></video>'
                 '<div class="phead__scrim"></div></div>')
    elif kind == "still":
        media = '<div class="phead__media phead__media--still"></div>'
    return f"""<section class="phead phead--{kind}">
  {media}
  <div class="wrap phead__in">
    <p class="eyebrow reveal">{eyebrow}</p>
    <h1 class="phead__h reveal">{title}</h1>
    <p class="lede reveal">{lede}</p>
    {extra}
  </div>
</section>"""


def build():
    pages = {}

    # ══ HOME ═══════════════════════════════════════════════════════════════
    room_teasers = "".join(f"""
      <article class="rcard">
        <a href="rooms.html#{r['slug']}">
          <span class="rcard__n">{r['n']}</span>
          <h3>{r['name']}</h3>
          <p>{r['shade']}</p>
          <span class="rcard__m">{r['size']} m² · sleeps {r['sleeps']} · from €{r['rate']}</span>
        </a>
      </article>""" for r in ROOMS[:3])

    now_rows = "".join(f"""
      <li class="tl__row" data-hour="{h[0]}">
        <span class="tl__t">{h[0]}</span>
        <span class="tl__n">{h[1]}</span>
        <span class="tl__d">{h[2]}</span>
      </li>""" for h in HOURS[:5])

    pages["index"] = shell("index", "A house built around the shade it makes",
        "La Sombra is a fourteen-room coastal estate on the Punta Aloe headland, built around the shade its palms make.",
        f"""
<section class="hero">
  <div class="hero__media">
    <video class="hero__v" id="heroVideo" muted loop playsinline autoplay disablepictureinpicture
           preload="none" tabindex="-1"></video>
    <div class="hero__scrim"></div>
  </div>
  <div class="wrap hero__in">
    <h1 class="hero__h">
      <span class="ln"><span>A house built</span></span>
      <span class="ln"><span>around the shade</span></span>
      <span class="ln"><span>it makes.</span></span>
    </h1>
    <p class="hero__lede">Fourteen rooms on the Punta Aloe headland. The palms were here first;
      everything since has been placed to sit under them.</p>
    <div class="hero__acts">
      <a class="btn" href="rooms.html">See the rooms</a>
      <a class="btn btn--line" href="hours.html">The estate's day</a>
    </div>
  </div>
  <button type="button" class="motion" id="motionBtn" aria-pressed="true" aria-label="Background video">
    <span class="motion__d"></span><span id="motionLabel">Playing</span>
  </button>
</section>

<section class="band band--sun">
  <div class="wrap two">
    <div class="two__l">
      <p class="eyebrow reveal">The place</p>
      <h2 class="reveal">Nine hectares, most of it left alone.</h2>
    </div>
    <div class="two__r">
      <p class="lede reveal">The estate was a working coconut and citrus farm until 1974 and a
        ruin for thirty years after that. We kept the cistern, the arcade and every palm that
        was still standing, and put the new building where the shade already fell.</p>
      <p class="reveal">There are fourteen rooms across five buildings, one kitchen, one sitting
        at the long table, and no reception desk to speak of. Nothing here is scheduled that
        does not need to be.</p>
      <dl class="facts reveal">
        <div><dt>Rooms</dt><dd>14</dd></div>
        <div><dt>Palms</dt><dd>41</dd></div>
        <div><dt>Hectares</dt><dd>9</dd></div>
        <div><dt>Since</dt><dd>2011</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="band band--shade">
  <div class="wrap">
    <blockquote class="pull reveal">
      <p>In a hot country the expensive thing is not the view. It is somewhere cool
        to sit at three in the afternoon.</p>
      <footer>— Rosa Iriarte, who has run the kitchen since 2013</footer>
    </blockquote>
  </div>
</section>

<section class="band band--sun">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">Rooms</p><h2 class="reveal">Six kinds of room, told apart by their shade.</h2></div>
      <p class="lede reveal">Every room here is described by which hours it is out of the sun,
        because on this headland that matters more than the square metres.</p>
    </header>
    <div class="rgrid">{room_teasers}</div>
    <p class="more reveal"><a href="rooms.html">All six rooms and their rates</a></p>
  </div>
</section>

<section class="band band--sun band--tight">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">The day</p><h2 class="reveal">It runs to the sun, not the clock.</h2></div>
      <p class="lede reveal">The estate keeps solar time. Meals, the boat and the siesta all move
        through the year with sunrise.</p>
    </header>
    <ol class="tl">{now_rows}</ol>
    <p class="more reveal"><a href="hours.html">The whole day, hour by hour</a></p>
  </div>
</section>

<section class="cta">
  <div class="wrap cta__in">
    <h2 class="reveal">Tell us when, and we will tell you which room.</h2>
    <p class="lede reveal">We answer enquiries ourselves, usually the same day, and we will say
      so plainly if we think another time of year would suit you better.</p>
    <a class="btn btn--lg" href="visit.html#enquire">Ask about a stay</a>
  </div>
</section>
""", scripts='\n<script>window.SOMBRA_HERO=1;</script>')

    # ══ ESTATE ═════════════════════════════════════════════════════════════
    pages["estate"] = shell("estate", "The Estate",
        "Nine hectares on the Punta Aloe headland: the land, the buildings, the water, and an interactive study of where the shade falls.",
        head_block("shade", "The Estate", "Everything here was placed by watching a shadow.",
            "Nine hectares, five buildings, forty-one palms and a rainwater cistern from the 1890s "
            "that still carries a third of our load.") + """
<section class="band band--sun">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">The land</p><h2 class="reveal">A farm, then a ruin, then this.</h2></div>
    <div class="two__r">
      <p class="lede reveal">Coconut and citrus until 1974. Abandoned for thirty years, which is
        the only reason the palms survived — nobody was here to clear them.</p>
      <p class="reveal">When we started in 2009 the arcade was standing, the cistern was intact
        and the rest was rubble. We spent the first summer doing nothing but recording where the
        shade fell, hour by hour, through June and August. The plan came out of that survey and
        not the other way round.</p>
      <p class="reveal">Two of the five buildings sit on old footings. The other three were sited
        to catch the canopy at the hours people actually use them: breakfast in the east arcade,
        the long table in the courtyard, and the west terrace held for late afternoon.</p>
    </div>
  </div>
</section>

<section class="band band--shade" id="shade-study">
  <div class="wrap">
    <header class="head head--inv">
      <div><p class="eyebrow reveal">Shade study</p><h2 class="reveal">Where to sit, at any hour.</h2></div>
      <p class="lede reveal">Move the sun through the day and watch it fall. This is the same
        survey we built the estate from, simplified to the five places you are most likely to want.</p>
    </header>

    <div class="study">
      <figure class="study__plan">
        <svg id="planSvg" viewBox="0 0 760 520" role="img"
             aria-label="Plan of the estate showing where shadows fall at the selected hour.">
          <defs>
            <linearGradient id="grndG" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#2A6076"/><stop offset="100%" stop-color="#1E4859"/>
            </linearGradient>
          </defs>
          <rect x="0" y="0" width="760" height="520" fill="url(#grndG)"/>
          <g id="planShadows"></g>
          <g id="planBuild"></g>
          <g id="planZones"></g>
          <g id="planPalms"></g>
          <g id="planLabels"></g>
        </svg>
        <figcaption class="study__cap">Plan looking down. Solid blocks are buildings, circles are
          palm canopies. Shadow lengths are computed from the sun's altitude at the hour shown.</figcaption>
      </figure>

      <div class="study__panel">
        <div class="study__read">
          <span class="study__hr" id="studyHour">14:00</span>
          <span class="study__alt" id="studyAlt">sun 58° above the horizon</span>
        </div>
        <label class="study__ctl" for="sunTime">
          <span>Hour of day</span>
          <input id="sunTime" type="range" min="5" max="21.5" step="0.25" value="14"
                 aria-describedby="studyList">
        </label>
        <ul class="study__list" id="studyList" aria-live="polite"></ul>
        <p class="study__note">Computed for 21 June, the worst case. In April and October the
          shaded hours run roughly forty minutes longer at each end.</p>
      </div>
    </div>
  </div>
</section>

<section class="band band--sun">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">Building</p><h2 class="reveal">Four materials, chosen for temperature.</h2></div>
      <p class="lede reveal">None of this is a style decision. Each one is here because of what
        it does to the inside of a room in August.</p>
    </header>
    <div class="mats">
      <article class="mat"><h3>Lime-rendered stone</h3><p>Walls between sixty centimetres and a
        metre thick, rendered in lime so they breathe. They take all day to warm through and give
        it back overnight, which is what keeps the rooms at twenty-four degrees.</p></article>
      <article class="mat"><h3>Chestnut shutters</h3><p>Solid, external, on every opening. Shutters
        outside the glass stop the heat before it enters; shutters inside only trap it. Closed by
        the housekeepers at eleven and opened again at six.</p></article>
      <article class="mat"><h3>Reed and cane</h3><p>The terrace roofs are cane laid over chestnut
        poles, cut on the estate. They drop the temperature underneath by five or six degrees and
        are replaced in sections every four years.</p></article>
      <article class="mat"><h3>Unglazed clay floors</h3><p>Fired locally, laid over sand with no
        membrane. They stay cold underfoot and they take up water in the wet months instead of
        sweating it back at you.</p></article>
    </div>
  </div>
</section>

<section class="band band--sun band--tight">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">Water</p><h2 class="reveal">The cistern still works.</h2></div>
    <div class="two__r">
      <p class="lede reveal">The 1890s rainwater system under the west court was never
        decommissioned. We relined it in 2012 and reconnected the roof runs.</p>
      <p class="reveal">Last winter it carried thirty-one per cent of the estate's water. Grey
        water from the rooms goes to the palms and the citrus; the kitchen garden is on drip from
        a second tank. The pool is salt, not chlorine, and it is emptied once a year rather than
        continuously backwashed.</p>
      <dl class="facts reveal">
        <div><dt>Cistern</dt><dd>240 m³</dd></div>
        <div><dt>Of our load</dt><dd>31%</dd></div>
        <div><dt>Relined</dt><dd>2012</dd></div>
        <div><dt>Solar</dt><dd>62 kWp</dd></div>
      </dl>
    </div>
  </div>
</section>
""", scripts='\n<script>window.SOMBRA_STUDY=1;</script>')

    # ══ ROOMS ══════════════════════════════════════════════════════════════
    room_rows = "".join(f"""
    <article class="room" id="{r['slug']}" data-aspect="{r['aspect'].lower()}">
      <div class="room__id"><span class="room__n">{r['n']}</span><h2>{r['name']}</h2></div>
      <div class="room__body">
        <p class="lede">{r['copy']}</p>
        <ul class="room__f">{''.join('<li>%s</li>' % d for d in r['detail'])}</ul>
        <p class="room__cta"><a class="btn btn--line btn--sm" href="visit.html#enquire">Ask about {r['name']}</a></p>
      </div>
      <dl class="room__m">
        <div><dt>Shade</dt><dd>{r['shade']}</dd></div>
        <div><dt>Aspect</dt><dd>{r['aspect']}</dd></div>
        <div><dt>Size</dt><dd>{r['size']} m²</dd></div>
        <div><dt>Sleeps</dt><dd>{r['sleeps']}</dd></div>
        <div><dt>From</dt><dd>€{r['rate']} a night</dd></div>
      </dl>
    </article>""" for r in ROOMS)

    pages["rooms"] = shell("rooms", "Rooms",
        "Six kinds of room across five buildings, each described by the hours it is out of the sun.",
        head_block("light", "Rooms", "Six rooms, told apart by their shade.",
            "Square metres tell you very little on this headland. What matters is which hours a "
            "room is out of the sun, so that is what we lead with.",
            """<div class="filter" role="group" aria-label="Filter rooms by aspect">
      <button type="button" class="filter__b is-on" data-f="all" aria-pressed="true">All six</button>
      <button type="button" class="filter__b" data-f="east" aria-pressed="false">Morning sun</button>
      <button type="button" class="filter__b" data-f="west" aria-pressed="false">Afternoon sun</button>
      <button type="button" class="filter__b" data-f="south" aria-pressed="false">Shaded all day</button>
    </div>
    <p class="filter__count" id="filterCount" aria-live="polite">Showing all six rooms</p>""") + f"""
<section class="band band--sun band--tight">
  <div class="wrap rooms">{room_rows}</div>
</section>

<section class="band band--shade">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">In every room</p><h2 class="reveal">What you get regardless.</h2></div>
    <div class="two__r">
      <ul class="ticks reveal">
        <li>Solid external shutters and cross ventilation</li>
        <li>Ceiling fan; no air conditioning anywhere on the estate</li>
        <li>Linen from a mill two valleys over, changed on the third day</li>
        <li>A filled water jug, refilled twice daily, and no plastic bottles</li>
        <li>Breakfast in the east arcade, included</li>
        <li>No television, and a working radio if you want one</li>
      </ul>
    </div>
  </div>
</section>
""", scripts='\n<script>window.SOMBRA_FILTER=1;</script>')

    # ══ TABLE ══════════════════════════════════════════════════════════════
    services = "".join(f"""
    <article class="svc reveal">
      <div class="svc__h"><h2>{s[0]}</h2><p class="svc__when">{s[1]} · {s[2]}</p></div>
      <p class="lede">{s[3]}</p>
      <ul class="svc__l">{''.join('<li>%s</li>' % x for x in s[4])}</ul>
    </article>""" for s in TABLE)

    pages["table"] = shell("table", "The Table",
        "One kitchen, three services, one sitting at the long table. Rosa Iriarte decides the menu on the morning of.",
        head_block("still", "The Table", "One kitchen. One sitting. No menu card.",
            "Rosa Iriarte has run it since 2013. She writes the day's four courses on the board "
            "by the kitchen door some time around ten, and that is the first anyone knows.") + f"""
<section class="band band--sun band--tight">
  <div class="wrap svcs">{services}</div>
</section>

<section class="band band--shade">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">The garden</p><h2 class="reveal">Two hundred metres from the stove.</h2></div>
    <div class="two__r">
      <p class="lede reveal">The kitchen garden runs up the north slope behind Huerta. It is
        worked by two people and it supplies most of what is on the table between April and
        November.</p>
      <p class="reveal">What we do not grow, we buy within about forty kilometres — fish landed
        in the cove or at the port, lamb from the valley, cheese from a family who have been
        making it longer than we have been here. The wine list is almost entirely from the region
        and the few exceptions are marked as such, with a reason.</p>
      <dl class="facts facts--inv reveal">
        <div><dt>Garden</dt><dd>0.8 ha</dd></div>
        <div><dt>Grown here</dt><dd>~60%</dd></div>
        <div><dt>Sourcing radius</dt><dd>40 km</dd></div>
        <div><dt>Covers a sitting</dt><dd>28</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="band band--sun">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">Eating with us</p><h2 class="reveal">A few things worth knowing.</h2></div>
      <p class="lede reveal">None of this is precious. It is just how a kitchen this size has
        to work if it is going to cook properly.</p>
    </header>
    <div class="mats">
      <article class="mat"><h3>Tell us in advance</h3><p>Allergies, anything you will not eat,
        anyone who needs feeding early. Say it when you book and Rosa builds around it. Told on
        the day, she will manage, but it will be the less interesting plate.</p></article>
      <article class="mat"><h3>The table is shared</h3><p>Lunch is one long table and everyone
        sits at it. If you would rather not, we will lay a small table under the arcade and
        nobody will think anything of it.</p></article>
      <article class="mat"><h3>Children eat the same</h3><p>There is no separate menu. Portions
        are adjusted and the kitchen will always make plain rice and grilled fish for anyone
        who wants it, of any age.</p></article>
      <article class="mat"><h3>Non-residents</h3><p>We keep four places at lunch and two tables
        at dinner for people not staying. Call the kitchen directly, ideally a week out.</p></article>
    </div>
  </div>
</section>
""")

    # ══ HOURS ══════════════════════════════════════════════════════════════
    hour_rows = "".join(f"""
    <li class="hr hr--{h[3]}" data-hour="{h[0]}">
      <span class="hr__t">{h[0]}</span>
      <div class="hr__c"><h2>{h[1]}</h2><p>{h[2]}</p></div>
      <span class="hr__tag">{'in the sun' if h[3]=='sun' else 'in the shade'}</span>
    </li>""" for h in HOURS)

    pages["hours"] = shell("hours", "Hours",
        "The estate keeps solar time. Here is the whole day, from first light to lamps down.",
        head_block("light", "Hours", "The estate keeps solar time.",
            "Everything here moves with sunrise rather than the clock, so these times shift by "
            "about ninety minutes across the year. What does not change is the order.",
            '<div class="bigdial" id="bigDial" aria-hidden="true"></div>') + f"""
<section class="band band--sun band--tight">
  <div class="wrap"><ol class="hrs" id="hrs">{hour_rows}</ol></div>
</section>

<section class="band band--shade">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">Booked separately</p><h2 class="reveal">Four things worth putting in the diary.</h2></div>
    <div class="two__r">
      <ul class="ticks reveal">
        <li><b>The cove boat</b> — 11:00, six places, ninety minutes. Ask at breakfast.</li>
        <li><b>Kitchen morning</b> — Tuesdays and Fridays, 09:00, four people, with Rosa.</li>
        <li><b>The headland walk</b> — 07:30 on Sundays, two hours, guided by whoever is free.</li>
        <li><b>Cellar tasting</b> — 18:30, six regional growers, on request and often at short notice.</li>
      </ul>
    </div>
  </div>
</section>
""", scripts='\n<script>window.SOMBRA_HOURS=1;</script>')

    # ══ JOURNAL ════════════════════════════════════════════════════════════
    feat = JOURNAL[0]
    rest = "".join(f"""
    <article class="post reveal">
      <p class="post__m"><span>{p['kicker']}</span><span>{p['date']}</span><span>{p['read']}</span></p>
      <h2>{'<a href="%s.html">%s</a>' % (p['slug'], p['title']) if p['slug'] else p['title']}</h2>
      <p>{p['standfirst']}</p>
    </article>""" for p in JOURNAL[1:])

    pages["journal"] = shell("journal", "Journal",
        "Notes from the estate: building in the shade, the kitchen, the water, and the sea.",
        head_block("light", "Journal", "Notes from the headland.",
            "Written by whoever did the thing. Published when there is something to say rather "
            "than on a schedule.") + f"""
<section class="band band--sun band--tight">
  <div class="wrap">
    <a class="feature reveal" href="{feat['slug']}.html">
      <p class="post__m"><span>{feat['kicker']}</span><span>{feat['date']}</span><span>{feat['read']}</span></p>
      <h2>{feat['title']}</h2>
      <p class="lede">{feat['standfirst']}</p>
      <span class="feature__go">Read it</span>
    </a>
    <div class="posts">{rest}</div>
  </div>
</section>
""")

    # ══ ARTICLE ════════════════════════════════════════════════════════════
    pages["journal-shade"] = shell("journal-shade", feat["title"], feat["standfirst"], f"""
<article class="art">
  <header class="wrap art__head">
    <p class="post__m reveal"><span><a href="journal.html">Journal</a></span><span>{feat['kicker']}</span><span>{feat['date']}</span><span>{feat['read']}</span></p>
    <h1 class="reveal">{feat['title']}</h1>
    <p class="lede reveal">{feat['standfirst']}</p>
    <p class="art__by reveal">By Nuria Camps, who drew the plan</p>
  </header>

  <div class="art__fig">
    <div class="art__figimg"></div>
    <p class="art__cap">The east arcade at 09:20 in June, about ten minutes before the shade leaves it.</p>
  </div>

  <div class="wrap art__body">
    <p>The first drawing I made of this estate was not a plan. It was a stack of eleven tracing
      sheets, one for every daylight hour, each with the shadows inked in where they fell on
      21 June. I laid them over each other on a light box and the building more or less designed
      itself out of the gaps.</p>

    <p>That sounds like a nice story and it is also literally what happened. We had nine hectares,
      forty-one mature palms and a client brief that amounted to: it must be bearable in August
      without machinery. In this climate that is not a sustainability position, it is an
      engineering constraint. Air conditioning here would have cost more to install than the
      roof and more to run than the staff.</p>

    <h2>Shade is not one thing</h2>

    <p>The mistake people make is treating shade as a binary — a place is in it or out of it.
      It is not. A palm canopy gives dappled shade that drops the air temperature by perhaps
      three degrees and the surface temperature of anything under it by fifteen. A solid roof
      gives deep shade, cooler still, but it also stops the air moving if you build the walls
      wrong. A wall gives you hard shade that is cool for an hour and then gone.</p>

    <p>The east arcade is the clearest example. It takes the low sun straight on until about
      nine, and then the row of palms that were already there takes over for the rest of the day.
      We could have roofed it and had deep shade from dawn. We did not, because that hour of low
      light is the reason people sit there for two hours over breakfast instead of twenty minutes.</p>

    <blockquote><p>We spent the first summer doing nothing but recording where the shadow fell.
      The plan came out of that survey, not the other way round.</p></blockquote>

    <h2>Building to the survey</h2>

    <p>Two of the five buildings sit on old farm footings, so their position was decided in
      about 1890 by someone who understood this ground better than we do. The three new ones
      were placed on the tracing sheets first and on the site second.</p>

    <p>Cisterna went over the old water tank because a metre of stone and a void underneath is
      the best passive cooling available anywhere on the property. Palmar went into the densest
      part of the canopy and is consistently the coolest set of rooms we have — guests notice
      within about a minute of walking in, and we have measured the difference at four degrees
      in the afternoon.</p>

    <p>Mirador is the exception and the argument we had most. It faces north-west, it takes the
      full afternoon, and by the survey it should not exist. It has the view. We built it anyway,
      gave it the thickest shutters on the estate and told the truth about it in the room
      description, which is why the people who book it are never surprised.</p>

    <h2>What we would do differently</h2>

    <p>Plant earlier. The nine palms we put in during the first spring are only now, fifteen
      years on, throwing usable shade. If we were starting again the planting would go in three
      years before the first foundation, and we would site the west terrace two metres further
      back to catch them sooner.</p>

    <p>The other thing is that we drew for June and should have drawn for September. June is the
      extreme, but September is when the estate is fullest and the sun is lower and further
      south. The west terrace loses its shade about forty minutes earlier than the June survey
      implies, and for two weeks in late September the long table gets a strip of sun across
      one end that nobody wants to sit at. We move the table. It is a small failure but it is
      the kind you only find by living in the building.</p>

    <p>Everything else has held. Fifteen summers, no mechanical cooling, and the rooms sit at
      twenty-four degrees when it is thirty-six outside. The palms did that, mostly. We just
      read them carefully and tried not to get in the way.</p>
  </div>

  <div class="wrap art__foot">
    <a class="btn btn--line" href="journal.html">More from the journal</a>
    <a class="btn" href="estate.html#shade-study">See the shade study</a>
  </div>
</article>
""")

    # ══ VISIT ══════════════════════════════════════════════════════════════
    rate_rows = "".join(f"""
      <tr><th scope="row">{r[0]}</th><td>€{r[1]}</td><td>€{r[2]}</td><td>€{r[3]}</td></tr>""" for r in RATES)
    faq_items = "".join(f"""
      <div class="faq__i">
        <h3><button type="button" class="faq__q" aria-expanded="false" aria-controls="faq{i}">{q}<span class="faq__x" aria-hidden="true"></span></button></h3>
        <div class="faq__a" id="faq{i}"><div><p>{a}</p></div></div>
      </div>""" for i, (q, a) in enumerate(FAQS))
    room_opts = "".join('<option value="%s">%s</option>' % (r["name"], r["name"]) for r in ROOMS)

    pages["visit"] = shell("visit", "Visit",
        "Rates, how to get to the Punta Aloe headland, answers to the questions we are actually asked, and an enquiry form.",
        head_block("shade", "Visit", "Three nights is the shortest we would recommend.",
            "It takes about a day and a half to stop looking at your phone. The rest of the "
            "stay is the part you came for.") + f"""
<section class="band band--sun">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">Rates</p><h2 class="reveal">Per room, per night, breakfast included.</h2></div>
      <p class="lede reveal">No resort fee, no service charge and no charge for the boat. Tourist
        tax is €3.30 a person a night and is collected on departure.</p>
    </header>
    <div class="tablewrap reveal">
      <table class="rates">
        <caption class="vh">Nightly rates by room and season</caption>
        <thead><tr><th scope="col">Room</th><th scope="col">Apr–Jun, Sep–Oct</th>
          <th scope="col">Jul–Aug</th><th scope="col">Nov–Mar</th></tr></thead>
        <tbody>{rate_rows}</tbody>
      </table>
    </div>
    <p class="note reveal">Minimum three nights from May to October, five over the August
      fortnight. Out of season we take single nights whenever there is a gap.</p>
  </div>
</section>

<section class="band band--sun band--tight">
  <div class="wrap two">
    <div class="two__l"><p class="eyebrow reveal">Getting here</p><h2 class="reveal">Fifty minutes from the airport, then a private track.</h2></div>
    <div class="two__r">
      <ol class="steps reveal">
        <li><b>Fly in</b><p>The nearest airport is fifty minutes by road. Most people arrive
          mid-afternoon, which works well — you will be at the west terrace by the time it turns.</p></li>
        <li><b>Let us send a car</b><p>Tell us the flight and we will meet it. €70 each way,
          the same as a taxi, and the driver knows the track.</p></li>
        <li><b>Or drive</b><p>Two hours from the city on good road. The last two kilometres are
          our track — passable in anything, slowly. There is parking in the car court.</p></li>
        <li><b>Arriving late</b><p>There is no night reception. If you land after ten, say so and
          we will leave the room open, a key on the sill and something cold in the fridge.</p></li>
      </ol>
    </div>
  </div>
</section>

<section class="band band--sun band--tight">
  <div class="wrap">
    <header class="head">
      <div><p class="eyebrow reveal">Questions</p><h2 class="reveal">The ones we are actually asked.</h2></div>
      <p class="lede reveal">Including the two we would rather answer here than in an email
        after you have booked.</p>
    </header>
    <div class="faq" id="faq">{faq_items}</div>
  </div>
</section>

<section class="band band--shade" id="enquire">
  <div class="wrap">
    <header class="head head--inv">
      <div><p class="eyebrow reveal">Enquire</p><h2 class="reveal">Write to us and a person will reply.</h2></div>
      <p class="lede reveal">Usually the same day, always within two. If we think a different
        month would suit you better, we will say so.</p>
    </header>

    <form class="form" id="enquiry">
      <div class="form__grid">
        <p class="f"><label for="fName">Your name</label>
          <input id="fName" name="name" type="text" autocomplete="name" required></p>
        <p class="f"><label for="fMail">Email</label>
          <input id="fMail" name="email" type="email" autocomplete="email" required></p>
        <p class="f"><label for="fFrom">Arriving</label>
          <input id="fFrom" name="from" type="date"></p>
        <p class="f"><label for="fNights">Nights</label>
          <input id="fNights" name="nights" type="number" min="1" max="30" value="4"></p>
        <p class="f"><label for="fRoom">Room, if you have a preference</label>
          <select id="fRoom" name="room"><option value="">No preference</option>{room_opts}</select></p>
        <p class="f"><label for="fPeople">People</label>
          <input id="fPeople" name="people" type="number" min="1" max="12" value="2"></p>
        <p class="f f--wide"><label for="fMsg">Anything we should know</label>
          <textarea id="fMsg" name="message" rows="4" placeholder="Allergies, an anniversary, arriving late, travelling with children — whatever is useful."></textarea></p>
      </div>
      <div class="form__foot">
        <button class="btn btn--lg" type="submit">Send the enquiry</button>
        <p class="form__note">We will only use this to answer you. No list, no newsletter.</p>
      </div>
      <noscript><p class="form__note">This form needs JavaScript. Write to
        <a href="mailto:{SITE['mail']}">{SITE['mail']}</a> or call {SITE['tel']} instead.</p></noscript>
      <p class="form__ok" id="formOk" role="status" hidden></p>
    </form>
  </div>
</section>
""", scripts='\n<script>window.SOMBRA_VISIT=1;</script>')

    # ── write ─────────────────────────────────────────────────────────────
    probe = os.path.join(OUT, "assets", "css", "site.css")
    if not os.path.isfile(probe):
        raise SystemExit(
            "build.py could not find assets/ beside itself.\n"
            "  expected: %s\n"
            "Keep build.py in the project root, next to assets/, and run it from there.\n"
            "Pages written anywhere else cannot resolve their own stylesheet." % probe)

    n = 0
    for slug, doc in pages.items():
        with open(os.path.join(OUT, slug + ".html"), "w") as f:
            f.write(doc)
        n += 1
    print("built %d pages into %s" % (n, OUT))
    for slug in sorted(pages):
        p = os.path.join(OUT, slug + ".html")
        print("  %-20s %6.1f KB" % (slug + ".html", os.path.getsize(p) / 1024))
    print("open index.html from that folder; assets/ must stay beside it.")


if __name__ == "__main__":
    build()
