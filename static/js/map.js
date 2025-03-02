// Rich dummy data for the map
const dummyData = {
  days: [
    {
      date: "2023-07-01",
      places: [
        {
          name: "Central Park",
          lat: 40.7829,
          lng: -73.9654,
          time: "09:00 AM - 11:00 AM",
          description: "Start your day with a morning walk through Central Park",
          rating: 4.8,
          image: "/placeholder.svg?height=200&width=300",
          visitors: [
            { name: "Alice", timeSlot: "09:30 AM - 10:30 AM", avatar: "A", interests: ["Photography", "Nature"] },
            { name: "Bob", timeSlot: "10:00 AM - 11:00 AM", avatar: "B", interests: ["Jogging", "Birdwatching"] },
          ],
        },
        {
          name: "Metropolitan Museum of Art",
          lat: 40.7794,
          lng: -73.9632,
          time: "11:30 AM - 02:30 PM",
          description: "Explore world-class art collections",
          rating: 4.9,
          image: "/placeholder.svg?height=200&width=300",
          visitors: [{ name: "Diana", timeSlot: "12:00 PM - 02:00 PM", avatar: "D", interests: ["Art", "History"] }],
        },
      ],
    },
  ],
}

let map
let markers = []
let currentDay = 0
let polyline = null

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

    // Initialize map with error handling
    map = L.map("map", {
      zoomControl: false,
      scrollWheelZoom: true,
    }).setView([40.7128, -74.006], 12)

    // Add tile layer with error handling
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
      maxZoom: 19,
    }).addTo(map)

    // Add zoom control to top-right
    L.control
      .zoom({
        position: "topright",
      })
      .addTo(map)

    // Initialize with first day's data
    updateMap()

    // Log success
    console.log("Map initialized successfully")
  } catch (error) {
    console.error("Error initializing map:", error)
  }
}

function updateMap() {
  try {
    // Clear existing markers and polyline
    markers.forEach((marker) => map.removeLayer(marker))
    markers = []
    if (polyline) map.removeLayer(polyline)

    const places = dummyData.days[currentDay].places
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
        .bindPopup(`
        <div class="popup-content">
          <h3>${place.name}</h3>
          <p>${place.time}</p>
          <button onclick="showUserPopup('${place.name}')">View Visitors</button>
        </div>
      `)

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
    document.getElementById("current-day").textContent = `Day ${currentDay + 1}`
    document.getElementById("current-date").textContent = dummyData.days[currentDay].date

    // Update the timeline
    updateTimeline(places)

    // Log success
    console.log("Map updated successfully")
  } catch (error) {
    console.error("Error updating map:", error)
  }
}

function updateTimeline(places) {
  const planList = document.getElementById("plan-list")
  planList.innerHTML = ""

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
      </div>
    `
    planList.appendChild(timelineItem)
  })

  // Set timeline progress
  const progress = (100 * (places.length - 1)) / places.length
  document.querySelector(".timeline").style.setProperty("--progress", `${progress}%`)
}

function showUserPopup(placeName) {
  const place = dummyData.days[currentDay].places.find((p) => p.name === placeName)
  if (!place) return

  document.getElementById("place-name").textContent = placeName
  const userList = document.getElementById("user-list")
  userList.innerHTML = ""

  place.visitors.forEach((visitor) => {
    const userCard = document.createElement("div")
    userCard.className = "user-card"
    userCard.innerHTML = `
      <div class="user-avatar">${visitor.avatar}</div>
      <div class="user-info">
        <div class="user-name">${visitor.name}</div>
        <div class="user-time">${visitor.timeSlot}</div>
        <div class="user-interests">
          ${visitor.interests
            .map(
              (interest) => `
            <span class="interest-tag">${interest}</span>
          `,
            )
            .join("")}
        </div>
      </div>
      <button class="connect-btn" onclick="requestDetails('${visitor.name}')">
        Connect
      </button>
    `
    userList.appendChild(userCard)
  })

  document.getElementById("user-popup").style.display = "block"
}

function requestDetails(userName) {
  // Implement the logic to send an approval request to the selected user
  alert(`Connection request sent to ${userName}! They will be notified of your interest to meet.`)
}

document.getElementById("close-popup").addEventListener("click", () => {
  document.getElementById("user-popup").style.display = "none"
})

document.getElementById("prev-day").addEventListener("click", () => {
  if (currentDay > 0) {
    currentDay--
    updateMap()
  }
})

document.getElementById("next-day").addEventListener("click", () => {
  if (currentDay < dummyData.days.length - 1) {
    currentDay++
    updateMap()
  }
})

// Add custom marker styles
const style = document.createElement("style")
style.textContent = `
  .custom-marker {
    background: var(--primary);
    border: 2px solid white;
    border-radius: 50%;
    color: white;
    width: 32px !important;
    height: 32px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }

  .marker-content {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: var(--primary);
    transition: all 0.3s ease;
  }

  .custom-marker:hover .marker-content {
    transform: scale(1.1);
    background: var(--primary-dark);
  }

  .interest-tag {
    display: inline-block;
    padding: 2px 8px;
    background: var(--primary-light);
    color: var(--primary);
    border-radius: 12px;
    font-size: 0.75rem;
    margin: 2px;
  }
`
document.head.appendChild(style)

// Event Listeners

// Initialize map on load
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing map...")
  initMap()
})

// Make initMap available globally
window.initMap = initMap

