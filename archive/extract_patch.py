"""
Extract specific test case from SWE-bench Verified benchmark
and create a gold patch file.
"""

from datasets import load_dataset
from pathlib import Path
import json


def extract_patch_for_instance(instance_id, output_file):
    """
    Load SWE-bench Verified dataset and extract patch for specific instance.

    Args:
        instance_id: The instance ID to extract (e.g., 'scikit-learn__scikit-learn-10297')
        output_file: Output patch file name
    """
    print(f"Loading SWE-bench Verified dataset...")
    dataset = load_dataset('princeton-nlp/SWE-bench_Verified', split='test')

    print(f"Total problems in dataset: {len(dataset)}")
    print(f"Searching for instance: {instance_id}")

    # Search for the specific instance
    found = False
    for item in dataset:
        if item['instance_id'] == instance_id:
            found = True
            print(f"\nFound instance!")
            print(f"  Repo: {item['repo']}")
            print(f"  Instance ID: {item['instance_id']}")
            print(f"  Base commit: {item['base_commit']}")

            # Extract the patch
            patch_content = item.get('patch', '')

            if not patch_content:
                print("ERROR: No patch found in this instance!")
                return False

            # Write to output file
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(patch_content)

            print(f"\nSuccessfully created: {output_path.absolute()}")
            print(f"Patch size: {len(patch_content)} characters")
            print(f"Patch lines: {len(patch_content.splitlines())} lines")

            return True

    if not found:
        print(f"\nERROR: Instance '{instance_id}' not found in dataset!")
        print("\nTip: List all instance IDs with:")
        print("  [item['instance_id'] for item in dataset]")
        return False


def find_problems_with_same_setup(repo_name, environment_setup_commit, max_results=10):
    """
    Find problems from the same repository with the same environment_setup_commit.
    This ensures all problems can work with the same installed repository state.

    Args:
        repo_name: Repository name (e.g., 'scikit-learn/scikit-learn')
        environment_setup_commit: The environment setup commit hash
        max_results: Maximum number of problems to return

    Returns:
        List of full problem dictionaries
    """
    print(f"Loading SWE-bench Verified dataset...")
    dataset = load_dataset('princeton-nlp/SWE-bench_Verified', split='test')

    print(f"Searching for problems with:")
    print(f"  Repo: {repo_name}")
    print(f"  Setup commit: {environment_setup_commit}")

    matching_problems = []
    for item in dataset:
        if (item['repo'] == repo_name and
            item.get('environment_setup_commit', '') == environment_setup_commit):
            # Store the entire item as a dictionary
            problem_dict = dict(item)
            matching_problems.append(problem_dict)

            if len(matching_problems) >= max_results:
                break

    print(f"\nFound {len(matching_problems)} problems with matching setup:")
    print("-" * 80)
    for i, problem in enumerate(matching_problems, 1):
        print(f"\n{i}. Instance ID: {problem['instance_id']}")
        print(f"   Base commit: {problem['base_commit']}")
        problem_preview = problem.get('problem_statement', '')[:150]
        print(f"   Problem: {problem_preview}...")

    return matching_problems


def export_problems_to_json(repo_name, environment_setup_commit, output_file="problems.json", max_results=10):
    """
    Export all problem information for problems with the same environment setup to a JSON file.

    Args:
        repo_name: Repository name (e.g., 'scikit-learn/scikit-learn')
        environment_setup_commit: The environment setup commit hash
        output_file: Output JSON file name
        max_results: Maximum number of problems to export

    Returns:
        Number of problems exported
    """
    problems = find_problems_with_same_setup(repo_name, environment_setup_commit, max_results=max_results)

    if not problems:
        print(f"\nNo problems found with matching setup commit")
        return 0

    output_path = Path(output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Successfully exported {len(problems)} problems to: {output_path.absolute()}")
    print(f"Each problem includes:")
    print(f"  - instance_id")
    print(f"  - repo")
    print(f"  - base_commit")
    print(f"  - environment_setup_commit")
    print(f"  - problem_statement")
    print(f"  - patch")
    print(f"  - test_patch")
    print(f"  - and other metadata")
    print(f"{'='*80}\n")

    return len(problems)


if __name__ == "__main__":
    # Extract patch for scikit-learn instance 10297
    instance_id = "scikit-learn__scikit-learn-10297"
    output_file = "patch_gold_10297.patch"

    # success = extract_patch_for_instance(instance_id, output_file)

    # if success:
    #     print("\nDone!")
    # else:
    #     print("\nFailed to extract patch.")
    #     exit(1)

    # Uncomment below to find and export problems with the same environment setup
    print("\n" + "="*80)
    print("Finding more problems with same environment setup...")
    print("="*80 + "\n")
    count = export_problems_to_json(
        repo_name="scikit-learn/scikit-learn",
        environment_setup_commit="55bf5d93e5674f13a1134d93a11fd0cd11aabcd1",
        output_file="scikit_learn_problems.json",
        max_results=10
    )
