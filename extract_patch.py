"""
Extract specific test case from SWE-bench Verified benchmark
and create a gold patch file.
"""

from datasets import load_dataset
from pathlib import Path


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


if __name__ == "__main__":
    # Extract patch for scikit-learn instance 10297
    instance_id = "scikit-learn__scikit-learn-10297"
    output_file = "patch_gold_10297.patch"

    success = extract_patch_for_instance(instance_id, output_file)

    if success:
        print("\nDone!")
    else:
        print("\nFailed to extract patch.")
        exit(1)
