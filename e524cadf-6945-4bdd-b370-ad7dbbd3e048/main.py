from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, SMA
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["TICKER1", "TICKER2", "TICKER3"]  # Example micro-cap tickers
        self.lookback_period = 20  # Lookback period for calculating average volume & RSI

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        return "1day"

    def run(self, data):
        target_allocations = {}
        
        for ticker in self.tickers:
            recent_data = data["ohlcv"][-self.lookback_period:]  # Get the last lookback_period days of data
            
            # Calculate the RSI to identify momentum
            rsi_values = RSI(ticker, recent_data, self.lookback_period)
            if rsi_values is None or len(rsi_values) == 0:
                continue

            last_rsi = rsi_values[-1]
            
            # Calculate the current volume vs. the 20-day SMA volume to identify increased interest
            current_volume = recent_data[-1][ticker]["volume"]
            volume_sma = SMA(ticker, recent_data, self.lookback_period, "volume")[-1]
            
            if volume_sma == 0:  # Prevent division by zero
                continue
            
            volume_increase_factor = current_volume / volume_sma
            
            # If momentum is strong (RSI > 60) and there's a noticeable increase in volume (e.g., 20% increase)
            if last_rsi > 60 and volume_increase_factor > 1.2:
                # Allocate a higher portion of the portfolio to this stock, indicating a strong buy signal
                target_allocations[ticker] = 1.0 / len(self.tickers)
            else:
                # Otherwise, do not allocate to this stock
                target_allocations[ticker] = 0.0

        # Normalize allocations (this simple example assumes equal weighting for simplicity)
        if sum(target_allocations.values()) > 1:
            target_allocations = {ticker: val / len(target_allocations) for ticker, val in target_allocations.items()}

        return TargetAllocation(target_allocations)