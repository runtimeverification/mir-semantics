#!/usr/bin/env python3
"""
Script to verify the add1 function from cse_call_add1_1time.rs using KMIR.
Returns an APRProof object and saves the proof show output to the proof directory.
"""

from pathlib import Path
from pyk.cterm.show import CTermShow
from pyk.kast.pretty import PrettyPrinter
from pyk.proof.show import APRProofShow

from kmir.kmir import KMIR, KMIRAPRNodePrinter
from kmir.build import LLVM_DEF_DIR
from kmir.options import ProveRSOpts, ShowOpts


def verify_add1(start_symbol='add1'):
    """
    Verify the add1 function and return the APRProof object.
    Also saves the proof show output to the proof directory.
    """
    # Path to the SMIR JSON file (pre-generated)
    smir_file = Path('/Users/steven/Desktop/projs/mir-semantics/kmir/src/tests/integration/data/exec-smir/cse/cse_call_add1_1time.smir.json')
    
    # Check if the SMIR file exists
    if not smir_file.exists():
        raise FileNotFoundError(f"SMIR JSON file not found: {smir_file}")
    
    # Initialize KMIR with LLVM backend
    print(f"Initializing KMIR with LLVM backend...")
    kmir = KMIR(LLVM_DEF_DIR)
    
    # Set up proof directory
    proof_dir = Path('./add1_proof')
    proof_dir.mkdir(exist_ok=True)
    
    # Configure prove options with specified entry point
    prove_opts = ProveRSOpts(
        smir_file,
        start_symbol=start_symbol,  # Use specified function as entry point
        proof_dir=proof_dir,
        max_iterations=100,
        smir=True,  # Use pre-generated SMIR JSON
        save_smir=False  # No need to save since we're using existing SMIR
    )
    
    # Run verification
    print(f"Starting verification of function '{start_symbol}' from {smir_file.name}...")
    apr_proof = kmir.prove_rs(prove_opts)
    
    # Print verification results
    print(f"\n=== Verification Results ===")
    print(f"Proof ID: {apr_proof.id}")
    print(f"Proof passed: {apr_proof.passed}")
    print(f"Proof failed: {apr_proof.failed}")
    print(f"Number of nodes: {len(apr_proof.kcfg.nodes)}")
    print(f"Number of edges: {len(apr_proof.kcfg.edges())}")
    
    # Generate and save proof show output
    print(f"\n=== Generating Proof Show Output ===")
    
    # Create printer and show objects
    printer = PrettyPrinter(kmir.definition)
    cterm_show = CTermShow(printer.print)
    
    # Create display options
    display_opts = ShowOpts(
        proof_dir=smir_file.parent,
        id=apr_proof.id,
        full_printer=False,
        smir_info=None,
        omit_current_body=False
    )
    
    # Create the shower
    shower = APRProofShow(
        kmir.definition, 
        node_printer=KMIRAPRNodePrinter(cterm_show, apr_proof, display_opts)
    )
    
    # Generate the show output
    show_lines = shower.show(apr_proof)
    show_output = '\n'.join(show_lines)
    
    # Save to proof directory
    show_output_file = proof_dir / f"{apr_proof.id}.show"
    with open(show_output_file, 'w') as f:
        f.write(show_output)
    
    print(f"Proof show output saved to: {show_output_file}")
    
    # Minimize the KCFG to remove redundant nodes
    print(f"\n=== Minimizing KCFG ===")
    original_nodes = len(apr_proof.kcfg.nodes)
    original_edges = len(apr_proof.kcfg.edges())
    
    # Minimize the KCFG
    apr_proof.minimize_kcfg()
    
    minimized_nodes = len(apr_proof.kcfg.nodes)
    minimized_edges = len(apr_proof.kcfg.edges())
    print(f"Original: {original_nodes} nodes, {original_edges} edges")
    print(f"Minimized: {minimized_nodes} nodes, {minimized_edges} edges")
    print(f"Reduction: {original_nodes - minimized_nodes} nodes, {original_edges - minimized_edges} edges")
    
    # Generate K module from the minimized KCFG
    print(f"\n=== Generating K Module ===")
    module_name = f"{start_symbol.upper()}-PROOF"
    k_module = apr_proof.kcfg.to_module(
        module_name=module_name,
        defunc_with=kmir.definition
    )
    
    # Save K module to file
    module_file = proof_dir / f"{apr_proof.id}.k"
    with open(module_file, 'w') as f:
        f.write(str(k_module))
    print(f"K module '{module_name}' saved to: {module_file}")
    
    # Generate and save minimized proof show output
    print(f"\n=== Generating Minimized Proof Show Output ===")
    minimized_show_lines = shower.show(apr_proof)
    minimized_show_output = '\n'.join(minimized_show_lines)
    
    minimized_show_file = proof_dir / f"{apr_proof.id}.minimized.show"
    with open(minimized_show_file, 'w') as f:
        f.write(minimized_show_output)
    print(f"Minimized proof show output saved to: {minimized_show_file}")
    
    # Also save a summary
    summary_file = proof_dir / f"{apr_proof.id}.summary"
    with open(summary_file, 'w') as f:
        f.write(f"Proof ID: {apr_proof.id}\n")
        f.write(f"Start Symbol: {start_symbol}\n")
        f.write(f"SMIR File: {smir_file}\n")
        f.write(f"Proof Passed: {apr_proof.passed}\n")
        f.write(f"Proof Failed: {apr_proof.failed}\n")
        f.write(f"Original Nodes: {original_nodes}\n")
        f.write(f"Original Edges: {original_edges}\n")
        f.write(f"Minimized Nodes: {minimized_nodes}\n")
        f.write(f"Minimized Edges: {minimized_edges}\n")
        f.write(f"K Module Name: {module_name}\n")
    
    print(f"Proof summary saved to: {summary_file}")
    
    # Return the APRProof object
    return apr_proof


if __name__ == "__main__":
    import sys
    
    # Allow specifying the start symbol from command line
    start_symbol = sys.argv[1] if len(sys.argv) > 1 else 'add1'
    
    try:
        proof = verify_add1(start_symbol)
        print(f"\n=== Script completed successfully ===")
        print(f"APRProof object returned: {proof}")
    except Exception as e:
        print(f"\n=== Error occurred ===")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)