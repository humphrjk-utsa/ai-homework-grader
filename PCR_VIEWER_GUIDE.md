# PCR Curve Viewer - Quick Guide

## What was fixed

The `eds_to_json_exporter.py` script was using `'fluorescence'` as the key name in the amplification curve, but it should be `'rn'` to match the expected format.

**Fixed:** Changed `'fluorescence':` to `'rn':` in the amplification curve generation.

## Files

1. **eds_to_json_exporter.py** - Extracts EDS files to JSON (FIXED)
   - Location: `/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ollama_sentiment/`

2. **pcr_curve_viewer.py** - Interactive curve viewer
   - Location: `/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ollama_sentiment/`

## Usage

### Re-extract EDS files (if needed)

```bash
# Single file
python3 eds_to_json_exporter.py input.eds output.json

# Batch process all EDS files in a directory
python3 eds_to_json_exporter.py --batch /path/to/eds/files
```

### View PCR Curves

```bash
# Default directory
python3 pcr_curve_viewer.py

# Or specify directory
python3 pcr_curve_viewer.py /path/to/json/files
```

## Viewer Features

- **Navigate files**: ◄◄ File / File ►► buttons or Up/Down arrow keys
- **Navigate wells**: ◄ Well / Well ► buttons or Left/Right arrow keys
- **Keyboard shortcuts**: Arrow keys or WASD
- **Color coding**: Curves colored by dye (FAM=green, VIC=orange, ROX=red, CY5=blue)
- **Cq display**: Shows Cq value in title and as vertical line on plot
- **Well info**: Displays well ID, sample name, detector, and Cq value

## Data Format

The JSON files now have the correct structure:
```json
{
  "well": "0",
  "sample_name": "POS",
  "detector": "KLEPNE",
  "ct": 17.739443,
  "amplification_curve": [
    {
      "cycle": 1,
      "rn": 193138.25,
      "delta_rn": 3051.535
    }
  ]
}
```
