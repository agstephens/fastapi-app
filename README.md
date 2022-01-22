# All this in a YouTube video

https://www.youtube.com/watch?v=kCggyi_7pHg

Create: app.py

 hypercorn main:app --reload --bind 0.0.0.0:8999

Or

Create: ceda_moles.py

 hypercorn ceda_moles:app --reload --bind 0.0.0.0:8999

Create: meta-wps.py

 hypercorn meta-wps:app --reload --bind 0.0.0.0:8998

## Dependencies

pip install hypercorn requests fastapi

