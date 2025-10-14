"""
Geospatial Enhancement Test Suite
Tests database schema, functions, and integration with valuation endpoint.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import app, engine
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)


class GeospatialTester:
    """Test suite for geospatial enhancement features."""
    
    def __init__(self) -> None:
        """Initialize tester with database connection."""
        self.passed: int = 0
        self.failed: int = 0
        self.conn = None
        
    def setup(self) -> bool:
        """Setup test environment."""
        try:
            # Use raw connection from engine for direct SQL queries
            self.conn = engine.raw_connection()
            logger.info("✅ Database connection established")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            return False
    
    def teardown(self) -> None:
        """Cleanup test environment."""
        if self.conn:
            self.conn.close()
            logger.info("✅ Database connection closed")
    
    def assert_true(self, condition: bool, test_name: str, message: str = "") -> None:
        """Assert condition is true."""
        if condition:
            self.passed += 1
            logger.info(f"✅ PASS: {test_name}")
            if message:
                logger.info(f"   {message}")
        else:
            self.failed += 1
            logger.error(f"❌ FAIL: {test_name}")
            if message:
                logger.error(f"   {message}")
    
    def test_database_schema(self) -> bool:
        """Test 1: Verify database tables exist."""
        logger.info("\n" + "="*60)
        logger.info("Test 1: Database Schema")
        logger.info("="*60)
        
        try:
            cursor = self.conn.cursor()
            
            # Check area_coordinates table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'area_coordinates'
                )
            """)
            area_table_exists = cursor.fetchone()[0]
            self.assert_true(
                area_table_exists,
                "area_coordinates table exists",
                "Table found in database"
            )
            
            # Check amenities table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'amenities'
                )
            """)
            amenities_table_exists = cursor.fetchone()[0]
            self.assert_true(
                amenities_table_exists,
                "amenities table exists",
                "Table found in database"
            )
            
            # Check property_location_cache table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'property_location_cache'
                )
            """)
            cache_table_exists = cursor.fetchone()[0]
            self.assert_true(
                cache_table_exists,
                "property_location_cache table exists",
                "Table found in database"
            )
            
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Database schema test failed: {e}")
            return False
    
    def test_area_coordinates_data(self) -> bool:
        """Test 2: Verify area coordinates data is loaded."""
        logger.info("\n" + "="*60)
        logger.info("Test 2: Area Coordinates Data")
        logger.info("="*60)
        
        try:
            cursor = self.conn.cursor()
            
            # Count rows
            cursor.execute("SELECT COUNT(*) FROM area_coordinates")
            count = cursor.fetchone()[0]
            self.assert_true(
                count >= 10,
                "area_coordinates has data",
                f"Found {count} areas"
            )
            
            # Check Dubai Marina specifically
            cursor.execute("""
                SELECT latitude, longitude, distance_to_metro_km, 
                       distance_to_beach_km, distance_to_mall_km
                FROM area_coordinates
                WHERE area_name = 'Dubai Marina'
            """)
            dubai_marina = cursor.fetchone()
            self.assert_true(
                dubai_marina is not None,
                "Dubai Marina coordinates exist",
                f"Lat: {dubai_marina[0]}, Lon: {dubai_marina[1]}" if dubai_marina else ""
            )
            
            if dubai_marina:
                # Validate coordinates are in Dubai range
                lat, lon = float(dubai_marina[0]), float(dubai_marina[1])
                in_dubai = 24.5 < lat < 25.5 and 54.5 < lon < 56.0
                self.assert_true(
                    in_dubai,
                    "Dubai Marina coordinates are valid",
                    f"Within Dubai bounds: {lat}, {lon}"
                )
                
                # Check distance values
                metro_dist = float(dubai_marina[2]) if dubai_marina[2] else None
                beach_dist = float(dubai_marina[3]) if dubai_marina[3] else None
                
                self.assert_true(
                    metro_dist is not None and metro_dist < 2.0,
                    "Dubai Marina metro distance is reasonable",
                    f"{metro_dist} km (should be < 2km)"
                )
                
                self.assert_true(
                    beach_dist is not None and beach_dist < 1.0,
                    "Dubai Marina beach distance is reasonable",
                    f"{beach_dist} km (should be < 1km - it's waterfront!)"
                )
            
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Area coordinates data test failed: {e}")
            return False
    
    def test_amenities_data(self) -> bool:
        """Test 3: Verify amenities data is loaded."""
        logger.info("\n" + "="*60)
        logger.info("Test 3: Amenities Data")
        logger.info("="*60)
        
        try:
            cursor = self.conn.cursor()
            
            # Count rows
            cursor.execute("SELECT COUNT(*) FROM amenities")
            count = cursor.fetchone()[0]
            self.assert_true(
                count >= 10,
                "amenities table has data",
                f"Found {count} amenities"
            )
            
            # Check we have key amenity types
            for amenity_type in ['metro', 'beach', 'mall']:
                cursor.execute("""
                    SELECT COUNT(*) FROM amenities 
                    WHERE type = %s
                """, (amenity_type,))
                type_count = cursor.fetchone()[0]
                self.assert_true(
                    type_count > 0,
                    f"{amenity_type} amenities exist",
                    f"Found {type_count} {amenity_type} locations"
                )
            
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Amenities data test failed: {e}")
            return False
    
    def test_geospatial_functions_in_app(self) -> bool:
        """Test 4: Test geospatial functions integrated in app.py."""
        logger.info("\n" + "="*60)
        logger.info("Test 4: Geospatial Functions in app.py")
        logger.info("="*60)
        
        try:
            from app import (
                calculate_haversine_distance,
                get_location_cache,
                calculate_location_premium,
                update_location_cache
            )
            
            # Test Haversine distance calculation
            # Dubai Marina to Burj Khalifa (approximately 15-16 km)
            dubai_marina_lat, dubai_marina_lon = 25.0772, 55.1370
            burj_khalifa_lat, burj_khalifa_lon = 25.1972, 55.2744
            
            distance = calculate_haversine_distance(
                dubai_marina_lat, dubai_marina_lon,
                burj_khalifa_lat, burj_khalifa_lon
            )
            
            self.assert_true(
                distance is not None and 14 < distance < 18,
                "Haversine distance calculation is accurate",
                f"Dubai Marina to Burj Khalifa: {distance:.2f} km (expected ~15-16 km)"
            )
            
            # Test cache miss
            cache_result = get_location_cache('Test Area XYZ', 'Unit', '2')
            self.assert_true(
                not cache_result.get('cache_hit'),
                "Cache returns miss for non-existent entry",
                f"Cache status: {cache_result}"
            )
            
            # Test calculate_location_premium with Dubai Marina
            premium_data = calculate_location_premium('Dubai Marina')
            self.assert_true(
                premium_data is not None and 'total_premium' in premium_data,
                "calculate_location_premium returns data for Dubai Marina",
                f"Premium: {premium_data.get('total_premium', 0):+.2f}%"
            )
            
            if premium_data:
                total_premium = premium_data.get('total_premium', 0)
                self.assert_true(
                    total_premium > 5,
                    "Dubai Marina has positive location premium",
                    f"Premium: {total_premium:+.2f}% (expected > 5% for prime location)"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Geospatial functions test failed: {e}")
            return False
    
    def test_cache_operations(self) -> bool:
        """Test 5: Test cache get/update operations."""
        logger.info("\n" + "="*60)
        logger.info("Test 5: Cache Operations")
        logger.info("="*60)
        
        try:
            from app import get_location_cache, update_location_cache
            
            # Test cache miss
            test_area = 'Test Area Cache 123'
            cache_result = get_location_cache(test_area, 'Unit', '2')
            self.assert_true(
                not cache_result.get('cache_hit'),
                "Cache returns miss for new entry",
                f"Result: {cache_result}"
            )
            
            # Test cache update
            test_premium_data = {
                'total_premium': 12.5,
                'metro_premium': 5.0,
                'beach_premium': 3.0,
                'mall_premium': 2.0,
                'school_premium': 1.5,
                'business_premium': 0.5,
                'neighborhood_premium': 0.5
            }
            
            update_location_cache(test_area, 'Unit', '2', test_premium_data)
            
            # Test cache hit
            cache_result = get_location_cache(test_area, 'Unit', '2')
            self.assert_true(
                cache_result.get('cache_hit'),
                "Cache returns hit after update",
                f"Cached premium: {cache_result.get('premium', 0)}%"
            )
            
            if cache_result.get('cache_hit'):
                cached_premium = cache_result.get('premium', 0)
                self.assert_true(
                    abs(cached_premium - test_premium_data['total_premium']) < 0.1,
                    "Cached premium matches stored value",
                    f"Expected: {test_premium_data['total_premium']}%, Got: {cached_premium}%"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Cache operations test failed: {e}")
            return False
    
    def test_valuation_integration(self) -> bool:
        """Test 6: Test integration with valuation endpoint."""
        logger.info("\n" + "="*60)
        logger.info("Test 6: Valuation Integration")
        logger.info("="*60)
        
        try:
            from app import calculate_valuation_from_database
            
            # Test valuation with geospatial data
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Dubai Marina',
                size_sqm=100,
                bedrooms='2',
                development_status=None,
                engine=engine
            )
            
            self.assert_true(
                result.get('success', False),
                "Valuation calculation succeeds",
                f"Result keys: {list(result.keys())}"
            )
            
            if result.get('success'):
                valuation = result.get('valuation', {})
                
                self.assert_true(
                    'location_premium' in valuation,
                    "Valuation includes location_premium data",
                    f"Premium data: {valuation.get('location_premium')}"
                )
                
                location_premium = valuation.get('location_premium', {})
                self.assert_true(
                    'total_premium_pct' in location_premium,
                    "location_premium includes total_premium_pct",
                    f"Total premium: {location_premium.get('total_premium_pct')}%"
                )
                
                self.assert_true(
                    'cache_status' in location_premium,
                    "location_premium includes cache_status",
                    f"Cache status: {location_premium.get('cache_status')}"
                )
                
                self.assert_true(
                    'estimated_value' in valuation,
                    "Valuation includes estimated_value",
                    f"Estimated value: AED {valuation.get('estimated_value', 0):,.0f}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Valuation integration test failed: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test 7: Performance benchmarks."""
        logger.info("\n" + "="*60)
        logger.info("Test 7: Performance Benchmarks")
        logger.info("="*60)
        
        try:
            from app import get_location_cache, calculate_location_premium
            
            # Test cache lookup performance
            start = time.time()
            iterations = 100
            for _ in range(iterations):
                get_location_cache('Dubai Marina', 'Unit', '2')
            duration = time.time() - start
            
            avg_time_ms = (duration / iterations) * 1000
            self.assert_true(
                duration < 1.0,
                f"{iterations} cache lookups complete in < 1 second",
                f"Duration: {duration:.3f}s (avg {avg_time_ms:.1f}ms per lookup)"
            )
            
            # Test premium calculation performance
            start = time.time()
            iterations = 10
            for _ in range(iterations):
                calculate_location_premium('Dubai Marina')
            duration = time.time() - start
            
            avg_time_ms = (duration / iterations) * 1000
            self.assert_true(
                avg_time_ms < 100,
                f"{iterations} premium calculations complete with acceptable speed",
                f"Duration: {duration:.3f}s (avg {avg_time_ms:.1f}ms per calculation)"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests and report results."""
        logger.info("\n" + "="*60)
        logger.info("GEOSPATIAL ENHANCEMENT TEST SUITE")
        logger.info("="*60)
        
        if not self.setup():
            logger.error("Failed to setup test environment. Aborting.")
            return False
        
        try:
            # Run all tests
            self.test_database_schema()
            self.test_area_coordinates_data()
            self.test_amenities_data()
            self.test_geospatial_functions_in_app()
            self.test_cache_operations()
            self.test_valuation_integration()
            self.test_performance()
            
        finally:
            self.teardown()
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Passed: {self.passed}")
        logger.info(f"❌ Failed: {self.failed}")
        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info("="*60)
        
        return self.failed == 0


def main() -> None:
    """Main entry point."""
    tester = GeospatialTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
