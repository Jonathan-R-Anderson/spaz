import os
import random
import ipaddress
from pathlib import Path
from flask import Flask
from flask_restful import Api
from werkzeug.datastructures import ImmutableDict
from web3 import Web3
from web3.exceptions import ContractLogicError
import json
import logging
import threading
import subprocess
import time
import docker
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json, os, logging, hmac, hashlib, base64, requests, subprocess
from werkzeug.utils import secure_filename
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from flask import Blueprint, render_template, request, jsonify, send_from_directory


LOG_FILE_PATH = os.path.join("logs", "app.log")


# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),  # Specify log file
        logging.StreamHandler()  # Also log to console
    ]
)

class ManiwaniApp(Flask):
    jinja_options = ImmutableDict()

app = ManiwaniApp(__name__, static_url_path='')
app.config['TEMPLATES_AUTO_RELOAD'] = os.getenv('TEMPLATES_AUTO_RELOAD', True)
HMAC_SECRET_KEY = os.getenv('HMAC_SECRET_KEY', '11257560')
session_store = {}
    
app.url_map.strict_slashes = False
rest_api = Api(app)

# Contract addresses
gremlinThreadAddress = '0x713e6c01A9B3E60790dAFBbc22c5F43556fF0Df1'
gremlinReplyAddress = '0x801d41C70a2A08EDad145c460D28C53742782d1b'
gremlinLeaderboardAddress = '0xf6d30668497075629A403828930b7A9292D5B554'
gremlinDAOAddress = '0xd0CC0d9d0654eE9F0Eb52e321e9d4b65BbB1b7C4'
gremlinProfileAddress = '0xE7fc3C7B10829443d728f798d4fF845465d78c5A'
gremlinAdminAddress = '0x4344253aC1c686fcc3B4a36c54FdeBA24Aa2065C'
gremlinChallengeAddress = '0x92c13553B8dAd209D0A1cc97D4f74F73103cbD4F'
gremlinJournalAddress = '0xA40C6e32553D88cbd73087A20043CA41A843bA92'
# Contract ABIs
gremlinAdminABI = [
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_gremlinThreadAddress",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_gremlinReplyAddress",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_treasuryAddress",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "admin",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "canManageThreads",
          "type": "bool"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "canManageReplies",
          "type": "bool"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "canManageTax",
          "type": "bool"
        },
        {
          "indexed": False,
          "internalType": "bool",
          "name": "canManageTreasury",
          "type": "bool"
        }
      ],
      "name": "AdminAdded",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "admin",
          "type": "address"
        }
      ],
      "name": "AdminRemoved",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "recipient",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "amount",
          "type": "uint256"
        }
      ],
      "name": "TaxCollectionTransferred",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "newTax",
          "type": "uint256"
        }
      ],
      "name": "TaxUpdated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_admin",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "_canManageThreads",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "_canManageReplies",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "_canManageTax",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "_canManageTreasury",
          "type": "bool"
        }
      ],
      "name": "addAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "adminAddresses",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "adminCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "admins",
      "outputs": [
        {
          "internalType": "bool",
          "name": "isAdmin",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "canManageThreads",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "canManageReplies",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "canManageTax",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "canManageTreasury",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "banUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "blacklistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "blacklistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_amount",
          "type": "uint256"
        }
      ],
      "name": "collectTaxFromChallenge",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "deleteReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "deleteThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllAdmins",
      "outputs": [
        {
          "internalType": "address[]",
          "name": "",
          "type": "address[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "globalTax",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinReply",
      "outputs": [
        {
          "internalType": "contract GremlinReply",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinThread",
      "outputs": [
        {
          "internalType": "contract GremlinThread",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_address",
          "type": "address"
        }
      ],
      "name": "isAdmin",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_admin",
          "type": "address"
        }
      ],
      "name": "removeAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_newTax",
          "type": "uint256"
        }
      ],
      "name": "setGlobalTax",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_newTreasuryAddress",
          "type": "address"
        }
      ],
      "name": "setTreasuryAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address payable",
          "name": "_recipient",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_amount",
          "type": "uint256"
        }
      ],
      "name": "transferTax",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "treasuryAddress",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "unbanUser",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "whitelistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "receive"
    }
  ]
  
gremlinChallengeABI =   [
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_leaderboardAddress",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_daoAddress",
          "type": "address"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "winner",
          "type": "address"
        }
      ],
      "name": "ChallengeCompleted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "string",
          "name": "category",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "overview",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "dataURL",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "modelsURL",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "rules",
          "type": "string"
        }
      ],
      "name": "ChallengeDetailsSet",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "winner",
          "type": "address"
        }
      ],
      "name": "ChallengeExpired",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "team",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "JoinRequestApproved",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "team",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "requester",
          "type": "address"
        }
      ],
      "name": "JoinRequestCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "team",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "score",
          "type": "uint256"
        }
      ],
      "name": "ScoreSubmitted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "teamOwner",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "team",
          "type": "address"
        }
      ],
      "name": "TeamCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "team",
          "type": "address"
        }
      ],
      "name": "TeamLeft",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_requester",
          "type": "address"
        }
      ],
      "name": "approveJoinRequest",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "challengeActive",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "challengeComplete",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "challengeDetails",
      "outputs": [
        {
          "internalType": "string",
          "name": "category",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "overview",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "dataURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "modelsURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "rules",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "gremlinThread",
          "type": "address"
        },
        {
          "internalType": "bool",
          "name": "exists",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "checkChallengeStatus",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_teamOwner",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        }
      ],
      "name": "createTeam",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "daoAddress",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "deadline",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "additionalDays",
          "type": "uint256"
        }
      ],
      "name": "extendChallenge",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_user",
          "type": "address"
        }
      ],
      "name": "isTeamMember",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "joinRequests",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "leaderboardAddress",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        }
      ],
      "name": "leaveTeam",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        }
      ],
      "name": "requestJoinTeam",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_category",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_overview",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_dataURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_modelsURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_rules",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_gremlinThread",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_durationInDays",
          "type": "uint256"
        }
      ],
      "name": "setChallengeDetails",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_score",
          "type": "uint256"
        }
      ],
      "name": "submitScore",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "teamMembers",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "teamOwners",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "teams",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "withdrawFunds",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "receive"
    }
  ]

gremlinDAOABI =   [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "challengeId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "description",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "category",
          "type": "string"
        }
      ],
      "name": "ChallengeSubmitted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "newTaxPercentage",
          "type": "uint256"
        }
      ],
      "name": "DAOTaxUpdated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "challengeId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "newAmount",
          "type": "uint256"
        }
      ],
      "name": "PrizePoolUpdated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "challengeId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "taxAmount",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "treasury",
          "type": "address"
        }
      ],
      "name": "TaxCollected",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "challengeId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "address",
          "name": "winner",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "prizeAfterTax",
          "type": "uint256"
        }
      ],
      "name": "WinnerAnnounced",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "addToPrizePool",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_winner",
          "type": "address"
        }
      ],
      "name": "announceWinner",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "challengeCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "challenges",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "category",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "description",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "dataURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "modelsURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "rules",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "gremlinThreadAddress",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "prizePool",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "active",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "daoBalance",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "daoTaxPercentage",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "endChallenge",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "getChallengeDetails",
      "outputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "category",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "description",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "dataURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "modelsURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "rules",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "prizePool",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "active",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "getPrizePool",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "getSubmissions",
      "outputs": [
        {
          "internalType": "address[]",
          "name": "",
          "type": "address[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "gremlinAdmin",
      "outputs": [
        {
          "internalType": "contract IGremlinAdmin",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        }
      ],
      "name": "removeChallenge",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_gremlinAdminAddress",
          "type": "address"
        }
      ],
      "name": "setGremlinAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_category",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_description",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_dataURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_modelsURL",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_rules",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "_gremlinThreadAddress",
          "type": "address"
        }
      ],
      "name": "submitChallenge",
      "outputs": [],
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_challengeId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "_submission",
          "type": "address"
        }
      ],
      "name": "submitSolution",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_newTaxPercentage",
          "type": "uint256"
        }
      ],
      "name": "updateDAOTax",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_recipient",
          "type": "address"
        }
      ],
      "name": "withdrawDAOBalance",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "stateMutability": "payable",
      "type": "receive"
    }
  ]

gremlinLeaderboardABI =   [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "address",
          "name": "entity",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "score",
          "type": "uint256"
        }
      ],
      "name": "LeaderboardUpdated",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "getHighestScorer",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getLeaderboard",
      "outputs": [
        {
          "components": [
            {
              "internalType": "address",
              "name": "entity",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "score",
              "type": "uint256"
            }
          ],
          "internalType": "struct GremlinLeaderboard.LeaderboardEntry[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "hasSubmitted",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "leaderboard",
      "outputs": [
        {
          "internalType": "address",
          "name": "entity",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "score",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_score",
          "type": "uint256"
        }
      ],
      "name": "submitScore",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_team",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_score",
          "type": "uint256"
        }
      ],
      "name": "submitScoreForTeam",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]
  
gremlinReplyABI =   [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "banAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "bannedAddresses",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "blacklistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_content",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_magnetUrl",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_parentId",
          "type": "uint256"
        }
      ],
      "name": "createReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "deleteReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllReplies",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            }
          ],
          "internalType": "struct GremlinReply.Reply[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "replies",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "content",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "magnetUrl",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "parentId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "whitelisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "blacklisted",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "replyCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "unbanAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_replyId",
          "type": "uint256"
        }
      ],
      "name": "whitelistReply",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinThreadABI = [
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "ThreadBlacklisted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "parentThreadId",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "subject",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "email",
          "type": "string"
        }
      ],
      "name": "ThreadCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "ThreadDeleted",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "ThreadWhitelisted",
      "type": "event"
    },
    {
      "inputs": [],
      "name": "admin",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "banAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "bannedAddresses",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "blacklistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_subject",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_magnetUrl",
          "type": "string"
        },
        {
          "internalType": "string[]",
          "name": "_tags",
          "type": "string[]"
        },
        {
          "internalType": "string",
          "name": "_content",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_parentThreadId",
          "type": "uint256"
        }
      ],
      "name": "createThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "deleteThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "getAllThreads",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "name",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "subject",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "string[]",
              "name": "tags",
              "type": "string[]"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentThreadId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "deleted",
              "type": "bool"
            }
          ],
          "internalType": "struct GremlinThread.Thread[]",
          "name": "",
          "type": "tuple[]"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "getThread",
      "outputs": [
        {
          "components": [
            {
              "internalType": "uint256",
              "name": "id",
              "type": "uint256"
            },
            {
              "internalType": "string",
              "name": "name",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "subject",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "email",
              "type": "string"
            },
            {
              "internalType": "string",
              "name": "magnetUrl",
              "type": "string"
            },
            {
              "internalType": "string[]",
              "name": "tags",
              "type": "string[]"
            },
            {
              "internalType": "string",
              "name": "content",
              "type": "string"
            },
            {
              "internalType": "uint256",
              "name": "parentThreadId",
              "type": "uint256"
            },
            {
              "internalType": "address",
              "name": "sender",
              "type": "address"
            },
            {
              "internalType": "uint256",
              "name": "timestamp",
              "type": "uint256"
            },
            {
              "internalType": "bool",
              "name": "whitelisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "blacklisted",
              "type": "bool"
            },
            {
              "internalType": "bool",
              "name": "deleted",
              "type": "bool"
            }
          ],
          "internalType": "struct GremlinThread.Thread",
          "name": "",
          "type": "tuple"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "threadCount",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "name": "threads",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "id",
          "type": "uint256"
        },
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "subject",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "email",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "magnetUrl",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "content",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "parentThreadId",
          "type": "uint256"
        },
        {
          "internalType": "address",
          "name": "sender",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "timestamp",
          "type": "uint256"
        },
        {
          "internalType": "bool",
          "name": "whitelisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "blacklisted",
          "type": "bool"
        },
        {
          "internalType": "bool",
          "name": "deleted",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "newAdmin",
          "type": "address"
        }
      ],
      "name": "transferAdmin",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_addr",
          "type": "address"
        }
      ],
      "name": "unbanAddress",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "uint256",
          "name": "_threadId",
          "type": "uint256"
        }
      ],
      "name": "whitelistThread",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinProfileABI = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "name",
          "type": "string"
        }
      ],
      "name": "ProfileCreated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "field",
          "type": "string"
        }
      ],
      "name": "ProfileUpdated",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": True,
          "internalType": "address",
          "name": "user",
          "type": "address"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "name": "StreamUrlUpdated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "bio",
          "type": "string"
        }
      ],
      "name": "createProfile",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "user",
          "type": "address"
        }
      ],
      "name": "getProfile",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "user",
          "type": "address"
        }
      ],
      "name": "getStreamUrl",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "profiles",
      "outputs": [
        {
          "internalType": "string",
          "name": "name",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "bio",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "css",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "html",
          "type": "string"
        },
        {
          "internalType": "address",
          "name": "owner",
          "type": "address"
        },
        {
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "css",
          "type": "string"
        }
      ],
      "name": "updateProfileCSS",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "html",
          "type": "string"
        }
      ],
      "name": "updateProfileHTML",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "videoStreamUrl",
          "type": "string"
        }
      ],
      "name": "updateStreamUrl",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]

gremlinJournalABI = [
			{
				"anonymous": False,
				"inputs": [
					{
						"indexed": True,
						"internalType": "uint256",
						"name": "paperId",
						"type": "uint256"
					},
					{
						"indexed": True,
						"internalType": "address",
						"name": "reviewer",
						"type": "address"
					},
					{
						"indexed": False,
						"internalType": "int256",
						"name": "vote",
						"type": "int256"
					}
				],
				"name": "PaperReviewed",
				"type": "event"
			},
			{
				"anonymous": False,
				"inputs": [
					{
						"indexed": True,
						"internalType": "uint256",
						"name": "paperId",
						"type": "uint256"
					},
					{
						"indexed": False,
						"internalType": "string",
						"name": "title",
						"type": "string"
					},
					{
						"indexed": True,
						"internalType": "address",
						"name": "author",
						"type": "address"
					}
				],
				"name": "PaperSubmitted",
				"type": "event"
			},
			{
				"anonymous": False,
				"inputs": [
					{
						"indexed": True,
						"internalType": "uint256",
						"name": "paperId",
						"type": "uint256"
					},
					{
						"indexed": True,
						"internalType": "address",
						"name": "author",
						"type": "address"
					},
					{
						"indexed": True,
						"internalType": "address",
						"name": "tipper",
						"type": "address"
					},
					{
						"indexed": False,
						"internalType": "uint256",
						"name": "amount",
						"type": "uint256"
					}
				],
				"name": "TipSent",
				"type": "event"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "_sortCriteria",
						"type": "string"
					}
				],
				"name": "getAllPaperIds",
				"outputs": [
					{
						"internalType": "uint256[]",
						"name": "",
						"type": "uint256[]"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256",
						"name": "_paperId",
						"type": "uint256"
					}
				],
				"name": "getPaperDetails",
				"outputs": [
					{
						"internalType": "string",
						"name": "title",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "description",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "magnetURL",
						"type": "string"
					},
					{
						"internalType": "address",
						"name": "author",
						"type": "address"
					},
					{
						"internalType": "address[]",
						"name": "reviewers",
						"type": "address[]"
					},
					{
						"internalType": "int256",
						"name": "totalScore",
						"type": "int256"
					},
					{
						"internalType": "uint256",
						"name": "totalWeight",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "tipAmount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "submissionDate",
						"type": "uint256"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "_user",
						"type": "address"
					}
				],
				"name": "getPapersByUser",
				"outputs": [
					{
						"internalType": "uint256[]",
						"name": "",
						"type": "uint256[]"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "_user",
						"type": "address"
					}
				],
				"name": "getWeight",
				"outputs": [
					{
						"internalType": "uint256",
						"name": "",
						"type": "uint256"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256",
						"name": "_paperId",
						"type": "uint256"
					},
					{
						"internalType": "int256",
						"name": "_vote",
						"type": "int256"
					}
				],
				"name": "reviewPaper",
				"outputs": [],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256[]",
						"name": "_paperIds",
						"type": "uint256[]"
					}
				],
				"name": "sortByDate",
				"outputs": [
					{
						"internalType": "uint256[]",
						"name": "",
						"type": "uint256[]"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256[]",
						"name": "_paperIds",
						"type": "uint256[]"
					}
				],
				"name": "sortBySubmissionOrder",
				"outputs": [
					{
						"internalType": "uint256[]",
						"name": "",
						"type": "uint256[]"
					}
				],
				"stateMutability": "pure",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256[]",
						"name": "_paperIds",
						"type": "uint256[]"
					}
				],
				"name": "sortByTitle",
				"outputs": [
					{
						"internalType": "uint256[]",
						"name": "",
						"type": "uint256[]"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "_title",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "_description",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "_magnetURL",
						"type": "string"
					}
				],
				"name": "submitPaper",
				"outputs": [],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256",
						"name": "_paperId",
						"type": "uint256"
					}
				],
				"name": "tipAuthor",
				"outputs": [],
				"stateMutability": "payable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "",
						"type": "address"
					}
				],
				"name": "users",
				"outputs": [
					{
						"internalType": "uint256",
						"name": "paperCount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "reviewCount",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "totalVotesCast",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "totalVotesReceived",
						"type": "uint256"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"stateMutability": "payable",
				"type": "receive"
			}
		]

FILE_DIR = os.getenv('FILE_DIR', 'hosted')
TRACKER_PORT = os.getenv('TRACKER_PORT', 5000)


WEBTORRENT_CONTAINER_URL = f"{os.getenv('WEBTORRENT_CONTAINER_URL', 'https://webtorrent_seeder')}:{os.getenv('WEBTORRENT_SEEDER_PORT', 5002)}"
PROFILE_DB_URL = f"{os.getenv('PROFILE_DB_URL', 'http://profile_db')}:{os.getenv('PROFILE_DB_PORT', 5003)}"

RTMP_URLS = {}
client = docker.from_env()


# Helper Functions
def gen_poster_id():
    return '%04X' % random.randint(0, 0xffff)

def ip_to_int(ip_str):
    return int.from_bytes(
        ipaddress.ip_address(ip_str).packed,
        byteorder="little"
    ) << 8

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return True

# Generate a random encryption key per session using elliptic curve
def generate_ecc_key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key

# Serialize the public key to send it to the client
def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

# Encrypt the HMAC secret using the public key (ECC)
def encrypt_secret(secret, public_key):
    encrypted_secret = public_key.encrypt(
        secret.encode(),
        ec.ECIESHKDF(salt=None, algorithm=hashes.SHA256())
    )
    return base64.b64encode(encrypted_secret).decode('utf-8')

