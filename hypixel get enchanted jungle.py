import aiohttp
import asyncio

API_KEY = "{INSERT_API_KEY}"

async def fetch_bazaar_data(session):
    bazaar_url = f"https://api.hypixel.net/skyblock/bazaar?key={API_KEY}"
    async with session.get(bazaar_url) as response:
        return await response.json()

async def fetch_auction_data(session, page):
    auction_url = f"https://api.hypixel.net/skyblock/auctions?page={page}&key={API_KEY}"
    async with session.get(auction_url) as response:
        return await response.json()

async def get_jungle_log_prices(session):
    global fetching
    data = await fetch_bazaar_data(session)
    
    # Fetch Enchanted Jungle Log price
    enchanted_log = data.get("products", {}).get("ENCHANTED_JUNGLE_LOG", {})
    if enchanted_log:
        enchanted_sell_price = enchanted_log["sell_summary"][0]["pricePerUnit"]
        enchanted_buy_price = enchanted_log["buy_summary"][0]["pricePerUnit"]
        print(f"\nEnchanted Jungle Log - Sell Price: {enchanted_sell_price} coins, Buy Price: {enchanted_buy_price} coins")
    else:
        print("\nEnchanted Jungle Log not found in Bazaar.")
        enchanted_sell_price, enchanted_buy_price = float('inf'), float('inf')
    
    # Fetch Jungle Log price using LOG:3
    jungle_log = data.get("products", {}).get("LOG:3", {})
    if jungle_log:
        jungle_sell_price = jungle_log["sell_summary"][0]["pricePerUnit"]
        jungle_buy_price = jungle_log["buy_summary"][0]["pricePerUnit"]
        print(f"Jungle Log - Sell Price: {jungle_sell_price} coins, Buy Price: {jungle_buy_price} coins")
    else:
        print("Jungle Log not found in Bazaar.")
        jungle_sell_price, jungle_buy_price = float('inf'), float('inf')

    # Compare 160 Jungle Logs to 1 Enchanted Jungle Log
    total_log_cost = jungle_sell_price * 160
    if total_log_cost < enchanted_sell_price:
        print(f"\n⚠️  Warning: Buying 160 Jungle Logs ({total_log_cost} coins) is cheaper than 1 Enchanted Jungle Log ({enchanted_sell_price} coins)! ⚠️")
    elif total_log_cost < enchanted_buy_price:
        print(f"\n⚠️ Warning: Selling 160 Jungle Logs ({total_log_cost} coins) is cheaper than 1 Enchanted Jungle Log ({enchanted_buy_price} coins)! ⚠️")
    else:
        print(f"\n160 Jungle Logs ({total_log_cost} coins) is more expensive than 1 Enchanted Jungle Log.")

async def get_cheapest_jungle_axe_bin(session):
    global fetching
    page = 0
    cheapest_auction = None
    
    while True:
        data = await fetch_auction_data(session, page)
        for auction in data["auctions"]:
            if auction["item_name"] == "Jungle Axe" and auction.get("bin", False):
                if cheapest_auction is None or auction["starting_bid"] < cheapest_auction["starting_bid"]:
                    cheapest_auction = auction

        if page >= data["totalPages"] - 1:
            break
        page += 1

    if cheapest_auction:
        print(f"\nCheapest Jungle Axe BIN auction:")
        print(f"  BIN Price: {cheapest_auction['starting_bid']} coins")
    else:
        print("\nNo Jungle Axe BIN auctions found.")

    # Once auction data is fetched, set fetching to False
    fetching = False

async def show_loading_message():
    while fetching:
        print("Fetching prices...", end="\r")
        await asyncio.sleep(1)
    print("Fetching complete.               ")

async def main():
    global fetching
    fetching = True  # Start with fetching = True
    
    async with aiohttp.ClientSession() as session:
        # Start the loading message and data fetching tasks concurrently
        tasks = [
            asyncio.create_task(show_loading_message()),
            asyncio.create_task(get_jungle_log_prices(session)),
            asyncio.create_task(get_cheapest_jungle_axe_bin(session))
        ]
        
        # Wait for all tasks to finish
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
