# Settlers of Catan

A browser-based implementation of the classic board game **Settlers of Catan**, built with vanilla HTML5 Canvas, CSS, and JavaScript — no frameworks, no dependencies.

<p align="center">
  <img src="preview.png" alt="Catan Board Game Screenshot" width="800">
</p>

## Play Now

**[Open `index.html` in your browser](index.html)** — that's it. No build step, no install.

Or play the hosted version: *[Add your GitHub Pages link here]*

## Features

- **Randomized hex board** with proper Catan tile layout (19 hexes, shuffled each game)
- **4-player hot-seat multiplayer** with turn-based gameplay
- **Setup phase** — place 2 settlements and 2 roads per player (forward + reverse order)
- **Dice rolling** with animated dice and per-player resource distribution feedback
- **Building** — roads, settlements, and city upgrades with resource costs and piece limits (5 settlements, 4 cities, 15 roads)
- **Robber mechanics** — activated on 7, player-chosen discard for 7+ cards, robber movement, and stealing from adjacent players
- **Bank trading** at 4:1 ratio
- **Longest Road** — 2 VP awarded to the first player with 5+ continuous road segments, with proper transfer and tie-breaking
- **Victory tracking** — first to 10 VP wins, all interaction blocked after win
- **Hidden information** — other players' resources hidden during play, revealed on win
- **Keyboard shortcuts** — R (roll), E (end turn), T (trade), 1/2/3 (build road/settlement/city), ESC (cancel)
- **New Game** button with confirmation
- **Responsive design** — works on desktop and tablet
- **Ocean-themed UI** with parchment aesthetics

## How to Play

1. **Setup Phase**: Each player places 2 settlements and 2 roads on the board. Click on the highlighted spots to place them.
2. **Roll Dice**: Click "Roll Dice" (or press R) to start your turn. Resources are automatically distributed to players with settlements/cities on matching numbers.
3. **Build**: Spend resources to build roads, settlements, or cities. Use keyboard shortcuts 1/2/3 or click the buttons.
4. **Trade**: Use the bank trade (4:1) to exchange resources. Press T or click the button.
5. **Win**: First player to reach **10 Victory Points** wins!

### Resource Types

| Resource | Source | Used For |
|----------|--------|----------|
| Wood | Forest | Roads, Settlements |
| Brick | Hills | Roads, Settlements |
| Wheat | Fields | Settlements, Cities |
| Sheep | Pasture | Settlements |
| Ore | Mountains | Cities |

## Tech Stack

- **HTML5 Canvas** — hex board rendering
- **Vanilla CSS** — ocean-themed UI with CSS custom properties, animations, and gradients
- **Vanilla JavaScript** — game logic, state management, event handling
- **Google Fonts** — Cinzel (headings) + Alegreya Sans (body)

Zero dependencies. Single file. ~1800 lines.

## Project Structure

```
settlers-of-catan/
├── index.html    # The entire game (HTML + CSS + JS)
└── README.md     # You are here
```

## Deployment

### GitHub Pages
1. Go to your repo, then Settings, then Pages
2. Set source to `main` branch, root directory
3. Your game will be live at `https://yourusername.github.io/settlers-of-catan/`

### Any Static Host
Just serve `index.html`. Works with Netlify, Vercel, Cloudflare Pages, or any web server.

## Roadmap

- Development cards (knights, monopoly, year of plenty, road building, victory points)
- Largest army
- Port trading (2:1 and 3:1)
- AI players
- Online multiplayer via WebSockets
- Sound effects
- Mobile touch optimization

## License

[MIT](LICENSE) — do whatever you want with it.

---

> *Disclaimer: This is a fan-made project for educational purposes. Settlers of Catan is a trademark of Catan GmbH.*
