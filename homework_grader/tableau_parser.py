"""
Tableau Workbook Parser
Extracts and analyzes TWBX files for automated grading
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
import json


class TableauWorkbookParser:
    """Parse and analyze Tableau workbook files (.twbx)"""
    
    def __init__(self, twbx_path: str):
        self.twbx_path = Path(twbx_path)
        self.extract_dir = self.twbx_path.parent / f"{self.twbx_path.stem}_extracted"
        self.twb_path = None
        self.tree = None
        self.root = None
        
    def extract_workbook(self) -> bool:
        """Extract TWBX file to temporary directory"""
        try:
            self.extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(self.twbx_path, 'r') as zip_ref:
                zip_ref.extractall(self.extract_dir)
            
            # Find the .twb file
            twb_files = list(self.extract_dir.glob("*.twb"))
            if not twb_files:
                print(f"❌ No .twb file found in {self.twbx_path}")
                return False
                
            self.twb_path = twb_files[0]
            
            # Parse XML
            self.tree = ET.parse(self.twb_path)
            self.root = self.tree.getroot()
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting workbook: {e}")
            return False
    
    def get_worksheets(self) -> List[Dict]:
        """Extract all worksheet names and basic info"""
        worksheets = []
        
        for worksheet in self.root.findall('.//worksheet'):
            name = worksheet.get('name', 'Unnamed')
            
            # Count marks/visualizations
            marks = len(worksheet.findall('.//mark'))
            
            # Get table type (if any)
            table = worksheet.find('.//table')
            table_type = table.find('.//view').get('type') if table is not None and table.find('.//view') is not None else 'unknown'
            
            worksheets.append({
                'name': name,
                'marks_count': marks,
                'type': table_type
            })
        
        return worksheets
    
    def get_dashboards(self) -> List[Dict]:
        """Extract all dashboard names and components"""
        dashboards = []
        
        for dashboard in self.root.findall('.//dashboard'):
            name = dashboard.get('name', 'Unnamed')
            
            # Count zones (dashboard components)
            zones = len(dashboard.findall('.//zone'))
            
            # Get worksheet references
            worksheet_refs = []
            for zone in dashboard.findall('.//zone'):
                worksheet_name = zone.get('name')
                if worksheet_name:
                    worksheet_refs.append(worksheet_name)
            
            dashboards.append({
                'name': name,
                'zones_count': zones,
                'worksheets': worksheet_refs
            })
        
        return dashboards
    
    def get_calculated_fields(self) -> List[Dict]:
        """Extract all calculated fields and their formulas"""
        calculated_fields = []
        
        # Look for columns with calculations
        for column in self.root.findall('.//column'):
            calculation = column.find('calculation')
            if calculation is not None:
                formula = calculation.get('formula', '')
                caption = column.get('caption', column.get('name', 'Unnamed'))
                datatype = column.get('datatype', 'unknown')
                
                calculated_fields.append({
                    'name': caption,
                    'formula': formula,
                    'datatype': datatype
                })
        
        return calculated_fields
    
    def get_data_sources(self) -> List[Dict]:
        """Extract data source information"""
        data_sources = []
        
        for datasource in self.root.findall('.//datasource'):
            caption = datasource.get('caption', 'Unnamed')
            
            # Get connection info
            connection = datasource.find('.//connection')
            if connection is not None:
                conn_class = connection.get('class', 'unknown')
                
                # Try to get filename for file-based sources
                filename = connection.get('filename', '')
                
                data_sources.append({
                    'name': caption,
                    'type': conn_class,
                    'filename': filename
                })
        
        return data_sources
    
    def get_filters(self) -> List[Dict]:
        """Extract filters used in worksheets"""
        filters = []
        
        for filter_elem in self.root.findall('.//filter'):
            column = filter_elem.get('column', 'Unknown')
            filter_class = filter_elem.get('class', 'unknown')
            
            filters.append({
                'column': column,
                'type': filter_class
            })
        
        return filters
    
    def analyze_workbook(self) -> Dict:
        """Comprehensive analysis of the workbook"""
        if not self.extract_workbook():
            return {'error': 'Failed to extract workbook'}
        
        analysis = {
            'filename': self.twbx_path.name,
            'worksheets': self.get_worksheets(),
            'dashboards': self.get_dashboards(),
            'calculated_fields': self.get_calculated_fields(),
            'data_sources': self.get_data_sources(),
            'filters': self.get_filters(),
            'summary': {
                'total_worksheets': len(self.get_worksheets()),
                'total_dashboards': len(self.get_dashboards()),
                'total_calculated_fields': len(self.get_calculated_fields()),
                'total_data_sources': len(self.get_data_sources())
            }
        }
        
        return analysis
    
    def print_analysis(self):
        """Print a formatted analysis report"""
        analysis = self.analyze_workbook()
        
        if 'error' in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        print("\n" + "="*60)
        print(f"📊 TABLEAU WORKBOOK ANALYSIS: {analysis['filename']}")
        print("="*60)
        
        print(f"\n📈 SUMMARY:")
        print(f"  • Worksheets: {analysis['summary']['total_worksheets']}")
        print(f"  • Dashboards: {analysis['summary']['total_dashboards']}")
        print(f"  • Calculated Fields: {analysis['summary']['total_calculated_fields']}")
        print(f"  • Data Sources: {analysis['summary']['total_data_sources']}")
        
        if analysis['worksheets']:
            print(f"\n📄 WORKSHEETS:")
            for ws in analysis['worksheets']:
                print(f"  • {ws['name']} (Type: {ws['type']}, Marks: {ws['marks_count']})")
        
        if analysis['dashboards']:
            print(f"\n📊 DASHBOARDS:")
            for db in analysis['dashboards']:
                print(f"  • {db['name']} ({db['zones_count']} zones)")
                if db['worksheets']:
                    print(f"    Contains: {', '.join(db['worksheets'])}")
        
        if analysis['calculated_fields']:
            print(f"\n🧮 CALCULATED FIELDS:")
            for calc in analysis['calculated_fields']:
                print(f"  • {calc['name']}")
                print(f"    Formula: {calc['formula']}")
                print(f"    Type: {calc['datatype']}")
        
        if analysis['data_sources']:
            print(f"\n💾 DATA SOURCES:")
            for ds in analysis['data_sources']:
                print(f"  • {ds['name']} ({ds['type']})")
                if ds['filename']:
                    print(f"    File: {ds['filename']}")
        
        print("\n" + "="*60)
        
        return analysis


def test_parser(twbx_path: str):
    """Test the parser with a sample file"""
    parser = TableauWorkbookParser(twbx_path)
    analysis = parser.print_analysis()
    
    # Save to JSON for further processing
    if analysis and 'error' not in analysis:
        output_path = Path(twbx_path).parent / f"{Path(twbx_path).stem}_analysis.json"
        with open(output_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n✅ Analysis saved to: {output_path}")


if __name__ == "__main__":
    # Test with the sample file
    test_parser("data/processed/Book1Executive Sales Performance Dashboard.twbx")
