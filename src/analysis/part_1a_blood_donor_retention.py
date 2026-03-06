"""
BNM Data Scientist Assessment - Part 1a: Blood Donor Retention Analysis

Task: Evaluate Malaysia's blood donor retention effectiveness and assess changes 
       over the past 10 years. Propose practical strategies for improving donations.

Data Source: https://data.kijang.net/dea/retention/data.parquet
"""

import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class BloodDonorRetentionAnalysis:
    """Comprehensive blood donor retention analysis framework"""
    
    def __init__(self, parquet_path):
        """
        Initialize with parquet data
        Args:
            parquet_path: Path to data.parquet file
        """
        self.df = pd.read_parquet(parquet_path)
        self.analysis_results = {}
        
    def data_exploration(self):
        """Initial data exploration and profiling"""
        print("=" * 80)
        print("DATA EXPLORATION & PROFILING")
        print("=" * 80)
        
        print(f"\nDataset Shape: {self.df.shape}")
        print(f"\nColumn Names & Types:\n{self.df.dtypes}")
        print(f"\nFirst Few Rows:\n{self.df.head()}")
        print(f"\nMissing Values:\n{self.df.isnull().sum()}")
        print(f"\nBasic Statistics:\n{self.df.describe()}")
        
        return self.df
    
    def calculate_retention_metrics(self):
        """
        Calculate key retention metrics
        - Retention rate: % of donors who return for another donation
        - Repeat donation rate: frequency of repeat donations
        - Lapsed donor rate: donors who haven't donated in past year
        - New vs. repeat donor split
        """
        print("\n" + "=" * 80)
        print("RETENTION METRICS CALCULATION")
        print("=" * 80)
        
        # Ensure donation_date is datetime
        self.df['donation_date'] = pd.to_datetime(self.df['donation_date'])
        
        # Extract year for analysis
        self.df['year'] = self.df['donation_date'].dt.year
        self.df['month'] = self.df['donation_date'].dt.month
        
        # Metrics by donor
        donor_stats = self.df.groupby('donor_id').agg({
            'donation_date': ['count', 'min', 'max'],
            'donor_id': 'first'
        }).reset_index(drop=True)
        
        donor_stats.columns = ['total_donations', 'first_donation', 'last_donation']
        donor_stats['donation_span_days'] = (donor_stats['last_donation'] - 
                                            donor_stats['first_donation']).dt.days
        donor_stats['is_repeat_donor'] = donor_stats['total_donations'] > 1
        
        # Calculate retention rate (donors with 2+ donations / total unique donors)
        retention_rate = (donor_stats['is_repeat_donor'].sum() / len(donor_stats)) * 100
        
        self.analysis_results['retention_rate'] = retention_rate
        self.analysis_results['donor_stats'] = donor_stats
        
        print(f"\nTotal Unique Donors: {len(donor_stats):,}")
        print(f"Repeat Donors (2+ donations): {donor_stats['is_repeat_donor'].sum():,}")
        print(f"First-Time Donors: {(~donor_stats['is_repeat_donor']).sum():,}")
        print(f"Overall Retention Rate: {retention_rate:.2f}%")
        print(f"\nDonation Frequency Distribution:")
        print(donor_stats['total_donations'].value_counts().sort_index().head(10))
        
        return donor_stats
    
    def analyze_retention_trends(self):
        """
        Analyze retention trends over 10 years
        Compare cohort retention: donors by first donation year
        """
        print("\n" + "=" * 80)
        print("RETENTION TRENDS ANALYSIS (10-YEAR)")
        print("=" * 80)
        
        # Create donor cohorts by first donation year
        donor_cohorts = self.df.groupby('donor_id').agg({
            'donation_date': 'min',
            'donor_id': 'first'
        }).reset_index(drop=True)
        donor_cohorts.columns = ['first_donation_date', 'donor_id']
        donor_cohorts['cohort_year'] = donor_cohorts['first_donation_date'].dt.year
        
        # Merge back to get all donations per cohort
        cohort_data = self.df.merge(
            donor_cohorts[['donor_id', 'cohort_year', 'first_donation_date']],
            on='donor_id'
        )
        
        # Calculate retention by cohort and years since first donation
        cohort_data['years_since_first'] = (
            cohort_data['donation_date'] - cohort_data['first_donation_date']
        ).dt.days / 365.25
        
        # Cohort retention table
        cohort_retention = cohort_data.groupby('cohort_year').agg({
            'donor_id': 'nunique',
            'donation_date': 'count',
            'years_since_first': 'max'
        }).reset_index()
        cohort_retention.columns = ['cohort_year', 'cohort_size', 'total_donations', 'max_years']
        cohort_retention['avg_donations_per_donor'] = (
            cohort_retention['total_donations'] / cohort_retention['cohort_size']
        )
        
        print("\nCohort Retention Analysis:")
        print(cohort_retention.sort_values('cohort_year'))
        
        # Year-over-year retention rate
        yoy_retention = self._calculate_yoy_retention()
        print("\n\nYear-over-Year Retention Rate:")
        print(yoy_retention)
        
        self.analysis_results['cohort_retention'] = cohort_retention
        self.analysis_results['yoy_retention'] = yoy_retention
        
        return cohort_retention, yoy_retention
    
    def _calculate_yoy_retention(self):
        """Calculate year-over-year retention rate"""
        yearly_donors = {}
        
        for year in sorted(self.df['year'].unique()):
            donors_this_year = set(self.df[self.df['year'] == year]['donor_id'].unique())
            yearly_donors[year] = donors_this_year
        
        yoy_retention = {}
        for year in sorted(yearly_donors.keys())[:-1]:
            retained = len(yearly_donors[year] & yearly_donors[year + 1])
            total_prev = len(yearly_donors[year])
            if total_prev > 0:
                yoy_retention[year] = (retained / total_prev) * 100
        
        return pd.DataFrame(
            list(yoy_retention.items()),
            columns=['year', 'retention_rate_percent']
        )
    
    def segment_donors(self):
        """
        Segment donors into categories:
        - Active: donated in past 6 months
        - Inactive: haven't donated in 6-12 months
        - Lapsed: haven't donated in 12+ months
        - At-risk: only 1 donation total
        """
        print("\n" + "=" * 80)
        print("DONOR SEGMENTATION ANALYSIS")
        print("=" * 80)
        
        current_date = self.df['donation_date'].max()
        
        # Add last donation date to each donor
        last_donations = self.df.groupby('donor_id')['donation_date'].max()
        self.df['last_donation'] = self.df['donor_id'].map(last_donations)
        self.df['days_since_last'] = (current_date - self.df['last_donation']).dt.days
        
        # Create segments (use unique donors)
        donor_segments = self.df.groupby('donor_id').agg({
            'donation_date': ['count', 'max'],
            'blood_type': 'first',
            'center_id': 'first'
        }).reset_index()
        
        donor_segments.columns = ['donor_id', 'total_donations', 'last_donation', 
                                 'blood_type', 'center_id']
        donor_segments['days_since_last'] = (current_date - donor_segments['last_donation']).dt.days
        
        # Assign segments
        def assign_segment(row):
            if row['days_since_last'] <= 180:
                return 'Active'
            elif row['days_since_last'] <= 365:
                return 'Inactive'
            elif row['days_since_last'] > 365:
                return 'Lapsed'
            return 'Unknown'
        
        donor_segments['segment'] = donor_segments.apply(assign_segment, axis=1)
        
        # Add risk classification
        def assign_risk(row):
            if row['total_donations'] == 1:
                return 'At-Risk (New)'
            elif row['total_donations'] <= 3 and row['days_since_last'] > 180:
                return 'At-Risk (Low Activity)'
            elif row['days_since_last'] > 365:
                return 'At-Risk (Lapsed)'
            else:
                return 'Stable'
        
        donor_segments['risk_profile'] = donor_segments.apply(assign_risk, axis=1)
        
        print("\nDonor Segment Distribution:")
        print(donor_segments['segment'].value_counts())
        print("\nDonor Risk Profile Distribution:")
        print(donor_segments['risk_profile'].value_counts())
        
        # Segment statistics
        print("\n\nSegment Statistics:")
        segment_stats = donor_segments.groupby('segment').agg({
            'donor_id': 'count',
            'total_donations': ['mean', 'median'],
            'days_since_last': ['mean', 'median']
        }).round(2)
        print(segment_stats)
        
        self.analysis_results['donor_segments'] = donor_segments
        
        return donor_segments
    
    def identify_dropoff_patterns(self):
        """
        Identify where donors drop off in the donation journey
        - After 1st donation
        - After 2nd donation
        - After specific time periods
        """
        print("\n" + "=" * 80)
        print("DONOR DROPOFF PATTERN ANALYSIS")
        print("=" * 80)
        
        donor_stats = self.analysis_results['donor_stats']
        
        # Dropoff by donation count
        dropoff_rates = {}
        for i in range(1, 10):
            total_at_level = (donor_stats['total_donations'] >= i).sum()
            if total_at_level > 0:
                advance_rate = ((donor_stats['total_donations'] > i).sum() / total_at_level) * 100
                dropoff_rates[f'{i}_to_{i+1}'] = {
                    'donors_at_level': total_at_level,
                    'advance_rate_percent': advance_rate,
                    'dropoff_rate_percent': 100 - advance_rate
                }
        
        dropoff_df = pd.DataFrame(dropoff_rates).T
        print("\nDonation Progression & Dropoff Rates:")
        print(dropoff_df)
        
        # Time to second donation (critical retention metric)
        two_plus = donor_stats[donor_stats['total_donations'] >= 2].copy()
        print(f"\n\nTime to Second Donation (N={len(two_plus)}):")
        print(f"  Mean: {two_plus['donation_span_days'].mean():.0f} days")
        print(f"  Median: {two_plus['donation_span_days'].median():.0f} days")
        print(f"  Std Dev: {two_plus['donation_span_days'].std():.0f} days")
        
        self.analysis_results['dropoff_analysis'] = dropoff_df
        
        return dropoff_df
    
    def generate_recommendations(self):
        """
        Generate practical recommendations for improving retention
        Based on analysis findings
        """
        print("\n" + "=" * 80)
        print("STRATEGIC RECOMMENDATIONS FOR IMPROVING DONOR RETENTION")
        print("=" * 80)
        
        retention_rate = self.analysis_results.get('retention_rate', 0)
        donor_segments = self.analysis_results.get('donor_segments')
        
        recommendations = {
            'Critical': [],
            'High Priority': [],
            'Medium Priority': [],
            'Implementation Notes': []
        }
        
        # Recommendation 1: Critical - First donation follow-up
        at_risk_new = donor_segments[donor_segments['risk_profile'] == 'At-Risk (New)']
        pct_new = (len(at_risk_new) / len(donor_segments)) * 100
        recommendations['Critical'].append(
            f"Implement 'Second Donation Incentive' Program\n"
            f"  - {pct_new:.1f}% of donors are first-timers at risk of dropout\n"
            f"  - Establish targeted outreach within 30 days of first donation\n"
            f"  - Offer small incentives (e.g., health screening, merchandise)\n"
            f"  - Set goal: Convert 50% of first-timers to repeat donors"
        )
        
        # Recommendation 2: High Priority - Reactivation campaigns
        lapsed = donor_segments[donor_segments['segment'] == 'Lapsed']
        pct_lapsed = (len(lapsed) / len(donor_segments)) * 100
        recommendations['High Priority'].append(
            f"Reactivation Campaign for Lapsed Donors\n"
            f"  - {pct_lapsed:.1f}% of donor base is lapsed (>12 months inactive)\n"
            f"  - Segment lapsed donors by time: 12-24mo vs 24+ months\n"
            f"  - Personalized re-engagement messaging (SMS, email)\n"
            f"  - Address barriers: health concerns, time constraints, low frequency info"
        )
        
        # Recommendation 3: Inactive retention
        inactive = donor_segments[donor_segments['segment'] == 'Inactive']
        pct_inactive = (len(inactive) / len(donor_segments)) * 100
        recommendations['High Priority'].append(
            f"Prevent Inactive Donors from Becoming Lapsed\n"
            f"  - {pct_inactive:.1f}% are in inactive phase (6-12mo)\n"
            f"  - Gentle reminder campaigns at 8-month mark\n"
            f"  - Make scheduling easy: online booking, reminders\n"
            f"  - Mobile app: blood drive notifications, impact tracking"
        )
        
        # Recommendation 4: Retention programs
        recommendations['Medium Priority'].append(
            "Develop Tiered Loyalty Recognition Program\n"
            f"  - Current repeat donor rate: {retention_rate:.1f}%\n"
            f"  - Recognition milestones: 5, 10, 25, 50+ donations\n"
            f"  - Benefits: certificates, exclusive events, media recognition\n"
            f"  - Gamification: donation streaks, challenge campaigns"
        )
        
        recommendations['Medium Priority'].append(
            "Streamline and Optimize Donation Experience\n"
            f"  - Reduce appointment wait times\n"
            f"  - Collect feedback post-donation (NPS surveys)\n"
            f"  - Analyze: what drives repeat donations? What causes dropout?\n"
            f"  - Center-specific strategies based on retention metrics"
        )
        
        recommendations['Implementation Notes'].append(
            "Data-Driven Initiatives:\n"
            f"  - Implement predictive churn modeling (next phase)\n"
            f"  - A/B test messaging approaches for reactivation\n"
            f"  - Track: conversion rates, cost per reactivated donor\n"
            f"  - Dashboard: real-time retention KPIs by center and region"
        )
        
        for priority, recs in recommendations.items():
            print(f"\n{priority}:")
            for i, rec in enumerate(recs, 1):
                print(f"\n  {i}. {rec}")
        
        self.analysis_results['recommendations'] = recommendations
        
        return recommendations
    
    def create_visualizations(self, output_dir='./blood_donor_visualizations'):
        """Create visualizations for presentation"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Retention rate over time
        yoy = self.analysis_results['yoy_retention']
        axes[0, 0].plot(yoy['year'], yoy['retention_rate_percent'], marker='o', linewidth=2)
        axes[0, 0].set_title('Year-over-Year Donor Retention Rate (10 Years)', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Retention Rate (%)')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Donor segments
        segments = self.analysis_results['donor_segments']['segment'].value_counts()
        axes[0, 1].bar(segments.index, segments.values, color=['#2ecc71', '#f39c12', '#e74c3c'])
        axes[0, 1].set_title('Current Donor Segments', fontsize=12, fontweight='bold')
        axes[0, 1].set_ylabel('Number of Donors')
        
        # 3. Donation frequency distribution
        donor_stats = self.analysis_results['donor_stats']
        freq_dist = donor_stats['total_donations'].value_counts().sort_index().head(15)
        axes[1, 0].bar(freq_dist.index, freq_dist.values, color='#3498db')
        axes[1, 0].set_title('Donation Frequency Distribution (Top 15)', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Number of Donations')
        axes[1, 0].set_ylabel('Number of Donors')
        axes[1, 0].set_yscale('log')
        
        # 4. Risk profile
        risk = self.analysis_results['donor_segments']['risk_profile'].value_counts()
        axes[1, 1].barh(risk.index, risk.values, color=['#e74c3c', '#f39c12', '#2ecc71'])
        axes[1, 1].set_title('Donor Risk Profile Distribution', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Number of Donors')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/donor_retention_analysis.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Visualizations saved to: {output_dir}/donor_retention_analysis.png")
        
        return fig


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("BNM DATA SCIENTIST ASSESSMENT - PART 1a")
    print("BLOOD DONOR RETENTION ANALYSIS")
    print("="*80)
    
    try:
        # Initialize analysis
        analysis = BloodDonorRetentionAnalysis(
            parquet_path='https://data.kijang.net/dea/retention/data.parquet'
        )
        
        # Run all analyses
        analysis.data_exploration()
        analysis.calculate_retention_metrics()
        analysis.analyze_retention_trends()
        analysis.segment_donors()
        analysis.identify_dropoff_patterns()
        analysis.generate_recommendations()
        analysis.create_visualizations()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        
        return analysis
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    analysis = main()
