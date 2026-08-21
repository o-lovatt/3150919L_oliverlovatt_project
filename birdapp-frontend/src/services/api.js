//[STUDENT-WRITTEN]

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8000/api`;

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

export async function fetchRecentSightings(lat, lon){
    const sightings = await fetch(`${API_BASE_URL}/recent-sightings/?lat=${lat}&lon=${lon}`); //[AI-GENERATED - Claude AI 13-08-2026]
    const sighting_data = await sightings.json();
    return sighting_data;
}

export async function fetchSpeciesRecentSightings(speciesCode){
    const species_sightings = await fetch(`${API_BASE_URL}/species-recent-sightings/?species_code=${speciesCode}`);
    const species_sighting_data = await species_sightings.json();
    return species_sighting_data
}