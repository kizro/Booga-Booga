from flask import Flask, request, render_template
from openai import OpenAI
import requests

# Initialize OpenAI client with your API key
client = OpenAI(api_key='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')

# Replace YOUR_PEXELS_API_KEY with your actual Pexels API key
pexels_api_key = 'ZXZF4I2d7Fbd6Jrlf2Lo6cfjK4IGnxFr5LCCiAHLD8MtCdUEPs6C1mpi'

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    destinations = request.form['destinations']
    destinations_list = destinations.split(',')
    prompt_for_recommendations = f"Given that a user enjoys visiting {', '.join(destinations_list)}, can you recommend 3 to 5 other destinations they might be interested in?"

    recommendations_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will return only the names of the destinations separated by commas."},
            {"role": "user", "content": prompt_for_recommendations}
        ]
    )

    recommendations = recommendations_response.choices[0].message.content.split(', ')
    
    # Fetch images for each recommended destination from Pexels
    headers = {'Authorization': pexels_api_key}
    images = {}
    for destination in recommendations:
        search_url = f'https://api.pexels.com/v1/search?query={destination.strip()}&per_page=1'
        response = requests.get(search_url, headers=headers).json()
        image_url = response['photos'][0]['src']['large'] if response['photos'] else 'https://via.placeholder.com/150'
        images[destination.strip()] = image_url

    prompt_for_input_themes = f"""
    Imagine describing destinations such as {' '.join(destinations_list)} to someone who travels not just for leisure but to immerse in unique experiences that are off the beaten path. Identify characteristics that are distinctly non-generic, focusing on geographical and temporal traits that set these places apart from typical tourist attractions. For example, avoid broad terms like 'Urban' or 'Culturally-rich' or 'Historic'; instead, use precise descriptors like 'Metropolitan with ancient temples' or 'Home to UNESCO world heritage sites'. List these using single, specific keywords or short phrases, aiming for 'Asia' for region, 'modern' for era, 'warm' or 'cold' for climate. These characteristics should be common to these destinations. Avoid responses that include the name of cities.
    """
    input_themes_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "List 4 unique characteristics that define popular vacation destinations using single, specific words only. Focus on aspects like location, climate, geography, and activities. Avoid plurals and broad terms. Separate by commas."},
            {"role": "user", "content": prompt_for_input_themes}
        ]
    )

    input_themes = input_themes_response.choices[0].message.content

    prompt_for_recommended_themes = f"""
    Imagine describing destinations such as {', '.join(recommendations)} to someone who travels not just for leisure but to immerse in unique experiences that are off the beaten path. Identify characteristics that are distinctly non-generic, focusing on geographical and temporal traits that set these places apart from typical tourist attractions. For example, avoid broad terms like 'Urban' or 'Culturally-rich' or 'Historic'; instead, use precise descriptors like 'Metropolitan with ancient temples' or 'Home to UNESCO world heritage sites'. List these using single, specific keywords or short phrases, aiming for 'Asia' for region, 'modern' for era, 'warm' or 'cold' for climate. These characteristics should be common to these destinations.
    """
    recommended_themes_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "List 4 unique characteristics that define popular vacation destinations using single, specific words only. Focus on aspects like location, climate, geography, and activities. Avoid plurals and broad terms. Separate by commas."},
            {"role": "user", "content": prompt_for_recommended_themes}
        ]
    )

    recommended_themes = recommended_themes_response.choices[0].message.content

    # Pass the themes, recommendations, images to the template
    return render_template('recommendations.html', recommendations=recommendations, images=images, input_themes=input_themes, recommended_themes=recommended_themes)

if __name__ == '__main__':
    app.run(debug=True)
