#!/bin/bash
# ECET 337 Quick Navigation and Helper Script
# Spring 2026

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

COURSE_DIR="/home/barney/School Work/Spring 2026/ECET 337"

# Function to display menu
show_menu() {
    clear
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   ECET 337 Course Navigation System${NC}"
    echo -e "${BLUE}   Continuous Systems Analysis & Design${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${GREEN}Quick Navigation:${NC}"
    echo "  1) Homework folder"
    echo "  2) Lab Exercises folder"
    echo "  3) Lectures folder"
    echo "  4) Course Info"
    echo "  5) Textbook"
    echo "  6) Mock Exams"
    echo ""
    echo -e "${GREEN}Current Week Tools:${NC}"
    echo "  7) Show current week assignments"
    echo "  8) Open assignment tracker"
    echo ""
    echo -e "${GREEN}Study Tools:${NC}"
    echo "  9) Find lecture by topic"
    echo " 10) Find lab by number"
    echo " 11) Quick reference guide"
    echo ""
    echo -e "${GREEN}MATLAB/Multisim:${NC}"
    echo " 12) List all MATLAB files"
    echo " 13) List all Multisim files"
    echo " 14) Open MATLAB file picker"
    echo ""
    echo " 15) Exit"
    echo ""
    echo -n "Enter choice: "
}

# Navigation functions
goto_homework() {
    cd "$COURSE_DIR/Homework"
    echo -e "${GREEN}Now in Homework folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier"
}

goto_labs() {
    cd "$COURSE_DIR/Lab Exercises"
    echo -e "${GREEN}Now in Lab Exercises folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier" | head -20
}

goto_lectures() {
    cd "$COURSE_DIR/Lectures"
    echo -e "${GREEN}Now in Lectures folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier" | head -20
}

goto_courseinfo() {
    cd "$COURSE_DIR/Course Info"
    echo -e "${GREEN}Now in Course Info folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier"
}

goto_textbook() {
    cd "$COURSE_DIR/Textbook"
    echo -e "${GREEN}Now in Textbook folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier"
}

goto_mockexams() {
    cd "$COURSE_DIR/Mock Exams"
    echo -e "${GREEN}Now in Mock Exams folder${NC}"
    ls -lh *.pdf 2>/dev/null | grep -v "Zone.Identifier"
}

# Current week function
show_current_week() {
    echo -e "${YELLOW}Current Week Assignments:${NC}"
    cat "$COURSE_DIR/current-week.txt" 2>/dev/null || echo "No current week data. Run update-week.sh"
}

# Find functions
find_lecture() {
    echo -n "Enter topic keyword: "
    read topic
    echo -e "${GREEN}Searching lectures for: $topic${NC}"
    find "$COURSE_DIR/Lectures" -iname "*$topic*" ! -name "*.Zone.Identifier" -type f
}

find_lab() {
    echo -n "Enter lab number (e.g., 01, 02): "
    read labnum
    echo -e "${GREEN}Searching for Lab $labnum:${NC}"
    find "$COURSE_DIR/Lab Exercises" -iname "*$labnum*" ! -name "*.Zone.Identifier" -type f
}

# List MATLAB/Multisim files
list_matlab() {
    echo -e "${GREEN}All MATLAB files (.m):${NC}"
    find "$COURSE_DIR" -name "*.m" ! -name "*.Zone.Identifier" -type f | sort
}

list_multisim() {
    echo -e "${GREEN}All Multisim files (.ms14, .ms12):${NC}"
    find "$COURSE_DIR" -name "*.ms14" -o -name "*.ms12" ! -name "*.Zone.Identifier" -type f | sort
}

# Main loop
while true; do
    show_menu
    read choice

    case $choice in
        1) goto_homework ;;
        2) goto_labs ;;
        3) goto_lectures ;;
        4) goto_courseinfo ;;
        5) goto_textbook ;;
        6) goto_mockexams ;;
        7) show_current_week ;;
        8) cat "$COURSE_DIR/assignment-tracker.md" 2>/dev/null || echo "No tracker found" ;;
        9) find_lecture ;;
        10) find_lab ;;
        11) cat "$COURSE_DIR/quick-reference.md" 2>/dev/null || echo "No reference found" ;;
        12) list_matlab ;;
        13) list_multisim ;;
        14) echo "Opening MATLAB file picker..."; list_matlab ;;
        15) echo "Exiting..."; exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac

    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
done
