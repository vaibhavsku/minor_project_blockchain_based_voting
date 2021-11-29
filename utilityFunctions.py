from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from Crypto.PublicKey._slowmath import rsa_construct
import secrets
import os

def readPublicBallotKey(ballotNo):
    wrkd = os.getcwd()
    pathPublic = wrkd + "/Signatures/"+str(ballotNo)+"_ballotPublic.pem"
    PublicBallotKey = open(str(pathPublic), "rb").read()
    return PublicBallotKey

def readPrivateBallotKey(ballotNo):
    wrkd = os.getcwd()
    pathPrivate = wrkd + "/Signatures/"+str(ballotNo)+"_ballotPrivate.pem"
    PrivateBallotKey = open(str(pathPrivate), "rb").read()
    return PrivateBallotKey

def writePrivateBallotKey(ballotNo):
    wrkd = os.getcwd()
    pathPrivate = wrkd + "/Signatures/"+str(ballotNo)+"_ballotPrivate.pem"
    pathPublic = wrkd + "/Signatures/"+str(ballotNo)+"_ballotPublic.pem"
    if(os.path.isfile(str(pathPrivate)) == False):
        ballot = rsa.generate_private_key(65537, 512)
        ballot_private = ballot.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
        ballot_public = (ballot.public_key()).public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
        open(str(pathPrivate), "wb").write(ballot_private)
        open(str(pathPublic), "wb").write(ballot_public)
  

def signedKey(blindKey, ballotNo):
    ballot = serialization.load_pem_private_key(readPrivateBallotKey(ballotNo), None,None)
    rsa_priv_key = rsa_construct(ballot.private_numbers()._public_numbers._n, ballot.private_numbers()._public_numbers._e, ballot.private_numbers()._d, ballot.private_numbers()._p, ballot.private_numbers()._q)
    signedToken = rsa_priv_key._sign(blindKey)
    return signedToken

def verifySignedKey(signedKey, blindKey, ballotNo):
    ballot = serialization.load_pem_public_key(readPublicBallotKey(ballotNo))
    ballot.verify(signedKey, blindKey, padding.PSS(padding.MGF1(hashes.SHA256()), padding.PSS.MAX_LENGTH), hashes.SHA256())
    

#writePrivateBallotKey(223) use this once to generate private key for ballot no 223
#bkey = secrets.token_bytes(64)
#skey = signedKey(bkey, 223)
#print(skey)