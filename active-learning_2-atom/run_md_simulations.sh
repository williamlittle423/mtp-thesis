#!/bin/bash
# run_small_cell_stages.sh

# Define the LAMMPS executable
LAMMPS_EXEC="lmp_mpi"  # Replace with your actual LAMMPS command if different

# Define input files for Stage 1 and Stage 2
#INPUT_FILES=("lammps_inputs/stage1_2atom.in" "lammps_inputs/stage2_4atom.in")
INPUT_FILES=("lammps_inputs/stage1_2atom.in")

# Ensure the MTP model exists
MTP_MODEL="pot_V0.almtp"
if [ ! -f "$MTP_MODEL" ]; then
    echo "Error: MTP model '$MTP_MODEL' not found!"
    exit 1
fi

# Loop through each stage input file
for INPUT_FILE in "${INPUT_FILES[@]}"; do
    if [ ! -f "$INPUT_FILE" ]; then
        echo "Warning: Input file '$INPUT_FILE' not found. Skipping..."
        continue
    fi

    STAGE_NAME=$(basename "$INPUT_FILE" .in)
    echo "Running $STAGE_NAME simulation..."

    # Run LAMMPS directly without modifying the input
    $LAMMPS_EXEC -in "$INPUT_FILE"
    EXIT_CODE=$?

    # Create a directory for results
    OUTPUT_DIR="outputs/${STAGE_NAME}_output"
    mkdir -p "$OUTPUT_DIR"

    # Move useful output files
    mv log.lammps "$OUTPUT_DIR/" 2>/dev/null
    mv dump.* "$OUTPUT_DIR/" 2>/dev/null

    if [ $EXIT_CODE -ne 0 ]; then
        echo "Error: LAMMPS run for $STAGE_NAME failed."
    else
        echo "$STAGE_NAME simulation complete. Results in $OUTPUT_DIR"
    fi
done

echo "All small-cell stage simulations completed for this iteration. Beginning retraining."
