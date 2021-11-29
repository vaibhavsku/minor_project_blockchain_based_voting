import datetime
from solcx import compile_standard
from web3 import Web3
import json
import psycopg2
import psycopg2.extras
from utilityFunctions.utilityFunctions import writePrivateBallotKey


DB_HOST = "127.0.0.1"
DB_NAME = "userinfo"
DB_USER = "admin1"
DB_PASS = "a11b23@1#$4567"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def start():
    n = int(input("Enter number of ballots that are needed to be registered : "))
    for i in range(0, n):
        candidates = []
        ballot_name = input("Enter ballot name : ")
        ballot_id = int(input("Enter ballot_id : "))        
        year = int(input("Enter ballot expiration year : "))
        month = int(input("Enter ballot expiration month : "))
        day = int(input("Enter ballot expiration day : "))
        hour = int(input("Enter ballot expiration hour : "))
        ballot_expiration_date = int(datetime.datetime(year, month, day, hour).timestamp())
        ballot_creation_date = datetime.datetime.utcnow()
        numCandidates = int(input("Enter number of canditates to be contested from this ballot : "))
        for c in range(0, numCandidates):
            candidateName = input(f"Enter name of candidate {c+1} : ")
            candidates.append(candidateName)
        contract_id = deploy(ballot_name, ballot_expiration_date, candidates)
        addToDB(ballot_id,ballot_name,ballot_creation_date, contract_id, ballot_expiration_date)
        writePrivateBallotKey(ballot_id)

def infoMessage(receipt):
    t_hash,source,destination,exitcode,totalGas = receipt["transactionHash"],receipt["from"],receipt["to"],receipt["status"],receipt["cumulativeGasUsed"]
    print(f"Transaction {str(t_hash)} from {source} to {destination} exited with {exitcode} . Total gas used for this transaction is {totalGas}")



def deploy(ballotname, ballotendDate, ballotOptions):
    # with open("./ETHVoteBallot.sol", "r") as file:
    #     voting_contract = file.read()
    
    # compiled_sol = compile_standard({
    #     "language" : "Solidity",
    #     "sources" : {"ETHVoteBallot.sol" : {"content" : voting_contract}},
    #     "settings" : {
    #         "outputSelection" : {
    #         "*" : {"*" : ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
    #         }
    #     },
    # },
    # solc_version="0.8.0"
    # )
    with open("./compiled_sol.json", "r") as file:
        compiled_sol = json.load(file)

    bytecode = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["evm"]["bytecode"]["object"]
    abi = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["abi"]
    blockchain = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
    network_id = 1337
    registrar_address = "0x5aB6213f9e861E68Ae69862770716E408273B376"
    registrar_signature = "3ab8e51f02c09b44d71f097c51209afe660cde34567ab0770ad03adfde439a7e" #unsafe only for development purposes. Never share or hardcode your private key
    smartcontract = blockchain.eth.contract(abi = abi, bytecode=bytecode)

    #First get the latest transaction number of the id
    nonce = blockchain.eth.getTransactionCount(registrar_address)
    #Now to deploy our smart contract we neeed to make a transaction
    transaction = smartcontract.constructor(ballotname, ballotendDate).buildTransaction({"chainId":network_id, "gasPrice": blockchain.eth.gas_price, "from":registrar_address, "nonce":nonce})
    signed_transaction = blockchain.eth.account.sign_transaction(transaction, registrar_signature)
    tx_hash = blockchain.eth.send_raw_transaction(signed_transaction.rawTransaction)
    tx_receipt = blockchain.eth.wait_for_transaction_receipt(tx_hash)

    #get address of the deployed contract
    smartcontract_address = tx_receipt["contractAddress"]
    gUsed = tx_receipt["cumulativeGasUsed"]
    print(f"Contract successfully deployed with address {smartcontract_address} and gas used is {gUsed}")

    #Now load the ballotoptions into our smart contract

    print("Now, adding ballot options")

    c1 = blockchain.eth.contract(smartcontract_address, abi=abi)
    
    for b in ballotOptions:
        nonce = nonce + 1
        t1 = c1.functions.addVotingOption(b).buildTransaction({"chainId":network_id, "gasPrice": blockchain.eth.gas_price, "from":registrar_address, "nonce":nonce})
        s_t1 = blockchain.eth.account.sign_transaction(t1, registrar_signature)
        t1_hash = blockchain.eth.send_raw_transaction(s_t1.rawTransaction)
        t1_receipt = blockchain.eth.wait_for_transaction_receipt(t1_hash)
        infoMessage(t1_receipt)
       
    #Finalize voting options
    nonce = nonce+1
    t2 = c1.functions.finalizeVotingOptions().buildTransaction({"chainId":network_id, "gasPrice": blockchain.eth.gas_price, "from":registrar_address, "nonce":nonce})
    s_t2 = blockchain.eth.account.sign_transaction(t2, registrar_signature)
    t2_hash = blockchain.eth.send_raw_transaction(s_t2.rawTransaction)
    t2_receipt = blockchain.eth.wait_for_transaction_receipt(t2_hash)
    infoMessage(t2_receipt)

    print("Ballot options finalized on this ballot contract")

    return smartcontract_address

def addToDB(ballot_id, ballot_name, ballot_creation_date, contract_id, ballot_end_date):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            #cur.execute("CREATE TABLE ballotinfo (ballot_id INT, ballot_name VARCHAR NOT NULL, ballot_creation_time TIMESTAMP NOT NULL, ballot_contract_id VARCHAR NOT NULL, ballot_end_date BIGINT NOT NULL, PRIMARY KEY (ballot_id));")
            cur.execute("INSERT INTO ballotinfo (ballot_id,ballot_name,ballot_creation_time,ballot_contract_id,ballot_end_date) VALUES(%s, %s, %s, %s, %s);", (ballot_id, ballot_name,ballot_creation_date,contract_id,ballot_end_date))
            conn.commit()



    
    
    

   


start()
#deploy("Demo 1", 1637901000, ["A1", "A2", "A3"])





