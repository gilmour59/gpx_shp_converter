#!/bin/bash
cd "$(dirname "$0")"
chmod +x "./GPX_SHP_Converter"
open "http://localhost:8501" >/dev/null 2>&1 &
exec "./GPX_SHP_Converter"
