from os import wait
from flask import Flask, render_template, redirect, url_for, request, jsonify
from ApplicationServer import authentication, onlineAccountVerifier_getUserBallots, getCandidateNames, start


app = Flask(__name__)

@app.route('/candidates', methods=['POST'])
def getCandidates():
    res = request.json
    ballot_id = int(res['ballot_id'])
    candidates = getCandidateNames(ballot_id)
    return jsonify({"candidate_list":candidates})

@app.route('/castvote', methods=['GET','POST'])
def vote():
    error = None
    ballots=onlineAccountVerifier_getUserBallots(VOTER_ID)
    if request.method == 'POST':
        res = request.json
        try:
            receipt = start(VOTER_ID, VOTER_WALLET_ADDRESS, int(res['b_id']), res['priv_key'], int(res['c_index']))
            return jsonify({"response":"okay", "receipt":receipt})
        except:
            return jsonify({"response": "bad"})
    
    return render_template('castvote.html', error=error, ballots=ballots)


@app.route('/walletaddress', methods=['GET','POST'])
def getWalletAddress():
    error = None
    if request.method == 'POST':
        global VOTER_WALLET_ADDRESS 
        VOTER_WALLET_ADDRESS = request.form['walletAddress']
        return redirect(url_for('vote'))
    return render_template('walletaddress.html', error=error)

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        global VOTER_ID 
        VOTER_ID = request.form['user_id']
        voter_password = request.form['user_password']
        try:
            authentication(VOTER_ID, voter_password)
            return redirect(url_for('getWalletAddress'))
        except ValueError:
            error = 'Invalid VoterID format. Please try again.'
        except RuntimeError:
            error = 'Invalid login credentials. Please try again.'
            
    return render_template('login.html', error=error)

app.run()

