#!/usr/bin/env python3
"""
School Data Processing Time Calculator
Calculates processing time estimates for school data extraction projects
Based on analysis of actual processing data from UDISE Plus portal scraping
"""

import math

class ProcessingTimeCalculator:
    def __init__(self):
        # Processing rates based on actual data analysis
        self.phase1_rate = 0.29  # seconds per school (average)
        self.phase2_rate = 15.90  # seconds per school
        self.combined_rate = 16.19  # seconds per school (Phase 1 + Phase 2)
        
        # Buffer factors for risk mitigation
        self.phase1_buffer = 1.25  # 25% buffer
        self.phase2_buffer = 1.40  # 40% buffer
        self.combined_buffer = 1.35  # 35% buffer

    def calculate_phase1_time(self, num_schools, include_buffer=True):
        """Calculate Phase 1 processing time"""
        base_time = num_schools * self.phase1_rate
        if include_buffer:
            base_time *= self.phase1_buffer
        return base_time

    def calculate_phase2_time(self, num_schools, include_buffer=True):
        """Calculate Phase 2 processing time"""
        base_time = num_schools * self.phase2_rate
        if include_buffer:
            base_time *= self.phase2_buffer
        return base_time

    def calculate_combined_time(self, num_schools, include_buffer=True):
        """Calculate combined Phase 1 + Phase 2 processing time"""
        base_time = num_schools * self.combined_rate
        if include_buffer:
            base_time *= self.combined_buffer
        return base_time

    def format_time(self, seconds):
        """Format time in seconds to human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if secs > 0 and days == 0:  # Only show seconds if less than a day
            parts.append(f"{secs} second{'s' if secs != 1 else ''}")
        
        return ", ".join(parts) if parts else "0 seconds"

    def get_processing_estimate(self, num_schools, processing_type="combined", include_buffer=True):
        """Get comprehensive processing estimate"""
        if processing_type.lower() == "phase1":
            time_seconds = self.calculate_phase1_time(num_schools, include_buffer)
        elif processing_type.lower() == "phase2":
            time_seconds = self.calculate_phase2_time(num_schools, include_buffer)
        else:  # combined
            time_seconds = self.calculate_combined_time(num_schools, include_buffer)
        
        return {
            'schools': num_schools,
            'processing_type': processing_type,
            'time_seconds': time_seconds,
            'time_minutes': time_seconds / 60,
            'time_hours': time_seconds / 3600,
            'time_days': time_seconds / 86400,
            'formatted_time': self.format_time(time_seconds),
            'includes_buffer': include_buffer
        }

    def get_batch_recommendations(self, num_schools, processing_type="combined"):
        """Get batch processing recommendations"""
        if processing_type.lower() == "phase1":
            # Phase 1 batch recommendations
            if num_schools <= 1000:
                return {"batch_size": num_schools, "num_batches": 1, "batch_time": "2-5 minutes"}
            elif num_schools <= 5000:
                return {"batch_size": 2000, "num_batches": math.ceil(num_schools/2000), "batch_time": "10-15 minutes"}
            else:
                return {"batch_size": 5000, "num_batches": math.ceil(num_schools/5000), "batch_time": "25-30 minutes"}
        
        elif processing_type.lower() == "phase2":
            # Phase 2 batch recommendations
            if num_schools <= 100:
                return {"batch_size": num_schools, "num_batches": 1, "batch_time": "15-30 minutes"}
            elif num_schools <= 500:
                return {"batch_size": 200, "num_batches": math.ceil(num_schools/200), "batch_time": "50-60 minutes"}
            else:
                return {"batch_size": 500, "num_batches": math.ceil(num_schools/500), "batch_time": "2-2.5 hours"}
        
        else:  # combined
            # Combined processing recommendations
            if num_schools <= 500:
                return {"batch_size": num_schools, "num_batches": 1, "batch_time": "1-2 hours"}
            elif num_schools <= 2000:
                return {"batch_size": 1000, "num_batches": math.ceil(num_schools/1000), "batch_time": "4-5 hours"}
            else:
                return {"batch_size": 2000, "num_batches": math.ceil(num_schools/2000), "batch_time": "8-10 hours"}

    def print_detailed_estimate(self, num_schools, processing_type="combined", include_buffer=True):
        """Print detailed processing estimate"""
        estimate = self.get_processing_estimate(num_schools, processing_type, include_buffer)
        batch_rec = self.get_batch_recommendations(num_schools, processing_type)
        
        print(f"\n{'='*60}")
        print(f"PROCESSING TIME ESTIMATE")
        print(f"{'='*60}")
        print(f"Schools to process: {num_schools:,}")
        print(f"Processing type: {processing_type.upper()}")
        print(f"Buffer included: {'Yes' if include_buffer else 'No'}")
        print(f"\nESTIMATED TIME:")
        print(f"  Total time: {estimate['formatted_time']}")
        print(f"  In hours: {estimate['time_hours']:.1f}")
        print(f"  In days: {estimate['time_days']:.1f}")
        
        print(f"\nBATCH PROCESSING RECOMMENDATION:")
        print(f"  Recommended batch size: {batch_rec['batch_size']:,} schools")
        print(f"  Number of batches: {batch_rec['num_batches']}")
        print(f"  Time per batch: {batch_rec['batch_time']}")
        
        # Daily processing capacity
        daily_capacity = 86400 / (estimate['time_seconds'] / num_schools)
        print(f"\nDAILY PROCESSING CAPACITY:")
        print(f"  Schools per day (24h): {daily_capacity:.0f}")
        print(f"  Schools per day (8h): {daily_capacity/3:.0f}")

def main():
    """Interactive calculator"""
    calculator = ProcessingTimeCalculator()
    
    print("🚀 SCHOOL DATA PROCESSING TIME CALCULATOR")
    print("Based on actual UDISE Plus portal scraping performance data")
    print("="*60)
    
    while True:
        try:
            # Get user input
            print("\nEnter the number of schools to process (or 'quit' to exit):")
            user_input = input("> ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            num_schools = int(user_input.replace(',', ''))
            
            print("\nSelect processing type:")
            print("1. Phase 1 only (basic school data)")
            print("2. Phase 2 only (detailed school data)")
            print("3. Combined (Phase 1 + Phase 2)")
            
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                processing_type = "phase1"
            elif choice == "2":
                processing_type = "phase2"
            else:
                processing_type = "combined"
            
            print("\nInclude buffer time for risks? (recommended)")
            buffer_choice = input("Enter y/n (default: y): ").strip().lower()
            include_buffer = buffer_choice != 'n'
            
            # Calculate and display estimate
            calculator.print_detailed_estimate(num_schools, processing_type, include_buffer)
            
            # Ask if user wants to see comparison
            print("\nWould you like to see all processing types for comparison?")
            compare_choice = input("Enter y/n: ").strip().lower()
            
            if compare_choice == 'y':
                print(f"\n{'='*60}")
                print(f"COMPARISON FOR {num_schools:,} SCHOOLS")
                print(f"{'='*60}")
                
                for ptype in ["phase1", "phase2", "combined"]:
                    est = calculator.get_processing_estimate(num_schools, ptype, include_buffer)
                    print(f"{ptype.upper():>12}: {est['formatted_time']}")
            
        except ValueError:
            print("❌ Please enter a valid number of schools")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# Predefined estimates for common scenarios
def show_predefined_estimates():
    """Show predefined estimates for common scenarios"""
    calculator = ProcessingTimeCalculator()
    
    scenarios = [
        (500, "Small district"),
        (1000, "Medium district"),
        (5000, "Large district"),
        (10000, "Small state"),
        (25000, "Medium state"),
        (50000, "Large state"),
        (100000, "Very large state")
    ]
    
    print("\n📊 PREDEFINED PROCESSING TIME ESTIMATES")
    print("="*80)
    print(f"{'Scenario':<20} {'Schools':<10} {'Phase 1':<15} {'Phase 2':<15} {'Combined':<15}")
    print("-"*80)
    
    for schools, scenario in scenarios:
        p1 = calculator.get_processing_estimate(schools, "phase1", True)
        p2 = calculator.get_processing_estimate(schools, "phase2", True)
        combined = calculator.get_processing_estimate(schools, "combined", True)
        
        print(f"{scenario:<20} {schools:<10,} {p1['formatted_time']:<15} {p2['formatted_time']:<15} {combined['formatted_time']:<15}")

if __name__ == "__main__":
    # Show predefined estimates first
    show_predefined_estimates()
    
    # Then run interactive calculator
    main()
