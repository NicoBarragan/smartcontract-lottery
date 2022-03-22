from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import ( 
    get_contract, FORKED_LOCAL_ENVIORNMENTS, BLOCKCHAIN_LOCAL_ENVIORNMENTS, get_account, fund_with_link
    )
from web3 import Web3
import pytest

## wE COULD REFACTOR TESTS BY IMPORTING THE FUNCTIONS AND NOT RE-WRITING

## Unit test (Development network): A way of testing the smallest 
# pieces of code on an isolated instance

## Integration Tests (testnet): A way of testing interactions across multiple systems

def test_get_entrance_fee():
    if network.show_active() not in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2.000 eth/usd
    # usdEntryFee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # Assert
    assert expected_entrance_fee == entrance_fee
    
def test_cant_enter_unless_starter():
    # Arrange
    if network.show_active() not in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
    account = get_account()
    # Act
    lottery = deploy_lottery() # When deploy, default of lottery is closed
    # Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, 
                       "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery() # When deploy, default of lottery is closed
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, 
                    "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account
        
     
def test_can_end_lottery():
    # Arrange
    if network.show_active() not in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
    account = get_account()
    lottery = deploy_lottery() # When deploy, default of lottery is closed
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, 
                    "value": lottery.getEntranceFee()})
    # Act
    fund_with_link(lottery.address)
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lotteryState() == 2 # Idx of the enum of calc_winner
    
## This is similar or it is an integration test
def test_can_pick_winner_correctly():
    # Arrange
    if network.show_active() not in BLOCKCHAIN_LOCAL_ENVIORNMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
        )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    
    # 777 % 3 = 0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery