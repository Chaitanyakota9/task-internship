#!/bin/bash

echo "🧪 Running Tests..."
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate
fi

pytest

echo ""
echo "✅ Done!"
