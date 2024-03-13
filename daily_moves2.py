import pandas as pd

# Define symbols and their typical spreads
symbols_spreads = {
    'EURUSD': 0.0001,
    'GBPUSD': 0.00015,
    'USDJPY': 0.02,
    # Add more symbols and spreads as needed
}

# Specify the start date for data inclusion
date_start = '2014-01-01'  # Adjust this to the desired start date
outlier_threshold = 0.001  # 1% of the highest moves will be filtered out
risk_reversal = 0.1  # Risk taken when opening an initial position
position_size_multiplier_on_covers = 2  # Coefficient to increase risk on each cover
coverModeMaxLevels = 6  # Max number of positions taken
tpAdjustmentReversal = 80
slReversalModeLevelCoef = 1.5

# Initialize an empty DataFrame to store results
results_df = pd.DataFrame(
    columns=['symbol', 'typical_spread', 'largest_move', 'date_of_largest_move', 'max_covers', 'cover_coefficient',
             'spread_filter', 'total_risk_on_last_cover'])

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
    # Retrieve the date of the largest move
    date_of_largest_move = df_filtered_no_outliers['move'].idxmax()

    # Calculate the spread filter
    move_divided = largest_move / (coverModeMaxLevels + 1)
    # spread_filter = spread / move_divided
    spread_filter = spread / move_divided * (50 + tpAdjustmentReversal / 2) / 100 * slReversalModeLevelCoef

    # Calculate the total risk for the last cover
    risks = [risk_reversal]  # Initial position risk
    total_risk = risk_reversal

    for i in range(1, coverModeMaxLevels):
        # Calculate new cover risk
        new_cover_risk = risk_reversal * (2 ** (i * position_size_multiplier_on_covers))
        risks.append(new_cover_risk)

        # Increment total risk by new cover risk
        total_risk += new_cover_risk

        # Increment risk for all previous positions linearly
        total_risk += sum([risk for idx, risk in enumerate(risks[:-1])])

    new_row = pd.DataFrame({
        'symbol': [symbol],
        'typical_spread': [spread],
        'largest_move': [largest_move],
        'date_of_largest_move': [date_of_largest_move],
        'max_covers': [coverModeMaxLevels],
        'cover_coefficient': [position_size_multiplier_on_covers],
        'spread_filter': [spread_filter],
        'total_risk_on_last_cover': [total_risk]
    })
    results_df = pd.concat([results_df, new_row], ignore_index=True)

# Save results to CSV
results_df.to_csv("symbols_spreads_and_moves.csv", index=False)

# Print the entire DataFrame
print("\nComplete results:")
print(results_df.to_string(index=False))
