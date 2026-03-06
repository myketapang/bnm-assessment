"""
BNM Data Scientist Assessment - Part 1b: Outlier Detection

Task: Design and implement outlier detection to identify significant spikes or drops
       in blood donation activity at multiple levels of disaggregation:
       - National level
       - By hospital
       - By hospital and blood group

Datasets:
- https://data.kijang.net/dea/donations/historical.parquet
- Daily updates: https://data.kijang.net/dea/donations/YYYY-MM-DD.parquet
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class OutlierDetectionFramework:
    """Multi-level outlier detection for donation activity"""
    
    def __init__(self, historical_path, current_date=None):
        """
        Initialize with historical donation data
        Args:
            historical_path: Path to historical.parquet
            current_date: For testing; defaults to today
        """
        self.df_historical = pd.read_parquet(historical_path)
        self.current_date = current_date or datetime.now().date()
        self.outliers = {}
        self.methods = {}
        
    def prepare_data(self):
        """Prepare and validate data"""
        print("=" * 80)
        print("DATA PREPARATION")
        print("=" * 80)
        
        # Convert date columns
        self.df_historical['donation_date'] = pd.to_datetime(self.df_historical['donation_date'])
        
        # Validate
        print(f"Historical records: {len(self.df_historical):,}")
        print(f"Date range: {self.df_historical['donation_date'].min()} to {self.df_historical['donation_date'].max()}")
        print(f"Hospitals: {self.df_historical['hospital_id'].nunique()}")
        print(f"Blood groups: {self.df_historical['blood_type'].nunique()}")
        print(f"Blood types: {self.df_historical['blood_type'].unique()}")
        
        return self.df_historical
    
    def method_zscore(self, series, threshold=3.0, window=30):
        """
        Z-Score based outlier detection
        - Calculate rolling mean and std
        - Flag values beyond threshold std devs
        
        Args:
            series: Time series data
            threshold: Number of standard deviations (default 3.0)
            window: Rolling window size in days
        """
        series_clean = series.fillna(series.mean())
        
        rolling_mean = series_clean.rolling(window=window, center=True).mean()
        rolling_std = series_clean.rolling(window=window, center=True).std()
        
        z_scores = np.abs((series_clean - rolling_mean) / (rolling_std + 1e-8))
        
        is_outlier = z_scores > threshold
        
        return is_outlier, z_scores, rolling_mean, rolling_std
    
    def method_iqr(self, series, window=30, iqr_multiplier=1.5):
        """
        Interquartile Range (IQR) based detection
        - Uses rolling IQR to identify extreme values
        
        Args:
            series: Time series data
            window: Rolling window size
            iqr_multiplier: Multiplier for IQR bounds (default 1.5x)
        """
        series_clean = series.fillna(series.mean())
        
        rolling_q1 = series_clean.rolling(window=window, center=True).quantile(0.25)
        rolling_q3 = series_clean.rolling(window=window, center=True).quantile(0.75)
        rolling_iqr = rolling_q3 - rolling_q1
        
        lower_bound = rolling_q1 - (iqr_multiplier * rolling_iqr)
        upper_bound = rolling_q3 + (iqr_multiplier * rolling_iqr)
        
        is_outlier = (series_clean < lower_bound) | (series_clean > upper_bound)
        
        return is_outlier, lower_bound, upper_bound
    
    def method_mad(self, series, threshold=2.5, window=30):
        """
        Median Absolute Deviation (MAD) based detection
        - More robust to extreme outliers than Z-score
        
        Args:
            series: Time series data
            threshold: MAD threshold (typically 2.5 for 99%)
            window: Rolling window size
        """
        series_clean = series.fillna(series.mean())
        
        rolling_median = series_clean.rolling(window=window, center=True).median()
        rolling_mad = (series_clean - rolling_median).abs().rolling(window=window, center=True).median()
        
        # Modified Z-score using MAD
        with np.errstate(divide='ignore', invalid='ignore'):
            modified_z = 0.6745 * (series_clean - rolling_median) / (rolling_mad + 1e-8)
        
        is_outlier = np.abs(modified_z) > threshold
        
        return is_outlier, rolling_median, rolling_mad
    
    def detect_outliers_national(self):
        """
        National-level outlier detection
        Aggregate all donations by date, detect anomalies
        """
        print("\n" + "=" * 80)
        print("LEVEL 1: NATIONAL-LEVEL OUTLIER DETECTION")
        print("=" * 80)
        
        # Aggregate by date
        daily_donations = self.df_historical.groupby('donation_date').agg({
            'donation_id': 'count',  # Total donations
            'blood_type': 'nunique',  # Unique blood types
            'hospital_id': 'nunique'  # Participating hospitals
        }).reset_index()
        daily_donations.columns = ['date', 'total_donations', 'blood_types', 'hospitals']
        daily_donations = daily_donations.sort_values('date')
        
        # Apply detection methods
        results = {
            'date': daily_donations['date'].values,
            'total_donations': daily_donations['total_donations'].values,
            'zscore_outlier': False,
            'iqr_outlier': False,
            'mad_outlier': False,
            'anomaly_score': 0.0
        }
        
        # Z-Score
        results['zscore_outlier'], z_scores, mean, std = self.method_zscore(
            daily_donations['total_donations'].values
        )
        results['z_scores'] = z_scores
        
        # IQR
        results['iqr_outlier'], lower, upper = self.method_iqr(
            daily_donations['total_donations'].values
        )
        results['iqr_lower'] = lower
        results['iqr_upper'] = upper
        
        # MAD
        results['mad_outlier'], median, mad = self.method_mad(
            daily_donations['total_donations'].values
        )
        results['mad_median'] = median
        
        # Combine methods: flag if 2+ methods agree
        results['is_outlier'] = (
            (results['zscore_outlier'].astype(int) + 
             results['iqr_outlier'].astype(int) + 
             results['mad_outlier'].astype(int)) >= 2
        )
        
        results['anomaly_score'] = (
            results['zscore_outlier'].astype(float) * 0.4 +
            results['iqr_outlier'].astype(float) * 0.3 +
            results['mad_outlier'].astype(float) * 0.3
        )
        
        outlier_df = pd.DataFrame(results)
        detected = outlier_df[outlier_df['is_outlier']]
        
        print(f"\nAnalysis Period: {outlier_df['date'].min()} to {outlier_df['date'].max()}")
        print(f"Total Days: {len(outlier_df)}")
        print(f"Outliers Detected: {detected.shape[0]}")
        print(f"Outlier Rate: {(len(detected)/len(outlier_df)*100):.2f}%")
        
        print(f"\nDaily Donation Statistics:")
        print(f"  Mean: {daily_donations['total_donations'].mean():.0f}")
        print(f"  Median: {daily_donations['total_donations'].median():.0f}")
        print(f"  Std Dev: {daily_donations['total_donations'].std():.0f}")
        print(f"  Min: {daily_donations['total_donations'].min():.0f}")
        print(f"  Max: {daily_donations['total_donations'].max():.0f}")
        
        if len(detected) > 0:
            print(f"\n{'Date':<12} {'Donations':<12} {'Anomaly Score':<15} {'Classification'}")
            print("-" * 55)
            for idx, row in detected.iterrows():
                donations = int(row['total_donations'])
                anomaly = row['anomaly_score']
                
                if donations > daily_donations['total_donations'].mean() * 1.5:
                    classification = "SPIKE (High)"
                elif donations < daily_donations['total_donations'].mean() * 0.5:
                    classification = "DROP (Low)"
                else:
                    classification = "Moderate Anomaly"
                
                print(f"{str(row['date'].date()):<12} {donations:<12} {anomaly:<15.3f} {classification}")
        
        self.outliers['national'] = outlier_df
        self.methods['national'] = 'Z-Score + IQR + MAD (ensemble)'
        
        return outlier_df
    
    def detect_outliers_by_hospital(self):
        """
        Hospital-level outlier detection
        For each hospital, identify anomalous donation days
        """
        print("\n" + "=" * 80)
        print("LEVEL 2: HOSPITAL-LEVEL OUTLIER DETECTION")
        print("=" * 80)
        
        hospitals = self.df_historical['hospital_id'].unique()
        print(f"Analyzing {len(hospitals)} hospitals...\n")
        
        hospital_outliers = []
        hospital_stats = []
        
        for hospital_id in hospitals:
            hospital_data = self.df_historical[
                self.df_historical['hospital_id'] == hospital_id
            ]
            
            # Daily aggregation
            daily_hospital = hospital_data.groupby('donation_date').agg({
                'donation_id': 'count'
            }).reset_index()
            daily_hospital.columns = ['date', 'donations']
            daily_hospital = daily_hospital.sort_values('date')
            
            # Need minimum data points
            if len(daily_hospital) < 20:
                continue
            
            # Detect outliers using Z-score (primary method)
            is_outlier, z_scores, mean, std = self.method_zscore(
                daily_hospital['donations'].values,
                threshold=2.5
            )
            
            # Identify outlier dates
            outlier_dates = daily_hospital[is_outlier]
            
            if len(outlier_dates) > 0:
                for idx, row in outlier_dates.iterrows():
                    hospital_outliers.append({
                        'hospital_id': hospital_id,
                        'date': row['date'],
                        'donations': int(row['donations']),
                        'mean_donations': mean[idx] if not np.isnan(mean[idx]) else daily_hospital['donations'].mean(),
                        'z_score': z_scores[idx],
                        'anomaly_type': 'SPIKE' if row['donations'] > daily_hospital['donations'].mean() else 'DROP'
                    })
            
            # Hospital statistics
            hospital_stats.append({
                'hospital_id': hospital_id,
                'total_records': len(hospital_data),
                'avg_daily_donations': daily_hospital['donations'].mean(),
                'outlier_days': len(outlier_dates),
                'outlier_percentage': (len(outlier_dates) / len(daily_hospital) * 100)
            })
        
        hospital_outlier_df = pd.DataFrame(hospital_outliers)
        hospital_stats_df = pd.DataFrame(hospital_stats).sort_values('outlier_percentage', ascending=False)
        
        print(f"Hospitals with Detected Outliers: {len(hospital_outlier_df['hospital_id'].unique())}")
        print(f"\nTop 10 Hospitals by Outlier Frequency:")
        print(hospital_stats_df.head(10).to_string(index=False))
        
        if len(hospital_outlier_df) > 0:
            print(f"\nSample Outliers by Hospital:")
            print(hospital_outlier_df.groupby('hospital_id').head(2).to_string(index=False))
        
        self.outliers['hospital'] = hospital_outlier_df
        self.methods['hospital'] = 'Z-Score (threshold=2.5)'
        
        return hospital_outlier_df, hospital_stats_df
    
    def detect_outliers_by_hospital_bloodtype(self):
        """
        Hospital + Blood Type level outlier detection
        Most granular: detect anomalies for specific blood groups in specific hospitals
        """
        print("\n" + "=" * 80)
        print("LEVEL 3: HOSPITAL + BLOOD GROUP-LEVEL OUTLIER DETECTION")
        print("=" * 80)
        
        blood_types = self.df_historical['blood_type'].unique()
        hospitals = self.df_historical['hospital_id'].unique()
        
        print(f"Analyzing {len(hospitals)} hospitals × {len(blood_types)} blood types = {len(hospitals)*len(blood_types)} combinations...\n")
        
        ht_outliers = []
        
        for hospital_id in hospitals:
            for blood_type in blood_types:
                subset = self.df_historical[
                    (self.df_historical['hospital_id'] == hospital_id) &
                    (self.df_historical['blood_type'] == blood_type)
                ]
                
                if len(subset) < 10:  # Skip combinations with insufficient data
                    continue
                
                # Daily aggregation
                daily_ht = subset.groupby('donation_date').agg({
                    'donation_id': 'count'
                }).reset_index()
                daily_ht.columns = ['date', 'donations']
                daily_ht = daily_ht.sort_values('date')
                
                if len(daily_ht) < 15:
                    continue
                
                # Detect outliers using IQR (robust for small samples)
                is_outlier, lower, upper = self.method_iqr(
                    daily_ht['donations'].values,
                    window=14
                )
                
                outlier_dates = daily_ht[is_outlier]
                
                if len(outlier_dates) > 0:
                    for idx, row in outlier_dates.iterrows():
                        ht_outliers.append({
                            'hospital_id': hospital_id,
                            'blood_type': blood_type,
                            'date': row['date'],
                            'donations': int(row['donations']),
                            'expected_upper': upper[idx] if not np.isnan(upper[idx]) else daily_ht['donations'].quantile(0.75),
                            'expected_lower': lower[idx] if not np.isnan(lower[idx]) else daily_ht['donations'].quantile(0.25),
                            'anomaly_type': 'SPIKE' if row['donations'] > daily_ht['donations'].mean() else 'DROP'
                        })
        
        ht_outlier_df = pd.DataFrame(ht_outliers)
        
        print(f"Hospital-Blood Type Combinations with Outliers: {len(ht_outlier_df)}")
        print(f"Unique Hospital-Blood Type Pairs: {ht_outlier_df.groupby(['hospital_id', 'blood_type']).ngroups}")
        
        if len(ht_outlier_df) > 0:
            print(f"\nSample Outliers by Hospital-Blood Type:")
            sample = ht_outlier_df.drop_duplicates(['hospital_id', 'blood_type']).head(10)
            print(sample[['hospital_id', 'blood_type', 'date', 'donations', 'anomaly_type']].to_string(index=False))
        
        self.outliers['hospital_bloodtype'] = ht_outlier_df
        self.methods['hospital_bloodtype'] = 'IQR (window=14)'
        
        return ht_outlier_df
    
    def analyze_root_causes(self):
        """
        Analyze likely causes of detected anomalies
        """
        print("\n" + "=" * 80)
        print("ROOT CAUSE ANALYSIS OF ANOMALIES")
        print("=" * 80)
        
        national_outliers = self.outliers.get('national', pd.DataFrame())
        
        if len(national_outliers) == 0:
            print("No outliers detected at national level")
            return
        
        anomaly_outliers = national_outliers[national_outliers['is_outlier']]
        
        if len(anomaly_outliers) == 0:
            print("No confirmed outliers after ensemble method")
            return
        
        print(f"\nAnalyzing {len(anomaly_outliers)} anomalies...\n")
        
        # Temporal patterns
        anomaly_outliers['day_of_week'] = anomaly_outliers['date'].dt.day_name()
        anomaly_outliers['month'] = anomaly_outliers['date'].dt.month
        anomaly_outliers['year'] = anomaly_outliers['date'].dt.year
        
        print("Anomaly Distribution by Day of Week:")
        print(anomaly_outliers['day_of_week'].value_counts())
        
        print("\n\nAnomaly Distribution by Month:")
        print(anomaly_outliers['month'].value_counts().sort_index())
        
        # Classify anomalies
        mean_donations = anomaly_outliers['total_donations'].mean()
        
        spikes = anomaly_outliers[anomaly_outliers['total_donations'] > mean_donations * 1.2]
        drops = anomaly_outliers[anomaly_outliers['total_donations'] < mean_donations * 0.8]
        
        print(f"\n\nAnomaly Classification:")
        print(f"  Spikes (High): {len(spikes)}")
        print(f"  Drops (Low): {len(drops)}")
        print(f"  Moderate: {len(anomaly_outliers) - len(spikes) - len(drops)}")
        
        # Likely causes
        print("\n\nLikely Root Causes:")
        
        causes = {
            'SPIKE': [
                "National donation campaigns or awareness drives",
                "Celebrity/influencer engagement campaigns",
                "Company/institutional bulk donations",
                "Holiday seasons (year-end, Chinese New Year)",
                "Emergency appeals (major incident or blood shortage)",
                "Major sports events (participants blood testing)"
            ],
            'DROP': [
                "Scheduled maintenance or facility closures",
                "Staff holidays or reduced staffing",
                "Major holidays (Hari Raya, Deepavali)",
                "Public holidays affecting transportation",
                "Pandemic/health crisis lockdowns",
                "Severe weather or natural disasters",
                "System outages or data collection issues"
            ]
        }
        
        print("\nFor SPIKE anomalies, likely causes:")
        for cause in causes['SPIKE']:
            print(f"  • {cause}")
        
        print("\nFor DROP anomalies, likely causes:")
        for cause in causes['DROP']:
            print(f"  • {cause}")
        
        self.analysis_results = {
            'spikes': spikes,
            'drops': drops,
            'total_anomalies': len(anomaly_outliers),
            'causes': causes
        }
        
        return anomaly_outliers
    
    def generate_report(self):
        """Generate comprehensive outlier detection report"""
        print("\n" + "=" * 80)
        print("OUTLIER DETECTION SUMMARY REPORT")
        print("=" * 80)
        
        print("\n📊 DETECTION METHODS USED:")
        for level, method in self.methods.items():
            print(f"  • Level '{level}': {method}")
        
        print("\n📈 ANOMALIES DETECTED:")
        print(f"  • National Level: {len(self.outliers.get('national', []))} anomalies")
        print(f"  • Hospital Level: {len(self.outliers.get('hospital', []))} anomalies")
        print(f"  • Hospital × Blood Type: {len(self.outliers.get('hospital_bloodtype', []))} anomalies")
        
        print("\n💡 KEY INSIGHTS:")
        if len(self.outliers.get('national', [])) > 0:
            national = self.outliers['national']
            confirmed = national[national['is_outlier']]
            print(f"  • {len(confirmed)} confirmed anomalies at national level (ensemble consensus)")
            print(f"  • Outlier dates require investigation for causation")
        
        print("\n✅ RECOMMENDATIONS:")
        print("  1. Investigate each flagged date with operations team")
        print("  2. Correlate anomalies with known events (campaigns, holidays)")
        print("  3. Implement real-time anomaly alerts for >2σ deviations")
        print("  4. Build predictive models for expected donation volumes")
        print("  5. Create dashboard for continuous monitoring")


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("BNM DATA SCIENTIST ASSESSMENT - PART 1b")
    print("OUTLIER DETECTION IN BLOOD DONATIONS")
    print("=" * 80)
    
    try:
        # Initialize
        detector = OutlierDetectionFramework(
            historical_path='https://data.kijang.net/dea/donations/historical.parquet'
        )
        
        # Run analysis
        detector.prepare_data()
        detector.detect_outliers_national()
        detector.detect_outliers_by_hospital()
        detector.detect_outliers_by_hospital_bloodtype()
        detector.analyze_root_causes()
        detector.generate_report()
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
        return detector
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    detector = main()
