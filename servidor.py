from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Variável para armazenar a última posição recebida do ESP32
ultima_posicao = {
    "vehicle_id": "Aguardando...",
    "lat": -23.0910,  # Coordenada padrão em Indaiatuba
    "lng": -47.2180,
    "bateria": 0,
    "rssi": 0
}

# Página HTML com o mapa corrigido
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Monitor de Patinetes - IoT Indaiatuba</title>
    <meta charset="utf-8" />
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f4f4f9; }
        h2 { color: #333; }
        #map { height: 450px; width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />
    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>
</head>
<body>
    <div class="card">
        <h2>Painel de Monitoramento: Patinetes e Motos Elétricas</h2>
        <p><strong>Veículo:</strong> <span id="vid">Carregando...</span> | <strong>Bateria:</strong> <span id="bat">--</span>% | <strong>Sinal Wi-Fi (RSSI):</strong> <span id="rssi">--</span> dBm</p>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([-23.0910, -47.2180], 15);

        // Camada do OpenStreetMap corrigida e sem falhas
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        var marker = L.marker([-23.0910, -47.2180]).addTo(map)
            .bindPopup('Patinete ESP32')
            .openPopup();

        function atualizarDados() {
            fetch('/api/posicao')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('vid').innerText = data.vehicle_id;
                    document.getElementById('bat').innerText = data.bateria;
                    document.getElementById('rssi').innerText = data.rssi;

                    var novaLat = data.lat;
                    var novaLng = data.lng;
                    var newLatLng = new L.LatLng(novaLat, novaLng);

                    marker.setLatLng(newLatLng);
                    map.panTo(newLatLng);
                    marker.bindPopup("<b>" + data.vehicle_id + "</b><br>Bateria: " + data.bateria + "%").openPopup();
                });
        }

        setInterval(atualizarDados, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/telemetria', methods=['POST'])
def receber_telemetria():
    global ultima_posicao
    dados = request.json
    if dados:
        ultima_posicao = dados
        print(f"Dados recebidos do ESP32: {dados}")
        return jsonify({"status": "sucesso"}), 200
    return jsonify({"status": "erro"}), 400


@app.route('/api/posicao', methods=['GET'])
def enviar_posicao():
    return jsonify(ultima_posicao)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)