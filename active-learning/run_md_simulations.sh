#!/bin/bash
# run_md_simulations.sh

# Define the LAMMPS executable
LAMMPS_EXEC="lmp_mpi"  # Replace with the correct LAMMPS executable if necessary

# Input template (the LAMMPS input file)
INPUT_TEMPLATE="run_md.in"

# Check if the input template exists
if [ ! -f "$INPUT_TEMPLATE" ]; then
    echo "Error: Input template '$INPUT_TEMPLATE' not found!"
    exit 1
fi

# Enable nullglob so that the glob returns an empty list if no files match
shopt -s nullglob
DATA_FILES=(lammps_configs/Li_config_*.data)
if [ ${#DATA_FILES[@]} -eq 0 ]; then
    echo "Error: No .data files matching lammps_configs/Li_config_*.data found!"
    exit 1
fi

# Determine the latest MTP model
LATEST_MTP=$(ls -t mtp_*.mtp 2>/dev/null | head -n 1)

if [ -z "$LATEST_MTP" ]; then
    echo "Error: No trained MTP model found!"
    exit 1
fi

echo "Using MTP model: $LATEST_MTP"

CURR_FILE=1
# Loop over all .data files
for DATA_FILE in "${DATA_FILES[@]}"; do
    # Extract the base name (e.g., Li_config_1)
    CONFIG_NAME="${DATA_FILE##*/}"      # Remove directory prefix
    CONFIG_NAME="${CONFIG_NAME%.data}"  # Remove file extension

    echo "Running simulation for $DATA_FILE..."

    # Create a temporary input file by replacing placeholders
    TEMP_INPUT="lammps_configs/${CONFIG_NAME}_temp.in"
    sed "s|%%DATA_FILE%%|$DATA_FILE|g; s|%%MTP_MODEL%%|$LATEST_MTP|g" "$INPUT_TEMPLATE" > "$TEMP_INPUT"

    # Run the LAMMPS simulation
    $LAMMPS_EXEC -in "$TEMP_INPUT"

    mv out/preselected.cfg.0 out/preselected.cfg.$CURR_FILE
    CURR_FILE=$((CURR_FILE + 1))

    if [ $? -ne 0 ]; then
        echo "Error: LAMMPS simulation for $DATA_FILE failed."
        rm "$TEMP_INPUT"
        continue
    fi

    # Create an output directory inside lammps_configs/outputs/
    OUTPUT_DIR="lammps_configs/outputs/${CONFIG_NAME}_output"
    mkdir -p "$OUTPUT_DIR"

    # Move relevant output files to the output directory if they exist
    if [ -f log.lammps ]; then
        mv log.lammps "$OUTPUT_DIR/"
    else
        echo "Warning: log.lammps not found for $DATA_FILE."
    fi

    if [ -f final_config.data ]; then
        mv final_config.data "$OUTPUT_DIR/"
    else
        echo "Warning: final_config.data not found for $DATA_FILE."
    fi

    # Clean up the temporary input file
    rm "$TEMP_INPUT"

    echo "Simulation for $DATA_FILE completed. Results saved in $OUTPUT_DIR."
done

echo "All simulations completed."
