# Design System: VXP

## 0. Extracted baseline

The incumbent site is a single-column GitHub Pages documentation surface built on
`jekyll-theme-minimal`. It preserves the authoritative Markdown content and URLs,
but has no persistent index, no in-page search, no entry metadata treatment, and
no mobile table strategy. This design keeps the content and taxonomy intact while
replacing the presentation shell.

## 1. Visual Theme & Atmosphere

An editorial security field manual: warm paper, dark ink, exact rules, and a
single vermilion accent. Density is balanced rather than airy; the left index
makes a 79-entry reference navigable at a glance. The layout is asymmetric:
a narrow persistent index and a wider reading column. Motion is restrained and
only communicates state.

## 2. Color Palette & Roles

### Light

- **Warm Paper** (`#f4f1e8`) — page canvas
- **Readable Surface** (`#fbf9f3`) — search field and metadata surfaces
- **Quiet Surface** (`#e9e5d9`) — inline code and secondary fills
- **Charcoal Ink** (`#1b1b17`) — primary text; never pure black
- **Field Gray** (`#5f6058`) — secondary text and metadata
- **Rule Gray** (`#d4cfc1`) — 1px structural separators
- **Vermilion** (`#a23b20`) — the only accent: links, focus, selection, active state
- **Wash Vermilion** (`#f1e0d8`) — focus halo and selected surface

### Dark

- **Night Paper** (`#131510`) — page canvas
- **Raised Night** (`#191c16`) — search field and metadata surfaces
- **Quiet Night** (`#24281f`) — inline code and secondary fills
- **Bone Ink** (`#e9e5d9`) — primary text
- **Field Gray Dark** (`#a5a69a`) — secondary text
- **Rule Gray Dark** (`#353a30`) — separators
- **Signal Vermilion** (`#f08a67`) — the only accent

Exactly one accent hue. No purple, neon, gradient text, or colored glow.

## 3. Typography Rules

- **Display and body:** a deliberate system sans stack led by Avenir Next, Segoe UI
  Variable, and PingFang SC. This avoids remote font latency and renders Chinese
  consistently across macOS, Windows, and Linux.
- **Mono:** SFMono-Regular, Menlo, Consolas for IDs, counts, `kbd`, field names,
  and metadata labels.
- **Reading measure:** entry prose is capped at 64rem (1024px) on wide screens;
  entry titles stay between 28px and 40px. Headings are weight-driven, not enormous.
- **Scale:** 16px base, 1.8 line-height on body, 1.2 line-height on headings,
  letter-spacing no tighter than -0.04em.
- **Numbers:** tabular numerals in tables and counts.

## 4. Component Stylings

- **Header:** a 1px rule, solid surface, compact brand and utility navigation.
  Sticky only for orientation; no blur or glass.
- **Index:** persistent left rail on desktop, horizontal category rail on mobile.
  Category letters are compact mono badges, not decorative cards.
- **Search:** 52px bordered field on a raised surface; visible label for assistive
  technology; focus ring uses the accent wash; `/` focuses the field.
- **Catalog tables:** hairline row rules, 1px tree connectors for sub-entries,
  no zebra stripes, no card-per-row. On mobile each row becomes a compact
  two-column record with the level label beneath the title.
- **Entry metadata:** a bordered six-cell strip; mono labels, sans values.
- **Entry tables:** horizontally scrollable wrapper with keyboard focus and an
  accessible label.
- **Links:** vermilion underline with offset; no background pills.
- **Empty states:** search reports an exact zero-result message and a useful
  query hint instead of a blank table.

## 5. Layout Principles

- Max width 1700px. Desktop grid: 232px index plus a flexible content column.
- Entry content is capped at 1100px. The 200px page outline only appears at
  1760px and above, so it never narrows the reading column on common laptops.
- Mobile collapses to one column below 960px; tables recompose at 720px.
- Touch targets are at least 44px. No horizontal page overflow.
- Spacing uses a small fixed scale (4, 8, 12, 16, 24, 32, 48, 64, 96px).

## 6. Motion & Interaction

- State transitions are 150–180ms with an ease-out curve.
- Motion is limited to hover, focus, and the active outline marker.
- Respect `prefers-reduced-motion`.
- No orchestrated page-load sequences, perpetual animations, or parallax.

## 7. Anti-Patterns (Banned)

- No emoji, neon glows, purple gradients, or gradient text.
- No pure black or pure white surfaces.
- No 3-column equal card grids, hero metric cards, or fake statistics.
- No remote font or icon dependencies.
- No custom cursors.
- No overlapping text or decorative background grids.
- No hidden content that only JavaScript users can reach.
- No content rewrite: the extraction preserves the project's factual text.