from market_data_library import TradFiAPI

async def get_tradfi_api():
    return TradFiAPI()  # Initialize inside an active event loop