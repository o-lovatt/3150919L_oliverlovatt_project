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
import SpeciesInfoPanel from './components/SpeciesInfoPanel'

// [STUDENT-WRITTEN]
function App() {
  //refactored, now only called once
  const { predictions, loading } = usePredictions()

  //track with view is active
  const [activeTab, setActiveTab] = useState("location")

  //for sidebar
  const [selectedSpecies, setSelectedSpecies] = useState(null)

  //navigation tabs
  return (
    <div className="h-dvh bg-cream flex flex-col md:flex-row overflow-y-auto">
      <div className="flex-1 flex flex-col">
        <div className="flex gap-1 px-4 pt-4 pb-2">
          <button onClick={() => {
            setActiveTab("location")
            setSelectedSpecies(null)
          }}
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

        <div className="flex-1">
          {activeTab === "location" ? (
            <LocationPredictions predictions = {predictions} setSelectedSpecies = {setSelectedSpecies}/>
          ) : (
          <SpeciesMap
            predictions={predictions}
            selectedSpecies={selectedSpecies}
            setSelectedSpecies={setSelectedSpecies}
            />
          )}
        </div>
      </div>

      {/* only render sidebar when selecteSpecies has a value*/}
        {selectedSpecies && (
          <div className="w-full md:w-80 bg-cream">
            <SpeciesInfoPanel speciesName={selectedSpecies}/>
          </div>
        )}
      </div>
    )
  }

//removed old test blocks

export default App
