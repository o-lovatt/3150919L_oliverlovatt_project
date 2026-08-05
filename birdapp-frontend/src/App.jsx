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
    <div className="min-h-screen bg-cream p-4">
      <div className="flex gap-1 mb-1">
        <button onClick={() => setActiveTab("location")} 
        className={`px-4 py-2 rounded ${activeTab ==="location" ? "bg-forest text-cream" : "bg-cream text-charcoal border border-bark"}`}
        aria-label = "Find nearby birds in your location"
        >
          Location
        </button>
        <button onClick={() => setActiveTab("species")}
        className={`px-4 py-2 rounded ${activeTab ==="species" ? "bg-forest text-cream" : "bg-cream text-charcoal border border-bark"}`}
        aria-label = "Find sighting locations based on a specific species"
        >
          Species
        </button>
      </div>
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
