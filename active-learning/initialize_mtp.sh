#!/bin/bash

# Step 1: Generate training and validation sets
python3 create_training_set.py
mkdir -p qe_inputs_train
mv Li_config*.in qe_inputs_train/

python3 create_validation_set.py
mkdir -p qe_inputs_validate
mv Li_config*.in qe_inputs_validate/

# Ensure the training set was created
if [ ! -f "train.cfg" ]; then
    echo "Error: train.cfg not found. Please generate the training set first."
    exit 1
fi

# Train the initial MTP using MLIP-3
MTP_MODEL="mtp_initial.mtp"
TRAIN_LOG="train.log"

echo "Training initial MTP using MLIP-3..."
mlp train empty.mtp train.cfg --energy-weight=1 --force-weight=0.1 --stress-weight=0.001 --max-iter=500 --save_to=$MTP_MODEL > $TRAIN_LOG 2>&1

if [ $? -eq 0 ]; then
    echo "Initial MTP training completed successfully."
else
    echo "Error: Initial MTP training failed. Check $TRAIN_LOG for details."
    exit 1
fi

# Validate the trained MTP
echo "Validating the trained MTP..."
mlp check_errors mtp_V0.mtp validation.cfg --report_to validation_summary.log --log validation_details.log
