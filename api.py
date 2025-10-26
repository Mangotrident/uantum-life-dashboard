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
        # Load numpy data from uploaded .npz or .npy file
        contents = await file.read()
        data = np.load(io.BytesIO(contents))
        rho_series = [data[k] for k in data.files]

        # Compute raw QLS
        qls_raw, comps = compute_qls(rho_series)

        # === NORMALIZATION FIX ===
        # Adjust these min/max based on your training data or theoretical range
        QLS_MIN, QLS_MAX = 0.0, 3.0   # assuming your raw QLS ranged roughly 0–3
        qls_norm = (qls_raw - QLS_MIN) / (QLS_MAX - QLS_MIN)
        qls_norm = max(0.0, min(1.0, qls_norm))  # clamp to [0,1]

        # 90% prediction interval (±0.15, also clamped)
        interval = [
            max(0.0, qls_norm - 0.15),
            min(1.0, qls_norm + 0.15)
        ]

        return {
            "QLS": float(qls_norm),
            "interval": interval,
            "components": comps
        }

    except Exception as e:
        return {"error": f"Failed to compute QLS: {str(e)}"}
