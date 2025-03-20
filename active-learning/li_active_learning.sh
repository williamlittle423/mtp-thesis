#!/bin/bash

# Train the initial MTP on a preliminary Li BCC primitive cell data
./initialize_mtp.sh

mv mtp_initial.mtp mtp_V0.mtp

# Initialize directories
mkdir -p mtp_models
mkdir -p train_logs

# Active learning loop
MTP_VERSION=0
while true; do
    echo "Running MD simulations using MTP_V${MTP_VERSION}.mtp..."

    # Clear previous configurations
    rm out/*

    ./run_md_simulations.sh

    # Check if preselected configurations were generated
    if [ ! -d "out" ] || [ -z "$(ls -A out/preselected.cfg* 2>/dev/null)" ]; then
        echo "No new preselected configurations found. Stopping active learning."
        break
    fi

    # Step 2: Generate and run QE inputs
    echo "Generating and running QE input files..."
    python3 active_learning_conversions.py

    # Step 3: Retrain the MTP with the updated training set
    PREV_MTP_VERSION=$MTP_VERSION
    MTP_VERSION=$((MTP_VERSION + 1))
    PREV_MTP_NAME="mtp_V${PREV_MTP_VERSION}.mtp"
    MTP_NAME="mtp_V${MTP_VERSION}.mtp"
    TRAIN_LOG="train_${MTP_VERSION}.log"

    echo "Retraining MTP model: ${MTP_NAME}..."
    mlp train $PREV_MTP_NAME train.cfg --energy-weight=1 --force-weight=0.1 --stress-weight=0.001 --max-iter=500 --save_to=$MTP_NAME > $TRAIN_LOG 2>&1
    mv $PREV_MTP_NAME mtp_models/
    mv $TRAIN_LOG train_logs/

    if [ $? -eq 0 ]; then
        echo "MTP retraining completed successfully. New model: ${MTP_NAME}"
    else
        echo "Error: MTP retraining failed. Check $TRAIN_LOG for details."
        exit 1
    fi
done

echo "Active learning process completed after ${MTP_VERSION} iterations."
