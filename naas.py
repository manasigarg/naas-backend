from flask import Flask, request
from nft import NFT
import json
import web3.eth
from web3 import Web3
import binascii

app = Flask(__name__)

w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))

nft = NFT("0xEF578cf0543d85035b4bB5d5917D9f21AdE9C9D4", w3)

pri_key_raw_1 = [70, 210, 164, 184, 140, 135, 11, 174, 203, 252, 175, 155, 36, 225, 236, 217, 247, 138, 56, 227, 247, 191, 214, 123, 205, 56, 82, 205, 161, 98, 65, 1]
pri_key_raw_2 = [70, 210, 164, 184, 140, 135, 11, 174, 203, 252, 175, 155, 36, 225, 236, 217, 247, 138, 56, 227, 247, 191, 214, 123, 205, 56, 82, 205, 161, 98, 65, 2]
pri_key_raw_3 = [70, 210, 164, 184, 140, 135, 11, 174, 203, 252, 175, 155, 36, 225, 236, 217, 247, 138, 56, 227, 247, 191, 214, 123, 205, 56, 82, 205, 161, 98, 65, 3]
pri_key_raw_4 = [70, 210, 164, 184, 140, 135, 11, 174, 203, 252, 175, 155, 36, 225, 236, 217, 247, 138, 56, 227, 247, 191, 214, 123, 205, 56, 82, 205, 161, 98, 65, 4]
pri_key_raw_5 = [70, 210, 164, 184, 140, 135, 11, 174, 203, 252, 175, 155, 36, 225, 236, 217, 247, 138, 56, 227, 247, 191, 214, 123, 205, 56, 82, 205, 161, 98, 65, 5]

acct_1 = web3.eth.Account.privateKeyToAccount(bytearray(pri_key_raw_1))
acct_2 = web3.eth.Account.privateKeyToAccount(bytearray(pri_key_raw_2))
acct_3 = web3.eth.Account.privateKeyToAccount(bytearray(pri_key_raw_3))
acct_4 = web3.eth.Account.privateKeyToAccount(bytearray(pri_key_raw_4))
acct_5 = web3.eth.Account.privateKeyToAccount(bytearray(pri_key_raw_5))

pri_key_1 = "0x{}".format(binascii.hexlify(bytearray(pri_key_raw_1))).replace("b'","").replace("'","")
pri_key_2 = "0x{}".format(binascii.hexlify(bytearray(pri_key_raw_2))).replace("b'","").replace("'","")
pri_key_3 = "0x{}".format(binascii.hexlify(bytearray(pri_key_raw_3))).replace("b'","").replace("'","")
pri_key_4 = "0x{}".format(binascii.hexlify(bytearray(pri_key_raw_4))).replace("b'","").replace("'","")
pri_key_5 = "0x{}".format(binascii.hexlify(bytearray(pri_key_raw_5))).replace("b'","").replace("'","")

print(acct_1.address)
print(acct_2.address)
print(acct_3.address)
print(acct_4.address)
print(acct_5.address)

w3.eth.defaultAccount = acct_1.address

# Sample: http://10.0.2.15:5008/nft/create
@app.route('/nft/create/')
def nft_create():
    nft.compile("nft.sol", "MyNFT")
    tx_hash = nft.deploy(pri_key_1).replace("'", "").replace("b","")
    nft.verify_deployment()
    return {"contract_address": f"0x{tx_hash}"}

# Sample: http://10.0.2.15:5008/nft/mint?addr=0x32E20f16cBa8B51A5113053f434A37E5986Fc771&url=google.com
@app.route('/nft/mint', methods=['GET'])
def nft_mint():
    command = request.args.to_dict()
    addr = command['addr']
    url = command['url']
    return {"token_id": nft.mint(pri_key_1, addr, url)}

# Sample: http://10.0.2.15:5008/nft/balance?addr=0x32E20f16cBa8B51A5113053f434A37E5986Fc771
@app.route('/nft/balance', methods=['GET'])
def nft_balance():
    command = request.args.to_dict()
    addr = command['addr']
    balance = nft.get_balance(addr)
    return {"address": addr, "balance": balance}

# Sample: http://10.0.2.15:5008/nft/owner?token_id?=1
@app.route('/nft/owner', methods=['GET'])
def nft_owner():
    command = request.args.to_dict()
    token_id = int(command['token_id'])
    addr = nft.get_owner(token_id)
    return {"token_id": token_id, "owner": addr}

# Sample: http://10.0.2.15:5008/nft/url?token_id=1
@app.route('/nft/url', methods=['GET'])
def nft_uri():
    command = request.args.to_dict()
    token_id = int(command['token_id'])
    return {"token_id": token_id, "uri": nft.get_uri(token_id)}

# Sample: http://10.0.2.15:5008/nft/total
@app.route('/nft/total/')
def nft_total():
    total = nft.get_num_tokens()
    return {"total_nfts": total}

if __name__ == '__main__':

    # accept connections from anywhere
    app.run(host='0.0.0.0', port=5008)