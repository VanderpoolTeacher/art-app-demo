# Artwork Type Filter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a row of single-select filter chips above the discovery grid in `index.html` that filters both the grid cards and the Leaflet map markers by artwork type (`mural`, `gallery`, `sculpture`, `studio`).

**Architecture:** Single-file edit to `repo/index.html`. The filter is a small UI affordance plus three JS hooks: (a) tag each rendered grid card with `data-type`, (b) keep map markers in a `markersByType` lookup, (c) one `applyTypeFilter(type)` function wired to a delegated click handler on the chip row. Static state — no URL / localStorage persistence; refresh resets to `All`.

**Tech Stack:** Vanilla HTML/CSS/JS, Leaflet.js (already loaded). No new dependencies. No test harness exists in the repo — verification is manual in a browser, per the spec.

---

## File Structure

Single file modified: `repo/index.html`. Three localized edit regions:
- Around line 2510 (no change yet; reference point).
- Inside the `renderArtworks()` template at ~line 2626 (chip row markup) and ~line 2644 (`data-type` on card).
- Inside the map-build loop at ~line 2682 (track markers by type).
- A new `applyTypeFilter` function + handler near the bottom of the same `<script>` (after the existing card render block).
- CSS additions near the existing `.discovery-grid` styles (~line 723) and `.filter-btn` styles (~line 1420).

No new files. No new dependencies.

---

### Task 1: Tag grid cards with `data-type` and track markers by type

**Files:**
- Modify: `repo/index.html` (template inside `renderArtworks()` around line 2644; map-build loop around line 2682)

This task does the data-layer prep so the filter has something to grab onto. It introduces no visible change.

- [ ] **Step 1: Add `data-type` to each card element**

Locate the `<div class="artwork-card">` line inside the `renderArtworks()` template (currently around line 2644). Change:

```html
<div class="artwork-card">
```

to:

```html
<div class="artwork-card" data-type="${art.type || 'unknown'}">
```

- [ ] **Step 2: Track map markers by type**

Locate the marker-build loop (currently around line 2682, starts with `artworks.forEach(function(art) {`). Just before the loop, add:

```js
    var markersByType = { mural: [], gallery: [], sculpture: [], studio: [], textile: [] };
```

Then inside the loop, after the line that creates `marker` (currently `var marker = L.circleMarker(...).addTo(map);`), add:

```js
      if (markersByType[art.type]) markersByType[art.type].push(marker);
```

Keep the existing `markersById[art.id] = marker;` line untouched — both lookups coexist.

- [ ] **Step 3: Verify in browser**

Open `repo/index.html` in a browser. Open DevTools.

Run in the console:
```js
document.querySelectorAll('.artwork-card[data-type="mural"]').length
```

Expected: a number > 0 (matches the mural count in `data/artworks.json`).

The page should look and behave identically to before this change (no chips yet).

- [ ] **Step 4: Commit**

```bash
cd "/Users/michaelvanderpool/Documents/GitHub/ART APP/repo"
git add index.html
git commit -m "Prep: tag artwork cards with data-type and bucket markers by type"
```

---

### Task 2: Add the chip row HTML + CSS

**Files:**
- Modify: `repo/index.html` (template around line 2626; CSS near line 723 and 1420)

- [ ] **Step 1: Add the chip row markup**

Inside `renderArtworks()`, the grid is built by `categories.innerHTML = `<div class="discovery-grid">…`. Change that line so a `<div class="type-filter">…</div>` precedes the grid div, all inside the same template string:

Find:
```js
    categories.innerHTML = `<div class="discovery-grid">
```

Replace with:
```js
    categories.innerHTML = `
    <div class="type-filter" role="group" aria-label="Filter artworks by type">
      <button class="type-filter-btn active" data-type-filter="all" type="button">All</button>
      <button class="type-filter-btn" data-type-filter="mural" type="button">Murals</button>
      <button class="type-filter-btn" data-type-filter="gallery" type="button">Galleries</button>
      <button class="type-filter-btn" data-type-filter="sculpture" type="button">Sculptures</button>
      <button class="type-filter-btn" data-type-filter="studio" type="button">Studios</button>
    </div>
    <div class="discovery-empty" hidden>No artworks of this type yet.</div>
    <div class="discovery-grid">
```

(Note: `type-filter-btn` is a new class — distinct from the existing `.filter-btn` used on the design-doc page — to avoid cascade surprises.)

- [ ] **Step 2: Add the CSS**

Find the `.discovery-grid {` selector (currently around line 723). Just *before* it, insert:

```css
  .type-filter {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 0 0 18px;
    padding: 0;
  }
  .type-filter-btn {
    font-family: 'Reddit Sans', sans-serif;
    font-size: 0.85rem;
    padding: 8px 18px;
    border-radius: 50px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    background: transparent;
    color: var(--text);
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
  }
  .type-filter-btn:hover {
    border-color: rgba(255, 255, 255, 0.45);
  }
  .type-filter-btn.active {
    background: var(--coral);
    border-color: var(--coral);
    color: #fff;
  }
  .discovery-empty {
    padding: 24px 12px;
    text-align: center;
    color: var(--muted, rgba(255, 255, 255, 0.6));
    font-style: italic;
  }
```

- [ ] **Step 3: Verify in browser**

Reload `repo/index.html`. Expected:
- A row of five pill buttons appears between the hero carousel and the grid.
- "All" is filled coral; the other four are outlined.
- Hovering any inactive chip thickens its border.
- Clicking a chip does nothing yet (no handler) — that comes in Task 3.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Add type-filter chip row markup and styles above discovery grid"
```

---

### Task 3: Wire up `applyTypeFilter` and the click handler

**Files:**
- Modify: `repo/index.html` (add JS after the marker-build loop, before `}` closes `renderArtworks()`)

- [ ] **Step 1: Define `applyTypeFilter` and wire the click handler**

After the marker-build loop in `renderArtworks()` (i.e., after the `artworks.forEach(function(art) { … });` block that creates markers), and before any code that uses `markersById` later, insert:

```js
    // ── Type filter ─────────────────────────────────────────────
    var typeFilterRoot = document.querySelector('.type-filter');
    var emptyMsg = document.querySelector('.discovery-empty');

    function applyTypeFilter(selected) {
      // 1. Update chip active state
      typeFilterRoot.querySelectorAll('.type-filter-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.typeFilter === selected);
      });

      // 2. Filter grid cards
      var visibleCount = 0;
      document.querySelectorAll('.artwork-card').forEach(function(card) {
        var show = selected === 'all' || card.dataset.type === selected;
        card.style.display = show ? '' : 'none';
        if (show) visibleCount++;
      });

      // 3. Filter map markers
      Object.keys(markersByType).forEach(function(t) {
        var shouldShow = selected === 'all' || t === selected;
        markersByType[t].forEach(function(m) {
          if (shouldShow) {
            if (!map.hasLayer(m)) m.addTo(map);
          } else {
            if (map.hasLayer(m)) map.removeLayer(m);
          }
        });
      });

      // 4. Empty state
      emptyMsg.hidden = visibleCount > 0;
    }

    typeFilterRoot.addEventListener('click', function(e) {
      var btn = e.target.closest('.type-filter-btn');
      if (!btn) return;
      applyTypeFilter(btn.dataset.typeFilter);
    });
```

- [ ] **Step 2: Verify each chip in the browser**

Reload. For each chip in turn (`All`, `Murals`, `Galleries`, `Sculptures`, `Studios`), confirm:

| Chip | Grid expectation | Map expectation |
|------|------------------|-----------------|
| All | All cards visible | All markers visible |
| Murals | Only mural cards | Only red markers |
| Galleries | Only gallery cards | Only blue markers |
| Sculptures | Only sculpture cards | Only yellow markers |
| Studios | Only studio cards | Only navy markers |

Also confirm:
- The active chip turns coral and the previous active chip returns to outlined.
- The hero carousel keeps cycling all artworks regardless of chip selection.
- Page refresh returns to `All` (no persistence).

- [ ] **Step 3: Force an empty result to verify empty state**

In DevTools console, run:
```js
applyTypeFilter('textile')
```

Expected: the four named chips all go inactive, the empty-state message "No artworks of this type yet." appears below the chip row, and the grid is empty. (We don't have a `Textiles` chip; this is only to exercise the empty state.)

Click `All` to restore.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Wire applyTypeFilter to filter grid cards and map markers by type"
```

---

### Task 4: Batch in the earlier recent-window fix and push

The 7-day rolling-window fix to `isRecent` (index.html:2511) is already in the working tree from an earlier turn. It should ride along with this feature.

- [ ] **Step 1: Verify the recent-window fix is still uncommitted and untouched**

```bash
git diff index.html | grep -A 2 "isRecent" | head -20
```

Expected: shows the new `const isRecent` body (7-day window) in the diff. If `git status` shows `index.html` as clean, the fix was already committed — skip to Step 3.

- [ ] **Step 2: Commit the recent-window fix**

```bash
git add index.html
git commit -m "Extend NEW badge window from 2 days to 7 days for recent submissions"
```

- [ ] **Step 3: Commit the spec and plan docs**

```bash
git add docs/superpowers/specs/2026-05-21-artwork-type-filter-design.md \
        docs/superpowers/plans/2026-05-21-artwork-type-filter.md
git commit -m "Add design spec and implementation plan for artwork type filter"
```

- [ ] **Step 4: Push to origin/main**

```bash
git push origin main
```

Expected: clean push, no rejections. `git status` after should report "Your branch is up to date with 'origin/main'."

---

## Verification summary (what counts as done)

- Chip row visible above the discovery grid with five pills.
- Clicking each named chip narrows both grid and map to that single type; `All` restores everything.
- Hero carousel is unaffected by chip selection.
- Empty-state message renders when forced (no real type yields zero today).
- Active chip styling reflects current selection.
- NEW badges still appear on entries within the 7-day window.
- Everything pushed to `origin/main`.
