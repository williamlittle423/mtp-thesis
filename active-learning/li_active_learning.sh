#!/bin/bash

# Step 1: Train the initial MTP on a preliminary Li BCC primitive cell data
# ./initialize_mtp.sh

# Active learning loop
MTP_VERSION=0
while true; do
    echo "Running MD simulations using MTP_V${MTP_VERSION}.mtp..."
    ./run_md_simulations.sh

    # Check if preselected configurations were generated
    if [ ! -d "out" ] || [ -z "$(ls -A out/preselected.cfg.0 2>/dev/null)" ]; then
        echo "No new preselected configurations found. Stopping active learning."
        break
    fi

    # Step 2: Generate and run QE inputs
    echo "Generating and running QE input files..."
    python3 active_learning_conversions.py

    # rename the preselected configurations 
    mv out/preselected.cfg.0 out/prev_preselected.cfg


    # Step 3: Retrain the MTP with the updated training set
    PREV_MTP_VERSION=$MTP_VERSION
    MTP_VERSION=$((MTP_VERSION + 1))
    PREV_MTP_NAME="mtp_V${PREV_MTP_VERSION}.mtp"
    MTP_NAME="mtp_V${MTP_VERSION}.mtp"
    TRAIN_LOG="train_${MTP_VERSION}.log"

    echo "Retraining MTP model: ${MTP_NAME}..."
    mlp train $PREV_MTP_NAME train.cfg --energy-weight=1 --force-weight=0.1 --stress-weight=0.001 --max-iter=500 --save_to=$MTP_NAME > $TRAIN_LOG 2>&1

    if [ $? -eq 0 ]; then
        echo "MTP retraining completed successfully. New model: ${MTP_NAME}"
    else
        echo "Error: MTP retraining failed. Check $TRAIN_LOG for details."
        exit 1
    fi
done

echo "Active learning process completed after ${MTP_VERSION} iterations."
