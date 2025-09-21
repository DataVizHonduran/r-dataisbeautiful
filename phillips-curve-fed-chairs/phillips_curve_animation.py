"""
Phillips Curve Animation Generator

Creates an animated visualization showing how unemployment vs inflation relationship
evolved under different Federal Reserve Chairpersons from 1970-2025.

The animation shows:
- Each Fed Chair's tenure as a colored path through unemployment/inflation space
- Completed tenures as filled polygon shapes
- Current economic position with "We are here" annotation
- Fed's dual mandate target zone (2% inflation, 4-6% unemployment)

Data sources: Federal Reserve Economic Data (FRED)
- UNRATE: Unemployment rate
- CPILFESL: Core CPI (Consumer Price Index)
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import pandas_datareader.data as web
from tqdm import tqdm
from matplotlib.patches import Polygon, Rectangle

#Pull data from Fred
start_date = '1970-01-01'
end_date = '2025-12-31'
unemployment = web.DataReader('UNRATE', 'fred', start_date, end_date)
core_pce = web.DataReader('CPILFESL', 'fred', start_date, end_date)
core_pce_yoy = core_pce.pct_change(periods=12) * 100
data = pd.merge(unemployment, core_pce_yoy, left_index=True, right_index=True)
data.columns = ['unemployment', 'core_cpi_yoy']
data = data.dropna()

fed_chairs = [
    ('Arthur Burns', '1970-02-01', '1978-01-31'),
    ('William Miller', '1978-03-08', '1979-08-06'),
    ('Paul Volcker', '1979-08-06', '1987-08-11'),
    ('Alan Greenspan', '1987-08-11', '2006-01-31'),
    ('Ben Bernanke', '2006-02-01', '2014-01-31'),
    ('Janet Yellen', '2014-02-03', '2018-02-03'),
    ('Jerome Powell', '2018-02-05', '2025-12-31')
]

#determines fed_chair for a given date
def assign_fed_chair(date):
    for chair, start, end in fed_chairs:
        if pd.to_datetime(start) <= date <= pd.to_datetime(end):
            return chair
    return 'Other'
data['fed_chair'] = data.index.map(assign_fed_chair)
data = data[data['fed_chair'] != 'Other']
data = data.reset_index()
data = data.sort_values('DATE')

def rgb_to_matplotlib(rgb_string):
    rgb_values = rgb_string.replace('rgb(', '').replace(')', '').split(',')
    r, g, b = [int(x.strip()) / 255.0 for x in rgb_values]
    return (r, g, b)

mpl_chair_colors = {
    'Arthur Burns': rgb_to_matplotlib('rgb(228,26,28)'),
    'William Miller': rgb_to_matplotlib('rgb(55,126,184)'),
    'Paul Volcker': rgb_to_matplotlib('rgb(77,175,74)'),
    'Alan Greenspan': rgb_to_matplotlib('rgb(152,78,163)'),
    'Ben Bernanke': rgb_to_matplotlib('rgb(255,127,0)'),
    'Janet Yellen': rgb_to_matplotlib('rgb(255,255,51)'),
    'Jerome Powell': rgb_to_matplotlib('rgb(166,86,40)')
}

fig, ax = plt.subplots(figsize=(8, 6))
plt.style.use('default')

# Keep track of completed Fed Chair shapes
completed_shapes = {}

# Global variable to track progress
pbar = None

def draw_preview_frame(ax):
    ax.clear()
    ax.set_facecolor('white')
    
    target_box = Rectangle((4, 2), 2, 1, facecolor='gray', alpha=0.5, 
                          edgecolor='black', linewidth=2, linestyle='-')
    ax.add_patch(target_box)
    ax.text(5, 2.5, 'Fed Target', ha='center', va='center', 
            fontsize=8, alpha=1.0, weight='bold')
    
    for chair in ['Arthur Burns', 'William Miller', 'Paul Volcker', 'Alan Greenspan', 'Ben Bernanke', 'Janet Yellen', 'Jerome Powell']:
        chair_data = data[data['fed_chair'] == chair].sort_values('DATE')
        if len(chair_data) >= 3:
            points = list(zip(chair_data['unemployment'], chair_data['core_cpi_yoy']))
            color = mpl_chair_colors[chair]
            darker_color = tuple(c * 0.5 for c in color)
            polygon = Polygon(points, facecolor=color, alpha=0.3, edgecolor=darker_color, linewidth=2)
            ax.add_patch(polygon)
    
    final_point = data.iloc[-1]
    ax.annotate('We are here', 
               xy=(final_point['unemployment'], final_point['core_cpi_yoy']),
               xytext=(final_point['unemployment'] + 1.5, final_point['core_cpi_yoy'] + 1),
               arrowprops=dict(arrowstyle='->', color='black', lw=2),
               fontsize=10, weight='bold', ha='left')
    
    ax.text(0.02, 0.95, 'PREVIEW', transform=ax.transAxes, fontsize=16, 
            weight='bold', ha='left', va='top', alpha=0.8, color='red',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9, edgecolor='red'))
    
    final_date = data.iloc[-1]['DATE']
    date_text = final_date.strftime("%b %Y")
    ax.text(0.98, 0.95, date_text, transform=ax.transAxes, fontsize=24, 
            weight='bold', ha='right', va='top', alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)
    ax.set_xlabel('Unemployment Rate (%)')
    ax.set_ylabel('Core CPI YoY (%)')
    ax.set_title(f'Phillips Curve Evolution by Fed Chair (1970-{final_date.strftime("%Y")})')
    
    #create legend
    legend_elements = []
    for chair, color in mpl_chair_colors.items():
        legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, markersize=6, label=chair))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    
def get_completed_chairs_at_frame(frame):
    """Get list of Fed Chairs whose terms have been completed by this frame to draw as filled polygons"""
    current_data = data.iloc[:frame+2]
    completed_chairs = []
    
    for chair in ['Arthur Burns', 'William Miller', 'Paul Volcker', 'Alan Greenspan', 'Ben Bernanke', 'Janet Yellen', 'Jerome Powell']:
        chair_data = current_data[current_data['fed_chair'] == chair]
        remaining_data = data.iloc[frame+2:]
        if len(chair_data) > 0 and chair not in remaining_data['fed_chair'].values:
            completed_chairs.append(chair)
    
    return completed_chairs

def animate(frame):
    global pbar, completed_shapes
    if pbar is not None:
        pbar.update(1)
    
    # Special handling for preview frame (frame = -1)
    if frame == -1:
        draw_preview_frame(ax)
        return
    
    ax.clear()
    ax.set_facecolor('white')
    
    # Add Fed dual mandate target box with higher contrast
    target_box = Rectangle((4, 2), 2, 1, facecolor='gray', alpha=0.5, 
                          edgecolor='black', linewidth=2, linestyle='-')
    ax.add_patch(target_box)
    ax.text(5, 2.5, 'Fed Target', ha='center', va='center', 
            fontsize=8, alpha=1.0, weight='bold')
    
    """current_datais a slice of the full dataset that represents all the economic data from the beginning
    up to the current animation frame"""
    current_data = data.iloc[:frame+2]
    
    # Plot filled shapes for completed Fed Chairs
    completed_chairs = get_completed_chairs_at_frame(frame)
    for chair in completed_chairs:
        if chair not in completed_shapes:
            # Create the filled shape for this completed chair
            chair_data = data[data['fed_chair'] == chair].sort_values('DATE')
            if len(chair_data) >= 3:  # Need at least 3 points to make a polygon
                points = list(zip(chair_data['unemployment'], chair_data['core_cpi_yoy']))
                color = mpl_chair_colors[chair]
                
                # Create polygon and add to completed shapes
                darker_color = tuple(c * 0.5 for c in color)  # Makes it 50% darker
                polygon = Polygon(points, facecolor=color, alpha=0.3, edgecolor=darker_color, linewidth=2)
                completed_shapes[chair] = polygon
        
        # Draw the completed shape
        if chair in completed_shapes:
            ax.add_patch(completed_shapes[chair])
    
    # Plot connecting lines for current data
    for chair in current_data['fed_chair'].unique():
        chair_data = current_data[current_data['fed_chair'] == chair].sort_values('DATE')
        color = mpl_chair_colors[chair]
        
        # Skip if this chair is already completed (we show the filled shape instead)
        if chair in completed_chairs:
            continue
            
        # Plot line if there's more than one point
        if len(chair_data) > 1:
            ax.plot(chair_data['unemployment'], chair_data['core_cpi_yoy'], 
                    '-', color=color, linewidth=2, alpha=0.8)
        
        # Plot points
        ax.scatter(chair_data['unemployment'], chair_data['core_cpi_yoy'], 
                  c=[color], s=30, alpha=0.9, edgecolors='white', linewidths=1)
    
    # Highlight the current point
    if frame < len(data) - 1:
        current_point = data.iloc[frame+1]
        current_color = mpl_chair_colors[current_point['fed_chair']]
        
        #this creates a "pulsing" effect as each new point gets highlighted
        ax.scatter(current_point['unemployment'], current_point['core_cpi_yoy'], 
                  s=50, facecolors='none', edgecolors=current_color, linewidths=3)
    
    # Add "We are here" annotation for the final point
    if frame >= len(data) - 1:
        final_point = data.iloc[-1]
        ax.annotate('We are here', 
                   xy=(final_point['unemployment'], final_point['core_cpi_yoy']),
                   xytext=(final_point['unemployment'] + 1.5, final_point['core_cpi_yoy'] + 1),
                   arrowprops=dict(arrowstyle='->', color='black', lw=2),
                   fontsize=10, weight='bold', ha='left')
    
    # Get current info for title and large date display
    current_date = current_data.iloc[-1]['DATE']
    current_chair = current_data.iloc[-1]['fed_chair']
    
    # Add large backdrop date display
    date_text = current_date.strftime("%b %Y")
    ax.text(0.98, 0.95, date_text, transform=ax.transAxes, fontsize=24, 
            weight='bold', ha='right', va='top', alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, edgecolor='gray'))
    
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 15)
    ax.set_xlabel('Unemployment Rate (%)')
    ax.set_ylabel('Core CPI YoY (%)')
    ax.set_title(f'Phillips Curve Path - {current_date.strftime("%Y-%m")} ({current_chair})')
    
    # Create legend
    legend_elements = []
    for chair, color in mpl_chair_colors.items():
        if chair in current_data['fed_chair'].values or chair in completed_chairs:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                            markerfacecolor=color, markersize=6, label=chair))
    
    ax.legend(handles=legend_elements, loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

# Create frames with single preview frame at the beginning
total_frames = len(data)
pause_frames = 25  # Number of frames to repeat the final frame for the pause
# Frame sequence: preview + animation + pause
all_frames = [-1] + list(range(total_frames)) + [total_frames-1] * pause_frames

#Track animation creation progress
print(f"Creating matplotlib animation with {len(all_frames)} frames (including 1 preview frame and {pause_frames} pause frames)...")
pbar = tqdm(total=len(all_frames), desc="Generating frames", leave=False)

#Calls the animate function which runs that entire figure creation and pauses for 50milliseconds
ani = animation.FuncAnimation(fig, animate, frames=all_frames, interval=50, repeat=False)
ani.save('phillips_matplotlib_filled_shapes_with_preview.gif', writer='pillow', fps=20)

pbar.close()
plt.close()
print("Matplotlib animation complete!")
