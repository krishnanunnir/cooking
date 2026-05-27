# 🍳 Cooking — Recipe Static Site Generator

A **pure text-file** recipe manager. Write recipes in YAML, run one command, get a beautiful static website with full nutrition tracking.

## Quick Start

```bash
# Build the site
./cooking

# Open it
open build/index.html
```

## What You Get

- **Homepage** — all recipes by category with search
- **Recipe pages** — full ingredients + nutrition table (kcal, protein, carbs, fat)
- **Category pages** — filter by meal type
- **Calculator** — standalone nutrition calculator (runs entirely in the browser)

## Adding a Recipe

Create a `.yaml` file in `recipes/<category>/`. Here's the format:

```yaml
title: "My Recipe"
category: dinner
servings: 2
prep_time: "10 min"
cook_time: "20 min"
tags: [quick, healthy]

ingredients:
  - { name: chicken breast, amount: 300, unit: g, kcal: 495, protein: 93, carbs: 0, fat: 11 }
  - { name: rice, amount: 200, unit: g, kcal: 260, protein: 5.4, carbs: 56, fat: 0.6 }

instructions:
  - Cook the chicken.
  - Serve with rice.
```

**Nutrition per ingredient** should be for the *total amount used* (not per 100g). Just multiply:
```
kcal = (kcal_per_100g / 100) × your_weight
```

## Structure

```
cooking/
├── cooking             # Build script (one command)
├── build.py            # Static site generator
├── recipes/            # Your YAML recipe files
│   ├── breakfast/
│   ├── lunch/
│   ├── dinner/
│   ├── snacks/
│   └── desserts/
└── build/              # Generated site (open index.html)
```

## The Calculator

The built-in nutrition calculator at `build/calculator/` lets you:
- Add any ingredient by weight
- See running totals for kcal, protein, carbs, fat
- Tap common ingredients from a quick-reference grid
- All runs in the browser — no backend needed
