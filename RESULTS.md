# Performance Report — Neural Core AR

Detailed optimization metrics and verification results for the Neural Core AR project.

---

## 🔗 URLs

| | URL |
| :--- | :--- |
| **Live Demo** | https://skilloutofbounds.github.io/neural-core-ar/ |
| **Repository** | https://github.com/skilloutofbounds/neural-core-ar |
| **FPS Stats** | https://skilloutofbounds.github.io/neural-core-ar/?stats |

---

## 📊 Optimization Metrics

The procedurally generated model was decimated from a high-poly source and exported with Draco mesh compression to meet mobile AR performance budgets.

### Before vs. After

| Metric | Before | After | Change |
| :--- | ---: | ---: | ---: |
| **Triangle count** | 360,448 | 10,000 | −97.2% |
| **Draw calls** | 2 | 1 | −1 |
| **Model file size** | 9.49 MB | 0.31 MB | −96.8% |

### Raw Data (`metrics.json`)

```json
{
  "tri_before": "360,448",
  "tri_after": "10,000",
  "tri_change": "-97.2%",
  "dc_before": 2,
  "dc_after": 1,
  "dc_change": "-1",
  "mb_before": "9.49",
  "mb_after": "0.31",
  "mb_change": "-96.8%"
}
```

---

## 📦 Asset File Sizes

| Asset | Size |
| :--- | ---: |
| `assets/neural_core.glb` | 0.31 MB (319,928 bytes) |
| `assets/targets.mind` | 0.60 MB (628,683 bytes) |
| `assets/target.png` | 1.30 MB (1,362,408 bytes) |

---

## ✅ Verification

| Check | Result |
| :--- | :--- |
| **Protocol** | HTTPS via GitHub Pages |
| **HTTP status** | All assets return HTTP 200 |
| **Console errors** | 0 — scene loads cleanly |
| **Draco decoder** | Google CDN v1.5.6 — loaded successfully |
| **Vertex count** | 8,310 vertices decoded at runtime |
| **Local testing** | Validated with headless Chrome & Chrome DevTools Protocol |

---

## 📱 Testing on Mobile

1. Open the live demo URL on your phone's browser:
   **https://skilloutofbounds.github.io/neural-core-ar/?stats**
2. Point your camera at `assets/target.png` displayed on a monitor or printed out
3. The Neural Core 3D model will appear floating and rotating above the target with real-time FPS stats
