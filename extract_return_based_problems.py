import json

# Read the full appsPlus.json file
with open('appsPlus.json', 'r', encoding='utf-8') as f:
    all_problems = json.load(f)

# Filter for competition-level problems that RETURN values (no print statements)
# and have function-based inputs/outputs (not stdin/stdout)
return_based_problems = []

for problem in all_problems:
    # Check if it's interview or competition difficulty
    difficulty = problem.get('difficulty', '')
    if difficulty not in ['interview', 'competition']:
        continue

    canonical = problem.get('canonical_solution', '')

    # Skip if it has print() or sys.stdout or input() or sys.stdin
    if any(keyword in canonical.lower() for keyword in ['print(', 'sys.stdout', 'input()', 'sys.stdin']):
        continue

    # Must have a return statement
    if 'return' not in canonical.lower():
        continue

    # Check that inputs/outputs are not strings (which would indicate stdin/stdout format)
    inputs = problem.get('inputs', [])
    outputs = problem.get('outputs', [])

    # Skip if inputs or outputs are strings (indicating stdin format)
    if inputs and isinstance(inputs[0], str):
        continue
    if outputs and isinstance(outputs[0], str):
        continue

    return_based_problems.append(problem)

    # Stop after finding 10
    if len(return_based_problems) == 10:
        break

# Write to new file
with open('competition_problems_return_10.json', 'w', encoding='utf-8') as f:
    json.dump(return_based_problems, f, indent=4, ensure_ascii=False)

print(f"Successfully extracted {len(return_based_problems)} return-based competition problems")
if return_based_problems:
    print(f"Total problems scanned: {all_problems.index(return_based_problems[-1]) + 1}")
else:
    print("No suitable problems found")
