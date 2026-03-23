# neurons/forward.py
# Handles the actual forward pass from validators/sponsors

from agents.arbos_manager import ArbosManager

def process_challenge(challenge: str):
    """Main forward function called by the miner"""
    arbos = ArbosManager()
    result = arbos.run(challenge)
    return result
