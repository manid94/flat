import datetime
import time
import threading
import time
import os, sys
from urllib.parse import parse_qs, urlparse
import hashlib
import pandas as pd
from utils import ist_datatime, round_to_nearest_0_05, place_sell_order,place_buy_order,place_limit_order,place_market_order, is_order_complete
import pytz
from NorenRestApiPy.NorenApi import NorenApi



# Define the IST timezone
ist = pytz.timezone('Asia/Kolkata')


# Constants
SYMBOL = 'Nifty bank'
INITIAL_LOTS = 1  # Start with 1 lot
BUY_BACK_LOTS = 2
STRIKE_DIFFERENCE = 0
ONE_LOT_QUANTITY = 15  # Number of units per lot in Bank Nifty
TARGET_PROFIT = 5000
MAX_LOSS = 3000
MAX_LOSS_PER_LEG = 2000
SAFETY_STOP_LOSS_PERCENTAGE = 0.95
BUY_BACK_PERCENTAGE = 0.90
SELL_TARGET_PERCENTAGE = 0.02
BUY_BACK_LOSS_PERCENTAGE = 0.93
LEG_TOKEN = {}
PRICE_DATA = {
    'CE_PRICE_DATA' : {
        'INITIAL_SELL_CE' : 0,
        'INITIAL_BUY_CE' : 0,
        'BUY_BACK_BUY_CE' : 0,
        'BUY_BACK_SELL_CE' : 0,
        'RE_ENTRY_BUY_CE' : 0,
        'RE_ENTRY_SELL_CE': 0
    },
    'PE_PRICE_DATA' : {
        'INITIAL_SELL_PE' : 0,
        'INITIAL_BUY_PE' : 0,
        'BUY_BACK_BUY_PE' : 0,
        'BUY_BACK_SELL_PE' : 0,
        'RE_ENTRY_BUY_PE' : 0,
        'RE_ENTRY_SELL_PE': 0
    }
}
ORDER_STATUS = {}
ORDER_ID_DATAS = []

# flag to tell us if the websocket is open
socket_opened = False
SYMBOLDICT = {}

# Global variables
strategy_running = False
sell_price_ce = 0
sell_price_pe = 0
ce_lots = INITIAL_LOTS
pe_lots = INITIAL_LOTS




# Credentials - define these variables
password = 'Deepak@94'
userid = 'FT053455'
token = '79454ecf851e5a4daa328d39ddb92927b4c60da7372935b287a00273e2ad7a05'


class FlatTradeApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://piconnect.flattrade.in/PiConnectTP/', 
                          websocket='wss://piconnect.flattrade.in/PiConnectWSTp/')

api = FlatTradeApiPy()
api.set_session(userid=userid, password=password, usertoken=token)  # Set UID and token here







#application callbacks
def event_handler_order_update(message):
    global ORDER_STATUS
    # print('print("order event: " + str(message))')
    # order event: {
    #       't': 'om', 'norenordno': '24101600226847', 'uid': 'FT053455', 'actid': 'FT053455', 'exch': 'NFO', 'tsym': 'BANKNIFTY16OCT24P50500',
    #        'trantype': 'B', 'qty': '30', 'prc': '5.25', 'pcode': 'I', 'remarks': 'my_order_002', 'rejreason': ' ', 'status': 'COMPLETE',
    #        'reporttype': 'Fill', 'flqty': '30', 'flprc': '2.85', 'flid': '380225664', 'fltm': '16-10-2024 11:15:20', 'prctyp': 'LMT',
    #         'ret': 'DAY', 'exchordid': '1500000079566637', 'fillshares': '30', 'dscqty': '0', 'avgprc': '2.85', 'exch_tm': '16-10-2024 11:15:20'
    # }
    # print("order event: " + str(message))
    if 'norenordno' in message:
        ORDER_STATUS[message['norenordno']] = {}
        ORDER_STATUS[message['norenordno']]['status'] = message['status']
        ORDER_STATUS[message['norenordno']]['flqty'] =  message.get('flqty', 0)
        ORDER_STATUS[message['norenordno']]['qty'] =  message.get('qty', 0)

        # print('norenordno')
        # print(message['status'].lower())
        if message['status'].lower() == 'complete':
            ORDER_STATUS[message['norenordno']]['avgprc'] =  message.get('avgprc', 0)
            

    


def event_handler_quote_update(message):
    global SYMBOLDICT
    #e   Exchange
    #tk  Token
    #lp  LTP
    #pc  Percentage change
    #v   volume
    #o   Open price
    #h   High price
    #l   Low price
    #c   Close price
    #ap  Average trade price

    # print("quote event: {0}".format(time.strftime('%d-%m-%Y %H:%M:%S')) + str(message))

    key = message['tk']
    if key in SYMBOLDICT:
        symbol_info =  SYMBOLDICT[key]
        symbol_info.update(message)
        SYMBOLDICT[key] = symbol_info
    else:
        SYMBOLDICT[key] = message

    # print(SYMBOLDICT[key])

def open_callback():
    global socket_opened
    socket_opened = True
    #print('app is connected')

    #api.subscribe(['NSE|22', 'BSE|522032'])

#end of callbacks

def fetch_last_trade_price(option_type):
    temp_data = SYMBOLDICT[LEG_TOKEN[option_type]]['lp'] 
    # print('temp_data')
    # print(SYMBOLDICT)
    # print(temp_data)
    # print(LEG_TOKEN[option_type])
    # print(SYMBOLDICT[LEG_TOKEN[option_type]])
    # print(type(temp_data))
    return float(temp_data)



def open_socket():
    if socket_opened != True:
        print(socket_opened)
        api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)
    #api.start_websocket(order_update_callback=event_handler_order_update, subscribe_callback=event_handler_quote_update, socket_open_callback=open_callback)
    print(socket_opened)
    return True





# Utility function to fetch the ATM strike price
def fetch_atm_strike():
    global LEG_TOKEN, SYMBOLDICT

    print('entered fetch_atm_strike')
    socket = threading.Thread(target=open_socket, args=())
    socket.start()
    

    api.searchscrip(exchange='NSE', searchtext=SYMBOL)
    banknifty_price = api.get_quotes(exchange='NSE', token='26009')
    current_price = banknifty_price['lp']
    print(float(current_price))
    atm_strike = round(float(current_price) / 100) * 100
    print(atm_strike)
    nearest_symbol_ce = (str(atm_strike+STRIKE_DIFFERENCE)+' nifty bANK' + ' ce')
    nearest_symbol_pe = (str(atm_strike-STRIKE_DIFFERENCE)+' nifty bANK' + ' pe')
    # print(nearest_symbol_ce)
    # print(api.searchscrip(exchange='NFO', searchtext=nearest_symbol_ce))
    # print(api.searchscrip(exchange='NFO', searchtext=nearest_symbol_pe))
    option_chains_ce = api.searchscrip(exchange='NFO', searchtext=nearest_symbol_ce)
    option_chains_pe = api.searchscrip(exchange='NFO', searchtext=nearest_symbol_pe)
    pe_option = option_chains_pe['values'][0]
    ce_option = option_chains_ce['values'][0]
    subscribeDataPE = 'NFO|'+pe_option['token']
    subscribeDataCE = 'NFO|'+ce_option['token']
    LEG_TOKEN['PE'] = pe_option['token']
    LEG_TOKEN['CE'] = ce_option['token']
    LEG_TOKEN['PE_tsym'] = pe_option['tsym']
    LEG_TOKEN['CE_tsym'] = ce_option['tsym']


    socket.join()
    api.subscribe([subscribeDataPE,subscribeDataCE])
    return atm_strike  # Round to nearest 100


# Calculate PNL based on current leg status
def calculate_leg_pnl(option_type, type, lots):
    global PRICE_DATA
    
    # Check if PRICE_DATA and the required subkey exist
    price_data_key = option_type + '_PRICE_DATA'
    if price_data_key not in PRICE_DATA:
        print(f"Error: {price_data_key} not found in PRICE_DATA.")
        return None
    
    # Get the PRICE_DATAS for the given option_type
    PRICE_DATAS = PRICE_DATA[price_data_key]
    
    # Create the keys for sell and buy nodes
    node_sell = type + '_SELL_' + option_type
    node_buy = type + '_BUY_' + option_type

    # Initialize prices
    sold_price_or_ltp_price = 0
    bought_price_or_ltp_price = 0

    # Debug print statements to show keys and data
    # print(f"node_sell: {node_sell}")
    # print(f"node_buy: {node_buy}")
    # print("PRICE_DATAS:", PRICE_DATAS)

    # Check if the nodes exist in PRICE_DATAS before accessing
    if node_sell in PRICE_DATAS:
        # Use the stored price or fetch the last traded price if it's zero
        sold_price_or_ltp_price = PRICE_DATAS[node_sell]
        if sold_price_or_ltp_price == 0:
            sold_price_or_ltp_price = fetch_last_trade_price(option_type)
    else:
        print(f"Error: {node_sell} not found in PRICE_DATAS.")
    
    if node_buy in PRICE_DATAS:
        # Use the stored price or fetch the last traded price if it's zero
        bought_price_or_ltp_price = PRICE_DATAS[node_buy]
        if bought_price_or_ltp_price == 0:
            bought_price_or_ltp_price = fetch_last_trade_price(option_type)
    else:
        print(f"Error: {node_buy} not found in PRICE_DATAS.")
    
    # Calculate the PNL difference
    difference = sold_price_or_ltp_price - bought_price_or_ltp_price
    
    # Print the calculated values for debugging
    # print(f"Sold Price: {sold_price_or_ltp_price}")
    # print(f"Bought Price: {bought_price_or_ltp_price}")
    # print(f"PNL Difference: {difference}")
    
    # Calculate the PNL considering the number of lots
    pnl = difference * lots * ONE_LOT_QUANTITY
    return pnl


    
# Function to calculate total PNL
def calculate_total_pnl():
    ce_entry_pnl = calculate_leg_pnl('CE', 'INITIAL', INITIAL_LOTS)
    pe_entry_pnl = calculate_leg_pnl('PE', 'INITIAL', INITIAL_LOTS)
    ce_pnl = calculate_leg_pnl('CE', 'BUY_BACK', BUY_BACK_LOTS)
    pe_pnl = calculate_leg_pnl('PE', 'BUY_BACK', BUY_BACK_LOTS)
    ce_re_entry_pnl = calculate_leg_pnl('CE', 'RE_ENTRY', INITIAL_LOTS)
    pe_re_entry_pnl = calculate_leg_pnl('CE', 'RE_ENTRY', INITIAL_LOTS)
    return ce_pnl + pe_pnl + ce_entry_pnl + pe_entry_pnl + ce_re_entry_pnl + pe_re_entry_pnl  

def check_unsold_lots(id):
    fill = ORDER_STATUS[id]['fillqty']
    qty = ORDER_STATUS[id]['qty']
    return float(qty)-float(fill)



# Monitor individual leg logic (CE/PE)
def monitor_leg(option_type, sell_price, strike_price):
    global strategy_running, ce_lots, pe_lots, SYMBOLDICT, ORDER_STATUS
    leg_entry = False
    lots = INITIAL_LOTS * ONE_LOT_QUANTITY
    buy_back_lots = BUY_BACK_LOTS * ONE_LOT_QUANTITY
    print('monitor ')
    print(option_type)
    while strategy_running and not leg_entry:
        # print('while check monitor')
        ltp = fetch_last_trade_price(option_type)  # Fetch LTP for the option leg
        if ltp <= (float(sell_price) * float(SAFETY_STOP_LOSS_PERCENTAGE)):
            leg_entry = True
            print(f"{option_type} reached 76% of sell price, exiting...")
            safety_sell_order_id = place_buy_order(api, SYMBOLDICT,LEG_TOKEN, option_type, lots)
            ORDER_ID_DATAS.append(safety_sell_order_id)
            print('dd')
            while not is_order_complete(safety_sell_order_id, ORDER_STATUS):
                time.sleep(0.5)

            # important need to check for order execution if not succeded then retry with modify 
            buy_back_price = round_to_nearest_0_05(float(sell_price) * float(BUY_BACK_PERCENTAGE))
            buy_order_id = place_limit_order(api, SYMBOLDICT,LEG_TOKEN, option_type, 'B', buy_back_lots, limit_price=buy_back_price)
            ORDER_ID_DATAS.append(buy_order_id)

            while not is_order_complete(buy_order_id, ORDER_STATUS):
                time.sleep(1)
            
            sell_target_price = round_to_nearest_0_05(float(buy_back_price) * float(1 + SELL_TARGET_PERCENTAGE))
            sell_order_id = place_limit_order(api, SYMBOLDICT,LEG_TOKEN, option_type, 'S', buy_back_lots, limit_price=sell_target_price)
            ORDER_ID_DATAS.append(sell_order_id)
            ltp = fetch_last_trade_price(option_type)  # Fetch LTP for the option leg

            while not is_order_complete(sell_order_id, ORDER_STATUS): #static instead check weather ltp > selltarget_price
                ltp = fetch_last_trade_price(option_type)  # Fetch LTP for the option leg
                pnl = calculate_total_pnl()
                if pnl <= -MAX_LOSS_PER_LEG or ltp <=  (ORDER_STATUS[buy_order_id]['avgprc'] * BUY_BACK_LOSS_PERCENTAGE):
                    print(f"{option_type} reached 10% loss, exiting remaining orders.")
                    unsold_lots = check_unsold_lots(sell_order_id)
                    api.cancel_order(sell_order_id)
                    place_market_order(api, SYMBOLDICT,LEG_TOKEN, option_type, 'B', unsold_lots)
                    break
                time.sleep(1)
            
            if is_order_complete(sell_order_id, ORDER_STATUS):
                re_sell_order_id = place_sell_order(api, SYMBOLDICT,LEG_TOKEN, option_type, lots)
                ORDER_ID_DATAS.append(re_sell_order_id)

    return True


# Function to monitor the strategy
def monitor_strategy():
    global strategy_running
    while strategy_running:
        pnl = calculate_total_pnl()  # Fetch the PNL
        if pnl >= TARGET_PROFIT:
            print(f"Target profit of ₹{TARGET_PROFIT} reached. Exiting strategy.")
            strategy_running = False
            exit_strategy()
        elif pnl <= -MAX_LOSS:
            print(f"Max loss of ₹{MAX_LOSS} reached. Exiting strategy.")
            strategy_running = False
            exit_strategy()
            print('checking pnl')
        time.sleep(5)  # Check PNL every 5 seconds


# Retry logic with a maximum number of attempts to avoid an infinite loop
def wait_for_orders_to_complete(ce_order_id, pe_order_id, max_retries=100):
    global ORDER_STATUS
    attempts = 0
    print('wait_for_orders_to_complete')
    print(ORDER_STATUS)
    while not (is_order_complete(ce_order_id, ORDER_STATUS) and is_order_complete(pe_order_id, ORDER_STATUS)):
        # Sleep for 0.25 seconds
        time.sleep(0.25)
        attempts += 1
        print("ORDER_STATUS[order_id].get('status')")
        print(ORDER_STATUS)
        print(is_order_complete(ce_order_id, ORDER_STATUS) and is_order_complete(pe_order_id, ORDER_STATUS))
        # print(ORDER_STATUS)
        # print(ce_order_id)
        # print(pe_order_id)

        # Check if maximum retries reached
        if attempts >= max_retries:
            print(f"Max retries reached. Orders may not be complete: {ce_order_id}, {pe_order_id}")
            break
    else:
        print("Both orders are complete.")
        return True

# Function to exit the strategy
def exit_strategy():
    global strategy_running
    strategy_running = False #static rethink
    for key in ORDER_STATUS:
        print(f"Key: {key}")
        if ORDER_STATUS[key]['status'].lower() != 'complete':
            responce = api.cancel_order(key)
            if 'Ok ' in responce['stat']:
                return True # static place_buy_order()    
    
    # Implement logic to close all open orders and exit strategy
    print("Strategy exited.")

def run_strategy():
    global strategy_running, sell_price_ce, sell_price_pe, SYMBOLDICT, ORDER_STATUS
    start_time = ist_datatime.replace(hour=9, minute=20, second=0, microsecond=0).time()
    end_time = ist_datatime.replace(hour=23, minute=30, second=0, microsecond=0).time()
    lots = INITIAL_LOTS * ONE_LOT_QUANTITY
    while True:
        current_time = ist_datatime.time()
        if start_time <= current_time <= end_time:
            if not strategy_running:
                atm_strike = fetch_atm_strike()
                print('passed atm strike')

                ce_order_id = place_sell_order(api, SYMBOLDICT,LEG_TOKEN, 'CE', lots)
                pe_order_id = place_sell_order(api, SYMBOLDICT,LEG_TOKEN, 'PE', lots)
                ORDER_ID_DATAS.append(ce_order_id)
                ORDER_ID_DATAS.append(pe_order_id)
                time.sleep(2)
                wait_for_orders_to_complete(ce_order_id, pe_order_id, 4000)


                print('---------------------------------------------')
                print('status order')

                print(ORDER_STATUS)
                sell_price_ce =  ORDER_STATUS[ce_order_id]['avgprc']



                print('ORDER_STATUS')
                print(ORDER_STATUS)
                sell_price_pe = ORDER_STATUS[pe_order_id]['avgprc']
                print('---------------------------------------------')
                print(sell_price_ce)
                print(sell_price_pe)
                print('---------------------------------------------')
                strategy_running = True

                ce_thread = threading.Thread(target=monitor_leg, args=('CE', sell_price_ce, atm_strike + STRIKE_DIFFERENCE))
                pe_thread = threading.Thread(target=monitor_leg, args=('PE', sell_price_pe, atm_strike - STRIKE_DIFFERENCE))

                ce_thread.start()
                pe_thread.start()

                strategy_thread = threading.Thread(target=monitor_strategy) # static uncomment
                strategy_thread.start() # static uncomment

                ce_thread.join()
                pe_thread.join()
                strategy_thread.join() # static uncomment
        else:
            print("Outside trading hours, strategy paused.")
            time.sleep(60)



run_strategy()