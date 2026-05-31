# Gallery Exhibits — Design

**Date:** 2026-05-31
**Status:** Approved (verbal "go")

## Problem

ArtMap catalogs public art as a flat list of artworks (murals, sculptures) plus
venue records (`type: gallery` / `studio`). There is no way to represent a
**rotational exhibit** — a time-bounded show hosted *inside* a gallery venue
(e.g. Doug Hinebaugh's photography show "One City, Many Moments" at the Toledo
School for the Arts). We also have permanent indoor installations (the "Unity"
sculpture in the TSA lobby) that belong to a venue rather than the street map.

## Decisions

- **Exhibit = one record**, not one record per member work. Member photos live
  as images on the exhibit.
- **Exhibits are children of a gallery venue** (chosen storage: **Approach A —
  nested array on the gallery record**).
- **Past exhibits are kept**, surfaced with a "Past" label. Exhibits therefore
  carry run dates.
- **One gallery pin.** Exhibits inherit the gallery's coordinates; they never
  produce their own map markers. This is guaranteed structurally because exhibit
  data is nested, never a top-level record.

## Data model

A `gallery`/`studio` record gains an optional `exhibits[]` array. Each exhibit:

```json
{
  "id": "tsa-one-city-many-moments",
  "title": "One City, Many Moments",
  "artist": "Doug Hinebaugh",
  "start": null,
  "end": null,
  "status": "past",
  "note": "Need info: exact run dates",
  "description": "...",
  "images": ["images/tsa-one-city-many-moments-01.jpg", "..."]
}
```

Field semantics:

- `start` / `end` — `YYYY-MM` or `YYYY-MM-DD`, or `null` when unknown.
- `end: null` (with no explicit `status`) → **permanent / ongoing** installation
  (e.g. the Unity sculpture). This is how permanent pieces live under a gallery
  without a separate concept.
- `status` (optional) — explicit override: `"past" | "on-view" | "upcoming" |
  "permanent"`. Used when dates are unknown but the state is known.

### Status derivation (render time)

1. If `status` is explicitly set → use it.
2. Else if `end === null` → `permanent`.
3. Else compare today against `start`/`end`, padding month-precision values to
   month bounds (`YYYY-MM` start → `-01`, end → `-31`):
   - `today > endBound` → `past`
   - `today < startBound` → `upcoming`
   - otherwise → `on-view`

Nothing about status is stored except the optional override, so it can't go
stale.

## Rendering (`index.html`)

1. In `renderArtworks`, flatten each gallery's `exhibits[]` into image entries
   `{ src, source: 'exhibit', exhibitTitle, exhibitArtist, status, dateRange }`
   and append them to the card's existing `gallery` image array (after curator
   and submission images). The `📷 N` photo-count badge already keys off
   `gallery.length`, so it updates automatically.
2. Extend the lightbox (`buildLightboxList` / `showLightboxItem`) to pass through
   the exhibit fields. For `source === 'exhibit'`, the caption shows an exhibit
   pill (`title · artist`) plus a status sub-label (`Past exhibit`, `On view`,
   month range when known), mirroring the existing "Public submission" pill.
   Exhibit images override the card's title/artist in the caption with the
   exhibit's own.
3. **Map: unchanged.** Exhibits are nested, so no new markers — "one gallery pin"
   holds by construction.

## First data populated by this work

- New gallery **Toledo School for the Arts** (`type: gallery`, ~41.657, −83.543)
  with:
  - `exhibits[0]` — "One City, Many Moments" by Doug Hinebaugh (`status: past`):
    framed photographs + "you will do better…" neon skyline.
  - `exhibits[1]` — "Unity" rainbow stacked-disc lobby sculpture (`end: null`,
    permanent).
  - `exhibits[2]` — "The Next Big Thing" donor wall + abstract panel (`end:
    null`, permanent).

## Out of scope (YAGNI)

- No standalone exhibit pages or routes.
- No exhibit filter chips.
- Existing `#12` / `#17` "Various works" records are **not** migrated to the new
  exhibit shape in this pass.
