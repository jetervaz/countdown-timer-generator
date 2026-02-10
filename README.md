# Countdown Timer Video Frame Generator

Generate countdown timer video frames (24:00:00 → 00:00:00) in **20 different visual styles** — 10 digital and 10 circle (Time Timer style). Frames are saved as PNG images and can be assembled into video using ffmpeg.

## Digital Styles

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

## Circle Styles (Time Timer)

Visual pie/wedge countdown timers inspired by the [Time Timer](https://www.timetimer.com/). The colored wedge represents remaining time and shrinks as the countdown progresses.

### Circle Modern
Modern dark circle timer with cyan wedge
![Circle Modern](previews/preview_circle-modern.png)

### Circle Classic
Classic Time Timer style with red wedge on white
![Circle Classic](previews/preview_circle-classic.png)

### Circle Neon
Neon glowing circle timer on dark purple
![Circle Neon](previews/preview_circle-neon.png)

### Circle Minimal
Minimal circle timer with thin ring on white
![Circle Minimal](previews/preview_circle-minimal.png)

### Circle Retro
Retro amber circle timer with LED look
![Circle Retro](previews/preview_circle-retro.png)

### Circle Gradient
Circle timer on vibrant purple gradient
![Circle Gradient](previews/preview_circle-gradient.png)

### Circle Terminal
Terminal green circle timer on black
![Circle Terminal](previews/preview_circle-terminal.png)

### Circle Cinematic
Cinematic gold circle timer on dark gradient
![Circle Cinematic](previews/preview_circle-cinematic.png)

### Circle Sport
Sporty red circle timer with bold digits
![Circle Sport](previews/preview_circle-sport.png)

### Circle Elegant
Elegant cream circle timer with brown wedge
![Circle Elegant](previews/preview_circle-elegant.png)

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

# Generate circle timer countdown
python generate_countdown.py --style circle-classic --fps 30 --duration 60

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

## Contact

Questions, suggestions, or contributions? Reach out at **jetervaz@gmail.com**

## License

MIT - see [LICENSE](LICENSE)
