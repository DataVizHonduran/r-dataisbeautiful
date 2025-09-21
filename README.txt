# Phillips Curve Evolution by Federal Reserve Chairpersons (1970-2025)

An animated visualization showing how the relationship between unemployment and inflation has evolved under different Fed Chairs, illustrating the breakdown and evolution of the Phillips Curve over time.

![Phillips Curve Animation](phillips_matplotlib_filled_shapes_with_preview.gif)

## What This Shows
- **Each Fed Chair's tenure** as a colored path through unemployment/inflation space  
- **Completed tenures** as filled polygon shapes showing their full economic legacy
- **Current economic position** with "We are here" annotation
- **Fed's dual mandate target zone** (2% inflation, 4-6% unemployment range)

## Key Insights
This visualization reveals how monetary policy approaches have shaped economic outcomes:
- **Volcker's dramatic disinflation** (early 1980s recession to break inflation)
- **The Great Moderation** under Greenspan 
- **Financial crisis response** under Bernanke
- **Recent inflation challenges** under Powell

## Technical Features
- Sourced data from Federal Reserve Economic Data (FRED)
- Smooth animation with preview frame and pause at end
- Color-coded Fed Chair tenures with filled shapes for completed terms
- Interactive legend showing active chairs

## Data Sources
- **UNRATE**: Unemployment rate from FRED
- **CPILFESL**: Core CPI (Consumer Price Index) from FRED

## Usage
```bash
pip install matplotlib pandas pandas-datareader numpy tqdm
python phillips_curve_animation.py