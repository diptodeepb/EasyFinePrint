# EasyFinePrint Frontend

The client-side single page application (SPA) for **EasyFinePrint: Public Legal Agreements Auditor**, built with React 19, Vite 8, and Tailwind CSS v4.

---

## 🎨 UI & Design Principles

- **Minimalist Dark Aesthetic**: Deep zinc palette (`#09090b` base, `#121215` panel, `#27272a` borders) with crisp typography and subtle micro-interactions.
- **Custom Themed Scrollbars**: Native-styled dark scrollbars (`#27272a` thumb on `#09090b` track) configured across WebKit (Chrome, Safari, Edge, Android/iOS) and Firefox without layout shift.
- **Mobile-First Responsive Layouts**:
  - **Tracked Policies 2x2 Grid**: Monitored policies display in a 2x2 grid with final odd cards centered between the columns.
  - **Pagination (4 per page)**: Displays 4 policies per page (`PAGE_SIZE = 4`) with sliding-window page controls and persistent scroll position on pagination clicks.
  - **4-Tab Segmented Navigation**: Main policy detail tabs (`Clauses`, `Diffs`, `Log`, `Source Text`) adapt to a 4-column equal-width grid on mobile, eliminating horizontal scrolling.
  - **Automatic Route Scroll Restoration**: Navigating between routes (`/`, `/terms`, `/privacy`, `/policies/:id`) automatically scrolls to top `(0, 0)`.
  - **In-Place Validation Dismissal**: Input error banners feature interactive dismiss controls.

---

## 🧭 Routes & Pages

| Route | Component | Description |
|---|---|---|
| `/` | `Home.jsx` | Hero search, URL ingestion form, quick samples, highlighted features, and tracked policies grid/table. |
| `/policies/:id` | `PolicyDetail.jsx` | Full policy inspection: risk metrics card, verbatim findings, side-by-side Myers diffs, version history log, and raw text. |
| `/terms` | `TermsOfService.jsx` | Self-hosted Terms of Use with inline analyze button and canonical policy verification. |
| `/privacy` | `PolicyDoc.jsx` | Self-hosted Privacy Policy with zero-data-collection guarantees and direct auditor analysis. |

---

## 🧩 Key Components

- **`UrlForm.jsx`**: Public URL input with format validation, dismissible alert banners, elapsed progress timer, and instant sample triggers.
- **`DiscoveryModal.jsx`**: Zero-cost company legal URL lookup dialog backed by authoritative directory matching and SSRF-safe direct website inspection.
- **`DiffViewer.jsx`**: Side-by-side and unified Myers diffing engine highlighting word-level and paragraph-level additions (emerald) and deletions (rose).
- **`FindingCard.jsx`**: Clause risk findings with risk level pills, category badges, impact descriptions, and verbatim source quotation verification.
- **`VersionHistory.jsx`**: Chronological event timeline showing content hashes, check statuses, and snapshot diffs across revisions.
- **`ScrollToTop.jsx`**: Router listener that resets window and document scroll position on route transitions.
- **`BackToTop.jsx`**: Floating smooth-scroll button displayed when scrolled down long agreements.
- **`Header.jsx` & `Footer.jsx`**: Minimal navigation bar with status indicator and comprehensive legal/architecture footer.

---

## 🚀 Development & Build

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```
Starts Vite dev server at [http://localhost:5173](http://localhost:5173) with instantaneous Hot Module Replacement (HMR).

### Production Build
```bash
npm run build
```
Builds optimized production assets to `dist/`.

### Preview Production Build
```bash
npm run preview
```
Previews the production build locally.
