import os

class Config:
    # Ethereum node (Infura, Alchemy, or local Geth/Hardhat RPC)
    RPC_URL = os.getenv("RPC_URL", "https://mainnet.infura.io/v3/your_project_id")
    
    # Private key for signing transactions
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "your_private_key_here")

    # Contract storage directory
    CONTRACTS_DIR = os.getenv("CONTRACTS_DIR", "/contracts")

    # Shared volume for uploads and files
    SHARED_DIR = os.getenv("SHARED_DIR", "/app")
    UPLOAD_DIR = os.path.join(SHARED_DIR, "uploads")

    # Logging configuration
    LOG_FILE_PATH = os.getenv("BLOCKCHAIN_LOG_PATH", "logs/blockchain.log")

    # Flask server settings
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", 5005))
