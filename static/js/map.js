// Update the map.js file with enhanced functionality
let map
let markers = []
let currentDay = 0
let polyline = null
let mapData = null
let nearbyTravelers = []

function initMap(initialMapData) {
  try {
    // Check if Leaflet is loaded
    if (typeof L === "undefined") {
      console.error("Leaflet library not loaded")
      return
    }

    // Store the map data
    if (initialMapData) {
      mapData = initialMapData
      console.log("Received map data:", mapData)
    }

    // Initialize map with default center
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

    // If we have map data, update the map immediately
    if (mapData) {
      updateMap()
      updateTimeline()
      updateNearbyTravelersList()
    } else {
      // Otherwise, fetch map data from server
      fetchMapData()
    }

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

    if (!mapData || !mapData.days || !mapData.days[currentDay]) {
      console.error("No map data available for current day:", currentDay)
      return
    }

    console.log("Updating map with data:", mapData.days[currentDay])

    const places = mapData.days[currentDay].places
    const coordinates = places.map((place) => [place.lat, place.lng])

    // Add markers for each place
    places.forEach((place, index) => {
      console.log("Adding marker for place:", place)
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
    if (coordinates.length > 1) {
      polyline = L.polyline(coordinates, {
        color: "var(--primary)",
        weight: 3,
        opacity: 0.7,
        dashArray: "10, 10",
        lineCap: "round",
      }).addTo(map)
    }

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

// Update the createPopupContent function to remove the popup button
function createPopupContent(place) {
  return `
    <div class="popup-content">
      <img src="${place.image}" alt="${place.name}" class="popup-image">
      <h3>${place.name}</h3>
      <p class="popup-time">${place.time}</p>
      <p class="popup-description">${place.description || ""}</p>
      ${
        place.rating
          ? `
        <div class="popup-rating">
          <i class="fas fa-star"></i>
          <span>${place.rating.toFixed(1)}</span>
        </div>
      `
          : ""
      }
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
        <div class="timeline-details">${place.description || ""}</div>
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
  const peopleList = document.getElementById("people-list")
  if (!peopleList) return

  if (!mapData || !mapData.days || !mapData.days[currentDay]) {
    peopleList.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-users"></i>
        <p>No travelers found nearby</p>
      </div>
    `
    return
  }

  const places = mapData.days[currentDay].places
  let travelers = []

  places.forEach((place) => {
    if (place.visitors && place.visitors.length > 0) {
      travelers = travelers.concat(
        place.visitors.map((visitor) => ({
          ...visitor,
          place: place.name,
          time: place.time,
        })),
      )
    }
  })

  if (travelers.length === 0) {
    peopleList.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-users"></i>
        <p>No travelers found nearby</p>
      </div>
    `
    return
  }

  peopleList.innerHTML = travelers
    .map(
      (traveler) => `
    <div class="person-card">
      <div class="person-avatar">
        ${traveler.profile_image ? `<img src="${traveler.profile_image}" alt="${traveler.name}">` : traveler.name[0]}
      </div>
      <div class="person-info">
        <div class="person-name">${traveler.name}</div>
        <div class="person-time">${traveler.time} at ${traveler.place}</div>
      </div>
      <button class="connect-btn" onclick="requestContact(${traveler.id})">
        <i class="fas fa-envelope"></i>
      </button>
    </div>
  `,
    )
    .join("")
}

async function requestContact(travelerId) {
  try {
    const response = await fetch("/api/request_contact", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ traveler_id: travelerId }),
    })

    const data = await response.json()
    if (data.success) {
      alert(
        "Contact request sent successfully! The traveler will receive an email to approve sharing their contact details.",
      )
    } else {
      alert(data.error || "Failed to send contact request. Please try again.")
    }
  } catch (error) {
    console.error("Error requesting contact:", error)
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

// Update the map.js file to handle showing travelers in the right column
function showNearbyTravelers(placeName) {
  const peopleList = document.getElementById("people-list")
  const travelersAtPlace = nearbyTravelers.filter((traveler) => traveler.place === placeName)

  if (travelersAtPlace.length === 0) {
    peopleList.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-users"></i>
        <p>No travelers found at ${placeName}</p>
      </div>
    `
    return
  }

  peopleList.innerHTML = travelersAtPlace
    .map(
      (traveler) => `
    <div class="person-card" onclick="toggleContactRequest(this, ${traveler.id})">
      <div class="person-card-content">
        <div class="person-avatar">
          ${traveler.profile_image ? `<img src="${traveler.profile_image}" alt="${traveler.name}">` : traveler.name[0]}
        </div>
        <div class="person-info">
          <div class="person-name">${traveler.name}</div>
          <div class="person-time">${traveler.time}</div>
        </div>
      </div>
      <div class="contact-request hidden">
        <button class="connect-btn" onclick="event.stopPropagation(); requestContact(${traveler.id})">
          <i class="fas fa-envelope"></i>
          Send Contact Request
        </button>
      </div>
    </div>
  `,
    )
    .join("")

  // Update the section title
  const peopleHeader = document.querySelector(".people-header h2")
  peopleHeader.textContent = `Travelers at ${placeName}`
}

function toggleContactRequest(card, travelerId) {
  const contactRequest = card.querySelector(".contact-request")
  const wasHidden = contactRequest.classList.contains("hidden")

  // Close any other open contact requests
  document.querySelectorAll(".contact-request").forEach((el) => {
    if (el !== contactRequest) {
      el.classList.add("hidden")
    }
  })

  // Toggle this contact request
  contactRequest.classList.toggle("hidden")

  if (wasHidden) {
    card.classList.add("expanded")
  } else {
    card.classList.remove("expanded")
  }
}

// Event Listeners
document.getElementById("prev-day").addEventListener("click", () => {
  if (currentDay > 0) {
    currentDay--
    updateMap()
    updateTimeline()
    updateNearbyTravelersList()
  }
})

document.getElementById("next-day").addEventListener("click", () => {
  if (mapData && mapData.days && currentDay < mapData.days.length - 1) {
    currentDay++
    updateMap()
    updateTimeline()
    updateNearbyTravelersList()
  }
})

document.getElementById("close-popup").addEventListener("click", () => {
  document.getElementById("user-popup").style.display = "none"
})

// Initialize map when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const mapDataElement = document.getElementById("map-data")
  const initialMapData = mapDataElement ? JSON.parse(mapDataElement.textContent) : null
  initMap(initialMapData)
})

