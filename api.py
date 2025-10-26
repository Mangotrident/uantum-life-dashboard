from fastapi import FastAPI, UploadFile, File
import numpy as np, io
from qli.metrics import compute_qls

app = FastAPI(title="Quantum Life Cloud API")

@app.post("/compute-qls")
async def compute_qls_api(file: UploadFile = File(...)):
    data = np.load(io.BytesIO(await file.read()))
    rho_series = [data[k] for k in data.files]
    qls, comps = compute_qls(rho_series)
    return {"qls": float(qls), "components": comps}
