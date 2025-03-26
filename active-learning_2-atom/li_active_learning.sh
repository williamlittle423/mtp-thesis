#!/bin/bash
# active_learning.sh

# Train the initial MTP on a preliminary Li BCC primitive cell data
# ./initialize_mtp.sh
mlp train 10.almtp train.cfg --save_to=pot_V0.almtp --iteration_limit=500 --al_mode=nbh > init_train.log 2>&1

# Save initial model as the fixed filename

# Initialize directories
mkdir -p mtp_models
mkdir -p train_logs

ITER=0
while true; do
    echo "Iteration $ITER: Running MD simulations with pot_V0.almtp..."

    # Clear previous configurations
    rm -f out/*

    ./run_md_simulations.sh

    if [ ! -d "out" ] || [ -z "$(ls -A out/preselected*.cfg.0 2>/dev/null)" ]; then
        echo "No new preselected configurations found. Stopping active learning."
        break
    fi

    echo "Generating and running QE input files..."
    python3 active_learning_conversions.py

    # Backup previous MTP model
    mv pot_V0.almtp "mtp_models/mtp_backup_iter_$ITER.mtp"

    # Retrain MTP and overwrite pot_V0.almtp
    TRAIN_LOG="train_logs/train_iter_${ITER}.log"
    echo "Retraining MTP model (overwriting pot_V0.almtp)..."
    mlp train 10.almtp train.cfg --save_to=pot_V0.almtp --iteration_limit=500 --al_mode=nbh > $TRAIN_LOG 2>&1


    if [ $? -ne 0 ]; then
        echo "Error: MTP retraining failed. Check $TRAIN_LOG for details."
        exit 1
    fi

    # Move previous configurations
    mv out/preselected_stage1_2atom.cfg.0 out/prev/preselected_stage1_2atom.cfg.$ITER

    echo "MTP retrained successfully. Proceeding to next iteration."
    ITER=$((ITER + 1))
done

echo "Active learning completed after $ITER iterations."
