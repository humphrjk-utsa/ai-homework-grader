#!/usr/bin/env python3
"""
QuantStudio EDS File to JSON Exporter

Extracts data from QuantStudio .eds files (ZIP archives) and exports to JSON.
Parses the analysis_result.txt file for CT values and fluorescence data.

Usage:
    python eds_to_json_exporter.py <input.eds> [output.json]
    python eds_to_json_exporter.py --batch <directory>
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class EDSExtractor:
    """Extract and parse QuantStudio EDS files"""
    
    def __init__(self, eds_file_path: str):
        self.eds_file_path = eds_file_path
        self.eds_filename = os.path.basename(eds_file_path)
        
    def extract(self) -> Dict[str, Any]:
        """Main extraction method"""
        print(f"📂 Opening EDS file: {self.eds_filename}")
        
        with zipfile.ZipFile(self.eds_file_path, 'r') as zip_ref:
            # Extract experiment.xml for metadata
            experiment_xml = self._read_xml_from_zip(zip_ref, 'apldbio/sds/experiment.xml')
            
            # Extract analysis_result.txt for well data
            analysis_text = self._read_text_from_zip(zip_ref, 'apldbio/sds/analysis_result.txt')
            
            experiment_data = {
                'source_file': self.eds_filename,
                'extraction_date': datetime.now().isoformat(),
                'experiment': self._parse_experiment_xml(experiment_xml),
                'results': self._parse_analysis_results(analysis_text),
                'summary': {}
            }
            
            # Generate summary
            experiment_data['summary'] = self._generate_summary(experiment_data['results'])
            
        print(f"✅ Extraction complete: {len(experiment_data['results'])} wells processed")
        return experiment_data
    
    def _read_xml_from_zip(self, zip_ref: zipfile.ZipFile, file_path: str) -> ET.Element:
        """Read and parse XML file from ZIP"""
        try:
            with zip_ref.open(file_path) as xml_file:
                return ET.parse(xml_file).getroot()
        except KeyError:
            print(f"⚠️  Warning: {file_path} not found")
            return None
    
    def _read_text_from_zip(self, zip_ref: zipfile.ZipFile, file_path: str) -> str:
        """Read text file from ZIP"""
        try:
            with zip_ref.open(file_path) as text_file:
                return text_file.read().decode('utf-8')
        except KeyError:
            print(f"⚠️  Warning: {file_path} not found")
            return ""
    
    def _parse_experiment_xml(self, root: ET.Element) -> Dict[str, Any]:
        """Parse experiment.xml for metadata"""
        if root is None:
            return {}
        
        experiment = {
            'metadata': {},
            'samples': [],
            'detectors': []
        }
        
        # Extract experiment metadata
        experiment['metadata'] = {
            'experiment_name': root.findtext('.//Name', ''),
            'run_state': root.findtext('.//RunState', ''),
            'final_analysis_completed': root.findtext('.//FinalAnalysisCompleted', ''),
            'created_time': root.findtext('.//CreatedTime', ''),
            'modified_time': root.findtext('.//ModifiedTime', ''),
            'run_start_time': root.findtext('.//RunStartTime', ''),
            'run_end_time': root.findtext('.//RunEndTime', ''),
        }
        
        # Extract experiment type
        exp_type = root.find('.//Type')
        if exp_type is not None:
            experiment['metadata']['experiment_type'] = {
                'id': exp_type.findtext('.//Id', ''),
                'name': exp_type.findtext('.//Name', ''),
                'description': exp_type.findtext('.//Description', '')
            }
        
        # Extract samples
        for sample in root.findall('.//Samples'):
            experiment['samples'].append({
                'name': sample.findtext('.//Name', ''),
                'color': sample.findtext('.//Color', ''),
                'concentration': sample.findtext('.//Concentration', '')
            })
        
        # Extract detectors (targets)
        for detector in root.findall('.//Detector'):
            experiment['detectors'].append({
                'name': detector.get('Name', ''),
                'reporter': detector.get('Reporter', ''),
                'quencher': detector.get('Quencher', ''),
                'color': detector.get('Color', '')
            })
        
        return experiment
    
    def _parse_analysis_results(self, text: str) -> List[Dict[str, Any]]:
        """Parse analysis_result.txt file"""
        results = []
        lines = text.strip().split('\n')
        
        if len(lines) < 2:
            return results
        
        # Skip header lines
        i = 0
        while i < len(lines) and not lines[i].startswith('Well\t'):
            i += 1
        
        if i >= len(lines):
            return results
        
        i += 1  # Skip header line
        
        # Parse each well entry (3 lines per well: metadata, Rn values, Delta Rn values)
        while i < len(lines):
            if not lines[i].strip():
                i += 1
                continue
            
            # Parse well metadata line
            parts = lines[i].split('\t')
            if len(parts) < 13:
                i += 1
                continue
            
            well_data = {
                'well': parts[0],
                'sample_name': parts[1],
                'detector': parts[2],
                'task': parts[3],
                'ct': self._parse_float(parts[4]),
                'avg_ct': self._parse_float(parts[5]),
                'ct_sd': self._parse_float(parts[6]),
                'delta_ct': self._parse_float(parts[7]),
                'qty': self._parse_float(parts[8]),
                'avg_qty': self._parse_float(parts[9]),
                'qty_sd': self._parse_float(parts[10]),
                'amp_status': self._parse_int(parts[11]),
                'cq_conf': self._parse_float(parts[12]),
                'rn_values': [],
                'delta_rn_values': [],
                'amplification_curve': []
            }
            
            # Parse Rn values line
            i += 1
            if i < len(lines) and lines[i].startswith('Rn values'):
                rn_line = lines[i].replace('Rn values\t', '')
                well_data['rn_values'] = [float(x) for x in rn_line.split('\t') if x.strip()]
            
            # Parse Delta Rn values line
            i += 1
            if i < len(lines) and lines[i].startswith('Delta Rn values'):
                delta_rn_line = lines[i].replace('Delta Rn values\t', '')
                well_data['delta_rn_values'] = [float(x) for x in delta_rn_line.split('\t') if x.strip()]
            
            # Create aligned amplification curve
            for cycle_idx in range(len(well_data['rn_values'])):
                curve_point = {
                    'cycle': cycle_idx + 1,
                    'rn': well_data['rn_values'][cycle_idx] if cycle_idx < len(well_data['rn_values']) else None,
                    'delta_rn': well_data['delta_rn_values'][cycle_idx] if cycle_idx < len(well_data['delta_rn_values']) else None
                }
                well_data['amplification_curve'].append(curve_point)
            
            results.append(well_data)
            i += 1
        
        return results
    
    def _parse_float(self, value: str) -> float:
        """Safely parse float"""
        if not value or value.strip() == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value: str) -> int:
        """Safely parse int"""
        if not value or value.strip() == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _generate_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            'total_wells': len(results),
            'total_samples': len(set(r['sample_name'] for r in results if r['sample_name'])),
            'total_detectors': len(set(r['detector'] for r in results if r['detector'])),
            'amplified_wells': sum(1 for r in results if r['amp_status'] == 1),
            'total_cycles': len(results[0]['amplification_curve']) if results and results[0]['amplification_curve'] else 0
        }


def export_to_json(data: Dict[str, Any], output_path: str, compact: bool = False):
    """Export data to JSON file"""
    indent = None if compact else 2
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=indent)
    
    file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
    print(f"💾 Saved to: {output_path} ({file_size:.2f} MB)")


def batch_process(directory: str, output_dir: str = None):
    """Process all EDS files in a directory"""
    eds_files = list(Path(directory).glob('*.eds'))
    
    if not eds_files:
        print(f"❌ No .eds files found in {directory}")
        return
    
    print(f"🔄 Found {len(eds_files)} EDS files to process\n")
    
    if output_dir is None:
        output_dir = os.path.join(directory, 'eds_extraction')
    
    os.makedirs(output_dir, exist_ok=True)
    
    for eds_file in eds_files:
        print(f"\n{'='*60}")
        try:
            extractor = EDSExtractor(str(eds_file))
            data = extractor.extract()
            
            output_filename = eds_file.stem + '_data.json'
            output_path = os.path.join(output_dir, output_filename)
            
            export_to_json(data, output_path)
            
        except Exception as e:
            print(f"❌ Error processing {eds_file.name}: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python eds_to_json_exporter.py <input.eds> [output.json]")
        print("  Batch mode:  python eds_to_json_exporter.py --batch <directory>")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("❌ Please specify directory for batch processing")
            sys.exit(1)
        batch_process(sys.argv[2])
    else:
        eds_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else eds_file.replace('.eds', '_data.json')
        
        if not os.path.exists(eds_file):
            print(f"❌ File not found: {eds_file}")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        extractor = EDSExtractor(eds_file)
        data = extractor.extract()
        export_to_json(data, output_file)
        print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
