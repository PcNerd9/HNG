from flask import Flask, request, jsonify
from flask_simple_geoip import SimpleGeoIP

app = Flask(__name__)

@app.route("/api/hello", methods=['GET'])
def user_details():
    """
    Return user details in json format
    """
    weather_api = "3f144810364fcb5c811838812dd66639"
    name = request.args.get("visitor_name", "")
    client_ip_addr = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
    response = requests.get('https://ipinfo.io/{}/json'.format(client_ip_addr))
    location = response.json().get("city")
    response = res = requests.get('http://api.openweathermap.org/data/2.5/weather?q ={location}&appid ={weather_api}units=metric')
    main = response.json().get('main', None)
    if main is not None:
        temp = main.get("temp", "26")
    else:
        temp = "26"

    response = {"client_ip": client_ip_addr,
                "location": location,
                "greeting": f"Hello, {name}!,the temperature is {temp} degrees Celcius in New York"
                }
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
