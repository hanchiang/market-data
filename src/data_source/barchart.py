from market_data_library import TradFiAPI

tradfi_api = None

async def get_tradfi_api():
    init_tradfi_api()
    return tradfi_api

def init_tradfi_api():
    global tradfi_api
    if tradfi_api is None:
        tradfi_api = TradFiAPI()  # Initialize outside an active event loop
    return tradfi_api