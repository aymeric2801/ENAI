#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "  Ad Campaign Analytics Dashboard"
echo "  avec Integration Publicitaire"
echo "========================================"
echo ""

echo -e "${BLUE}[1/3] Verification des dependances Python...${NC}"
if ! pip show streamlit > /dev/null 2>&1; then
    echo "Installation de Streamlit..."
    pip install streamlit pandas numpy plotly
fi
echo -e "${GREEN}OK${NC}"

echo ""
echo -e "${BLUE}[2/3] Lancement de l'application Streamlit...${NC}"
streamlit run app.py --server.port 8501 --server.headless true &
STREAMLIT_PID=$!

echo ""
echo -e "${BLUE}[3/3] Attente du demarrage de Streamlit...${NC}"
sleep 5

echo ""
echo "Ouverture de la page web avec les ad units..."
if command -v google-chrome > /dev/null; then
    google-chrome index.html
elif command -v firefox > /dev/null; then
    firefox index.html
else
    open index.html
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Application lancee avec succes!${NC}"
echo -e "${GREEN}  - Streamlit: http://localhost:8501${NC}"
echo -e "${GREEN}  - Page web: index.html${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Appuyez sur Ctrl+C pour arreter Streamlit"

# Attendre que l'utilisateur tue le processus
wait $STREAMLIT_PID