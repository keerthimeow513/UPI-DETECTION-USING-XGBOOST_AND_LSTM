#!/usr/bin/env python3
"""
UPI Fraud Detection - Checksum Generation Script

This script generates SHA256 checksums for all model files after training.
Run this script after training to create a checksums.json file that will
be used for model integrity verification during inference.

Usage:
    # After training completes:
    python scripts/generate_checksums.py
    
    # Or specify custom paths:
    python scripts/generate_checksums.py --artifacts-dir 02_models/artifacts --output checksums.json

Example:
    $ python 03_training/train.py
    $ python scripts/generate_checksums.py
    Generated checksums:
      - lstm_model.h5: a1b2c3d4...
      - xgb_model.pkl: e5f6g7h8...
    Saved 2 checksums to 02_models/artifacts/checksums.json
"""

import os
import sys
import json
import argparse
from typing import Dict, List

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.security import calculate_checksum
from utils.logger import setup_logger

logger = setup_logger()


def generate_checksums(
    artifacts_dir: str,
    output_file: str,
    include_patterns: List[str] = None
) -> Dict[str, str]:
    """
    Generate SHA256 checksums for all model files in the artifacts directory.
    
    Args:
        artifacts_dir (str): Directory containing model files
        output_file (str): Path to save the checksums JSON file
        include_patterns (List[str]): List of file patterns to include
                                    (default: ['*.pkl', '*.h5'])
    
    Returns:
        Dict[str, str]: Dictionary mapping filenames to their SHA256 checksums
        
    Raises:
        FileNotFoundError: If artifacts directory does not exist
        IOError: If unable to write checksums file
    """
    if include_patterns is None:
        include_patterns = ['*.pkl', '*.h5', '*.json']
    
    # Verify artifacts directory exists
    if not os.path.exists(artifacts_dir):
        raise FileNotFoundError(
            f"Artifacts directory not found: {artifacts_dir}\n"
            f"Please run training first: python 03_training/train.py"
        )
    
    checksums = {}
    
    # Find all files matching patterns
    import fnmatch
    
    logger.info(f"Scanning {artifacts_dir} for model files...")
    
    for filename in sorted(os.listdir(artifacts_dir)):
        file_path = os.path.join(artifacts_dir, filename)
        
        # Skip directories and non-files
        if not os.path.isfile(file_path):
            continue
        
        # Check if file matches any pattern
        matches = any(fnmatch.fnmatch(filename, pattern) for pattern in include_patterns)
        
        if matches:
            try:
                checksum = calculate_checksum(file_path)
                checksums[filename] = checksum
                logger.info(f"  {filename}: {checksum}")
            except Exception as e:
                logger.error(f"Failed to generate checksum for {filename}: {str(e)}")
    
    if not checksums:
        logger.warning(f"No model files found in {artifacts_dir} matching patterns: {include_patterns}")
        return checksums
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save checksums to JSON file
    checksum_data = {
        'checksums': checksums,
        'algorithm': 'sha256',
        'count': len(checksums),
        'directory': artifacts_dir
    }
    
    try:
        with open(output_file, 'w') as f:
            json.dump(checksum_data, f, indent=2)
        logger.info(f"Saved {len(checksums)} checksums to {output_file}")
    except IOError as e:
        raise IOError(f"Failed to write checksums file: {str(e)}")
    
    return checksums


def verify_checksums(artifacts_dir: str, checksums_file: str) -> bool:
    """
    Verify that all files in checksums file match their stored checksums.
    
    Args:
        artifacts_dir (str): Directory containing model files
        checksums_file (str): Path to the checksums JSON file
        
    Returns:
        bool: True if all files pass verification, False otherwise
    """
    from utils.security import validate_model_integrity
    
    try:
        with open(checksums_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load checksums file: {str(e)}")
        return False
    
    checksums = data.get('checksums', {})
    all_valid = True
    
    logger.info(f"Verifying {len(checksums)} files...")
    
    for filename, expected_checksum in checksums.items():
        file_path = os.path.join(artifacts_dir, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File missing: {filename}")
            all_valid = False
            continue
        
        try:
            is_valid = validate_model_integrity(file_path, expected_checksum)
            if is_valid:
                logger.info(f"  [OK] {filename}")
            else:
                logger.error(f"  [FAIL] {filename} - checksum mismatch")
                all_valid = False
        except Exception as e:
            logger.error(f"  [ERROR] {filename} - {str(e)}")
            all_valid = False
    
    return all_valid


def main():
    """Main entry point for the checksum generation script."""
    parser = argparse.ArgumentParser(
        description='Generate SHA256 checksums for ML model files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate checksums for default artifacts directory
  python scripts/generate_checksums.py
  
  # Specify custom paths
  python scripts/generate_checksums.py --artifacts-dir ./models --output ./checksums.json
  
  # Verify existing checksums
  python scripts/generate_checksums.py --verify
        """
    )
    
    parser.add_argument(
        '--artifacts-dir',
        type=str,
        default='02_models/artifacts',
        help='Directory containing model files (default: 02_models/artifacts)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='02_models/artifacts/checksums.json',
        help='Output file for checksums (default: 02_models/artifacts/checksums.json)'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify existing checksums instead of generating new ones'
    )
    
    parser.add_argument(
        '--patterns',
        nargs='+',
        default=['*.pkl', '*.h5', '*.json'],
        help='File patterns to include (default: *.pkl *.h5 *.json)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verify:
            # Verify mode
            is_valid = verify_checksums(args.artifacts_dir, args.output)
            if is_valid:
                logger.info("All files verified successfully!")
                sys.exit(0)
            else:
                logger.error("Verification failed for one or more files")
                sys.exit(1)
        else:
            # Generate mode
            checksums = generate_checksums(
                args.artifacts_dir,
                args.output,
                args.patterns
            )
            
            if checksums:
                print("\n" + "="*60)
                print("CHECKSUMS GENERATED")
                print("="*60)
                for filename, checksum in sorted(checksums.items()):
                    print(f"{filename:30} {checksum}")
                print("="*60)
                print(f"Total: {len(checksums)} files")
                print(f"Output: {args.output}")
                print("="*60)
                sys.exit(0)
            else:
                logger.error("No checksums generated")
                sys.exit(1)
                
    except FileNotFoundError as e:
        logger.error(str(e))
        print("\nHint: Run training first to generate model files")
        print("  python 03_training/train.py")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
