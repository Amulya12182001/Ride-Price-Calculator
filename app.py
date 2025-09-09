from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>Trip Cost Calculator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        h2 {
            text-align: center;
            font-weight: 900;
            font-size: 2.2rem;
            color: #2d3e50;
            margin: 25px 0;
        }
        .layout {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            padding: 20px;
        }
        .panel {
            background: #fff;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(44, 62, 80, 0.15);
            padding: 24px;
            display: flex;
            flex-direction: column;
            overflow: auto;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 18px;
        }
        label {
            font-weight: 500;
            color: #34495e;
            margin-bottom: 6px;
        }
        input[type="text"], input[type="number"] {
            padding: 10px 12px;
            border: 1px solid #bfc9d2;
            border-radius: 8px;
            font-size: 1rem;
            background: #f7fafd;
            transition: border-color 0.2s;
        }
        input[type="text"]:focus, input[type="number"]:focus {
            border-color: #5dade2;
            outline: none;
        }
        button {
            background: linear-gradient(90deg, #5dade2 0%, #2d3e50 100%);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 12px 0;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s;
        }
        button:hover {
            background: linear-gradient(90deg, #2d3e50 0%, #5dade2 100%);
        }
        #prices {
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
            justify-content: center;
        }
        .price-btn {
            background: linear-gradient(90deg, #2ecc71, #27ae60);
            color: #fff;
            font-weight: 700;
            border: none;
            border-radius: 50px;
            padding: 12px 24px;
            font-size: 1.1rem;
            cursor: default;
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
            text-align: center;
            width: 60%;
        }
        .price-btn.premium {
            background: linear-gradient(90deg, #f5b041 0%, #f7cac9 100%);
            color: #1a2947;
            border: 2px solid #f5b041;
        }
        .price-btn.normal {
            background: linear-gradient(90deg, #5dade2 0%, #b2dfdb 100%);
            color: #1a2947;
            border: 2px solid #5dade2;
        }
        .price-btn.cheap {
            background: linear-gradient(90deg, #58d68d 0%, #d4efdf 100%);
            color: #1a2947;
            border: 2px solid #58d68d;
        }
        .price-btn.ride {
            background: linear-gradient(90deg, #a569bd 0%, #d2b4de 100%);
            color: #1a2947;
            border: 2px solid #a569bd;
        }
        #map {
            flex: 1;
            border-radius: 16px;
            box-shadow: 0 4px 16px rgba(44, 62, 80, 0.10);
            min-height: 400px;
        }
        @media (max-width: 900px) {
            .layout {
                grid-template-columns: 1fr;
            }
            #map {
                min-height: 250px;
            }
        }
    </style>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBtADTobrhIDCrJOEuFCmemizJTeeMVx1A&libraries=places"></script>
    <script>
        let map, directionsService, directionsRenderer, autocompleteStart, autocompleteEnd;
        function initMap() {
            map = new google.maps.Map(document.getElementById('map'), {
                center: {lat: 37.0902, lng: -95.7129}, // USA center
                zoom: 5
            });
            directionsService = new google.maps.DirectionsService();
            directionsRenderer = new google.maps.DirectionsRenderer();
            directionsRenderer.setMap(map);
            autocompleteStart = new google.maps.places.Autocomplete(document.getElementById('start'));
            autocompleteEnd = new google.maps.places.Autocomplete(document.getElementById('end'));
        }
        function calculateAndDisplayRoute() {
            const start = document.getElementById('start').value;
            const end = document.getElementById('end').value;
            directionsService.route(
                { origin: start, destination: end, travelMode: 'DRIVING' },
                (response, status) => {
                    if (status === 'OK') {
                        directionsRenderer.setDirections(response);
                        const distance = response.routes[0].legs[0].distance.value / 1609.34;
                        showPrices(distance);
                    } else {
                        alert('Directions request failed due to ' + status);
                    }
                }
            );
        }
        function showPrices(distance) {
            const gasPrice = parseFloat(document.getElementById('gas').value);
            const mileage = parseFloat(document.getElementById('mileage').value);

            if (isNaN(gasPrice) || isNaN(mileage) || mileage <= 0) {
                document.getElementById('prices').innerHTML =
                    '<span style="color:red">Please enter valid gas price and mileage.</span>';
                return;
            }

            // ---- Tunable parameters ----
            const BaseFee = 2.00, PerMileWear = 0.20, TimeRate = 0.25, avgSpeed = 25;
            const MinFare_Normal = 7.00, MinFare_Premium = 9.00, MinFare_Cheap = 5.00, PremiumAdd = 1.50;

            // ---- Core costs ----
            const timeMinutes = (distance / avgSpeed) * 60;
            const fuelCost = (distance / mileage) * gasPrice;
            const wearTear = PerMileWear * distance;
            const timeCost = TimeRate * timeMinutes;
            const operatingCost = BaseFee + fuelCost + wearTear + timeCost;

            // ---- Tiers ----
            const normal  = Math.max(MinFare_Normal, operatingCost * 1.10);
            const premium = Math.max(MinFare_Premium, operatingCost * 1.25) + PremiumAdd;
            const cheap   = Math.max(MinFare_Cheap, operatingCost * 0.90, BaseFee + fuelCost + wearTear);

            // ---- Rideshare Estimate ----
            const baseFare = 2.00, perMile = 1.25, perMinute = 0.25, bookingFee = 2.50;
            const rideshareTime = (distance / 25) * 60;
            const rideshare = baseFare + (perMile * distance) + (perMinute * rideshareTime) + bookingFee;

            document.getElementById('prices').innerHTML =
                `<div class="price-btn">Distance: ${distance.toFixed(2)} miles</div>
                 <div class="price-btn premium">Premium: $${premium.toFixed(2)}</div>
                 <div class="price-btn normal">Normal: $${normal.toFixed(2)}</div>
                 <div class="price-btn cheap">Cheap: $${cheap.toFixed(2)}</div>
                 \\
                 <div class="price-btn ride">Uber/Lyft: $${rideshare.toFixed(2)}</div>`;
        }
    </script>
</head>
<body onload="initMap()">
    <h2>🚗 Trip Cost Calculator</h2>
    <div class="layout">
        <!-- Left Panel: Inputs -->
        <div class="panel">
            <form onsubmit="event.preventDefault(); calculateAndDisplayRoute();">
                <label for="start">Start Location:</label>
                <input id="start" type="text" placeholder="Enter start location" required>
                <label for="end">End Location:</label>
                <input id="end" type="text" placeholder="Enter end location" required>
                <label for="gas">Gas Price ($/gal):</label>
                <input id="gas" type="number" step="0.01" placeholder="e.g. 3.50" required>
                <label for="mileage">Car Mileage (miles/gal):</label>
                <input id="mileage" type="number" step="0.1" placeholder="e.g. 25" required>
                <button type="submit">Calculate</button>
            </form>
            <div id="prices"></div>
        </div>

        <!-- Right Panel: Map -->
        <div class="panel">
            <div id="map"></div>
        </div>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
