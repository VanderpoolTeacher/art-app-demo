# Artwork Type Filter — Design

**Date:** 2026-05-21
**Author:** Michael (with Claude)
**Scope:** Add filter chips above the discovery grid so visitors can show only one artwork type at a time. The same selection drives the map: only markers of the chosen type stay visible.

## Goal

Let visitors narrow the discovery grid (and map) to one artwork type — Murals, Galleries, Sculptures, or Studios — without leaving the page.

## User experience

A single row of pill-shaped buttons sits between the hero carousel and the discovery grid:

```
[ All ] [ Murals ] [ Galleries ] [ Sculptures ] [ Studios ]
```

- `All` is selected on page load.
- Exactly one chip is active at a time (single-select).
- Active chip = solid coral background; inactive = outlined, matching the existing `.filter-btn` style elsewhere in `index.html`.
- Clicking a chip immediately:
  - hides every grid card whose `data-type` ≠ selected,
  - hides every map marker whose stored type ≠ selected.
- The hero carousel is unaffected — it keeps cycling through all artworks as a showcase.
- No URL / localStorage persistence. Refresh resets to `All`.

## Type handling

The catalog contains five types: `mural`, `gallery`, `sculpture`, `studio`, `textile`. The chip row covers only the first four. The lone textile entry (id 17, "Mark J. Bevington Collection") is visible under `All` but hidden by every type-specific chip. This is acceptable — when more textile entries land, a fifth chip can be added.

## Implementation surface

Single file: `index.html`. No new files, no new dependencies.

### HTML (~6 lines)

Insert above the discovery grid (currently rendered into `#artworkCategories`). Lives inside the `renderArtworks()` template, just before `<div class="discovery-grid">`:

```html
<div class="type-filter" role="tablist">
  <button class="filter-btn active" data-type-filter="all">All</button>
  <button class="filter-btn" data-type-filter="mural">Murals</button>
  <button class="filter-btn" data-type-filter="gallery">Galleries</button>
  <button class="filter-btn" data-type-filter="sculpture">Sculptures</button>
  <button class="filter-btn" data-type-filter="studio">Studios</button>
</div>
```

### CSS (~12 lines)

A scoped `.type-filter` rule (flex row, gap, wraps on mobile) plus tweaks if any of the existing `.filter-btn` rules cascade unfavorably. A `.discovery-empty` rule for the zero-results state.

### JS (~30 lines)

1. When building each card in `renderArtworks()`, add `data-type="${art.type}"` to the `.artwork-card` element.
2. When building each map marker, store `{marker, type}` in a `markersByType` map keyed by type.
3. Add a single `applyTypeFilter(type)` function that:
   - Toggles `.active` on chips.
   - Iterates `.artwork-card` and toggles `display:none` based on `data-type` match.
   - Iterates `markersByType` and `map.addLayer` / `map.removeLayer` based on match.
   - If zero cards visible in the grid, shows the empty-state message; otherwise hides it.
4. Wire one delegated click handler on `.type-filter` that reads `data-type-filter` and calls `applyTypeFilter`.

## Edge cases

- **Empty result:** if zero cards match, show a single inline message inside the grid container: "No artworks of this type yet." Hide it whenever any card is visible.
- **Map popup open when filter changes:** Leaflet auto-closes popups on `removeLayer`. No extra handling needed.
- **Hero carousel** stays untouched — its `recentArt` / `restArt` ordering is independent of the filter.
- **NEW badge:** Per-card. Filter just hides cards; visible NEW badges remain visible on matching cards.

## Out of scope (YAGNI)

- Multi-select chips.
- Chip counts (`Murals (8)`).
- Persisting filter state across reloads.
- Filtering the hero carousel or the self-guided tour view.
- A `Textiles` chip (defer until more textile entries exist).

## Testing

This is a static HTML / vanilla-JS app with no test harness. Manual verification:

1. Open `index.html` in a browser.
2. Confirm chip row appears between the hero carousel and the discovery grid.
3. Click each chip in turn; confirm:
   - Only matching cards remain in the grid.
   - Only matching markers remain on the map.
   - Hero carousel is unchanged.
   - Active chip styling updates.
4. Click `All` — all cards and markers return.
5. Filter to a type with zero entries (if forcing — e.g. temporarily change all `type` values in the JSON); confirm the empty-state message renders.
6. Refresh — confirm filter resets to `All`.
