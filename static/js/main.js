document.addEventListener('DOMContentLoaded', function() {
    console.log("Musafir app loaded");
  
    // AJAX form submission for itinerary processing
    var itineraryForm = document.getElementById('itinerary-form');
    if (itineraryForm) {
      itineraryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var formData = new FormData(itineraryForm);
        fetch(itineraryForm.action, {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          document.getElementById('response').innerText = JSON.stringify(data, null, 2);
        })
        .catch(err => console.error(err));
      });
    }
  });
  