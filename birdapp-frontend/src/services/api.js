//[STUDENT-WRITTEN]

const API_BASE_URL = `https://${window.location.hostname}:8000/api`; //prob need to change this later when deployed

export async function fetchVersion() {
    const response = await fetch(`${API_BASE_URL}/version/`);
    const data = await response.json();
    return data;
}

export async function fetchPredictions() {
    const predictions = await fetch(`${API_BASE_URL}/predictions/export/`);
    const prediction_data = await predictions.json();
    return prediction_data;
}