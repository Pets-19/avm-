"""
Export training data from PostgreSQL database for ML model training.
Extracts property transactions and prepares features for XGBoost model.
"""
import os
import logging
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_database_connection() -> Optional[str]:
    """Load database connection string from environment."""
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DATABASE_URL not found in environment variables")
        return None
    
    logger.info("✅ Database URL loaded successfully")
    return database_url


def export_properties_data(engine, output_file: str = "data/properties_training.csv") -> pd.DataFrame:
    """
    Export properties data from PostgreSQL to CSV.
    
    Args:
        engine: SQLAlchemy engine
        output_file: Path to save CSV file
        
    Returns:
        DataFrame with exported data
    """
    logger.info("Starting properties data export...")
    
    query = """
    SELECT 
        transaction_number,
        area_en,
        prop_type_en,
        prop_sb_type_en,
        trans_value,
        group_en,
        procedure_en,
        procedure_area,
        actual_area,
        rooms_en,
        parking,
        nearest_metro_en,
        nearest_mall_en,
        nearest_landmark_en,
        master_project_en,
        project_en,
        instance_date,
        is_offplan_en,
        usage_en,
        is_free_hold_en,
        total_buyer,
        total_seller
    FROM properties
    WHERE trans_value > 0 
        AND trans_value < 100000000
        AND CAST(actual_area AS FLOAT) > 0
        AND CAST(actual_area AS FLOAT) < 50000
        AND prop_type_en IS NOT NULL
        AND area_en IS NOT NULL
    ORDER BY instance_date DESC
    """
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        
        logger.info(f"✅ Exported {len(df):,} property records")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Date range: {df['instance_date'].min()} to {df['instance_date'].max()}")
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"✅ Data saved to {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error exporting data: {e}")
        raise


def export_rentals_data(engine, output_file: str = "data/rentals_training.csv") -> pd.DataFrame:
    """
    Export rentals data from PostgreSQL to CSV.
    
    Args:
        engine: SQLAlchemy engine
        output_file: Path to save CSV file
        
    Returns:
        DataFrame with exported data
    """
    logger.info("Starting rentals data export...")
    
    query = """
    SELECT 
        registration_date,
        start_date,
        end_date,
        version_en,
        area_en,
        prop_type_en,
        prop_sub_type_en,
        annual_amount,
        contract_amount,
        actual_area,
        rooms,
        usage_en,
        nearest_metro_en,
        nearest_mall_en,
        nearest_landmark_en,
        master_project_en,
        project_en,
        is_free_hold_en,
        parking,
        total_properties
    FROM rentals
    WHERE annual_amount > 0 
        AND annual_amount < 10000000
        AND prop_type_en IS NOT NULL
        AND area_en IS NOT NULL
    ORDER BY registration_date DESC
    """
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(query), conn)
        
        logger.info(f"✅ Exported {len(df):,} rental records")
        logger.info(f"Columns: {list(df.columns)}")
        if len(df) > 0:
            logger.info(f"Date range: {df['registration_date'].min()} to {df['registration_date'].max()}")
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        logger.info(f"✅ Data saved to {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error exporting rentals data: {e}")
        raise


def print_data_summary(df: pd.DataFrame, data_type: str = "Properties"):
    """Print summary statistics of the exported data."""
    logger.info(f"\n{'='*60}")
    logger.info(f"{data_type} Data Summary")
    logger.info(f"{'='*60}")
    
    logger.info(f"Total records: {len(df):,}")
    logger.info(f"Total columns: {len(df.columns)}")
    
    if data_type == "Properties":
        price_col = 'trans_value'
        area_col = 'actual_area'
    else:
        price_col = 'annual_amount'
        area_col = None
    
    logger.info(f"\n{price_col.replace('_', ' ').title()} Statistics:")
    logger.info(f"  Mean: AED {df[price_col].mean():,.2f}")
    logger.info(f"  Median: AED {df[price_col].median():,.2f}")
    logger.info(f"  Min: AED {df[price_col].min():,.2f}")
    logger.info(f"  Max: AED {df[price_col].max():,.2f}")
    
    if area_col and area_col in df.columns:
        logger.info(f"\n{area_col.replace('_', ' ').title()} Statistics:")
        logger.info(f"  Mean: {df[area_col].mean():,.2f} sqft")
        logger.info(f"  Median: {df[area_col].median():,.2f} sqft")
    
    logger.info(f"\nTop 10 Areas by Transaction Count:")
    area_counts = df['area_en'].value_counts().head(10)
    for area, count in area_counts.items():
        logger.info(f"  {area}: {count:,} transactions")
    
    logger.info(f"\nProperty Types Distribution:")
    type_counts = df['prop_type_en'].value_counts()
    for prop_type, count in type_counts.items():
        logger.info(f"  {prop_type}: {count:,} ({count/len(df)*100:.1f}%)")
    
    logger.info(f"\nMissing Values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        for col, count in missing.items():
            logger.info(f"  {col}: {count:,} ({count/len(df)*100:.1f}%)")
    else:
        logger.info("  No missing values in key columns ✅")
    
    logger.info(f"{'='*60}\n")


def main():
    """Main execution function."""
    logger.info("🚀 Starting data export process...")
    
    # Load database connection
    database_url = load_database_connection()
    if not database_url:
        logger.error("Cannot proceed without database connection")
        return
    
    # Create database engine
    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=5
        )
        logger.info("✅ Database engine created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database engine: {e}")
        return
    
    # Export properties data
    try:
        properties_df = export_properties_data(engine)
        print_data_summary(properties_df, "Properties")
    except Exception as e:
        logger.error(f"❌ Properties export failed: {e}")
        properties_df = None
    
    # Export rentals data
    try:
        rentals_df = export_rentals_data(engine)
        print_data_summary(rentals_df, "Rentals")
    except Exception as e:
        logger.error(f"❌ Rentals export failed: {e}")
        rentals_df = None
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("📊 Export Complete!")
    logger.info("="*60)
    if properties_df is not None:
        logger.info(f"✅ Properties: {len(properties_df):,} records → data/properties_training.csv")
    if rentals_df is not None:
        logger.info(f"✅ Rentals: {len(rentals_df):,} records → data/rentals_training.csv")
    logger.info("="*60)
    
    logger.info("\n🎯 Next Steps:")
    logger.info("1. Review the exported CSV files in the data/ directory")
    logger.info("2. Run train_model.py to train the XGBoost model")
    logger.info("3. Model files will be saved to models/ directory")


if __name__ == "__main__":
    main()
