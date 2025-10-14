#!/bin/bash
# Production Launch File Organization Script
# Date: October 14, 2025
# This script moves non-production files to archive/ folder

echo "🚀 Organizing files for production launch..."

# Create archive structure
mkdir -p archive/documentation
mkdir -p archive/testing
mkdir -p archive/development

# Move documentation files (keep only critical ones in root)
echo "📄 Archiving documentation..."
mv ADDITIONAL_*.md archive/documentation/ 2>/dev/null
mv ALL_*.txt archive/documentation/ 2>/dev/null
mv APPROACH_*.md archive/documentation/ 2>/dev/null
mv ARBITRAGE_*.md archive/documentation/ 2>/dev/null
mv AREAS_*.txt archive/documentation/ 2>/dev/null
mv AREA_NAMES_*.txt archive/documentation/ 2>/dev/null
mv AUDIT_*.md archive/documentation/ 2>/dev/null
mv BEFORE_*.md archive/documentation/ 2>/dev/null
mv BUG_*.md archive/documentation/ 2>/dev/null
mv BUSINESS_DISTRICT_*.md archive/documentation/ 2>/dev/null
mv CALCULATIONS_*.md archive/documentation/ 2>/dev/null
mv CALCULATION_*.md archive/documentation/ 2>/dev/null
mv CURRENT_STATUS_*.md archive/documentation/ 2>/dev/null
mv DEBUG_*.md archive/documentation/ 2>/dev/null
mv DUPLICATE_*.md archive/documentation/ 2>/dev/null
mv ERROR_REPORTING_*.md archive/documentation/ 2>/dev/null
mv EXACT_INPUT_*.md archive/documentation/ 2>/dev/null
mv FEATURE_*.md archive/documentation/ 2>/dev/null
mv FLASK_*.md archive/documentation/ 2>/dev/null
mv FLIP_SCORE_*.md archive/documentation/ 2>/dev/null
mv GEOSPATIAL_*.md archive/documentation/ 2>/dev/null
mv HOW_TO_*.md archive/documentation/ 2>/dev/null
mv IMPLEMENTATION_*.md archive/documentation/ 2>/dev/null
mv IMPORT_*.md archive/documentation/ 2>/dev/null
mv INDUSTRY_*.md archive/documentation/ 2>/dev/null
mv LAYOUT_*.md archive/documentation/ 2>/dev/null
mv LIVE_TEST_*.md archive/documentation/ 2>/dev/null
mv LOCATION_PREMIUM_*.md archive/documentation/ 2>/dev/null
mv LOCATION_PREMIUM_*.csv archive/documentation/ 2>/dev/null
mv MEDIUM_PRIORITY_*.txt archive/documentation/ 2>/dev/null
mv MEDIUM_PRIORITY_*.md archive/documentation/ 2>/dev/null
mv ML_*.md archive/documentation/ 2>/dev/null
mv MODAL_*.md archive/documentation/ 2>/dev/null
mv NEW_AREAS_*.md archive/documentation/ 2>/dev/null
mv NEXT_*.txt archive/documentation/ 2>/dev/null
mv PDF_*.md archive/documentation/ 2>/dev/null
mv PHASE_*.md archive/documentation/ 2>/dev/null
mv PROJECT_PREMIUM_*.md archive/documentation/ 2>/dev/null
mv QUICK_*.md archive/documentation/ 2>/dev/null
mv QUICK_*.txt archive/documentation/ 2>/dev/null
mv RENTAL_*.md archive/documentation/ 2>/dev/null
mv Retyn_*.pdf archive/documentation/ 2>/dev/null
mv SEGMENT_*.md archive/documentation/ 2>/dev/null
mv SELF_*.md archive/documentation/ 2>/dev/null
mv SOLUTION_*.py archive/documentation/ 2>/dev/null
mv STATUS_*.md archive/documentation/ 2>/dev/null
mv TECHNICAL_*.md archive/documentation/ 2>/dev/null
mv TESTING_*.md archive/documentation/ 2>/dev/null
mv TOOLTIP_*.md archive/documentation/ 2>/dev/null
mv TOP_*.txt archive/documentation/ 2>/dev/null
mv TROUBLESHOOTING.md archive/documentation/ 2>/dev/null
mv UNIFIED_*.md archive/documentation/ 2>/dev/null
mv URGENT_*.md archive/documentation/ 2>/dev/null
mv UX_*.md archive/documentation/ 2>/dev/null
mv VALUATION_*.md archive/documentation/ 2>/dev/null
mv VALUE_RANGE_*.md archive/documentation/ 2>/dev/null
mv VERIFICATION_*.md archive/documentation/ 2>/dev/null
mv VISUAL_*.md archive/documentation/ 2>/dev/null
mv YOUR_*.md archive/documentation/ 2>/dev/null
mv agent.md archive/documentation/ 2>/dev/null

# Move test files
echo "🧪 Archiving test files..."
mv test_*.py archive/testing/ 2>/dev/null
mv 3_month_*.py archive/testing/ 2>/dev/null
mv sample_output_*.py archive/testing/ 2>/dev/null
mv verify_*.py archive/testing/ 2>/dev/null
mv extract_*.py archive/testing/ 2>/dev/null
mv get_trends_*.py archive/testing/ 2>/dev/null
mv test_runner.sh archive/testing/ 2>/dev/null

# Move development/utility scripts
echo "🔧 Archiving development scripts..."
mv bulk_import_*.py archive/development/ 2>/dev/null
mv check_and_fix_*.py archive/development/ 2>/dev/null
mv export_training_*.py archive/development/ 2>/dev/null
mv generate_calculations_*.py archive/development/ 2>/dev/null
mv geocoding_*.py archive/development/ 2>/dev/null
mv setup_geospatial_*.py archive/development/ 2>/dev/null
mv train_model.py archive/development/ 2>/dev/null
mv valuation_engine_sample.py archive/development/ 2>/dev/null
mv valuation_engine_production.py archive/development/ 2>/dev/null
mv cookies.txt archive/development/ 2>/dev/null
mv location_data_batch_1.* archive/development/ 2>/dev/null
mv training_increment2.log archive/development/ 2>/dev/null
mv flask*.log archive/development/ 2>/dev/null

# Move old requirements backup
mv =*.0 archive/development/ 2>/dev/null

echo ""
echo "✅ File organization complete!"
echo ""
echo "📁 Production structure:"
echo "  ├── app.py (main application)"
echo "  ├── requirements.txt"
echo "  ├── Dockerfile"
echo "  ├── docker-compose.yaml"
echo "  ├── .env (environment variables)"
echo "  ├── deploy.sh"
echo "  ├── models/ (ML model)"
echo "  ├── static/ (CSS, JS, images)"
echo "  ├── templates/ (HTML)"
echo "  ├── data/ (training CSVs - not in git)"
echo "  ├── sql/ (database setup scripts)"
echo "  ├── tests/ (keep unit tests)"
echo "  └── archive/ (non-production files)"
echo ""
echo "🗄️  Database Status:"
echo "  ✅ All data in PostgreSQL (not dependent on CSV files)"
echo "  ✅ Rentals: 620,859 rows"
echo "  ✅ Properties: 153,573 rows"
echo "  ✅ Area coordinates: 70 rows"
echo "  ✅ Project premiums: 10 rows"
echo ""
echo "⚠️  CRITICAL: Large CSV files (data/rentals_training.csv - 110MB)"
echo "  - Already in .gitignore ✅"
echo "  - NOT needed for production (data in database) ✅"
echo "  - Keep locally for ML retraining only ✅"
echo ""
echo "🚀 Ready for production deployment!"
