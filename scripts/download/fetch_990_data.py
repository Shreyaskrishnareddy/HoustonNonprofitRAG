#!/usr/bin/env python3
"""
Script to download and process IRS Form 990 data for Houston nonprofits
"""

import os
import requests
import zipfile
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IRS990Downloader:
    def __init__(self, data_dir: str = "../../data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # IRS data URLs
        self.base_url = "https://apps.irs.gov/pub/epostcard/990/xml"
        
    def download_index_file(self, year: int) -> Optional[pd.DataFrame]:
        """Download the index CSV file for a given year"""
        url = f"{self.base_url}/{year}/index_{year}.csv"
        file_path = self.raw_dir / f"index_{year}.csv"
        
        try:
            logger.info(f"Downloading index file for {year}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Read and return the CSV
            df = pd.read_csv(file_path)
            logger.info(f"Downloaded {len(df)} records for {year}")
            return df
            
        except Exception as e:
            logger.error(f"Error downloading index for {year}: {e}")
            return None
    
    def filter_houston_nonprofits(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter nonprofits to Houston area - using names for now"""
        # Since the index file doesn't contain geographic data, 
        # we'll filter by organization names containing Houston keywords
        houston_keywords = [
            'houston', 'harris county', 'galveston', 'montgomery county',
            'fort bend', 'brazoria', 'chambers', 'liberty county'
        ]
        
        # Create a case-insensitive filter
        mask = df['TAXPAYER_NAME'].str.lower().str.contains(
            '|'.join(houston_keywords), na=False
        )
        
        houston_df = df[mask].copy()
        
        logger.info(f"Found {len(houston_df)} Houston area nonprofits")
        return houston_df
    
    def download_990_xml(self, object_id: str, year: int) -> Optional[str]:
        """Download individual 990 XML file"""
        url = f"{self.base_url}/{year}/{object_id}_public.xml"
        file_path = self.raw_dir / f"{object_id}_{year}.xml"
        
        if file_path.exists():
            return str(file_path)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error downloading {object_id}: {e}")
            return None
    
    def parse_990_xml(self, xml_path: str) -> Optional[Dict]:
        """Parse 990 XML file and extract key information"""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Define namespace (IRS XML uses namespaces)
            ns = {'irs': 'http://www.irs.gov/efile'}
            
            data = {}
            
            # Basic organization info
            org_info = root.find('.//irs:Filer', ns)
            if org_info is not None:
                data['ein'] = self.get_text(org_info, './/irs:EIN', ns)
                data['name'] = self.get_text(org_info, './/irs:BusinessName/irs:BusinessNameLine1Txt', ns)
                
                # Address
                address = org_info.find('.//irs:USAddress', ns)
                if address is not None:
                    data['street_address'] = self.get_text(address, './/irs:AddressLine1Txt', ns)
                    data['city'] = self.get_text(address, './/irs:CityNm', ns)
                    data['state'] = self.get_text(address, './/irs:StateAbbreviationCd', ns)
                    data['zip_code'] = self.get_text(address, './/irs:ZIPCd', ns)
            
            # Mission description
            data['mission_description'] = self.get_text(root, './/irs:MissionDesc', ns)
            data['activities_description'] = self.get_text(root, './/irs:ActivityOrMissionDesc', ns)
            
            # Financial data
            data['total_revenue'] = self.get_numeric(root, './/irs:TotalRevenueAmt', ns)
            data['total_expenses'] = self.get_numeric(root, './/irs:TotalExpensesAmt', ns)
            data['net_assets'] = self.get_numeric(root, './/irs:NetAssetsOrFundBalancesEOYAmt', ns)
            
            # Website
            data['website'] = self.get_text(root, './/irs:WebsiteAddressTxt', ns)
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing {xml_path}: {e}")
            return None
    
    def get_text(self, root, xpath: str, ns: Dict) -> Optional[str]:
        """Helper to safely extract text from XML"""
        element = root.find(xpath, ns)
        return element.text if element is not None else None
    
    def get_numeric(self, root, xpath: str, ns: Dict) -> Optional[float]:
        """Helper to safely extract numeric values from XML"""
        element = root.find(xpath, ns)
        if element is not None:
            try:
                return float(element.text)
            except (ValueError, TypeError):
                pass
        return None
    
    def process_year(self, year: int, max_downloads: int = 100):
        """Process all Houston nonprofits for a given year"""
        logger.info(f"Processing year {year}")
        
        # Download index
        index_df = self.download_index_file(year)
        if index_df is None:
            return
        
        # Filter for Houston
        houston_df = self.filter_houston_nonprofits(index_df)
        
        # Limit downloads for testing
        houston_df = houston_df.head(max_downloads)
        
        # Process each nonprofit
        processed_data = []
        for idx, row in houston_df.iterrows():
            object_id = row['OBJECT_ID']
            
            # Download XML
            xml_path = self.download_990_xml(object_id, year)
            if xml_path is None:
                continue
            
            # Parse XML
            nonprofit_data = self.parse_990_xml(xml_path)
            if nonprofit_data is None:
                continue
            
            # Add metadata
            nonprofit_data['tax_year'] = year
            nonprofit_data['object_id'] = object_id
            nonprofit_data['ntee_code'] = row.get('NTEE_CD')
            
            processed_data.append(nonprofit_data)
            
            if len(processed_data) % 10 == 0:
                logger.info(f"Processed {len(processed_data)} organizations...")
        
        # Save processed data
        if processed_data:
            output_file = self.processed_dir / f"houston_nonprofits_{year}.json"
            with open(output_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            logger.info(f"Saved {len(processed_data)} organizations to {output_file}")
        
        return processed_data

def main():
    downloader = IRS990Downloader()
    
    # Process recent years (start with 2022 for testing)
    years = [2022, 2023]
    
    all_data = []
    for year in years:
        year_data = downloader.process_year(year, max_downloads=50)  # Limit for testing
        if year_data:
            all_data.extend(year_data)
    
    logger.info(f"Total organizations processed: {len(all_data)}")

if __name__ == "__main__":
    main()