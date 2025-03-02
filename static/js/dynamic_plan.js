const dummyPlaces = [
  {
    name: "Central Park",
    lat: 40.7829,
    lng: -73.9654,
    description:
      "Iconic urban park with various attractions including the Belvedere Castle, Bethesda Fountain, and Central Park Zoo.",
    image: "/placeholder.svg?height=200&width=300",
    rating: 4.8,
    highlights: ["Bethesda Fountain", "Belvedere Castle", "The Lake"],
    activities: ["Walking Tours", "Boating", "Zoo Visit"],
  },
  {
    name: "Metropolitan Museum of Art",
    lat: 40.7794,
    lng: -73.9632,
    description:
      "One of the world's largest and most comprehensive art museums, featuring over 2 million works of art.",
    image: "/placeholder.svg?height=200&width=300",
    rating: 4.9,
    highlights: ["Egyptian Collection", "European Paintings", "Rooftop Garden"],
    activities: ["Guided Tours", "Art Workshops", "Rooftop Views"],
  },
  {
    name: "Times Square",
    lat: 40.758,
    lng: -73.9855,
    description: "Iconic intersection known for its bright lights, Broadway theaters, and vibrant atmosphere.",
    image: "/placeholder.svg?height=200&width=300",
    rating: 4.6,
    highlights: ["Broadway Theaters", "TKTS Booth", "Street Performances"],
    activities: ["Shopping", "Theater Shows", "Photo Ops"],
  },
  {
    name: "Statue of Liberty",
    lat: 40.6892,
    lng: -74.0445,
    description: "Iconic symbol of freedom and democracy, offering harbor views and historical exhibits.",
    image: "/placeholder.svg?height=200&width=300",
    rating: 4.7,
    highlights: ["Crown Access", "Ellis Island", "Harbor Views"],
    activities: ["Guided Tours", "Museum Visit", "Ferry Ride"],
  },
  {
    name: "Empire State Building",
    lat: 40.7484,
    lng: -73.9857,
    description: "Historic 102-story skyscraper with observation decks offering panoramic city views.",
    image: "/placeholder.svg?height=200&width=300",
    rating: 4.8,
    highlights: ["Observation Deck", "Art Deco Lobby", "Night Views"],
    activities: ["Observation", "Historical Tour", "Photography"],
  },
]

let map
let currentPlace
const acceptedPlaces = []
const markers = []
let currentMarker = null
let routeLine = null

function initMap() {
  try {
    // Check if Leaflet is loaded
    if (typeof L === "undefined") {
      console.error("Leaflet library not loaded")
      return
    }

    // Check if container exists
    const container = document.getElementById("map")
    if (!container) {
      console.error("Map container not found")
      return
    }

    // Initialize map
    map = L.map("map", {
      zoomControl: false,
    }).setView([40.7128, -74.006], 12)

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(map)

    L.control
      .zoom({
        position: "topright",
      })
      .addTo(map)

    // Log success
    console.log("Map initialized successfully")

    // Show the first place
    showNextPlace()
  } catch (error) {
    console.error("Error initializing map:", error)
  }
}

function showNextPlace() {
  if (currentMarker) {
    map.removeLayer(currentMarker)
  }

  if (dummyPlaces.length > 0) {
    currentPlace = dummyPlaces.shift()

    // Update place details with animation
    const placeCard = document.getElementById("current-place")
    placeCard.style.opacity = "0"

    setTimeout(() => {
      document.getElementById("place-name").textContent = currentPlace.name
      document.getElementById("place-description").textContent = currentPlace.description
      document.getElementById("place-image").src = currentPlace.image
      document.getElementById("place-rating").textContent = currentPlace.rating.toFixed(1)

      // Add highlights and activities
      const detailsHtml = `
        <div class="place-highlights">
          <h4>Highlights</h4>
          <div class="tags">
            ${currentPlace.highlights.map((h) => `<span class="tag">${h}</span>`).join("")}
          </div>
        </div>
        <div class="place-activities">
          <h4>Activities</h4>
          <div class="tags">
            ${currentPlace.activities.map((a) => `<span class="tag">${a}</span>`).join("")}
          </div>
        </div>
      `

      document.querySelector(".place-details").insertAdjacentHTML("beforeend", detailsHtml)

      placeCard.style.opacity = "1"
    }, 300)

    // Add marker to map with animation
    currentMarker = L.marker([currentPlace.lat, currentPlace.lng], {
      icon: L.divIcon({
        className: "custom-marker preview",
        html: `<div class="marker-content">?</div>`,
        iconSize: [32, 32],
      }),
    }).addTo(map)

    map.flyTo([currentPlace.lat, currentPlace.lng], 14, {
      duration: 1.5,
      easeLinearity: 0.25,
    })

    // Update route if there are accepted places
    updateRoute()

    // Update timeline
    updateTimeline()
  } else {
    showCompletionMessage()
  }
}

function updateRoute() {
  if (routeLine) {
    map.removeLayer(routeLine)
  }

  if (acceptedPlaces.length > 0) {
    const coordinates = acceptedPlaces.map((place) => [place.lat, place.lng])
    if (currentPlace) {
      coordinates.push([currentPlace.lat, currentPlace.lng])
    }

    routeLine = L.polyline(coordinates, {
      color: "var(--primary)",
      weight: 3,
      opacity: 0.7,
      dashArray: "10, 10",
    }).addTo(map)
  }
}

function updateTimeline() {
  const timelineContainer = document.getElementById("selected-places-list")
  timelineContainer.innerHTML = ""

  acceptedPlaces.forEach((place, index) => {
    const timelineItem = document.createElement("div")
    timelineItem.className = "timeline-item"
    timelineItem.innerHTML = `
      <div class="timeline-content">
        <div class="timeline-time">
          <i class="fas fa-clock"></i>
          ${calculateTimeSlot(index, place.timeSpent)}
        </div>
        <div class="timeline-place">${place.name}</div>
        <div class="timeline-details">
          <div class="tags">
            ${place.highlights
              .slice(0, 2)
              .map((h) => `<span class="tag">${h}</span>`)
              .join("")}
          </div>
        </div>
      </div>
    `
    timelineContainer.appendChild(timelineItem)
  })
}

function showCompletionMessage() {
  const placeCard = document.querySelector(".place-card")
  placeCard.innerHTML = `
    <div class="completion-message">
      <i class="fas fa-check-circle"></i>
      <h2>Day Planning Complete!</h2>
      <p>You've added ${acceptedPlaces.length} places to your itinerary.</p>
      <div class="completion-stats">
        <div class="stat">
          <span class="stat-value">${acceptedPlaces.length}</span>
          <span class="stat-label">Places</span>
        </div>
        <div class="stat">
          <span class="stat-value">${calculateTotalTime()}</span>
          <span class="stat-label">Hours</span>
        </div>
      </div>
      <button onclick="finishPlanning()" class="btn-end">
        <i class="fas fa-map-marked-alt"></i>
        View on Map
      </button>
    </div>
  `
}

function calculateTotalTime() {
  return acceptedPlaces.reduce((total, place) => total + Number.parseFloat(place.timeSpent), 0)
}

function calculateTimeSlot(index, duration) {
  const startTime = new Date()
  startTime.setHours(9, 0, 0) // Start at 9 AM

  // Add previous durations
  for (let i = 0; i < index; i++) {
    startTime.setHours(startTime.getHours() + Number.parseInt(acceptedPlaces[i].timeSpent))
  }

  const endTime = new Date(startTime)
  endTime.setHours(startTime.getHours() + Number.parseInt(duration))

  return `${formatTime(startTime)} - ${formatTime(endTime)}`
}

function formatTime(date) {
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

// Update the finishPlanning function
function finishPlanning() {
  const loadingOverlay = document.createElement("div")
  loadingOverlay.className = "loading-overlay"
  loadingOverlay.innerHTML = `
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <p>Generating your itinerary...</p>
    </div>
  `
  document.body.appendChild(loadingOverlay)

  // Convert accepted places to the format expected by the backend
  const places = acceptedPlaces.map((place) => ({
    name: place.name,
    description: place.description,
    time: calculateTimeSlot(0, place.timeSpent),
    timeSpent: place.timeSpent,
    address: place.address || `${place.name}, New York, NY`, // Add default address if none provided
  }))

  // Send to backend
  fetch("/finalize_trip", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      dynamic_plan: true,
      places: places,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.body.removeChild(loadingOverlay)
      if (data.finalized) {
        window.location.href = `/view_itinerary?trip_id=${data.trip_id}`
      } else {
        alert("Failed to generate itinerary. Please try again.")
      }
    })
    .catch((error) => {
      console.error("Error:", error)
      document.body.removeChild(loadingOverlay)
      alert("An error occurred. Please try again.")
    })
}

// Add custom styles for new elements
const style = document.createElement("style")
style.textContent = `
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 0.5rem 0;
  }

  .tag {
    background: var(--primary-light);
    color: var(--primary);
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
  }

  .completion-message {
    text-align: center;
    padding: 2rem;
  }

  .completion-message i {
    font-size: 4rem;
    color: var(--primary);
    margin-bottom: 1rem;
  }

  .completion-stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 1.5rem 0;
  }

  .stat {
    text-align: center;
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 600;
    color: var(--primary);
    display: block;
  }

  .stat-label {
    color: var(--text-light);
    font-size: 0.875rem;
  }

  .custom-marker.preview {
    background: var(--primary-light);
    border-color: var(--primary);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }
`
document.head.appendChild(style)

// Event Listeners
document.getElementById("accept-place").addEventListener("click", () => {
  const timeSpent = document.getElementById("time-spent").value
  const travelDistance = document.getElementById("travel-distance").value

  acceptedPlaces.push({
    ...currentPlace,
    timeSpent,
    travelDistance,
  })

  // Update current marker to accepted style
  if (currentMarker) {
    map.removeLayer(currentMarker)
    const marker = L.marker([currentPlace.lat, currentPlace.lng], {
      icon: L.divIcon({
        className: "custom-marker",
        html: `<div class="marker-content">${acceptedPlaces.length}</div>`,
        iconSize: [32, 32],
      }),
    }).addTo(map)
    markers.push(marker)
  }

  showNextPlace()
})

document.getElementById("reject-place").addEventListener("click", showNextPlace)

document.getElementById("end-day").addEventListener("click", () => {
  if (acceptedPlaces.length > 0) {
    finishPlanning()
  } else {
    alert("Please add at least one place to your plan before finishing.")
  }
})

// Make initMap available globally
window.initMap = initMap

// Remove the window.onload event listener, as we're now calling initMap from the HTML

