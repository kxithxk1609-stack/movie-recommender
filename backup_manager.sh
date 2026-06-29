#!/bin/bash

# ============================================
# MOVIE RECOMMENDER - BACKUP & RESTORE
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

clear
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🎬 MOVIE RECOMMENDER BACKUP TOOL${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "1) 📤 Create Backup"
echo "2) 📥 Restore from Backup"
echo "3) 📋 View Backups"
echo "4) 🚪 Exit"
echo ""
echo -e "${YELLOW}Choose option (1-4):${NC}"
read choice

case $choice in
    1)
        echo -e "\n${BLUE}Creating backup...${NC}"
        TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
        
        # Backup app.py
        if [ -f "app.py" ]; then
            cp app.py "$BACKUP_DIR/app_backup_$TIMESTAMP.py"
            echo -e "${GREEN}✅ app.py backed up${NC}"
        else
            echo -e "${RED}❌ app.py not found${NC}"
        fi
        
        # Backup index.html
        if [ -f "templates/index.html" ]; then
            cp templates/index.html "$BACKUP_DIR/index_backup_$TIMESTAMP.html"
            echo -e "${GREEN}✅ index.html backed up${NC}"
        else
            echo -e "${RED}❌ index.html not found${NC}"
        fi
        
        # Backup users.json if exists
        if [ -f "users.json" ]; then
            cp users.json "$BACKUP_DIR/users_backup_$TIMESTAMP.json"
            echo -e "${GREEN}✅ users.json backed up${NC}"
        fi
        
        echo -e "\n${GREEN}✅ Backup Complete!${NC}"
        echo -e "${YELLOW}📁 Saved in:${NC} $BACKUP_DIR/"
        ;;
        
    2)
        echo -e "\n${BLUE}Available backups:${NC}"
        echo -e "${YELLOW}----------------------------------------${NC}"
        
        # List app.py backups
        echo -e "\n${GREEN}📄 app.py backups:${NC}"
        ls -lt "$BACKUP_DIR"/app_backup_*.py 2>/dev/null | head -5 || echo "No app.py backups found"
        
        # List index.html backups
        echo -e "\n${GREEN}📄 index.html backups:${NC}"
        ls -lt "$BACKUP_DIR"/index_backup_*.html 2>/dev/null | head -5 || echo "No index.html backups found"
        
        # List users.json backups
        echo -e "\n${GREEN}📄 users.json backups:${NC}"
        ls -lt "$BACKUP_DIR"/users_backup_*.json 2>/dev/null | head -5 || echo "No users.json backups found"
        
        echo -e "\n${YELLOW}----------------------------------------${NC}"
        echo ""
        echo "1) Restore app.py"
        echo "2) Restore index.html"
        echo "3) Restore users.json"
        echo "4) Restore ALL (latest versions)"
        echo "5) Cancel"
        echo ""
        echo -e "${YELLOW}Choose option:${NC}"
        read restore_choice
        
        case $restore_choice in
            1)
                LATEST=$(ls -t "$BACKUP_DIR"/app_backup_*.py 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" app.py
                    echo -e "${GREEN}✅ Restored:${NC} app.py from $(basename "$LATEST")"
                else
                    echo -e "${RED}❌ No app.py backup found!${NC}"
                fi
                ;;
            2)
                LATEST=$(ls -t "$BACKUP_DIR"/index_backup_*.html 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" templates/index.html
                    echo -e "${GREEN}✅ Restored:${NC} index.html from $(basename "$LATEST")"
                else
                    echo -e "${RED}❌ No index.html backup found!${NC}"
                fi
                ;;
            3)
                LATEST=$(ls -t "$BACKUP_DIR"/users_backup_*.json 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" users.json
                    echo -e "${GREEN}✅ Restored:${NC} users.json from $(basename "$LATEST")"
                else
                    echo -e "${RED}❌ No users.json backup found!${NC}"
                fi
                ;;
            4)
                # Restore app.py
                LATEST=$(ls -t "$BACKUP_DIR"/app_backup_*.py 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" app.py
                    echo -e "${GREEN}✅ Restored:${NC} app.py"
                fi
                
                # Restore index.html
                LATEST=$(ls -t "$BACKUP_DIR"/index_backup_*.html 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" templates/index.html
                    echo -e "${GREEN}✅ Restored:${NC} index.html"
                fi
                
                # Restore users.json
                LATEST=$(ls -t "$BACKUP_DIR"/users_backup_*.json 2>/dev/null | head -1)
                if [ -f "$LATEST" ]; then
                    cp "$LATEST" users.json
                    echo -e "${GREEN}✅ Restored:${NC} users.json"
                fi
                
                echo -e "\n${GREEN}✅ All files restored to latest versions!${NC}"
                ;;
            5)
                echo -e "${YELLOW}❌ Canceled${NC}"
                ;;
            *)
                echo -e "${RED}❌ Invalid choice!${NC}"
                ;;
        esac
        ;;
        
    3)
        echo -e "\n${BLUE}📂 All Backups:${NC}"
        echo -e "${YELLOW}========================================${NC}"
        ls -lht "$BACKUP_DIR" | head -15
        echo -e "${YELLOW}========================================${NC}"
        ;;
        
    4)
        echo -e "${GREEN}👋 Goodbye!${NC}"
        exit 0
        ;;
        
    *)
        echo -e "${RED}❌ Invalid option!${NC}"
        ;;
esac

echo -e "\n${YELLOW}Press Enter to exit...${NC}"
read