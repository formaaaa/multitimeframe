import pandas as pd

# Step 1: Define symbols and their typical spreads
symbols_spreads = {
    'EURUSD': 0.0001,
    'GBPUSD': 0.00015,
    'USDJPY': 0.02,
    # Add more symbols and spreads as needed
}

# Specify the start date for data inclusion and the percentage of outliers to filter
date_start = '2004-01-01'
max_covers = 4
outlier_threshold = 0.001  # how many biggest moves will be filtered

# Initialize an empty DataFrame to store results
results_df = pd.DataFrame(columns=['symbol', 'typical_spread', 'largest_move', 'spread_filter'])

for symbol, spread in symbols_spreads.items():
    # Load and process data for each symbol
    file_path = f"volatility_trend-main/Input data/OHLC_data/{symbol}/{symbol}1440.csv"
    df = pd.read_csv(file_path, names=['date', 'time', 'open', 'high', 'low', 'close', 'volume'])
    df.drop(columns=['time', 'volume'], inplace=True)

    # Convert the 'date' column to datetime format explicitly stating the format
    df['date'] = pd.to_datetime(df['date'], format='%Y.%m.%d')
    df.set_index('date', inplace=True)

    df['move'] = df['high'] - df['low']

    # Filter the DataFrame based on date_start
    df_filtered = df[df.index >= pd.to_datetime(date_start)]

    # Exclude top 1% of the moves as outliers before finding the largest move
    threshold_value = df_filtered['move'].quantile(1 - outlier_threshold)
    df_filtered_no_outliers = df_filtered[df_filtered['move'] <= threshold_value]

    # Find the maximum 'move' value in the filtered data without outliers
    largest_move = df_filtered_no_outliers['move'].max()

    # Calculate the spread filter
    move_divided = largest_move / (max_covers + 1)
    spread_filter = spread / move_divided

    # Create a new row DataFrame to add to results_df
    new_row = pd.DataFrame({
        'symbol': [symbol],
        'typical_spread': [spread],
        'largest_move': [largest_move],
        'spread_filter': [spread_filter]
    })

    # Use pandas.concat instead of append
    results_df = pd.concat([results_df, new_row], ignore_index=True)

# Save results to CSV
results_df.to_csv("symbols_spreads_and_moves.csv", index=False)

# Print the entire DataFrame
print("\nComplete results:")
print(results_df.to_string(index=False))
