import os
from flask import Flask, request, render_template, session
from openai import OpenAI
import requests

# Initialize OpenAI client with your API key
client = OpenAI(api_key='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')

# Replace YOUR_PEXELS_API_KEY with your actual Pexels API key
pexels_api_key = 'ZXZF4I2d7Fbd6Jrlf2Lo6cfjK4IGnxFr5LCCiAHLD8MtCdUEPs6C1mpi'

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/prompt', methods=['GET', 'POST'])
def prompt():
    if request.method == 'POST':
        destinations = request.form['destinations']
        destinations_list = destinations.split(',')

        prompt_for_recommendations = f"Given that a user enjoys visiting {', '.join(destinations_list)}, can you recommend 3 to 5 other destinations they might be interested in?"

        # Assuming `client.chat.completions.create` is a call to OpenAI's API
        recommendations_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You will return only the names of the destinations separated by commas. Do not exceed 5 words. There should not be a period at the end of any destination. There should not be punctuation besides separated by commas. No periods"},
                {"role": "user", "content": prompt_for_recommendations}
            ]
        )

        recommendations = recommendations_response.choices[0].message.content.split(', ')

        session['recommendations'] = recommendations
        session['destinations_list'] = destinations_list
        
    else:
        session.pop('destinations_list', None)
        return render_template('prompt.html')

@app.route('/themes', methods=['POST'])
def themes():
    prompt()
    destinations_list = session.get('destinations_list', [])
    prompt_for_input_themes = f"""
    Imagine describing destinations such as {' '.join(destinations_list)}. List these using single, specific keywords or short phrases. These characteristics should be common to these destinations. Avoid responses that include the name of cities. Include 1 temperature description and 1 geospatial description."
    """

    input_themes_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "List 4 unique characteristics that define popular vacation destinations using single, specific words only. Focus on aspects like location, climate, geography, and activities. Avoid plurals and broad terms. Separate by commas."},
            {"role": "user", "content": prompt_for_input_themes}
        ]
    )

    input_themes = input_themes_response.choices[0].message.content

    return render_template('themes.html', input_themes=input_themes)

@app.route('/recommendations', methods=['POST'])
def recommendations():
    recommendations = session.get('recommendations', [])
    headers = {'Authorization': pexels_api_key}
    images = {}
    for destination in recommendations:
        search_url = f'https://api.pexels.com/v1/search?query={destination.strip()}&per_page=1'
        response = requests.get(search_url, headers=headers).json()
        image_url = response['photos'][0]['src']['large'] if response['photos'] else 'https://via.placeholder.com/150'
        images[destination.strip()] = image_url
    
    return render_template('recommendations.html',recommendations = recommendations,images=images)

@app.route('/search-flights', methods=['POST'])
def search_flights():
    from_id = request.form['fromId']
    to_id = request.form['toId']
    depart_date = request.form['departDate']

    # Setup for API request
    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    querystring = {
        "fromId": f"{from_id}.AIRPORT",
        "toId": f"{to_id}.AIRPORT",
        "departDate": depart_date,
        "pageNo": "1",
        "adults": "1",
        "currency_code": "USD",  # Adjust based on your requirement
    }
    headers = {
        "X-RapidAPI-Key": "868ebe4141mshfb7bc2dea2b3702p10b6d7jsn37eb9db537f0",
        "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code != 200:
        # Handle unsuccessful API calls
        return render_template('flights.html', error="Failed to fetch flight data.")

    flights_data = response.json()
    flights = []

    # Process the API response
    if 'data' in flights_data and 'flightDeals' in flights_data['data']:
        flight_deals = flights_data['data']['flightDeals']
        for deal in flight_deals:
            if deal.get('key') in ['CHEAPEST', 'FASTEST']:
                flights.append({
                    'type': deal['key'],
                    'price': deal['price']['units'],
                    'currency': deal['price']['currencyCode'],
                    'offerToken': deal['offerToken']
                })

    return render_template('flights.html', flights=flights)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/title')
def title():
    return render_template('title.html')



if __name__ == '__main__':
    app.run(debug=True)
