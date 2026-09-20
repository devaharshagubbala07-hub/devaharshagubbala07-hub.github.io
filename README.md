# Devaharsha Gubbala | Healthcare Analytics Portfolio

Personal portfolio covering healthcare claims analysis, reporting, dashboard validation, and health informatics.

## Featured work

**[Claims cost explorer](https://devaharshagubbala07-hub.github.io/demo/):** a working Python and SQL demonstration with synthetic data, documented definitions, quality checks and a filterable dashboard. [Source repository](https://github.com/devaharshagubbala07-hub/healthcare-claims-analytics).

Four professional case studies:

- Healthcare program cohort analysis
- High-cost claimant and cost trend analysis
- Healthcare dashboard migration and validation
- Diabetes population and quality analysis

Two academic project summaries:

- FHIR ETL and referral management
- Sleep quality and physical activity analysis

This repository contains the portfolio website and a published copy of the demonstration dashboard. The new demonstration was developed with AI assistance and uses generated records; it is separate from the professional case studies and earlier academic work. The academic summaries do not include the original project code or notebooks. Professional examples use general descriptions without client data or internal deliverables.

## Design and interaction

The site uses an analyst’s desk theme: deep navy, white paper, restrained blue accents, editorial type, numbered case notes, and chart details. No third-party fonts, animation libraries, trackers, or build dependencies are required.

- The opening chart switches between two reporting years using the same pipeline results as the claims demonstration.
- The Analysis Lab includes a selectable SQL excerpt from the demonstration's `sql/schema.sql`, with a plain-language explanation, source link, and static grid backdrop. It shares the site's brief reveal animation and motion preferences.
- The reporting-method notebook shows how questions, population definitions, validation, and interpretation fit together.
- Brief entrance, chart, and scroll animations respect `prefers-reduced-motion`. A motion switch also saves a visitor’s preference locally.
- Navigation, case notes, and the static chart remain readable without JavaScript. Interactive controls use native buttons and visible keyboard focus.
- Layouts adapt to narrow screens; the mobile menu closes with Escape and restores focus to its button.

The `demo/dashboard.css` file is also maintained in the analysis repository at `dashboard/dashboard.css` so a freshly generated demo retains the same appearance.

## Background artwork

The opening section uses a custom generated analyst-workspace image, with CSS desaturation and a navy overlay for readable text and a smaller image for narrow screens. Case notes keep their clean light background. The photograph is illustrative, and its decorative charts are unrelated to the working demo's data. [Asset files and generation prompt](assets/README.md).

## View locally

Keep `index.html`, `styles.css`, and `script.js` together, then open `index.html` in a browser. There are no dependencies or build steps. Core content and case studies remain available without JavaScript.

## Website

[View the portfolio](https://devaharshagubbala07-hub.github.io/).

GitHub Pages serves the site from the `main` branch and repository root. Update the HTML, CSS, or JavaScript and commit to `main` to publish changes. Keep `.nojekyll` in the root.

See [GitHub Pages documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site).
