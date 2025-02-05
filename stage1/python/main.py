from flask import Flask, request, jsonify
from flask_cors import CORS
import requests


app = Flask(__name__)
CORS(app)

def isAmstrong(value):
    """
    checks if a number is amstrong
    return True is yes other returns False
    """
    digits = [s for s in str(value)]
    power = len(digits)

    return value == sum(int(d) ** power for d in digits)


def isPrime(value):
    """
    returns True is a number is prime otherwise return False
    """
    if value < 2:
        return False
    
    for i in range(2, int(value ** 0.5) + 1):
        if value % i == 0:
            return False
        
    return True


def isPerfect(value):
    """
    returns True is value is perfect otherwise return False
    """

    if value < 2:
        return False
    
    divisor_sum = sum(i for i in range(1, value) if value % i == 0)

    return divisor_sum == value



def digitSum(number):
    """
    returns the sum of the digits that make up a number
    """

    
    return sum([int(d) for d in str(number)])

@app.get("/api/classify-number", strict_slashes=False)
def number_property():
    """
    get the number from the query parameter "number"
    and return the property of the number
    for example:
        /api/classify-number?number=371
    result:
        {
    "number": 371,
    "is_prime": false,
    "is_perfect": false,
    "properties": ["armstrong", "odd"],
    "digit_sum": 11,  // sum of its digits
    "fun_fact": "371 is an Armstrong number because 3^3 + 7^3 + 1^3 = 371" //gotten from the numbers API
    }
    """

    number = request.args.get("number", None)
    if not number:
        return jsonify(
            {

                "number": "is empty",
                "error": True
            }
        ), 400

    number = int(number)
    request_query = "http://numbersapi.com/{}/math".format(number)
    request_body = requests.get(request_query)

    properties = []
    if isAmstrong(number):
        properties.append("armstrong")
    if number % 2:
        properties.append("odd")
    else:
        properties.append("even")

    return jsonify({
        "number": number,
        "is_prime": isPrime(number),
        "is_perfect": isPerfect(number),
        "properties": properties,
        "digit_sum": digitSum(number),
        "fun_fact": request_body.text
    }), 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)


