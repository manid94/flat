import pytz
from datetime import date, datetime
import time


ist = pytz.timezone('Asia/Kolkata')
ist_datatime = datetime.now(ist)

def round_to_nearest_0_05(value):
    return round(value * 20) / 20


# Function to place sell orders for both legs
def place_sell_order(api, SYMBOLDICT,LEG_TOKEN, option_type, lots):
    # print('SYMBOLDICT[LEG_TOKEN[option_type]]')
    # print(LEG_TOKEN[option_type])

    # tsym = SYMBOLDICT[LEG_TOKEN[option_type]]['ts']
    tsym = LEG_TOKEN[option_type+'_tsym']
    order_responce = api.place_order(buy_or_sell='S', product_type='I',
                        exchange='NFO', tradingsymbol=tsym, 
                        quantity=lots, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
    

    order_id = order_responce['norenordno']
    return order_id


def place_buy_order(api, SYMBOLDICT,LEG_TOKEN, option_type, lots):
    # tsym = SYMBOLDICT[LEG_TOKEN[option_type]]['ts']
    tsym = LEG_TOKEN[option_type+'_tsym']
    
    order_responce = api.place_order(buy_or_sell='B', product_type='I',
                        exchange='NFO', tradingsymbol=tsym, 
                        quantity=lots, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='my_order_002')
    
    order_id = order_responce['norenordno']
    return order_id


def place_limit_order(api, SYMBOLDICT,LEG_TOKEN, option_type, type, lots, limit_price):
    # tsym = SYMBOLDICT[LEG_TOKEN[option_type]]['ts']
    tsym = LEG_TOKEN[option_type+'_tsym']
    order_responce = api.place_order(buy_or_sell=type, product_type='I',
                        exchange='NFO', tradingsymbol=tsym, 
                        quantity=lots, discloseqty=0,price_type='LMT', price=limit_price, trigger_price=None,
                        retention='DAY', remarks='my_order_002')

    order_id = order_responce['norenordno']
    return order_id

def place_market_order(api, SYMBOLDICT,LEG_TOKEN, option_type, type, lots):
    # tsym = SYMBOLDICT[LEG_TOKEN[option_type]]['ts']
    tsym = LEG_TOKEN[option_type+'_tsym']
    order_responce = api.place_order(buy_or_sell=type, product_type='I',
                        exchange='NFO', tradingsymbol=tsym, 
                        quantity=lots, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='my_order_002')

    order_id = order_responce['norenordno']
    return order_id




# Function to check if the order status is complete
def is_order_complete(order_id, ORDER_STATUS):
    # Check if the order exists in the ORDER_STATUS dictionary
    if order_id in ORDER_STATUS:
        return ORDER_STATUS[order_id].get('status').lower() == 'complete'
    return False



