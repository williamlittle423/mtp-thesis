import os
import re
import matplotlib.pyplot as plt

# Directory containing the log files
log_dir = '.'

# Lists to store iteration numbers and corresponding errors
iterations = []
max_errors = []
avg_errors = []
rms_errors = []

# Regular expressions for extracting values
iteration_pattern = re.compile(r'train_(\d+)\.log')
max_pattern = re.compile(r'Maximal absolute difference = ([\d\.]+)')
avg_pattern = re.compile(r'Average absolute difference = ([\d\.]+)')
rms_pattern = re.compile(r'RMS\s+absolute difference = ([\d\.]+)')

# Loop through log files in sequential order
for file in sorted(os.listdir(log_dir)):
    if iteration_pattern.match(file):
        iteration = int(iteration_pattern.match(file).group(1))
        with open(file, 'r') as f:
            content = f.read()
            max_match = max_pattern.search(content)
            avg_match = avg_pattern.search(content)
            rms_match = rms_pattern.search(content)

            if max_match and avg_match and rms_match:
                iterations.append(iteration)
                max_errors.append(float(max_match.group(1)))
                avg_errors.append(float(avg_match.group(1)))
                rms_errors.append(float(rms_match.group(1)))

# Plotting the results
plt.figure(figsize=(10, 6))
plt.scatter(iterations, avg_errors, label='Average Error', marker='o')
plt.xlabel('Active Learning Iteration')
plt.ylabel('Energy per Atom Error (eV)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('training_metrics.png')
plt.show()
