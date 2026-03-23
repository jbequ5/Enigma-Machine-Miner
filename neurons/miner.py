# neurons/miner.py
# REAL SN63 Miner with full error handling

import bittensor as bt
import time
from agents.arbos_manager import ArbosManager

class EnigmaMiner:
    def __init__(self):
        self.config = bt.config()
        self.wallet = bt.wallet(config=self.config)
        self.subtensor = bt.subtensor(config=self.config)
        self.axon = bt.axon(config=self.config)
        self.arbos = ArbosManager()
        
        self.subtensor.register_wallet(self.wallet)
        print(f"✅ Miner registered on SN63 — hotkey {self.wallet.hotkey.ss58_address}")

    def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        try:
            challenge = synapse.input or "Default challenge"
            print(f"📥 Received challenge: {challenge[:100]}...")

            result = self.arbos.run(challenge)
            
            synapse.output = result["solution"]
            synapse.runtime_hours = 3.5  # placeholder — monitor will track real time
            return synapse
            
        except Exception as e:
            print(f"❌ Forward error: {e}")
            synapse.output = f"ERROR: {str(e)}"
            return synapse

if __name__ == "__main__":
    miner = EnigmaMiner()
    miner.axon.serve(netuid=63)
    miner.axon.start()
    print("🚀 Enigma Miner is LIVE on SN63")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("👋 Miner stopped")
