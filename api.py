from fastapi import FastAPI, UploadFile, File
import numpy as np
import io

app = FastAPI(title="Quantum Life Cloud API")

def compute_qls(rho_series):
    """
    Placeholder for your actual QLS computation logic.
    Should return:
      qls_raw: float (unscaled QLS value)
      components: dict or list of components (for analysis/visualization)
    """
    # Example dummy computation (replace with your actual physics logic)
    qls_raw = np.mean([np.trace(rho @ rho.conj().T).real for rho in rho_series])
    comps = {"num_samples": len(rho_series)}
    return qls_raw, comps


@app.post("/compute-qls")
async def compute_qls_api(file: UploadFile = File(...)):
    """
    Compute normalized Quantum Life Score (QLS) from uploaded density matrix data.
    Ensures the QLS is scaled between 0 and 1, returning both the score and components.
    """
    try:
        contents = await file.read()
        data = np.load(io.BytesIO(contents))
        rho_series = [data[k] for k in data.files]

        # Compute raw QLS
        qls_raw, comps = compute_qls(rho_series)

        # === NORMALIZATION FIX ===
        # Your raw numbers are about 0–3, so normalize by that range
        qls_norm = float(qls_raw) / 3.0
        qls_norm = max(0.0, min(1.0, qls_norm))  # Clamp to [0, 1]

        # Prediction interval ±0.15, clamped
        interval = [
            max(0.0, qls_norm - 0.15),
            min(1.0, qls_norm + 0.15)
        ]

        return {
            "QLS": qls_norm,
            "interval": interval,
            "components": comps,
            "debug_raw": qls_raw  # optional: to verify scaling
        }

    except Exception as e:
        return {"error": f"Failed to compute QLS: {str(e)}"}
