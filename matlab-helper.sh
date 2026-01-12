#!/bin/bash
# MATLAB Helper Script for ECET 337
# Organizes and manages MATLAB files

COURSE_DIR="/home/barney/School Work/Spring 2026/ECET 337"
MATLAB_WORK="$COURSE_DIR/MATLAB_Work"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create MATLAB working directory if it doesn't exist
mkdir -p "$MATLAB_WORK"

show_menu() {
    clear
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  ECET 337 MATLAB Helper${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "1) List all MATLAB files in course"
    echo "2) Copy MATLAB file to working directory"
    echo "3) Search for MATLAB file by keyword"
    echo "4) View MATLAB file categories"
    echo "5) Create new MATLAB script from template"
    echo "6) Open MATLAB working directory"
    echo "7) List recent MATLAB files"
    echo "8) Back up MATLAB work"
    echo "9) Exit"
    echo ""
    echo -n "Enter choice: "
}

list_all_matlab() {
    echo -e "${GREEN}All MATLAB files in course:${NC}"
    echo ""
    find "$COURSE_DIR" -name "*.m" ! -name "*.Zone.Identifier" -type f | \
    while read file; do
        dir=$(basename "$(dirname "$file")")
        name=$(basename "$file")
        echo -e "  [$dir] $name"
    done | sort
}

copy_to_work() {
    echo -n "Enter filename or keyword: "
    read keyword

    files=$(find "$COURSE_DIR/Lectures" -name "*$keyword*.m" ! -name "*.Zone.Identifier" -type f)

    if [ -z "$files" ]; then
        echo -e "${YELLOW}No files found matching: $keyword${NC}"
        return
    fi

    count=$(echo "$files" | wc -l)

    if [ $count -eq 1 ]; then
        cp "$files" "$MATLAB_WORK/"
        echo -e "${GREEN}Copied to: $MATLAB_WORK/$(basename "$files")${NC}"
    else
        echo -e "${YELLOW}Multiple files found:${NC}"
        select file in $files; do
            if [ -n "$file" ]; then
                cp "$file" "$MATLAB_WORK/"
                echo -e "${GREEN}Copied to: $MATLAB_WORK/$(basename "$file")${NC}"
                break
            fi
        done
    fi
}

search_matlab() {
    echo -n "Enter search keyword: "
    read keyword
    echo -e "${GREEN}Searching for: $keyword${NC}"
    echo ""
    find "$COURSE_DIR" -name "*$keyword*.m" ! -name "*.Zone.Identifier" -type f -exec ls -lh {} \;
}

categorize_files() {
    echo -e "${GREEN}MATLAB Files by Category:${NC}"
    echo ""

    echo -e "${YELLOW}=== RC/RL Circuits ===${NC}"
    find "$COURSE_DIR/Lectures" \( -name "*RC*.m" -o -name "*RL*.m" -o -name "*LR*.m" \) ! -name "*.Zone.Identifier"

    echo ""
    echo -e "${YELLOW}=== RLC/Second Order ===${NC}"
    find "$COURSE_DIR/Lectures" -name "*RLC*.m" ! -name "*.Zone.Identifier"

    echo ""
    echo -e "${YELLOW}=== Filters ===${NC}"
    find "$COURSE_DIR/Lectures" \( -name "*Butter*.m" -o -name "*Bessel*.m" -o -name "*Cheby*.m" -o -name "*BP*.m" -o -name "*LP*.m" -o -name "*HP*.m" \) ! -name "*.Zone.Identifier"

    echo ""
    echo -e "${YELLOW}=== Motors ===${NC}"
    find "$COURSE_DIR/Lectures" -name "*motor*.m" ! -name "*.Zone.Identifier"
}

create_template() {
    echo "Select template type:"
    echo "1) Basic Analysis Script"
    echo "2) Transfer Function Analysis"
    echo "3) Bode Plot"
    echo "4) Step Response"
    echo "5) Filter Design"
    echo -n "Choice: "
    read choice

    echo -n "Enter filename (without .m): "
    read filename

    filepath="$MATLAB_WORK/${filename}.m"

    case $choice in
        1)
            cat > "$filepath" << 'EOF'
% ECET 337 - Basic Analysis Script
% Author: [Your Name]
% Date: [Date]
% Description: [Purpose of this script]

clear all; close all; clc;

%% Define Parameters


%% Calculations


%% Results
fprintf('Results:\n');


%% Plots
figure;
% Add your plots here

grid on;
xlabel('');
ylabel('');
title('');
legend('');
EOF
            ;;
        2)
            cat > "$filepath" << 'EOF'
% ECET 337 - Transfer Function Analysis
% Author: [Your Name]
% Date: [Date]

clear all; close all; clc;

%% Define Transfer Function
num = [1];           % Numerator coefficients
den = [1 1];         % Denominator coefficients
H = tf(num, den);

fprintf('Transfer Function:\n');
H

%% Poles and Zeros
p = pole(H);
z = zero(H);
fprintf('Poles: ');
disp(p');
fprintf('Zeros: ');
disp(z');

%% Step Response
figure(1);
step(H);
grid on;
title('Step Response');

%% Frequency Response
figure(2);
bode(H);
grid on;
title('Bode Plot');
EOF
            ;;
        3)
            cat > "$filepath" << 'EOF'
% ECET 337 - Bode Plot Analysis
% Author: [Your Name]
% Date: [Date]

clear all; close all; clc;

%% Define Transfer Function
num = [1];
den = [1 1];
H = tf(num, den);

%% Bode Plot
figure;
bode(H);
grid on;

%% Get magnitude and phase at specific frequency
w = 2*pi*[0.1 1 10 100];  % Frequencies in rad/s
[mag, phase] = bode(H, w);

fprintf('Frequency Response:\n');
for i = 1:length(w)
    fprintf('f = %.2f Hz: Mag = %.2f dB, Phase = %.2f deg\n', ...
        w(i)/(2*pi), 20*log10(mag(i)), phase(i));
end
EOF
            ;;
        4)
            cat > "$filepath" << 'EOF'
% ECET 337 - Step Response Analysis
% Author: [Your Name]
% Date: [Date]

clear all; close all; clc;

%% Define System
num = [1];
den = [1 2 1];
H = tf(num, den);

%% Step Response
figure;
step(H);
grid on;
title('Step Response');
xlabel('Time (s)');
ylabel('Amplitude');

%% Get Step Response Parameters
info = stepinfo(H);

fprintf('Step Response Characteristics:\n');
fprintf('Rise Time: %.4f s\n', info.RiseTime);
fprintf('Settling Time: %.4f s\n', info.SettlingTime);
fprintf('Overshoot: %.2f %%\n', info.Overshoot);
fprintf('Peak: %.4f\n', info.Peak);
fprintf('Peak Time: %.4f s\n', info.PeakTime);
EOF
            ;;
        5)
            cat > "$filepath" << 'EOF'
% ECET 337 - Filter Design
% Author: [Your Name]
% Date: [Date]

clear all; close all; clc;

%% Filter Specifications
fc = 1000;           % Cutoff frequency (Hz)
n = 2;               % Filter order
type = 'low';        % 'low', 'high', 'bandpass', 'stop'

%% Design Filter
wc = 2*pi*fc;        % Convert to rad/s
[b, a] = butter(n, wc, type, 's');  % Analog filter
H = tf(b, a);

fprintf('Filter Transfer Function:\n');
H

%% Frequency Response
figure(1);
bode(H);
grid on;
title(sprintf('%d-Order Butterworth %s-Pass Filter (fc = %d Hz)', n, type, fc));

%% Step Response
figure(2);
step(H);
grid on;
title('Step Response');
EOF
            ;;
    esac

    echo -e "${GREEN}Template created: $filepath${NC}"
    echo "Opening in default editor..."
    ${EDITOR:-nano} "$filepath"
}

open_work_dir() {
    cd "$MATLAB_WORK"
    echo -e "${GREEN}Current directory: $MATLAB_WORK${NC}"
    echo ""
    echo "Files in working directory:"
    ls -lh *.m 2>/dev/null || echo "No MATLAB files yet"
}

list_recent() {
    echo -e "${GREEN}Recently modified MATLAB files:${NC}"
    find "$MATLAB_WORK" -name "*.m" -type f -mtime -7 -exec ls -lht {} \;
}

backup_work() {
    backup_dir="$COURSE_DIR/MATLAB_Backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    cp -r "$MATLAB_WORK"/* "$backup_dir/" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Backup created: $backup_dir${NC}"
    else
        echo -e "${YELLOW}No files to backup${NC}"
    fi
}

# Main loop
while true; do
    show_menu
    read choice

    case $choice in
        1) list_all_matlab ;;
        2) copy_to_work ;;
        3) search_matlab ;;
        4) categorize_files ;;
        5) create_template ;;
        6) open_work_dir ;;
        7) list_recent ;;
        8) backup_work ;;
        9) echo "Exiting..."; exit 0 ;;
        *) echo -e "${YELLOW}Invalid choice${NC}" ;;
    esac

    echo ""
    echo "Press Enter to continue..."
    read
done
