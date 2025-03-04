#!/bin/bash

# Step 1: Generate training and validation set and train the initial MTP
python3 create_training_set.py

mkdir -p qe_inputs_train
mv Li_config*.in qe_inputs_train

python3 create_validation_set.py
mkdir -p qe_inputs_validate
mv Li_config*.in qe_inputs_validate


# Check if train.cfg exists
if [ ! -f "train.cfg" ]; then
    echo "Error: train.cfg not found. Please generate the training set first."
    exit 1
fi

# Set output file names for the MTP model and log
MTP_MODEL="mtp_initial.mtp"
TRAIN_LOG="train.log"

# Train the initial MTP using MLIP-3
echo "Training initial MTP using MLIP-3..."
mlp train empty.mtp train.cfg --energy-weight=1 --force-weight=0.1 --stress-weight=0.001 --max-iter=500 --save_to=$MTP_MODEL > $TRAIN_LOG 2>&1

# Check if training was successful
if [ $? -eq 0 ]; then
    echo "Initial MTP training completed successfully."
    echo "Model saved as: $MTP_MODEL"
    echo "Training log saved as: $TRAIN_LOG"
else
    echo "Error: Initial MTP training failed. Check $TRAIN_LOG for details."
    exit 1
fi

# Display summary of the training log
echo "Initial Training Summary:"
grep -E "_________________Errors report_________________" $TRAIN_LOG | tail -n 50

# Step 2: Validate the trained MTP on a validation set (validate.cfg)

# Check if validate.cfg exists
if [ ! -f "validate.cfg" ]; then
    echo "Error: validate.cfg not found. Please provide a validation set."
    exit 1
fi

VALIDATION_LOG="validation.log"

echo "Validating the trained MTP using MLIP-3..."
mlp check_errors mtp_initial.mtp validation.cfg --report_to validation_summary.log --log validation_details.log

# Check if validation was successful
if [ $? -eq 0 ]; then
    echo "Validation completed successfully."
    echo "Validation log saved as: $VALIDATION_LOG"
else
    echo "Error: Validation failed. Check $VALIDATION_LOG for details."
    exit 1
fi

# Display summary of validation results
echo "Validation Summary:"
grep -E "_________________Errors report_________________" $VALIDATION_LOG | tail -n 50

