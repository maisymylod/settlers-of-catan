# 🏝️ Settlers of Catan

A browser-based implementation of the classic board game **Settlers of Catan**, built with vanilla HTML5 Canvas, CSS, and JavaScript — no frameworks, no dependencies.

<p align="center">
  <img src="preview.png" alt="Catan Board Game Screenshot" width="800">
</p>

## 🎮 Play Now

**[Open `index.html` in your browser](index.html)** — that's it. No build step, no install.

Or play the hosted version: *[Add your GitHub Pages link here]*

## ✨ Features

- **Full hex board** with proper Catan tile layout (19 hexes, standard resource distribution)
- **4-player hot-seat multiplayer** with turn-based gameplay
- **Setup phase** — place 2 settlements and 2 roads per player (forward + reverse order)
- **Dice rolling** with animated dice and automatic resource distribution
- **Building** — roads, settlements, and city upgrades with resource costs
- **Robber mechanics** — activated on 7, move the robber, discard on 7+ cards
- **Bank trading** at 4:1 ratio
- **Victory tracking** — first to 10 VP wins
- **Responsive design** — works on desktop and tablet
- **Beautiful ocean-themed UI** with parchment aesthetics

## 🎯 How to Play

1. **Setup Phase**: Each player places 2 settlements and 2 roads on the board. Click on the highlighted spots to place them.
2. **Roll Dice**: Click "Roll Dice" to start your turn. Resources are automatically distributed to players with settlements/cities on matching numbers.
3. **Build**: Spend resources to build roads (🪵🧱), settlements (🪵🧱🌾🐑), or cities (🌾🌾⛏️⛏️⛏️).
4. **Trade**: Use the bank trade (4:1) to exchange resources.
5. **Win**: First player to reach **10 Victory Points** wins!

### Resource Types

| Resource | Source | Used For |
|----------|--------|----------|
| 🪵 Wood | Forest | Roads, Settlements |
| 🧱 Brick | Hills | Roads, Settlements |
| 🌾 Wheat | Fields | Settlements, Cities |
| 🐑 Sheep | Pasture | Settlements |
| ⛏️ Ore | Mountains | Cities |

## 🛠️ Tech Stack

- **HTML5 Canvas** — hex board rendering
- **Vanilla CSS** — ocean-themed UI with CSS custom properties, animations, and gradients
- **Vanilla JavaScript** — game logic, state management, event handling
- **Google Fonts** — Cinzel (headings) + Alegreya Sans (body)

Zero dependencies. Single file. ~800 lines.

## 📁 Project Structure

```
catan-board-game/
├── index.html    # The entire game (HTML + CSS + JS)
├── README.md     # You are here
└── LICENSE        # MIT License
```

## 🚀 Deployment

### GitHub Pages
1. Go to your repo → **Settings** → **Pages**
2. Set source to `main` branch, root directory
3. Your game will be live at `https://yourusername.github.io/catan-board-game/`

### Any Static Host
Just serve `index.html`. Works with Netlify, Vercel, Cloudflare Pages, or any web server.

## 📝 Roadmap

- [ ] Development cards (knights, monopoly, year of plenty, road building, victory points)
- [ ] Port trading (2:1 and 3:1)
- [ ] Longest road & largest army
- [ ] AI players
- [ ] Online multiplayer via WebSockets
- [ ] Sound effects
- [ ] Mobile touch optimization

## 📄 License

[MIT](LICENSE) — do whatever you want with it.

---

> *Disclaimer: This is a fan-made project for educational purposes. Settlers of Catan is a trademark of Catan GmbH.*
