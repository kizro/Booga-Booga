from flask import Flask, request, render_template
from openai import OpenAI

client = OpenAI(api_key='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')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    destinations = request.form['destinations']
    destinations_list = destinations.split(',')
    prompt_for_recommendations = f"Given that a user enjoys visiting {', '.join(destinations_list)}, can you recommend 3 to 5 other destinations they might be interested in?"

    # Request for recommendations based on user's input destinations
    recommendations_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will return only the names of the destinations separated by commas."},
            {"role": "user", "content": prompt_for_recommendations}
        ]
    )

    recommendations = recommendations_response.choices[0].message.content

    # Analyzing common themes in the input destinations
    prompt_for_input_themes = f"What do the destinations {', '.join(destinations_list)} have in common?"
    input_themes_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will return common characteristics for each destination. Good ones are: common location, common weather, common geographical features, common activities. Return 5 words."},
            {"role": "user", "content": prompt_for_input_themes}
        ]
    )

    input_themes = input_themes_response.choices[0].message.content

    # Analyzing common themes in the recommended destinations
    prompt_for_recommended_themes = f"What do the destinations {recommendations} have in common?"
    recommended_themes_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You will return common characteristics for each destination. Good ones are: common location, common weather, common geographical features, common activities. Return 5 words."},
            {"role": "user", "content": prompt_for_recommended_themes}
        ]
    )

    recommended_themes = recommended_themes_response.choices[0].message.content

    # Pass the themes and recommendations to the template
    return render_template('recommendations.html', recommendations=recommendations, input_themes=input_themes, recommended_themes=recommended_themes)

if __name__ == '__main__':
    app.run(debug=True)
