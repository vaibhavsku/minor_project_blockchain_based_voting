from math import exp
import uuid
import psycopg2
import psycopg2.extras
psycopg2.extras.register_uuid()
from utilityFunctions.utilityFunctions import readPublicBallotKey, signedKey
from random import SystemRandom
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from Crypto.PublicKey._slowmath import rsa_construct
import getpass
import secrets
import binascii
import datetime
from web3 import Web3
import json

DB_HOST = "127.0.0.1"
DB_NAME = "userinfo"
DB_USER = "admin1"
DB_PASS = "a11b23@1#$4567"

blockchain = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
network_id = 1337

def getSmartContract():
    with open("./compiled_sol.json", "r") as file:
        compiled_sol = json.load(file)

    bytecode = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["abi"]
    return (bytecode, abi)

def infoMessage(receipt):
    t_hash,source,destination,exitcode,totalGas = receipt["transactionHash"],receipt["from"],receipt["to"],receipt["status"],receipt["cumulativeGasUsed"]
    print(f"Transaction {t_hash} from {source} to {destination} exited with {exitcode} . Total gas used for this transaction is {totalGas}")

def authorize_user_to_vote(e_ID, c_ID):
    registrar_address = "0x5aB6213f9e861E68Ae69862770716E408273B376"
    registrar_signature = "3ab8e51f02c09b44d71f097c51209afe660cde34567ab0770ad03adfde439a7e" #Unsafe for development purposes only. Never expose private key of your account
    smc = blockchain.eth.contract(c_ID,abi=getSmartContract()[1])
    nonce = blockchain.eth.getTransactionCount(registrar_address)
    transaction = smc.functions.giveRightToVote(e_ID).buildTransaction({"chainId":network_id, "gasPrice": blockchain.eth.gas_price, "from":registrar_address, "nonce":nonce})
    signed_transaction = blockchain.eth.account.sign_transaction(transaction, registrar_signature)
    tx_hash = blockchain.eth.send_raw_transaction(signed_transaction.rawTransaction)
    tx_receipt = blockchain.eth.wait_for_transaction_receipt(tx_hash)
    infoMessage(tx_receipt)
    
    

def user_vote(e_ID, c_ID):
    smc = blockchain.eth.contract(c_ID,abi=getSmartContract()[1])
    ballot_name = smc.functions.getBallotName().call()
    num_of_candidates = smc.functions.getVotingOptionsLength().call()
    print(f"Your ballot name is {ballot_name}")
    print("The candidates for the election are as follows : ")
    for i in range(0, num_of_candidates):
        optionName = smc.functions.getVotingOptionsName(i).call()
        print(f"Index : {i} Candidate Name: {optionName}")
    optionIndex = int(input("Enter the index for the candidate you want to vote : "))
    e_PR = getpass.getpass("Enter your private key to complete this transaction : ")
    nonce = blockchain.eth.getTransactionCount(e_ID)
    transaction = smc.functions.vote(optionIndex).buildTransaction({"chainId":network_id, "gasPrice": blockchain.eth.gas_price, "from":e_ID, "nonce":nonce})
    signed_transaction = blockchain.eth.account.sign_transaction(transaction, e_PR)
    tx_hash = blockchain.eth.send_raw_transaction(signed_transaction.rawTransaction)
    tx_receipt = blockchain.eth.wait_for_transaction_receipt(tx_hash)
    infoMessage(tx_receipt)
    print("You have successfully voted")


def authentication(username, password):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT user_password FROM registeredvoter WHERE voter_id = %s;", [uuid.UUID(username)])
            res = cur.fetchall()
            if(len(res) == 0):
                raise RuntimeError("Given voterID does not exist")
            user_pass = res[0][0]
            if(password != user_pass):
                raise RuntimeError("Given password is wrong")
            return True

def onlineAccountVerifier_sign_token(user_id, ballot_id, blind_token):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT ballot_id FROM registeredvoterballots WHERE voter_id = %s;", [uuid.UUID(user_id)])
            fetch_query1 = cur.fetchall()
            voter_ballots = []
            for i in range(0, len(fetch_query1)):
                voter_ballots.append(fetch_query1[i][0])
            if (ballot_id not in voter_ballots):
                raise RuntimeError("Entered ballotID does not exist in the database")
            cur.execute("SELECT voter_id FROM ballot_token_requests WHERE voter_id = %s;", [uuid.UUID(user_id)])
            res = cur.fetchall()
            if(len(res) > 0):
                raise RuntimeError("Voting entry already exists with this voterID")
            creation_date = datetime.datetime.utcnow()
            cur.execute("INSERT INTO ballot_token_requests(blind_token_hash, voter_id, ballot_id, created_on) VALUES(%s, %s, %s, %s);", (hex(blind_token), uuid.UUID(user_id), ballot_id, creation_date))
            conn.commit()
            signed_blind_token = signedKey(blind_token, ballot_id)
            return signed_blind_token

def onlineAccountVerifier_register_vote(ethereumID, ballot_id, signed_key, key):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            public_ballot_key = serialization.load_pem_public_key(readPublicBallotKey(ballot_id))
            rsa_key = rsa_construct(public_ballot_key.public_numbers()._n, public_ballot_key.public_numbers()._e)
            if not rsa_key._verify(key, signed_key):
                raise RuntimeError("Invalid signed_key")
            cur.execute("SELECT signed_token_hash FROM ballot_token_registration WHERE signed_token_hash = %s;", [hex(signed_key)])
            res = cur.fetchall()
            if(len(res) > 0):
                raise RuntimeError("This token alread exists in the database")
            creation_date = datetime.datetime.utcnow()
            cur.execute("INSERT INTO ballot_token_registration(signed_token_hash, voter_address, ballot_id, created_on) VALUES(%s, %s, %s, %s);", (hex(signed_key), ethereumID, ballot_id, creation_date))
            conn.commit()
            cur.execute("SELECT ballot_contract_id FROM ballotinfo WHERE ballot_id = %s;", [ballot_id])
            res = cur.fetchall()
            b_contract_id = res[0][0]
            authorize_user_to_vote(ethereumID, b_contract_id)
            user_vote(ethereumID, b_contract_id)


            
            
def start():
    user_id = input("Please enter your voter_id : ")
    passwd = getpass.getpass("Enter your password : ")
    ballot_id = int(input("Enter your ballot id : "))
    authentication(user_id, passwd)
    key = int(secrets.token_hex(16), 16)
    public_ballot_key = serialization.load_pem_public_key(readPublicBallotKey(ballot_id))
    r_number = SystemRandom().randrange(public_ballot_key.public_numbers()._n >> 10, public_ballot_key.public_numbers()._n)
    rsa_key = rsa_construct(public_ballot_key.public_numbers()._n, public_ballot_key.public_numbers()._e)
    blindkey = rsa_key._blind(key, r_number)
    signed_blindkey = onlineAccountVerifier_sign_token(user_id, ballot_id, blindkey)
    signed_key = rsa_key._unblind(signed_blindkey, r_number)
    if not rsa_key._verify(key, signed_key):
        raise RuntimeError("Invalid signed_key")
    user_eth_id = input("Please enter your ethereum address : ")
    onlineAccountVerifier_register_vote(user_eth_id, ballot_id, signed_key, key)



start()
#onlineAccountVerifier_sign_token("8b034ceb-b4fe-4b17-90eb-ca846101bb4b", 1151, 0)
#authorize_user_to_vote("0xDDa005ccE9a3cb060e899fc34346f70f1E2A172E", "0xe769BF8AbC0F639CDE4b5bce69502000bB20a87E")


   

    
    
   

    
    












            