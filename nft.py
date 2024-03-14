import web3.eth
from web3 import Web3
from web3._utils.contracts import (
        prepare_transaction,
        encode_transaction_data
)
import binascii
from eth_keys import keys
from solcx import compile_files
import sys

SELECTED_OUTPUT_VALUES = (
    "abi",
    "asm",
    "ast",
    "bin",
    "bin-runtime",
    # "clone-bin",
    "devdoc",
    "interface",
    "opcodes",
    "userdoc",
)

class NFT:

    def __init__(self, address, w3):

        self.address = address
        self.num_tokens = 0
        self.nonce = 28
        self.w3 = w3

    def compile(self, contract_file, contract_name):

        contracts = compile_files(source_files=[contract_file],
                                  output_values=SELECTED_OUTPUT_VALUES,
                                  optimize=False,
                                  optimize_yul=False)
        self.contract = contracts.pop(f"{contract_file}:{contract_name}")
        self.contract_interface = self.w3.eth.contract(abi=self.contract['abi'], bytecode=self.contract['bin'])

    def deploy(self, pri_key):

        # Do not include 'to' field for contract deployment
        transaction = \
        {
            'from': self.address,
            'nonce': self.nonce, # Note: Nonce starts from zero
            # 'value': 0,
            'data': f"{self.contract['bin']}",
            'gas': int(21000+32000+1000+10000000*(len(self.contract["bin"])/2)),
            'gasPrice': 100000,
            'chainId': 19536287
        }

        # Sign transaction
        signed = self.w3.eth.account.sign_transaction(transaction, pri_key)

        # Deploy contract
        self.tx_hash_bin = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        self.tx_hash = binascii.hexlify(self.tx_hash_bin)
        self.tx_hash = str(self.tx_hash).replace("b'", "").replace("'", "")
        print(f"Deployed new contract to : {self.tx_hash}")

        # Get transaction receipt
        self.tx_receipt = self.w3.eth.wait_for_transaction_receipt(self.tx_hash_bin, poll_latency=10)

        self.nonce += 1

        return self.tx_hash

    def verify_deployment(self):

        # Get contract instance
        self.contract_instance = self.w3.eth.contract(
            address=self.tx_receipt.contractAddress,
            abi=self.contract["abi"],
            bytecode=self.contract['bin']
        )

        # To check if contract is deployed successfully
        # If contract code is empty the the deployment is not successful
        contract_code = self.w3.eth.getCode(self.contract_instance.address)
        print(f"Contract size: {len(contract_code)}")

        contract_creator_fctn = self.contract_instance.get_function_by_signature('owner()')
        self.contract_creator = contract_creator_fctn().call()
        contract_name_fctn = self.contract_instance.get_function_by_signature('name()')
        self.contract_name = contract_name_fctn().call()

    def mint(self, pri_key, addr, url):

        # Construct contract function
        contract_function = self.contract_instance.functions.mintNFT(addr, url)
        tx_data = encode_transaction_data(
            self.w3,
            contract_function.function_identifier,
            contract_function.contract_abi,
            contract_function.abi,
            contract_function.args,
            contract_function.kwargs,
        )

        # Construct transaction
        transaction = \
            {
                'from': self.address,
                'to': self.contract_instance.address,
                'nonce': self.nonce,  # Note: Nonce starts from zero
                'value': 0,
                'data': tx_data,
                'gas': int(21000 + 5000 * (len(tx_data) / 2 + 10)),
                'gasPrice': 250000,
                'chainId': 19536287
            }

        # Sign transaction
        signed = self.w3.eth.account.sign_transaction(transaction, pri_key)

        # Send transaction
        tx_hash_bin = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        tx_hash = binascii.hexlify(tx_hash_bin)
        print(f"Minted NFT (tx hash: {tx_hash}")

        self.nonce += 1

        self.num_tokens += 1
        return self.num_tokens

    def get_balance(self, address):

        balance_of = self.contract_instance.get_function_by_signature('balanceOf(address)')
        return balance_of(address).call()

    def get_owner(self, token_id):

        owner_of = self.contract_instance.get_function_by_signature('ownerOf(uint256)')
        return owner_of(token_id).call()

    def get_uri(self, token_id):

        token_uri = self.contract_instance.get_function_by_signature('tokenURI(uint256)')
        return token_uri(token_id).call()

    def get_num_tokens(self):

        return self.num_tokens