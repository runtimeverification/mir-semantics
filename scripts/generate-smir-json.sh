#!/usr/bin/env bash

# Convenience script: Generate Stable MIR JSON/DOT/PNG/PDF files from Rust source code
# Usage: ./scripts/generate-smir-json.sh <rust_file> [output_dir] [format]

set -xeuo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <rust_file> [output_dir] [format]"
    echo ""
    echo "Parameters:"
    echo "  rust_file   - Rust source file path"
    echo "  output_dir  - Output directory (default: source file directory)"  
    echo "  format      - Output format: json(default), dot, png, pdf"
    echo ""
    echo "Examples:"
    echo "  $0 test.rs                    # Generate JSON to source file directory"
    echo "  $0 test.rs output/            # Generate JSON to output/ directory"
    echo "  $0 test.rs . dot              # Generate DOT file to current directory"
    echo "  $0 test.rs . png              # Generate PNG image to current directory"
    echo "  $0 test.rs . pdf              # Generate PDF document to current directory"
    exit 1
fi

RUST_FILE="$1"
OUTPUT_DIR="${2:-$(dirname "$RUST_FILE")}"
FORMAT="${3:-json}"

if [ ! -f "$RUST_FILE" ]; then
    echo "❌ Error: File '$RUST_FILE' does not exist"
    exit 1
fi

if [ "$FORMAT" != "json" ] && [ "$FORMAT" != "dot" ] && [ "$FORMAT" != "png" ] && [ "$FORMAT" != "pdf" ]; then
    echo "❌ Error: Format must be 'json', 'dot', 'png', or 'pdf'"
    exit 1
fi

# Check if Graphviz is installed (required for PNG/PDF formats)
if [ "$FORMAT" = "png" ] || [ "$FORMAT" = "pdf" ]; then
    if ! command -v dot >/dev/null 2>&1; then
        echo "❌ Error: PNG/PDF format requires Graphviz installation"
        echo "   macOS: brew install graphviz"
        echo "   Ubuntu/Debian: sudo apt-get install graphviz"
        exit 1
    fi
fi

echo "🔄 Generating SMIR $FORMAT file from $RUST_FILE..."
echo "📁 Output directory: $OUTPUT_DIR"

# Create output directory (if it doesn't exist)
mkdir -p "$OUTPUT_DIR"

# Run stable-mir-json tool
# Get absolute paths (macOS compatible)
ABS_OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
ABS_RUST_FILE="$(cd "$(dirname "$RUST_FILE")" && pwd)/$(basename "$RUST_FILE")"
BASENAME=$(basename "$RUST_FILE" .rs)

# Set parameters based on format
if [ "$FORMAT" = "json" ]; then
    FORMAT_ARG="--json"
    FILE_EXT="smir.json"
    OUTPUT_FILE="$OUTPUT_DIR/${BASENAME}.$FILE_EXT"
    
    (cd deps/stable-mir-json && cargo run -- \
        $FORMAT_ARG \
        -Z no-codegen \
        --crate-type bin \
        --out-dir "$ABS_OUTPUT_DIR" \
        "$ABS_RUST_FILE")
        
    if [ -f "$OUTPUT_FILE" ]; then
        echo "✅ Successfully generated: $OUTPUT_FILE"
        echo "📊 File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
    else
        echo "❌ Generated JSON file not found"
        exit 1
    fi
    
else
    # DOT, PNG, PDF formats all need to generate DOT file first
    DOT_FILE="$OUTPUT_DIR/${BASENAME}.smir.dot"
    
    (cd deps/stable-mir-json && cargo run -- \
        --dot \
        -Z no-codegen \
        --crate-type bin \
        --out-dir "$ABS_OUTPUT_DIR" \
        "$ABS_RUST_FILE")
    
    if [ ! -f "$DOT_FILE" ]; then
        echo "❌ Generated DOT file not found"
        exit 1
    fi
    
    echo "✅ Successfully generated: $DOT_FILE"
    echo "📊 DOT file size: $(ls -lh "$DOT_FILE" | awk '{print $5}')"
    
    # Process based on format
    if [ "$FORMAT" = "dot" ]; then
        echo "💡 Tip: You can use Graphviz to convert to images:"
        echo "   dot -Tpng '$DOT_FILE' -o '${DOT_FILE%.dot}.png'"
        echo "   dot -Tpdf '$DOT_FILE' -o '${DOT_FILE%.dot}.pdf'"
        echo "   Or view online: https://dreampuf.github.io/GraphvizOnline/"
        
    elif [ "$FORMAT" = "png" ]; then
        PNG_FILE="${DOT_FILE%.dot}.png"
        echo "🖼️  Converting to PNG image..."
        
        if dot -Tpng "$DOT_FILE" -o "$PNG_FILE"; then
            echo "✅ Successfully generated: $PNG_FILE"
            echo "📊 PNG file size: $(ls -lh "$PNG_FILE" | awk '{print $5}')"
            echo "💡 Tip: Intermediate file $DOT_FILE is also preserved"
        else
            echo "❌ PNG conversion failed"
            exit 1
        fi
        
    elif [ "$FORMAT" = "pdf" ]; then
        PDF_FILE="${DOT_FILE%.dot}.pdf"
        echo "📄 Converting to PDF document..."
        
        if dot -Tpdf "$DOT_FILE" -o "$PDF_FILE"; then
            echo "✅ Successfully generated: $PDF_FILE"
            echo "📊 PDF file size: $(ls -lh "$PDF_FILE" | awk '{print $5}')"
            echo "💡 Tip: Intermediate file $DOT_FILE is also preserved"
        else
            echo "❌ PDF conversion failed"
            exit 1
        fi
    fi
fi
