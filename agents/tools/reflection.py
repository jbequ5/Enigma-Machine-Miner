# agents/tools/reflection.py
# Full Reflection Pattern - self-critique and iterative improvement

def reflect_and_improve(task: str, output: str, llm_call, max_iterations: int = 4):
    """
    Reflection Pattern (from Agentic Design Patterns book)
    Generates → critiques → revises → loops until APPROVED.
    """
    current = output
    trace = []

    for i in range(max_iterations):
        critique = llm_call(f"""
            Task: {task}
            Output: {current}
            
            Critique for: accuracy, completeness, logic, hallucinations, clarity, and H100 runtime.
            Reply ONLY with "APPROVED" if perfect, otherwise list specific fixes.
        """)
        
        trace.append({"iteration": i+1, "critique": critique[:300]})

        if "APPROVED" in critique.upper():
            return current, trace
        
        # Revise
        current = llm_call(f"Improve based on critique:\nCritique: {critique}\nOriginal: {current}")
    
    return current, trace
