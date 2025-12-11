#!/usr/bin/env python3
"""Quick PCR Curve Viewer for EDS extracted data"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import numpy as np

class PCRCurveViewer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.files = sorted([f for f in self.data_dir.glob("*_data.json")])
        self.current_file_idx = 0
        self.current_well_idx = 0
        self.data = None
        self.wells = []
        self.dye_colors = {
            'FAM': '#00FF00',
            'VIC': '#FFA500', 
            'ROX': '#FF0000',
            'CY5': '#0000FF',
            'None': '#808080'
        }
        
        if not self.files:
            raise ValueError(f"No *_data.json files found in {data_dir}")
        
        self.load_file(0)
        self.setup_plot()
    
    def load_file(self, idx):
        """Load a data file"""
        self.current_file_idx = idx
        with open(self.files[idx]) as f:
            self.data = json.load(f)
        
        # Filter out header row and get actual wells
        self.wells = [r for r in self.data['results'] if r['well'] != 'Well' and r['amplification_curve']]
        self.current_well_idx = 0
        print(f"Loaded: {self.files[idx].name} ({len(self.wells)} wells with curves)")
        
        # Skip files with no wells
        if not self.wells and len(self.files) > 1:
            print(f"  Skipping empty file...")
            next_idx = (idx + 1) % len(self.files)
            if next_idx != idx:  # Prevent infinite loop
                self.load_file(next_idx)
    
    def get_dye_color(self, detector_name):
        """Get color for a detector based on its dye"""
        for det in self.data['experiment']['detectors']:
            if det['name'] == detector_name:
                return self.dye_colors.get(det['reporter'], '#808080')
        return '#808080'
    
    def plot_well(self):
        """Plot curves for current well"""
        self.ax.clear()
        
        if not self.wells:
            self.ax.text(0.5, 0.5, 'No wells with curves', ha='center', va='center')
            return
        
        well = self.wells[self.current_well_idx]
        
        # Plot the curve
        curve = well['amplification_curve']
        cycles = [p['cycle'] for p in curve]
        # Use normalized fluorescence if available, otherwise delta_rn
        fluorescence = [p.get('normalized_fluorescence', p['delta_rn']) for p in curve]
        
        color = self.get_dye_color(well['detector'])
        self.ax.plot(cycles, fluorescence, '-o', color=color, markersize=3, linewidth=2)
        
        # Mark Cq if available
        if well['ct']:
            self.ax.axvline(well['ct'], color='red', linestyle='--', alpha=0.5, label=f"Cq={well['ct']:.2f}")
        
        # Labels
        self.ax.set_xlabel('Cycle')
        self.ax.set_ylabel('Normalized Fluorescence (0-2000)')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_ylim(bottom=0, top=2200)
        
        # Title with well info
        title = f"Well {well['well']} | {well['sample_name']} | {well['detector']}"
        if well['ct']:
            title += f" | Cq: {well['ct']:.2f}"
        else:
            title += " | No Cq"
        self.ax.set_title(title, fontsize=10, fontweight='bold')
        
        if well['ct']:
            self.ax.legend()
        
        # Update file/well counter
        self.counter_text.set_text(
            f"File {self.current_file_idx + 1}/{len(self.files)} | "
            f"Well {self.current_well_idx + 1}/{len(self.wells)}\n"
            f"{self.files[self.current_file_idx].name}"
        )
        
        plt.draw()
    
    def next_well(self, event=None):
        """Navigate to next well"""
        if self.wells:
            self.current_well_idx = (self.current_well_idx + 1) % len(self.wells)
            self.plot_well()
    
    def prev_well(self, event=None):
        """Navigate to previous well"""
        if self.wells:
            self.current_well_idx = (self.current_well_idx - 1) % len(self.wells)
            self.plot_well()
    
    def next_file(self, event=None):
        """Navigate to next file"""
        self.load_file((self.current_file_idx + 1) % len(self.files))
        self.plot_well()
    
    def prev_file(self, event=None):
        """Navigate to previous file"""
        self.load_file((self.current_file_idx - 1) % len(self.files))
        self.plot_well()
    
    def setup_plot(self):
        """Setup the matplotlib figure and controls"""
        self.fig = plt.figure(figsize=(12, 8))
        
        # Main plot area
        self.ax = plt.axes([0.1, 0.25, 0.85, 0.65])
        
        # Navigation buttons
        btn_prev_file = Button(plt.axes([0.1, 0.12, 0.1, 0.05]), '◄◄ File')
        btn_prev_file.on_clicked(self.prev_file)
        
        btn_prev_well = Button(plt.axes([0.22, 0.12, 0.1, 0.05]), '◄ Well')
        btn_prev_well.on_clicked(self.prev_well)
        
        btn_next_well = Button(plt.axes([0.58, 0.12, 0.1, 0.05]), 'Well ►')
        btn_next_well.on_clicked(self.next_well)
        
        btn_next_file = Button(plt.axes([0.7, 0.12, 0.1, 0.05]), 'File ►►')
        btn_next_file.on_clicked(self.next_file)
        
        # Counter text
        self.counter_text = self.fig.text(0.5, 0.05, '', ha='center', fontsize=9)
        
        # Keyboard shortcuts
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        self.plot_well()
        plt.show()
    
    def on_key(self, event):
        """Handle keyboard shortcuts"""
        if event.key == 'right' or event.key == 'd':
            self.next_well()
        elif event.key == 'left' or event.key == 'a':
            self.prev_well()
        elif event.key == 'up' or event.key == 'w':
            self.next_file()
        elif event.key == 'down' or event.key == 's':
            self.prev_file()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ollama_sentiment/thermopcr/data/eds_extraction"
    
    viewer = PCRCurveViewer(data_dir)
