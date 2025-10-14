#!/usr/bin/env python3
"""
Bulk Location Premium Data Importer

This script reads a CSV file with location premium data and:
1. Validates the data
2. Generates SQL INSERT statements
3. Optionally inserts directly into PostgreSQL database

Usage:
    python bulk_import_locations.py <csv_file> [--insert] [--validate-only]

Example:
    python bulk_import_locations.py new_areas.csv --validate-only
    python bulk_import_locations.py new_areas.csv --insert
"""

import csv
import logging
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LocationDataValidator:
    """Validates location premium data for import"""
    
    # Dubai GPS bounds (approximate)
    DUBAI_LAT_MIN = 24.8
    DUBAI_LAT_MAX = 25.5
    DUBAI_LON_MIN = 54.9
    DUBAI_LON_MAX = 55.6
    
    # Reasonable distance limits (km)
    DISTANCE_MIN = 0.0
    DISTANCE_MAX = 50.0
    
    # Neighborhood score limits
    SCORE_MIN = 1.0
    SCORE_MAX = 5.0
    
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_row(self, row_num: int, data: Dict[str, str]) -> bool:
        """
        Validate a single row of data
        
        Args:
            row_num: Row number for error reporting
            data: Dictionary with column names as keys
            
        Returns:
            True if valid, False if errors found
        """
        row_errors = []
        row_warnings = []
        
        # Validate area name
        area_name = data.get('Area Name', '').strip()
        if not area_name:
            row_errors.append(f"Row {row_num}: Area Name is empty")
        elif area_name != area_name.title():
            row_warnings.append(f"Row {row_num}: Area Name '{area_name}' should be Title Case")
        
        # Validate latitude
        try:
            lat = Decimal(data.get('Latitude', '0'))
            if not (self.DUBAI_LAT_MIN <= lat <= self.DUBAI_LAT_MAX):
                row_errors.append(
                    f"Row {row_num}: Latitude {lat} outside Dubai bounds "
                    f"({self.DUBAI_LAT_MIN}-{self.DUBAI_LAT_MAX})"
                )
        except (ValueError, InvalidOperation):
            row_errors.append(f"Row {row_num}: Invalid Latitude value")
        
        # Validate longitude
        try:
            lon = Decimal(data.get('Longitude', '0'))
            if not (self.DUBAI_LON_MIN <= lon <= self.DUBAI_LON_MAX):
                row_errors.append(
                    f"Row {row_num}: Longitude {lon} outside Dubai bounds "
                    f"({self.DUBAI_LON_MIN}-{self.DUBAI_LON_MAX})"
                )
        except (ValueError, InvalidOperation):
            row_errors.append(f"Row {row_num}: Invalid Longitude value")
        
        # Validate distances
        distance_fields = [
            'Metro Distance (km)',
            'Beach Distance (km)',
            'Mall Distance (km)',
            'School Distance (km)',
            'Business Distance (km)'
        ]
        
        for field in distance_fields:
            try:
                distance = Decimal(data.get(field, '10.0'))
                if not (self.DISTANCE_MIN <= distance <= self.DISTANCE_MAX):
                    row_errors.append(
                        f"Row {row_num}: {field} {distance} outside valid range "
                        f"({self.DISTANCE_MIN}-{self.DISTANCE_MAX})"
                    )
            except (ValueError, InvalidOperation):
                row_errors.append(f"Row {row_num}: Invalid {field} value")
        
        # Validate neighborhood score
        try:
            score = Decimal(data.get('Neighborhood Score (1-5)', '3.5'))
            if not (self.SCORE_MIN <= score <= self.SCORE_MAX):
                row_errors.append(
                    f"Row {row_num}: Neighborhood Score {score} outside valid range "
                    f"({self.SCORE_MIN}-{self.SCORE_MAX})"
                )
        except (ValueError, InvalidOperation):
            row_errors.append(f"Row {row_num}: Invalid Neighborhood Score value")
        
        # Store errors and warnings
        self.errors.extend(row_errors)
        self.warnings.extend(row_warnings)
        
        return len(row_errors) == 0
    
    def get_validation_summary(self) -> str:
        """Get formatted validation summary"""
        summary = []
        
        if self.errors:
            summary.append(f"\n❌ {len(self.errors)} ERRORS FOUND:")
            for error in self.errors:
                summary.append(f"  - {error}")
        
        if self.warnings:
            summary.append(f"\n⚠️  {len(self.warnings)} WARNINGS:")
            for warning in self.warnings:
                summary.append(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            summary.append("\n✅ All data valid!")
        
        return "\n".join(summary)


class LocationDataImporter:
    """Imports location premium data from CSV to PostgreSQL"""
    
    def __init__(self, db_url: Optional[str] = None) -> None:
        """
        Initialize importer
        
        Args:
            db_url: PostgreSQL connection string (if None, uses environment variable)
        """
        self.db_url = db_url or self._get_db_url_from_env()
        self.validator = LocationDataValidator()
    
    def _get_db_url_from_env(self) -> str:
        """Get database URL from environment or app.py"""
        try:
            # Try to import from app.py
            sys.path.insert(0, str(Path(__file__).parent))
            from app import app
            return app.config['SQLALCHEMY_DATABASE_URI']
        except Exception as e:
            logger.warning(f"Could not get DB URL from app.py: {e}")
            return "postgresql://postgres:postgres@localhost:5432/avm_db"
    
    def read_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        """
        Read CSV file
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of dictionaries with column names as keys
        """
        logger.info(f"Reading CSV file: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        logger.info(f"Read {len(data)} rows")
        return data
    
    def validate_data(self, data: List[Dict[str, str]]) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Validate all data rows
        
        Args:
            data: List of data dictionaries
            
        Returns:
            Tuple of (all_valid, valid_rows)
        """
        logger.info("Validating data...")
        
        valid_rows = []
        for i, row in enumerate(data, start=2):  # Start at 2 (row 1 is header)
            if self.validator.validate_row(i, row):
                valid_rows.append(row)
        
        logger.info(self.validator.get_validation_summary())
        
        all_valid = len(self.validator.errors) == 0
        return all_valid, valid_rows
    
    def generate_sql_insert(self, row: Dict[str, str]) -> str:
        """
        Generate SQL INSERT statement for a row
        
        Args:
            row: Data dictionary
            
        Returns:
            SQL INSERT statement
        """
        area_name = row['Area Name'].strip()
        latitude = Decimal(row['Latitude'])
        longitude = Decimal(row['Longitude'])
        metro_dist = Decimal(row['Metro Distance (km)'])
        beach_dist = Decimal(row['Beach Distance (km)'])
        mall_dist = Decimal(row['Mall Distance (km)'])
        school_dist = Decimal(row.get('School Distance (km)', '10.0'))
        business_dist = Decimal(row['Business Distance (km)'])
        neighborhood_score = Decimal(row['Neighborhood Score (1-5)'])
        
        sql_stmt = f"""INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    '{area_name}', {latitude}, {longitude},
    {metro_dist}, {beach_dist}, {mall_dist}, {school_dist},
    {business_dist}, {neighborhood_score},
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();"""
        
        return sql_stmt
    
    def generate_sql_file(self, data: List[Dict[str, str]], output_path: Path) -> None:
        """
        Generate SQL file with all INSERT statements
        
        Args:
            data: List of validated data dictionaries
            output_path: Path to output SQL file
        """
        logger.info(f"Generating SQL file: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("-- Location Premium Data Import\n")
            f.write(f"-- Generated: {datetime.now().isoformat()}\n")
            f.write(f"-- Records: {len(data)}\n\n")
            
            f.write("BEGIN;\n\n")
            
            for i, row in enumerate(data, start=1):
                f.write(f"-- Area {i}: {row['Area Name']}\n")
                f.write(self.generate_sql_insert(row))
                f.write("\n\n")
            
            f.write("COMMIT;\n")
        
        logger.info(f"✅ SQL file generated successfully: {output_path}")
    
    def insert_to_database(self, data: List[Dict[str, str]]) -> None:
        """
        Insert data directly to PostgreSQL database
        
        Args:
            data: List of validated data dictionaries
        """
        logger.info("Connecting to database...")
        
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            logger.info("Inserting data...")
            
            inserted = 0
            updated = 0
            
            for row in data:
                area_name = row['Area Name'].strip()
                
                # Check if area exists
                cursor.execute(
                    "SELECT COUNT(*) FROM area_coordinates WHERE area_name = %s",
                    (area_name,)
                )
                exists = cursor.fetchone()[0] > 0
                
                # Insert or update
                cursor.execute(
                    self.generate_sql_insert(row)
                )
                
                if exists:
                    updated += 1
                    logger.info(f"  ↻ Updated: {area_name}")
                else:
                    inserted += 1
                    logger.info(f"  ✓ Inserted: {area_name}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"\n✅ Database update complete:")
            logger.info(f"   • {inserted} new areas inserted")
            logger.info(f"   • {updated} existing areas updated")
            logger.info(f"   • Total: {inserted + updated} areas processed")
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            raise
    
    def process_csv(
        self,
        csv_path: Path,
        insert: bool = False,
        validate_only: bool = False
    ) -> None:
        """
        Process CSV file (validate, generate SQL, optionally insert)
        
        Args:
            csv_path: Path to CSV file
            insert: Whether to insert directly to database
            validate_only: Only validate, don't generate output
        """
        # Read CSV
        data = self.read_csv(csv_path)
        
        # Validate
        all_valid, valid_rows = self.validate_data(data)
        
        if not all_valid:
            logger.error("\n❌ Validation failed. Fix errors and try again.")
            return
        
        logger.info(f"\n✅ All {len(valid_rows)} rows validated successfully!")
        
        if validate_only:
            logger.info("\n--validate-only flag set. Exiting.")
            return
        
        # Generate SQL file
        sql_output = csv_path.with_suffix('.sql')
        self.generate_sql_file(valid_rows, sql_output)
        
        # Insert to database if requested
        if insert:
            logger.info("\n--insert flag set. Inserting to database...")
            self.insert_to_database(valid_rows)
            
            # Clear cache
            logger.info("\nClearing location cache...")
            try:
                conn = psycopg2.connect(self.db_url)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM property_location_cache;")
                conn.commit()
                cursor.close()
                conn.close()
                logger.info("✅ Cache cleared")
            except Exception as e:
                logger.warning(f"⚠️  Could not clear cache: {e}")


def main() -> None:
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import location premium data from CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate only
  python bulk_import_locations.py data.csv --validate-only
  
  # Generate SQL file
  python bulk_import_locations.py data.csv
  
  # Insert directly to database
  python bulk_import_locations.py data.csv --insert
        """
    )
    
    parser.add_argument(
        'csv_file',
        type=Path,
        help='CSV file with location premium data'
    )
    
    parser.add_argument(
        '--insert',
        action='store_true',
        help='Insert data directly to PostgreSQL database'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate data, do not generate output'
    )
    
    parser.add_argument(
        '--db-url',
        type=str,
        help='PostgreSQL connection string (default: from app.py config)'
    )
    
    args = parser.parse_args()
    
    # Check CSV file exists
    if not args.csv_file.exists():
        logger.error(f"❌ CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    # Create importer and process
    importer = LocationDataImporter(db_url=args.db_url)
    
    try:
        importer.process_csv(
            csv_path=args.csv_file,
            insert=args.insert,
            validate_only=args.validate_only
        )
    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
