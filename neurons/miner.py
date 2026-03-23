# neurons/miner.py
# REAL Bittensor SN63 Miner - registers and runs Arbos

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
        
        # Register the miner
        self.subtensor.register_wallet(self.wallet)
        print(f"✅ Miner registered on SN63 with hotkey {self.wallet.hotkey.ss58_address}")

    def forward(self, synapse: bt.Synapse) -> bt.Synapse:
        """Real forward pass - receives challenge from validator"""
        challenge = synapse.input or "Default challenge"
        print(f"📥 Received challenge from validator: {challenge[:100]}...")

        start_time = time.time()
        
        # Run the full Arbos pipeline
        result = self.arbos.run(challenge)
        
        runtime = (time.time() - start_time) / 3600
        print(f"⏱️  Completed in {runtime:.2f}h")

        synapse.output = result["solution"]
        synapse.runtime_hours = runtime
        return synapse

if __name__ == "__main__":
    miner = EnigmaMiner()
    miner.axon.serve(netuid=63, subtensor=miner.subtensor)
    miner.axon.start()
    print("🚀 Enigma Miner is LIVE on SN63")
    bt.logging.info("Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("👋 Miner stopped")
