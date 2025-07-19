document.addEventListener('DOMContentLoaded', function() {
    const locateMeBtn = document.getElementById('locate-me');
    const mapContainer = document.getElementById('map');

    if (locateMeBtn && mapContainer) {
        locateMeBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    async function(position) {
                        locateMeBtn.disabled = true;
                        locateMeBtn.textContent = 'Loading...';
                        
                        try {
                            const response = await fetch('/update_map', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    lat: position.coords.latitude,
                                    lng: position.coords.longitude,
                                    action: 'my_location' // Indicate that we want to show the user's location
                                })
                            });

                            const data = await response.json();
                            mapContainer.innerHTML = data.map_html;
                            // Re-enable button after load
                            locateMeBtn.disabled = false;
                            locateMeBtn.textContent = 'Show My Location';
                            
                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to update map');
                            locateMeBtn.disabled = false;
                            locateMeBtn.textContent = 'Show My Location';
                        }
                    },
                    function(error) {
                        alert('Error getting your location: ' + error.message);
                        locateMeBtn.disabled = false;
                        locateMeBtn.textContent = 'Show My Location';
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser');
            }
        });
    }
});