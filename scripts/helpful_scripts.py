# pylint: disable=no-name-in-module

from brownie import (
    network,
    accounts,
    config,
    VRFCoordinatorMock,
    LinkToken,
    Contract
)

FORKED_LOCAL_NETWORKS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_NETWORKS = ["development", "ganache-local"]
OPENSEA_URL =  'https://testnets.opensea.io/assets/{}/{}'


DECIMALS = 8
STARTING_PRICE = 200000000000
BREED_MAPPING = {0: "PUG", 1: "SHIBA_INU", 2: "ST_BERNARD"}


def get_breed(breed_number):
    return BREED_MAPPING[breed_number]


def get_account(index=None, id=None):
    
    # account is dependent on the network running
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_NETWORKS
        or network.show_active() in FORKED_LOCAL_NETWORKS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    """
    This function will either deploy a mock for a network that doesn't have the conract
    or get an address from the config
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_NETWORKS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
        # MockV3Aggregator.abi
    return contract


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying mocks...")
    account = get_account()
    print("Deploying Mock LinkToken...")
    link_token = LinkToken.deploy({"from": account})
    print(f"Link Token deployed to {link_token.address}")
    print("Deploying Mock VRF Coordinator...")
    vrf_coordinator = VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print(f"VRFCoordinator deployed to {vrf_coordinator.address}")
    print("All done!")


def fund_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx
