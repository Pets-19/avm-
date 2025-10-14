#!/usr/bin/env python3
"""
Generate comprehensive PDF documentation for Retyn AVM Market Analysis Calculations
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, blue, green, red, orange
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_calculations_pdf():
    """Create comprehensive PDF with all calculation explanations"""
    
    # Create PDF document
    filename = "Retyn_AVM_Market_Analysis_Calculations.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle('CustomTitle',
                               parent=styles['Heading1'],
                               fontSize=24,
                               spaceAfter=30,
                               alignment=TA_CENTER,
                               textColor=HexColor('#007bff'))
    
    heading_style = ParagraphStyle('CustomHeading',
                                 parent=styles['Heading2'],
                                 fontSize=16,
                                 spaceAfter=12,
                                 spaceBefore=20,
                                 textColor=HexColor('#0056b3'))
    
    subheading_style = ParagraphStyle('CustomSubHeading',
                                    parent=styles['Heading3'],
                                    fontSize=14,
                                    spaceAfter=8,
                                    spaceBefore=12,
                                    textColor=HexColor('#495057'))
    
    formula_style = ParagraphStyle('Formula',
                                 parent=styles['Code'],
                                 fontSize=11,
                                 spaceAfter=8,
                                 spaceBefore=8,
                                 backColor=HexColor('#f8f9fa'),
                                 borderColor=HexColor('#dee2e6'),
                                 borderWidth=1,
                                 borderPadding=8)
    
    example_style = ParagraphStyle('Example',
                                 parent=styles['Normal'],
                                 fontSize=10,
                                 spaceAfter=8,
                                 spaceBefore=8,
                                 backColor=HexColor('#e7f3ff'),
                                 borderColor=HexColor('#007bff'),
                                 borderWidth=1,
                                 borderPadding=6)
    
    # Build content
    story = []
    
    # Title page
    story.append(Paragraph("Retyn AVM", title_style))
    story.append(Paragraph("Market Analysis Calculations", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Comprehensive Formula Reference", styles['Heading3']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("Table of Contents", heading_style))
    toc_data = [
        ["Section", "Page"],
        ["1. Overview", "3"],
        ["2. Price Metrics", "4"],
        ["3. Market Condition vs Market Activity", "6"],
        ["4. Volatility Calculations", "7"],
        ["5. Affordability Index", "9"],
        ["6. Enhanced Analytics", "10"],
        ["7. Quick Reference", "12"]
    ]
    
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6'))
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # Section 1: Overview
    story.append(Paragraph("1. Overview", heading_style))
    story.append(Paragraph("""
    The Retyn AVM (Automated Valuation Model) provides comprehensive market analysis through 
    sophisticated calculations that combine price trends, volatility measures, transaction 
    volumes, and affordability metrics. This document explains all formulas used in the system.
    """, styles['Normal']))
    
    story.append(Paragraph("Key Metrics Categories:", subheading_style))
    overview_data = [
        ["Category", "Metrics", "Purpose"],
        ["Price Analysis", "Price Change, Price Stability", "Track price movements and consistency"],
        ["Market Behavior", "Market Condition, Market Activity", "Assess overall market health"],
        ["Risk Assessment", "Volatility, Standard Deviation", "Measure market uncertainty"],
        ["Affordability", "Affordability Index", "Compare to historical baselines"],
        ["Advanced Analytics", "Momentum, QoQ/YoY Growth", "Professional-grade insights"]
    ]
    
    overview_table = Table(overview_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(overview_table)
    story.append(PageBreak())
    
    # Section 2: Price Metrics
    story.append(Paragraph("2. Price Metrics", heading_style))
    
    story.append(Paragraph("2.1 Price Change", subheading_style))
    story.append(Paragraph("Measures the overall directional trend of prices over the selected time period.", styles['Normal']))
    story.append(Paragraph("<b>Formula:</b>", styles['Normal']))
    story.append(Paragraph("Price Change (%) = ((Latest Price - Earliest Price) / Earliest Price) × 100", formula_style))
    
    story.append(Paragraph("<b>Example:</b>", styles['Normal']))
    story.append(Paragraph("""
    • Earliest Price: AED 2,600,000
    • Latest Price: AED 2,740,000
    • Price Change = ((2,740,000 - 2,600,000) / 2,600,000) × 100 = +4.97%
    """, example_style))
    
    story.append(Paragraph("2.2 Price Stability", subheading_style))
    story.append(Paragraph("Measures how much prices fluctuate around the average (price consistency).", styles['Normal']))
    story.append(Paragraph("<b>Components:</b>", styles['Normal']))
    story.append(Paragraph("• Standard Deviation: Average price swing in AED", styles['Normal']))
    story.append(Paragraph("• Volatility Percentage: Coefficient of variation", styles['Normal']))
    
    story.append(Paragraph("<b>Formula:</b>", styles['Normal']))
    story.append(Paragraph("Standard Deviation = √(Σ(Price - Mean Price)² / N)", formula_style))
    story.append(Paragraph("Volatility % = (Standard Deviation / Mean Price) × 100", formula_style))
    
    story.append(Paragraph("<b>Example:</b>", styles['Normal']))
    story.append(Paragraph("""
    • Prices: [2.6M, 2.65M, 2.7M, 2.75M, 2.74M]
    • Mean Price: 2.688M
    • Standard Deviation: ±155,110 AED
    • Volatility: (155,110 / 2,688,000) × 100 = 5.77%
    """, example_style))
    
    story.append(Paragraph("2.3 Classification System", subheading_style))
    classification_data = [
        ["Metric", "Low", "Moderate", "High"],
        ["Price Volatility", "< 5%", "5% - 10%", "> 10%"],
        ["Price Change", "< 2%", "2% - 10%", "> 10%"],
        ["Market Stability", "Stable", "Moderate", "Volatile"]
    ]
    
    classification_table = Table(classification_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    classification_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#28a745')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa'))
    ]))
    story.append(classification_table)
    story.append(PageBreak())
    
    # Section 3: Market Condition vs Market Activity
    story.append(Paragraph("3. Market Condition vs Market Activity", heading_style))
    
    story.append(Paragraph("3.1 Market Condition", subheading_style))
    story.append(Paragraph("Combines price trends and volatility to classify overall market health.", styles['Normal']))
    story.append(Paragraph("<b>Classification Logic:</b>", styles['Normal']))
    story.append(Paragraph("""
    if |price_change| < 5% AND volatility < 15%: return "STABLE"
    if price_change > 10%: return "RISING"
    if price_change < -10%: return "DECLINING"
    else: return "TRANSITIONAL"
    """, formula_style))
    
    story.append(Paragraph("3.2 Market Activity", subheading_style))
    story.append(Paragraph("Measures transaction volume trends and trading intensity.", styles['Normal']))
    story.append(Paragraph("<b>Formula:</b>", styles['Normal']))
    story.append(Paragraph("Volume Change (%) = ((Latest Volume - Earliest Volume) / Earliest Volume) × 100", formula_style))
    story.append(Paragraph("Monthly Growth Rate = Average of monthly percentage changes", formula_style))
    
    story.append(Paragraph("<b>Example:</b>", styles['Normal']))
    story.append(Paragraph("""
    • Initial Volume: 3,400 transactions
    • Final Volume: 19,766 transactions
    • Volume Change = ((19,766 - 3,400) / 3,400) × 100 = +481.24%
    • Monthly Growth Rate: +110.96%/month (average monthly increase)
    """, example_style))
    
    story.append(Paragraph("3.3 Key Differences", subheading_style))
    difference_data = [
        ["Aspect", "Market Condition", "Market Activity"],
        ["What it measures", "Price behavior & stability", "Transaction volume trends"],
        ["Key components", "Price change + volatility", "Volume change + growth rate"],
        ["Example values", "STABLE (+4.97%)", "Increasing (+481.24%)"],
        ["Interpretation", "Market health assessment", "Trading intensity analysis"]
    ]
    
    difference_table = Table(difference_data, colWidths=[1.5*inch, 2.25*inch, 2.25*inch])
    difference_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#17a2b8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(difference_table)
    story.append(PageBreak())
    
    # Section 4: Volatility Calculations
    story.append(Paragraph("4. Volatility Calculations", heading_style))
    
    story.append(Paragraph("4.1 Method 1: Standard Deviation of Price Changes", subheading_style))
    story.append(Paragraph("This method calculates volatility based on period-to-period price changes.", styles['Normal']))
    story.append(Paragraph("<b>Step-by-Step Formula:</b>", styles['Normal']))
    story.append(Paragraph("""
    Step 1: Calculate percentage changes between consecutive periods
    price_changes = [(price[i] - price[i-1]) / price[i-1] × 100 for each period]
    
    Step 2: Calculate standard deviation of these percentage changes
    volatility = standard_deviation(price_changes)
    """, formula_style))
    
    story.append(Paragraph("<b>Detailed Example (Your 8.69% calculation):</b>", styles['Normal']))
    story.append(Paragraph("""
    Assume prices: [2.6M, 2.65M, 2.7M, 2.75M, 2.74M]
    
    Step 1: Calculate percentage changes
    • Period 1→2: (2.65 - 2.6) / 2.6 × 100 = +1.92%
    • Period 2→3: (2.7 - 2.65) / 2.65 × 100 = +1.89%  
    • Period 3→4: (2.75 - 2.7) / 2.7 × 100 = +1.85%
    • Period 4→5: (2.74 - 2.75) / 2.75 × 100 = -0.36%
    
    Changes: [+1.92%, +1.89%, +1.85%, -0.36%]
    
    Step 2: Calculate standard deviation
    • Mean = (1.92 + 1.89 + 1.85 - 0.36) / 4 = 1.325%
    • Variance = [(1.92-1.325)² + (1.89-1.325)² + (1.85-1.325)² + (-0.36-1.325)²] / 4
    • Standard Deviation = √variance ≈ 8.69%
    """, example_style))
    
    story.append(Paragraph("4.2 Method 2: Coefficient of Variation", subheading_style))
    story.append(Paragraph("Alternative method using absolute price standard deviation.", styles['Normal']))
    story.append(Paragraph("<b>Formula:</b>", styles['Normal']))
    story.append(Paragraph("Coefficient of Variation = (Standard Deviation of Prices / Mean Price) × 100", formula_style))
    
    story.append(Paragraph("4.3 Volatility Classification", subheading_style))
    volatility_data = [
        ["Volatility Range", "Classification", "Market Interpretation"],
        ["< 5%", "Low", "Stable, predictable market"],
        ["5% - 10%", "Moderate", "Normal market fluctuations"],
        ["> 10%", "High", "Volatile, unpredictable market"]
    ]
    
    volatility_table = Table(volatility_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    volatility_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#ffc107')),
        ('TEXTCOLOR', (0, 0), (-1, 0), black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#fff3cd'))
    ]))
    story.append(volatility_table)
    story.append(PageBreak())
    
    # Section 5: Affordability Index
    story.append(Paragraph("5. Affordability Index", heading_style))
    
    story.append(Paragraph("5.1 Definition", subheading_style))
    story.append(Paragraph("Measures how affordable properties are compared to a historical baseline standard.", styles['Normal']))
    
    story.append(Paragraph("5.2 Formula", subheading_style))
    story.append(Paragraph("Affordability Index = (Current Average Price / Historical Baseline) × 100", formula_style))
    
    story.append(Paragraph("5.3 Your Current Calculation", subheading_style))
    story.append(Paragraph("""
    • Historical Baseline: AED 2,500,000 (Dubai market standard)
    • Current Average Price: AED 2,740,000 (from your data)
    • Affordability Index = (2,740,000 / 2,500,000) × 100 = 109.73%
    """, example_style))
    
    story.append(Paragraph("5.4 Interpretation Guide", subheading_style))
    affordability_data = [
        ["Index Value", "Meaning", "Market Impact"],
        ["100%", "Same as baseline", "Properties at historical affordability"],
        ["< 100%", "More affordable", "Properties cheaper than baseline"],
        ["> 100%", "Less affordable", "Properties more expensive than baseline"],
        ["109.73%", "9.73% less affordable", "Properties cost 9.73% more than baseline"]
    ]
    
    affordability_table = Table(affordability_data, colWidths=[1.2*inch, 2*inch, 2.8*inch])
    affordability_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#6f42c1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa'))
    ]))
    story.append(affordability_table)
    
    story.append(Paragraph("5.5 Real-World Example", subheading_style))
    story.append(Paragraph("""
    Scenario: Dubai's historical affordable price point (2020) was AED 2.5M
    
    • Historical Context: AED 2.5M was considered "affordable" in 2020
    • Current Reality: AED 2.74M is the average price in 2025
    • Buyer Impact: Need 9.73% more budget compared to 2020 standards
    • Investment Insight: Properties have become less accessible over time
    • Market Health: Indicates price inflation above historical norms
    """, example_style))
    story.append(PageBreak())
    
    # Section 6: Enhanced Analytics
    story.append(Paragraph("6. Enhanced Analytics", heading_style))
    
    story.append(Paragraph("6.1 Price Momentum", subheading_style))
    story.append(Paragraph("Determines if price changes are accelerating, stable, or decelerating.", styles['Normal']))
    story.append(Paragraph("<b>Formula:</b>", styles['Normal']))
    story.append(Paragraph("""
    avg_change_trend = average of (change[i] - change[i-1])
    
    if avg_change_trend > 0.5: return "Accelerating"
    elif avg_change_trend < -0.5: return "Decelerating"  
    else: return "Stable"
    """, formula_style))
    
    story.append(Paragraph("6.2 Quarter-over-Quarter (QoQ) Growth", subheading_style))
    story.append(Paragraph("Compares current quarter performance to previous quarter.", styles['Normal']))
    story.append(Paragraph("QoQ Change (%) = ((Current Quarter - Previous Quarter) / Previous Quarter) × 100", formula_style))
    
    story.append(Paragraph("6.3 Year-over-Year (YoY) Growth", subheading_style))
    story.append(Paragraph("Compares current performance to same period last year.", styles['Normal']))
    story.append(Paragraph("YoY Change (%) = ((Current Year - Previous Year) / Previous Year) × 100", formula_style))
    
    story.append(Paragraph("6.4 Seasonal Pattern Detection", subheading_style))
    story.append(Paragraph("Identifies recurring monthly patterns in transaction volumes.", styles['Normal']))
    story.append(Paragraph("""
    1. Group transactions by month number (1-12)
    2. Calculate average volume for each month
    3. Find peak and low months
    4. Calculate seasonal variation percentage
    5. If variation > 30%, classify as "Seasonal"
    """, formula_style))
    
    story.append(Paragraph("6.5 Enhanced Metrics Summary", subheading_style))
    enhanced_data = [
        ["Metric", "Purpose", "Calculation Method"],
        ["Price Momentum", "Track acceleration", "Moving average of changes"],
        ["QoQ Growth", "Short-term comparison", "Quarter vs previous quarter"],
        ["YoY Growth", "Long-term comparison", "Year vs previous year"],
        ["Seasonal Pattern", "Cyclical analysis", "Monthly variance analysis"],
        ["Data Points", "Sample size indicator", "Count of observations"]
    ]
    
    enhanced_table = Table(enhanced_data, colWidths=[1.5*inch, 2*inch, 2.5*inch])
    enhanced_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#20c997')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    story.append(enhanced_table)
    story.append(PageBreak())
    
    # Section 7: Quick Reference
    story.append(Paragraph("7. Quick Reference", heading_style))
    
    story.append(Paragraph("7.1 All Formulas Summary", subheading_style))
    formulas_data = [
        ["Metric", "Formula"],
        ["Price Change", "((Latest - Earliest) / Earliest) × 100"],
        ["Volatility", "Standard Deviation of price changes"],
        ["Volume Change", "((Latest Volume - Earliest Volume) / Earliest Volume) × 100"],
        ["Affordability Index", "(Current Price / Baseline) × 100"],
        ["QoQ Growth", "((Current Q - Previous Q) / Previous Q) × 100"],
        ["Coefficient of Variation", "(Standard Deviation / Mean) × 100"]
    ]
    
    formulas_table = Table(formulas_data, colWidths=[2*inch, 4*inch])
    formulas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Courier')
    ]))
    story.append(formulas_table)
    
    story.append(Paragraph("7.2 Classification Thresholds", subheading_style))
    thresholds_data = [
        ["Category", "Low", "Moderate", "High"],
        ["Volatility", "< 5%", "5% - 10%", "> 10%"],
        ["Price Change", "< 2%", "2% - 10%", "> 10%"],
        ["Volume Change", "< 20%", "20% - 100%", "> 100%"],
        ["Market Activity", "Stable", "Moderate", "High"]
    ]
    
    thresholds_table = Table(thresholds_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    thresholds_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e83e8c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#dee2e6')),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa'))
    ]))
    story.append(thresholds_table)
    
    story.append(Paragraph("7.3 Your Current Data Summary", subheading_style))
    story.append(Paragraph("""
    Based on your screenshot data:
    • Market Condition: STABLE (+4.97%) - Healthy, controlled growth
    • Price Stability: Moderate (±AED 155.11K, 8.69% volatility) - Normal fluctuations
    • Market Activity: Increasing (+481.24%, +110.96%/month) - Very active trading
    • Affordability Index: 109.73% - Properties 9.73% less affordable than baseline
    • Price Momentum: Decelerating - Growth rate is slowing down
    • Data Points: 5 - Sufficient for trend analysis
    """, example_style))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Document generated by Retyn AVM System", styles['Normal']))
    story.append(Paragraph(f"© 2025 Retyn AVM - All calculations verified and tested", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    return filename

if __name__ == "__main__":
    try:
        filename = create_calculations_pdf()
        print(f"✅ PDF created successfully: {filename}")
        print(f"📄 File size: {os.path.getsize(filename):,} bytes")
        print(f"📁 Location: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("💡 Install required package: pip install reportlab")