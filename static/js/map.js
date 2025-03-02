// Update the map.js file with enhanced functionality

let map
let markers = []
let currentDay = 0
let polyline = null
let mapData = null
let nearbyTravelers = []

function initMap() {
  try {
    // Check if Leaflet is loaded
    if (typeof L === "undefined") {
      console.error("Leaflet library not loaded")
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

    // Fetch map data from server
    fetchMapData()

    // Log success
    console.log("Map initialized successfully")
  } catch (error) {
    console.error("Error initializing map:", error)
  }
}

async function fetchMapData() {
  try {
    const tripId = new URLSearchParams(window.location.search).get("trip_id")
    if (!tripId) return

    const response = await fetch(`/api/map_data/${tripId}`)
    const data = await response.json()

    if (data.success) {
      mapData = data.mapData
      nearbyTravelers = data.nearbyTravelers
      updateMap()
      updateTimeline()
      updateNearbyTravelersList()
    }
  } catch (error) {
    console.error("Error fetching map data:", error)
  }
}

function updateMap() {
  try {
    // Clear existing markers and polyline
    markers.forEach((marker) => map.removeLayer(marker))
    markers = []
    if (polyline) map.removeLayer(polyline)

    if (!mapData || !mapData.days || !mapData.days[currentDay]) return

    const places = mapData.days[currentDay].places
    const coordinates = places.map((place) => [place.lat, place.lng])

    // Add markers for each place
    places.forEach((place, index) => {
      const marker = L.marker([place.lat, place.lng], {
        icon: L.divIcon({
          className: "custom-marker",
          html: `<div class="marker-content">${index + 1}</div>`,
          iconSize: [32, 32],
        }),
      })
        .addTo(map)
        .bindPopup(createPopupContent(place))

      markers.push(marker)
    })

    // Draw route line between places
    polyline = L.polyline(coordinates, {
      color: "var(--primary)",
      weight: 3,
      opacity: 0.7,
      dashArray: "10, 10",
      lineCap: "round",
    }).addTo(map)

    // Fit map bounds to show all markers
    if (markers.length > 0) {
      const bounds = L.latLngBounds(coordinates)
      map.fitBounds(bounds, { padding: [50, 50] })
    }

    // Update the day display
    updateDayDisplay()
  } catch (error) {
    console.error("Error updating map:", error)
  }
}

function createPopupContent(place) {
  return `
        <div class="popup-content">
            <img src="${place.image}" alt="${place.name}" class="popup-image">
            <h3>${place.name}</h3>
            <p class="popup-time">${place.time}</p>
            <p class="popup-description">${place.description}</p>
            <div class="popup-rating">
                <i class="fas fa-star"></i>
                <span>${place.rating.toFixed(1)}</span>
            </div>
            <button onclick="showNearbyTravelers('${place.name}')" class="popup-button">
                <i class="fas fa-users"></i>
                View Nearby Travelers
            </button>
        </div>
    `
}

function updateTimeline() {
  if (!mapData || !mapData.days || !mapData.days[currentDay]) return

  const planList = document.getElementById("plan-list")
  planList.innerHTML = ""

  const places = mapData.days[currentDay].places
  places.forEach((place, index) => {
    const timelineItem = document.createElement("div")
    timelineItem.className = `timeline-item ${index === places.length - 1 ? "future" : ""}`
    timelineItem.innerHTML = `
            <div class="timeline-content">
                <div class="timeline-time">
                    <i class="fas fa-clock"></i>
                    ${place.time}
                </div>
                <div class="timeline-place">${place.name}</div>
                <div class="timeline-details">${place.description}</div>
                <button onclick="showNearbyTravelers('${place.name}')" class="timeline-button">
                    <i class="fas fa-users"></i>
                    Find Travel Buddies
                </button>
            </div>
        `
    planList.appendChild(timelineItem)
  })

  // Set timeline progress
  const progress = (100 * (places.length - 1)) / places.length
  document.querySelector(".timeline").style.setProperty("--progress", `${progress}%`)
}

function updateDayDisplay() {
  if (!mapData || !mapData.days || !mapData.days[currentDay]) return

  const dayData = mapData.days[currentDay]
  document.getElementById("current-day").textContent = `Day ${currentDay + 1}`
  document.getElementById("current-date").textContent = dayData.date
}

function updateNearbyTravelersList() {
  // This function is intentionally left blank.
  // It serves as a placeholder for future functionality related to updating the nearby travelers list.
}

function showNearbyTravelers(placeName) {
  const travelers = nearbyTravelers.filter((t) => t.places.includes(placeName))
  const userList = document.getElementById("user-list")
  userList.innerHTML = ""

  if (travelers.length === 0) {
    userList.innerHTML = `
            <div class="no-travelers">
                <i class="fas fa-user-friends"></i>
                <p>No travelers found at this location during your dates.</p>
                <button onclick="expandSearch('${placeName}')" class="expand-search">
                    Search Nearby Dates
                </button>
            </div>
        `
  } else {
    travelers.forEach((traveler) => {
      const userCard = document.createElement("div")
      userCard.className = "user-card"
      userCard.innerHTML = `
                <div class="user-avatar">
                    <img src="${traveler.profile_image || "/placeholder.svg?height=48&width=48"}" 
                         alt="${traveler.name}">
                </div>
                <div class="user-info">
                    <h4>${traveler.name}</h4>
                    <p>${traveler.dates}</p>
                    <div class="user-interests">
                        ${traveler.interests
                          .map((interest) => `<span class="interest-tag">${interest}</span>`)
                          .join("")}
                    </div>
                </div>
                <button class="connect-btn" onclick="connectWithTraveler(${traveler.id})">
                    Connect
                </button>
            `
      userList.appendChild(userCard)
    })
  }

  document.getElementById("place-name").textContent = placeName
  document.getElementById("user-popup").style.display = "block"
}

async function connectWithTraveler(travelerId) {
  try {
    const response = await fetch("/api/connect", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ traveler_id: travelerId }),
    })

    const data = await response.json()
    if (data.success) {
      alert("Connection request sent successfully!")
    } else {
      alert("Failed to send connection request. Please try again.")
    }
  } catch (error) {
    console.error("Error connecting with traveler:", error)
    alert("An error occurred. Please try again.")
  }
}

async function expandSearch(placeName) {
  try {
    const response = await fetch(`/api/expand_search?place=${encodeURIComponent(placeName)}`)
    const data = await response.json()
    if (data.travelers) {
      nearbyTravelers = data.travelers
      showNearbyTravelers(placeName)
    }
  } catch (error) {
    console.error("Error expanding search:", error)
  }
}

// Event Listeners
document.getElementById("prev-day").addEventListener("click", () => {
  if (currentDay > 0) {
    currentDay--
    updateMap()
    updateTimeline()
  }
})

document.getElementById("next-day").addEventListener("click", () => {
  if (mapData && mapData.days && currentDay < mapData.days.length - 1) {
    currentDay++
    updateMap()
    updateTimeline()
  }
})

document.getElementById("close-popup").addEventListener("click", () => {
  document.getElementById("user-popup").style.display = "none"
})

// Initialize map when DOM is loaded
document.addEventListener("DOMContentLoaded", initMap)

