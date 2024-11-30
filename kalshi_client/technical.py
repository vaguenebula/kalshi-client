import pandas as pd


"""
These implementations may be very wrong, as they 
were generated with ChatGPT.
Use with caution!
"""


def calculate_rsi(candlesticks, period=14):
    """
    Calculate the Relative Strength Index (RSI) for a given price series.
    
    :param candlesticks: List of candlestick data
    :param period: Look-back period for RSI calculation (default is 14)
    :return: Latest RSI value
    """
    # Convert prices to a Pandas Series
    prices = pd.Series([i['price']['close'] for i in candlesticks])
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    # Calculate the average gains and losses
    avg_gains = gains.rolling(window=period, min_periods=1).mean()
    avg_losses = losses.rolling(window=period, min_periods=1).mean()
    
    # Calculate the Relative Strength (RS)
    rs = avg_gains / avg_losses
    
    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))
    return rsi.iat[-1]

def calculate_sma(candlesticks, period=14):
    """
    Calculate the Simple Moving Average (SMA) for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for SMA calculation (default is 14)
    :return: Latest SMA value
    """
    prices = pd.Series([i['price']['close'] for i in candlesticks])
    sma = prices.rolling(window=period).mean()
    return sma.iat[-1]

def calculate_ema(candlesticks, period=14):
    """
    Calculate the Exponential Moving Average (EMA) for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for EMA calculation (default is 14)
    :return: Latest EMA value
    """
    prices = pd.Series([i['price']['close'] for i in candlesticks])
    ema = prices.ewm(span=period, adjust=False).mean()
    return ema.iat[-1]

def calculate_macd(candlesticks, slow_period=26, fast_period=12, signal_period=9):
    """
    Calculate the Moving Average Convergence Divergence (MACD) for a given price series.

    :param candlesticks: List of candlestick data
    :param slow_period: Period for the slow EMA (default is 26)
    :param fast_period: Period for the fast EMA (default is 12)
    :param signal_period: Period for the signal line EMA (default is 9)
    :return: Latest MACD value and signal line value
    """
    prices = pd.Series([i['price']['close'] for i in candlesticks])
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line.iat[-1], signal_line.iat[-1]

def calculate_bollinger_bands(candlesticks, period=20, num_std_dev=2):
    """
    Calculate Bollinger Bands for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for Bollinger Bands calculation (default is 20)
    :param num_std_dev: Number of standard deviations for the bands (default is 2)
    :return: Latest middle band (SMA), upper band, and lower band values
    """
    prices = pd.Series([i['price']['close'] for i in candlesticks])
    sma = prices.rolling(window=period).mean()
    std_dev = prices.rolling(window=period).std()
    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)
    return sma.iat[-1], upper_band.iat[-1], lower_band.iat[-1]

def calculate_stochastic_oscillator(candlesticks, period=14):
    """
    Calculate the Stochastic Oscillator for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for Stochastic Oscillator calculation (default is 14)
    :return: Latest %K value
    """
    close_prices = pd.Series([i['price']['close'] for i in candlesticks])
    low_prices = pd.Series([i['price']['low'] for i in candlesticks])
    high_prices = pd.Series([i['price']['high'] for i in candlesticks])
    lowest_low = low_prices.rolling(window=period).min()
    highest_high = high_prices.rolling(window=period).max()
    percent_k = 100 * ((close_prices - lowest_low) / (highest_high - lowest_low))
    return percent_k.iat[-1]

def calculate_atr(candlesticks, period=14):
    """
    Calculate the Average True Range (ATR) for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for ATR calculation (default is 14)
    :return: Latest ATR value
    """
    high_prices = pd.Series([i['price']['high'] for i in candlesticks])
    low_prices = pd.Series([i['price']['low'] for i in candlesticks])
    close_prices = pd.Series([i['price']['close'] for i in candlesticks])

    true_ranges = []
    for i in range(1, len(candlesticks)):
        high = high_prices.iat[i]
        low = low_prices.iat[i]
        prev_close = close_prices.iat[i - 1]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)
    atr_series = pd.Series(true_ranges)
    atr = atr_series.rolling(window=period).mean()
    return atr.iat[-1]

def calculate_adx(candlesticks, period=14):
    """
    Calculate the Average Directional Index (ADX) for a given price series.

    :param candlesticks: List of candlestick data
    :param period: Look-back period for ADX calculation (default is 14)
    :return: Latest ADX value
    """
    high_prices = pd.Series([i['price']['high'] for i in candlesticks])
    low_prices = pd.Series([i['price']['low'] for i in candlesticks])
    close_prices = pd.Series([i['price']['close'] for i in candlesticks])

    plus_dm = high_prices.diff()
    minus_dm = low_prices.diff().abs()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr_list = []
    for i in range(1, len(candlesticks)):
        high = high_prices.iat[i]
        low = low_prices.iat[i]
        prev_close = close_prices.iat[i - 1]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_list.append(tr)
    tr_series = pd.Series(tr_list)

    atr = tr_series.rolling(window=period).mean()

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()
    return adx.iat[-1]

def calculate_obv(candlesticks):
    """
    Calculate the On-Balance Volume (OBV) for a given price series.

    :param candlesticks: List of candlestick data
    :return: Latest OBV value
    """
    close_prices = pd.Series([i['price']['close'] for i in candlesticks])
    volumes = pd.Series([i['volume'] for i in candlesticks])
    obv = [0]
    for i in range(1, len(close_prices)):
        if close_prices.iat[i] > close_prices.iat[i - 1]:
            obv.append(obv[-1] + volumes.iat[i])
        elif close_prices.iat[i] < close_prices.iat[i - 1]:
            obv.append(obv[-1] - volumes.iat[i])
        else:
            obv.append(obv[-1])
    return obv[-1]
