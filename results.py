from web3 import Web3
from datetime import datetime
import psycopg2
import psycopg2.extras
import json

DB_HOST = "127.0.0.1"
DB_NAME = "userinfo"
DB_USER = "admin1"
DB_PASS = "a11b23@1#$4567"

blockchain = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
network_id = 1337

with open("./compiled_sol.json", "r") as file:
    compiled_sol = json.load(file)

bytecode = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["ETHVoteBallot.sol"]["ETHVoteBallot"]["abi"]

def getResults(ballot_id):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT ballot_contract_id FROM ballotinfo WHERE ballot_id = %s;", [ballot_id])
            c_ID = cur.fetchall()[0][0]
    smc = blockchain.eth.contract(c_ID,abi=abi)
    ballot_name = smc.functions.getBallotName().call()
    ballot_registered_voters = smc.functions.getRegisteredVoterCount().call()
    ballot_end_date = datetime.fromtimestamp(smc.functions.getBallotEndTime().call())
    number_of_candidates = smc.functions.getVotingOptionsLength().call()
    print(f"Results for ballot name : {ballot_name}")
    print(f"Voters registered for this ballot : {ballot_registered_voters}")
    print(f"This ballot ends on : {ballot_end_date}")
    for i in range(0, number_of_candidates):
        candidate_name = smc.functions.getVotingOptionsName(i).call()
        vote_count = smc.functions.getVotingOptionsVoteCount(i).call()
        print(f"{candidate_name} : {vote_count}")

getResults(input("Enter ballot_id : "))


