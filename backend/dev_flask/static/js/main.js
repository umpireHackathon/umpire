// Base JavaScript that runs on all pages
document.addEventListener('DOMContentLoaded', function() {
    console.log('Application loaded');
});

document.addEventListener('DOMContentLoaded', function() {
    const terminalBtn = document.getElementById('left-menu-button-terminal');
    const stopsBtn = document.getElementById('left-menu-button-stop');
    const mapContainer = document.getElementById('map');

    if (terminalBtn && stopsBtn && mapContainer) {
        terminalBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                terminalBtn.disabled = true;
                terminalBtn.textContent = 'Loading...';
                navigator.geolocation.getCurrentPosition(
                    async function(position) {
                        try {
                            const response = await fetch('/update_map', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    lat: position.coords.latitude,
                                    lng: position.coords.longitude,
                                    action: 'show_terminals'
                                })
                            });

                            const data = await response.json();
                            mapContainer.innerHTML = data.map_html;
                            terminalBtn.disabled = false;
                            terminalBtn.textContent = 'Show Terminals';

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to update map');
                            terminalBtn.disabled = false;
                            terminalBtn.textContent = 'Show Terminals';
                        }
                    },
                    function(error) {
                        alert('Error getting your location: ' + error.message);
                        terminalBtn.disabled = false;
                        terminalBtn.textContent = 'Show Terminals';
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

        stopsBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                stopsBtn.disabled = true;
                stopsBtn.textContent = 'Loading...';
                navigator.geolocation.getCurrentPosition(
                    async function(position) {
                        try {
                            const response = await fetch('/update_map', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    lat: position.coords.latitude,
                                    lng: position.coords.longitude,
                                    action: 'show_stops'
                                })
                            });

                            const data = await response.json();
                            mapContainer.innerHTML = data.map_html;
                            stopsBtn.disabled = false;
                            stopsBtn.textContent = 'Show Stops';

                        } catch (error) {
                            console.error('Error:', error);
                            alert('Failed to update map');
                            stopsBtn.disabled = false;
                            stopsBtn.textContent = 'Show Stops';
                        }
                    },
                    function(error) {
                        alert('Error getting your location: ' + error.message);
                        stopsBtn.disabled = false;
                        stopsBtn.textContent = 'Show Stops';
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
