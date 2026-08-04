import { useState } from 'react'
import reactLogo from './assets/react.svg' //will need these later
import viteLogo from './assets/vite.svg' //will need these later
import heroImg from './assets/hero.png' //might need this later??
import './App.css'
import { useEffect } from 'react';
import { usePredictions } from './hooks/usePredictions'
import { getPredictionsForLocation } from './utils/getPredictionsForLocation'
import LocationPredictions from './components/LocationPredictions'
import SpeciesMap from './components/SpeciesMap'

// [STUDENT-WRITTEN]
function App() {
  //refactored, now only called once
  const { predictions, loading } = usePredictions()

  //track with view is active
  const [activeTab, setActiveTab] = useState("location")

  //navigation tabs
  return (
    <div>
      <button onClick={() => setActiveTab("location")} aria-label = "Find nearby birds based on your location">
        Location
      </button>
      <button onClick={() => setActiveTab("species")} aria-label = "Find sighting locations based on a specific species">
        Species
      </button>

      {activeTab === "location" ? (
        <LocationPredictions predictions = {predictions} />
      ) : (
      <SpeciesMap predictions = {predictions} />
      )}
    </div>
  )
}

//removed old test blocks

export default App
