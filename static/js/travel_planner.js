// Update the finalizeTrip function
function finalizeTrip() {
    const loadingOverlay = document.createElement("div")
    loadingOverlay.className = "loading-overlay"
    loadingOverlay.innerHTML = `
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>Finalizing your perfect itinerary...</p>
      </div>
    `
    document.body.appendChild(loadingOverlay)
  
    fetch("/finalize_trip", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ finalize: true }),
    })
      .then((response) => response.json())
      .then((data) => {
        document.body.removeChild(loadingOverlay)
  
        if (data.finalized) {
          // Redirect to the itinerary view page with the trip ID
          window.location.href = `/view_itinerary?trip_id=${data.trip_id}`
        } else {
          alert(data.message || "No final itinerary was generated. Please try again.")
        }
      })
      .catch((error) => {
        console.error("Error during finalizeTrip:", error)
        document.body.removeChild(loadingOverlay)
        alert("There was an error finalizing your trip. Please try again.")
      })
  }
  
  