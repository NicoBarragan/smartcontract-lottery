from brownie import (accounts,
                     network,
                     config,
                     Contract,
                     MockV3Aggregator,
                     VRFCoordinatorMock,
                     LinkToken,
                     interface,
                    )

FORKED_LOCAL_ENVIORNMENTS = ["mainnet-fork"]
BLOCKCHAIN_LOCAL_ENVIORNMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    ## Ways of getting an account:
    # accounts[0] --> index is useful here
    # accounts.load("id") --> id is useful here
    # accounts.add("env") --> This is for adding
    if index:
        return accounts[index]
 
    elif id:
        return accounts.load(id)
 
    if (network.show_active() in BLOCKCHAIN_LOCAL_ENVIORNMENTS \
    or network.show_active() in FORKED_LOCAL_ENVIORNMENTS):
        return accounts[0]
 
    # if nothing of that happens: 
    return accounts.add(config['wallets']['from_key'])

contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator,
                    "vrf_coordinator": VRFCoordinatorMock,
                    "link":LinkToken,}

def get_contract(contract_name):
    """This function will grab the contract addresses 
    if definded, otherwise, it will deploy a mock version
    of that contract, and return that mock contract.
    
        Args:
            contract_name(string)
            
        Returns:
            brownie.network.contract.ProjectContract: The most
            recently deployed version of this contract.
    """
    
    contract_type = contract_to_mock[contract_name]
    # We didn't include FORKED cause we don't need to mock in a fork
    if network.show_active() in BLOCKCHAIN_LOCAL_ENVIORNMENTS: 
    
    # Deploying a mock if there is not one already deployed.
        if len(contract_type) <= 0: # MockV3Aggregator.length
            deploy_mocks()
    
        contract = contract_type[-1] # If it's already deployted, take the last one
    
    else: # For real true contracts
        # Network of the contract:
        contract_address = config['networks'][network.show_active()][contract_name]
        # We still need to pass the address and abi of the contract to deploy it
        contract = Contract.from_abi( 
            # This method allows us to deploy a contract from an abi
            contract_type._name, # name from V3AGGREGATOR
            contract_address,
            contract_type.abi, # ABI from V3AGGREGATOR
        )
    return contract
        
            
DECIMALS = 8
INITIAL_VALUE = 200000000000
            
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account=get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed!")
    

def fund_with_link(contract_address, 
                   account=None,
                   link_token=None,
                   amount=100000000000000000 # 0.1 LINK
                   ):
    account = account if account else get_account()
    
    link_token = link_token if link_token else get_contract("link")
    tx = link_token.transfer(contract_address, amount, {"from": account})

## If for a reason we'd have to interact by interfaces, this commented lines
## are the way for Brownie to compile the ABI to do that:
    # link_token_interface = interface.LinkTokeInterface(link_token.address)
    # tx = link_token_interface.transfer(contract_address, amount, {"from": account})
    
    tx.wait(1)
    print("Funded!")
    return tx