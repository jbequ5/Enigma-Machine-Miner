# scripts/test_challenge.py
# Quick test script so you can run the miner locally

from neurons.miner import EnigmaMiner

if __name__ == "__main__":
    print("🧪 Testing Enigma Machine...")
    miner = EnigmaMiner()
    
    test_challenge = "Optimize a peaked quantum circuit for better stabilizer simulation"
    result = miner.forward(test_challenge)
    
    print("✅ Test complete!")
    print("Solution preview:", result.get("solution", "No solution")[:200] + "...")
