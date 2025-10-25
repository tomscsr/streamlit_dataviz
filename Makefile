# Makefile for France's Vacant Housing Dashboard
# Simple commands to run the application

.PHONY: help install run clean test

help:
	@echo "Available commands:"
	@echo "  make install    - Install required Python packages"
	@echo "  make run        - Run the Streamlit dashboard"
	@echo "  make clean      - Remove Python cache files"
	@echo "  make test       - Run basic data validation checks"

install:
	pip install -r requirements.txt

run:
	streamlit run app.py

clean:
	@echo "Cleaning Python cache files..."
	@powershell -Command "Get-ChildItem -Path . -Include __pycache__,*.pyc,*.pyo -Recurse | Remove-Item -Force -Recurse"
	@echo "Clean complete!"

test:
	@echo "Running basic validation..."
	@python -c "from utils.io import load_department_data, load_commune_data; df_d = load_department_data(); df_c = load_commune_data(); print(f'✓ Department data: {len(df_d)} rows'); print(f'✓ Commune data: {len(df_c)} rows'); print('✓ All checks passed!')"

# Quick start for first-time users
quickstart:
	@echo "Setting up France's Vacant Housing Dashboard..."
	pip install -r requirements.txt
	@echo ""
	@echo "Setup complete! Run 'make run' to start the dashboard."
