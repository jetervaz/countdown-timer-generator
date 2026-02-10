# Countdown Timer Video Frame Generator

Generate countdown timer video frames (24:00:00 → 00:00:00) in **10 different visual styles**. Frames are saved as PNG images and can be assembled into video using ffmpeg.

## Styles

### Modern
Clean dark background with cyan text and progress bar
![Modern](previews/preview_modern.png)

### Classic
Traditional white on black with border
![Classic](previews/preview_classic.png)

### Neon
Neon glow effect on dark purple background
![Neon](previews/preview_neon.png)

### Minimal
Clean white background with thin gray text
![Minimal](previews/preview_minimal.png)

### Retro
Amber LED display look with glow
![Retro](previews/preview_retro.png)

### Gradient
Vibrant purple gradient background with white text
![Gradient](previews/preview_gradient.png)

### Terminal
Green-on-black hacker terminal style
![Terminal](previews/preview_terminal.png)

### Cinematic
Gold text on dark gradient with glow
![Cinematic](previews/preview_cinematic.png)

### Sport
Bold red digits with progress bar
![Sport](previews/preview_sport.png)

### Elegant
Cream background with brown text and circle progress
![Elegant](previews/preview_elegant.png)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# List all available styles
python generate_countdown.py --list-styles

# Generate preview frames for all styles
python generate_countdown.py --preview-all

# Generate a 10-second clip at 30fps
python generate_countdown.py --style modern --fps 30 --duration 10

# Generate full 24-hour countdown at 1fps (smaller output)
python generate_countdown.py --style neon --fps 1

# Generate full 24h at 30fps (warning: ~2.5M frames!)
python generate_countdown.py --style classic --fps 30
```

### Assemble into video with ffmpeg

```bash
ffmpeg -framerate 30 -i output/modern/frame_%08d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 18 countdown_modern.mp4
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--style` | `modern` | Style name or `all` |
| `--fps` | `30` | Frames per second |
| `--duration` | `86400` | Duration in seconds (86400 = 24h) |
| `--start` | `86400` | Start time in seconds |
| `--output` | `output/` | Output directory |
| `--preview` | — | Generate single preview frame |
| `--preview-all` | — | Preview frames for all styles |
| `--list-styles` | — | List styles and exit |

## License

MIT
