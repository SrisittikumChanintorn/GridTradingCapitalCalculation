import numpy as np
import pandas as pd
import plotly.graph_objects as go


def visualization_zone_each_price(df, first_action_price, fundA, fundB, symbol):
    # Create figure
    fig = go.Figure()

    # Plot Market Price
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines',
                             line=dict(color='#2ef6cf'), name="Price"))

    # Plot Average Price (Trend)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_Trend'], mode='lines',
                             line=dict(color='#a32efe', width=1.75), name="EMA Trend"))

   # Plot Initial Investment
    fig.add_trace(go.Scatter(x=df.index, y=[first_action_price] * len(df), mode='lines',
                         line=dict(color='white', width=2), name="Initial Investment"))



    # Add horizontal lines for FundA
    for value in fundA:
        fig.add_hline(y=value, line=dict(color='red', width=1.5, dash='dash'))

    # Add horizontal lines for FundB
    for value in fundB:
        fig.add_hline(y=value, line=dict(color='#1d8348', width=0.75, dash='dash'))

    # Customize layout with fixed size
    fig.update_layout(
        xaxis=dict(title="Date", title_font=dict(color='white'), tickfont=dict(color='white')),
        yaxis=dict(title="Price", title_font=dict(color='white'), tickfont=dict(color='white')),
        paper_bgcolor='#1c2833',  # Background color for the entire figure
        plot_bgcolor='#212f3d',  # Background color for the plot area
        legend=dict(font=dict(color='white')),
        xaxis_gridcolor='gray',  # Set grid color
        yaxis_gridcolor='gray',  # Set grid color
        width=1200,  # Set plot width
        height=800   # Set plot height
    )

    return fig



def initail_investment_cost_calculation(first_action_price,action_level,asset_digit):
    action_level['Initail Invest'] = np.where(action_level['PriceLevel'] >= first_action_price  ,1 ,0)
    cumulative_summary_cost_for_initail_invest = sum(action_level['CostPerLevel'] * action_level['Initail Invest'])
    return np.round(cumulative_summary_cost_for_initail_invest,asset_digit)



def full_contract_price_for_cent_acc(first_action_price, min,max ,contract_size ,lot_size_fundA ,lot_size_fundB ,num_Zone_fundA ,num_Zone_fundB , balance=200 ,asset_digit=2):
    '''
    Ex : fundA , fundB , fundA_price , fundB_price , action_level   , first_action_cost , balance , reminding_funds , used_funds , lot_size_fundA , Total_fundA_price , lot_size_fundB , Total_fundB_price = full_contract_price_for_cent_acc(first_action_price , min=0,max=100,contract_size=10,lot_size_fundA=0.02,lot_size_fundB=0.01,num_Zone_fundA=4,num_Zone_fundB=8, balance=200 ,asset_digit=2)
    
    min : minimum boundary that asset must not hit ( assume 0 for standard Close System  with Strong Fundamental Values )
    max : maximum boundary ( for Long Bias Direction )
    contract_size  : Asset Contract Size ( up to asset ,Please Check actually from asset Spec or Broker )
    lot_size_fundA : Fund A Lot Size ( Fixed )
    lot_size_fundB : Fund B Lot Size ( Fixed )
    num_Zone_fundA : Number of Grid Sequences in Fund A 
    num_Zone_fundB : Number of Grid Sequences in Fund B 
    balance : balance in USD ( We multiply 100 to convert USD to USD inside this program )
    asset_digit : digits of asset 
    '''
    cent_multiplier = 100
    balance = balance * cent_multiplier
    
    # Fund A Grid Sequences
    fundA = np.round(np.linspace(max,min,num_Zone_fundA+1),asset_digit)[1:]

    # Last Zone calculation for Non-Equal digits of Asset
    if fundA[0] > 2:
        fundA[-1] += 1
    else :
        digit_multiplier = 10**(-1*asset_digit)
        fundA[-1] += digit_multiplier

    # FundA Price Calculation 
    fundA_price = fundA * contract_size * lot_size_fundA *cent_multiplier  # price each grid 
    Total_fundA_price = fundA_price.sum()                                                 # Total fundA price 

    # Fund B Grid Sequences
    fundB = np.round(np.linspace(max,min,  ( num_Zone_fundB + num_Zone_fundA ) +1),asset_digit)[1:-1]  #  num_Zone_fundB + num_Zone_fundA  to reduce dupplicate zone level of input from user view 

    # Last Zone calculation for Non-Equal digits of Asset   before sum the total of FundB to avoid impact of duplicate investment in the same Price Level problem 
    if fundB[0] > 2:
        fundB[-1] += 1
    else :
        digit_multiplier = 10**(-1*asset_digit)
        fundB[-1] += digit_multiplier
        
    fundB = np.array([b for b in fundB if b not in fundA])
    # FundA Price Calculation 
    fundB_price = fundB * contract_size *  lot_size_fundB *cent_multiplier  # price each grid 
    Total_fundB_price = fundB_price.sum()   # Total fundA price 

    # Remaining funds
    used_funds = Total_fundA_price + Total_fundB_price
    reminding_funds = np.round((balance - ( used_funds )), asset_digit)

    
    df_fundA = pd.DataFrame({'PriceLevel':fundA,'CostPerLevel':fundA_price})
    df_fundA['FundType'] = 'fundA'
    df_fundA['PositionSize'] = lot_size_fundA

    df_fundB = pd.DataFrame({'PriceLevel':fundB,'CostPerLevel':fundB_price})
    df_fundB['FundType'] = 'fundB'
    df_fundB['PositionSize'] = lot_size_fundB
    
    action_level = pd.concat((df_fundA,df_fundB),axis=0)
    action_level = action_level.sort_values(by='PriceLevel',ascending=False)
    action_level = action_level.reset_index(drop=True)

    first_action_cost = initail_investment_cost_calculation(first_action_price,action_level,asset_digit)

    # Warning for User 
    if first_action_cost <= 0:
        raise ValueError("Hey !!!  First Action Price is Out of Top Zone Range")
    if reminding_funds <= 1:
        raise ValueError("Hey !!!  No Enought Money")
    if first_action_price <= 0:
        raise ValueError("Hey !!!  First Action Price Can not Less Than 0 ")
        
    # Text Summary
    print('====== SUMMARY ======')
    print('Cost of First Investment :', first_action_cost)
    print(f'From Balance {balance}  Remaining funds {reminding_funds}  used {used_funds} USC in Worst Case Scenario')
    print(f'Fund A  investment size {lot_size_fundA} for each Zone , Total FundA Cost : {np.round(Total_fundA_price,asset_digit)}')
    print(f'Fund B  investment size {lot_size_fundB} for each Zone , Total FundB Cost : {np.round(Total_fundB_price,asset_digit)}\n')
    


    return  fundA , fundB , fundA_price , fundB_price , action_level   , first_action_cost , balance , reminding_funds , used_funds , lot_size_fundA , Total_fundA_price , lot_size_fundB , Total_fundB_price
