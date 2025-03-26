#!/bin/bash

# Step 1: Generate training and validation sets
python3 create_training_set.py
echo "Training set created successfully."
mkdir -p qe_inputs_train
mv Li_config*.in qe_inputs_train/

# Ensure the training set was created
if [ ! -f "train.cfg" ]; then
    echo "Error: train.cfg not found. Please generate the training set first."
    exit 1
fi

TRAIN_LOG="initial_train.log"

echo "Training initial MTP using MLIP-3..."
mlp train 10.almtp train.cfg --save_to=pot_V0.almtp --iteration_limit=500 --al_mode=nbh > $TRAIN_LOG 2>&1

if [ $? -eq 0 ]; then
    echo "Initial MTP training completed successfully."
else
    echo "Error: Initial MTP training failed. Check $TRAIN_LOG for details."
    exit 1
fi
