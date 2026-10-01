# Results: Neural Core AR

## URLs
- **Live URL**: https://skilloutofbounds.github.io/neural-core-ar/
- **Repository URL**: https://github.com/skilloutofbounds/neural-core-ar

## Optimization Metrics (`metrics.json`)
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

### Summary of Improvements
| Metric | Before | After | Change |
| :--- | :--- | :--- | :--- |
| **Triangle Count** | 360,448 | 10,000 | -97.2% |
| **Draw Calls** | 2 | 1 | -1 |
| **Model Size** | 9.49 MB | 0.31 MB | -96.8% |

## Asset File Sizes
- `assets/neural_core.glb`: **0.31 MB** (319,928 bytes)
- `assets/targets.mind`: **0.60 MB** (628,683 bytes)
- `assets/target.png`: **1.30 MB** (1,362,408 bytes)

## Verification
- **Local & Live Testing**: Fully validated with headless Chrome & Chrome DevTools Protocol.
- **Protocol**: HTTPS (`https://skilloutofbounds.github.io/neural-core-ar/`).
- **HTTP Status**: All assets (`index.html`, `neural_core.glb`, `targets.mind`, and Google Draco WASM decoder `1.5.6`) return HTTP 200.
- **Console Errors**: 0 errors. Scene successfully instantiates the 3D entity and decodes 8,310 vertices.

## Testing on Mobile
To test the AR tracking on your phone:
1. Open the live URL with the stats flag on your phone browser:
   **https://skilloutofbounds.github.io/neural-core-ar/?stats**
2. Point your phone's camera at `assets/target.png` displayed on your monitor or secondary screen.
3. Observe the Neural Core 3D model hover and rotate above the target image with real-time FPS stats.
