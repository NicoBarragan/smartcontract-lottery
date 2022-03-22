from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account() # id='flaite_test_address' --> if I want to use mine
    lottery = Lottery.deploy(
        get_contract('eth_usd_price_feed').address, # We only want the address of the contract
        get_contract("vrf_coordinator").address,
        get_contract("link").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed Lottery!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1] # The most recent deployment of Lottery contract
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1) # Wait for 1 blockw ait for the last transaction to be completed
    print("The lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1] # The most recent deployment of Lottery contract
    value = lottery.getEntranceFee() + 1000000 # Adding wei for the transaction with certainty 
    entering_tx = lottery.enter({"from": account,
# Value that we'll be sending ont the transaction. = To Value in Remix (msg.value)
                                        "value": value})
    entering_tx.wait(1) # Wait for 1 blockw ait for the last transaction to be completed
    print("You entered the lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1] # The most recent deployment of Lottery contract
# Fund contract with LINK token for the randomness function to work
    
    fund_tx = fund_with_link(lottery.address)
    fund_tx.wait(1)
    
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1) # Wait for 1 blockw ait for the last transaction to be completed
    time.sleep(60) # We give time to the node for the answer
    print(f"{lottery.recentWinner()} won the lottery!")

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
    
    
if __name__ == '__main__':
    main()