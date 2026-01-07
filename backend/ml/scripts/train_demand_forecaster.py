"""
Script to train demand forecasting model
"""
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def generate_forecast(data_path: str = None, output_dir: str = None, forecast_days: int = 7):
    """Generate demand forecast using moving average"""
    
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models' / 'demand_forecaster'
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load or generate data
    if data_path and Path(data_path).exists():
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
    else:
        # Generate sample data
        dates = pd.date_range(start='2024-01-01', periods=90, freq='D')
        np.random.seed(42)
        base_demand = 100
        trend = np.linspace(0, 20, 90)
        seasonality = 10 * np.sin(2 * np.pi * np.arange(90) / 7)
        noise = np.random.normal(0, 5, 90)
        demand = base_demand + trend + seasonality + noise
        demand = np.maximum(demand, 0)
        
        df = pd.DataFrame({
            'date': dates,
            'demand': demand.astype(int)
        })
    
    # Calculate moving average
    window = 7
    last_avg = df['demand'].tail(window).mean()
    
    # Generate forecast
    forecast_dates = pd.date_range(
        start=df['date'].max() + timedelta(days=1), 
        periods=forecast_days, 
        freq='D'
    )
    forecast = pd.DataFrame({
        'date': forecast_dates,
        'forecast': [last_avg] * forecast_days
    })
    
    # Save
    forecast.to_csv(output_dir / 'forecast.csv', index=False)
    
    print(f"✓ Forecast generated for {forecast_days} days")
    print(f"  Average demand: {last_avg:.2f}")
    print(f"  Forecast saved to {output_dir / 'forecast.csv'}")
    
    return forecast

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate demand forecast')
    parser.add_argument('--data', type=str, help='Path to historical demand data CSV')
    parser.add_argument('--output', type=str, help='Output directory')
    parser.add_argument('--days', type=int, default=7, help='Number of days to forecast')
    
    args = parser.parse_args()
    generate_forecast(data_path=args.data, output_dir=args.output, forecast_days=args.days)

