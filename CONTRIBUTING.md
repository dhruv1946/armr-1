# Contributing to Neural Core AR

Thanks for your interest in contributing! Here's how you can help.

---

## 🐛 Reporting Bugs

1. Check [existing issues](https://github.com/skilloutofbounds/neural-core-ar/issues) to avoid duplicates
2. Open a new issue with:
   - **Device & browser** (e.g., iPhone 14, Safari 17)
   - **Steps to reproduce**
   - **Expected vs. actual behavior**
   - Console logs if available

---

## 💡 Suggesting Features

Open an issue with the `enhancement` label describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

---

## 🔧 Pull Requests

1. **Fork** the repo and create a feature branch from `main`
2. Make your changes
3. Test on at least one mobile device (or Chrome DevTools mobile emulation)
4. Submit a PR with a clear description of your changes

### Guidelines

- Keep PRs focused — one feature or fix per PR
- If modifying the 3D model, include updated `metrics.json`
- If changing the Blender script, document any new parameters
- Ensure the live demo still works after your changes

---

## 🏗 Development Setup

```bash
git clone https://github.com/skilloutofbounds/neural-core-ar.git
cd neural-core-ar
npx serve .
```

Open `http://localhost:3000` in your browser. For camera access on mobile, use HTTPS (e.g., via [ngrok](https://ngrok.com/)).

---

## 📜 Code of Conduct

Be respectful, constructive, and inclusive. Harassment or abusive behavior will not be tolerated.
