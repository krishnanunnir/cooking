# 🍳 Cooking — Recipe Manager & Meal Planner

A static site generator for recipes with live calorie tracking. 24 recipes across big, small, very-small, and free categories. Auto-deploys via GitHub Actions to [cooking.bizzaretor.com](https://cooking.bizzaretor.com).

## Live Site

**[cooking.bizzaretor.com](https://cooking.bizzaretor.com)**

CI/CD automatically builds and deploys on every push. No manual steps needed.

## Commands

```bash
# Build locally
./cooking

# Or just push — GitHub Actions handles the rest
git push
```

## Structure

```
recipes/
├── big/          # 10 recipes (≤ 700 kcal)
├── small/        # 11 recipes (≤ 300 kcal)
├── very-small/   #  2 recipes (≤ 150 kcal)
└── free/         #  1 recipe (tracked, no cap)
```

## Adding a Recipe

Create a `.yaml` file with nutrition per ingredient:

```yaml
title: "My Recipe"
category: big
servings: 1
tags: [quick, healthy]

ingredients:
  - { name: chicken breast, amount: 200, unit: g, kcal: 330, protein: 62, carbs: 0, fat: 7 }
  - { name: rice, amount: 70, unit: g, kcal: 249, protein: 4.9, carbs: 55, fat: 0.4 }

instructions:
  - Cook chicken.
  - Serve over rice.
```

Push and it auto-deploys. Nutrition values should be for the **total amount used**, not per 100g.

## Features

- **Interactive recipe pages** — edit ingredient amounts, calories update live
- **Lock total calories** — pin a recipe's total, increase one ingredient and others auto-shrink
- **Weekly meal plan** — randomizes 2 big + 1 small + tea per day, seeded by week number
- **1-3 treat days** — extra very-small meal added to random days
- **Mobile responsive** — tables scroll horizontally, touch-friendly inputs
- **Static HTML** — no server, no database, just files
