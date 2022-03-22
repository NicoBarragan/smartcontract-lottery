from brownie import network
import pytest
import time
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import  (
    BLOCKCHAIN_LOCAL_ENVIORNMENTS, get_account, fund_with_link)

def test_can_pick_winner():
    if network.show_active() in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
        
    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    time.sleep(180)
    
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0