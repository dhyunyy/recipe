from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

cuisines = [
    "", "Italian", "Mexican", "Chinese", "Indian",
    "Japanese", "Thai", "French", "Mediterranean",
    "American", "Greek"
]

dietary_restrictions = [
    "Gluten-Free", "Dairy-Free", "Vegan", "Pescatarian",
    "Nut-Free", "Kosher", "Halal", "Low-Carb",
    "Organic", "Locally Sourced"
]

# 언어 딕셔너리: 키 = 화면에 표시될 언어 이름, 값 = 언어 코드
languages = {
    'Korean': 'ko',
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Russian': 'ru',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Arabic': 'ar',
    'Dutch': 'nl',
    'Swedish': 'sv',
    'Turkish': 'tr',
    'Greek': 'el',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Indonesian': 'id',
    'Thai': 'th',
    'Filipino': 'tl',
    'Vietnamese': 'vi'
}

@app.route('/')
def index():
    return render_template(
        'index.html',
        cuisines=cuisines,
        dietary_restrictions=dietary_restrictions,
        languages=languages
    )

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    # 1) 사용자 입력 받기
    ingredients = request.form.getlist('ingredient')      # ['tomato', 'basil', 'mozzarella']
    selected_cuisine = request.form.get('cuisine')       # ex) 'french'
    selected_restrictions = request.form.getlist('restrictions')  # ex) ['organic']
    selected_language = request.form.get('language')     # ex) 'French'

    # 2) 재료 3개 체크
    if len(ingredients) != 3:
        return "세 가지 재료를 정확히 입력해 주세요."

    # 3) selected_language 키로부터 실제 언어 코드 가져오기
    #    만약 선택된 언어가 languages 딕셔너리에 없으면 기본값 'ko' 사용
    selected_language_code = languages.get(selected_language, 'ko')

    # 4) 기본 프롬프트 (재료만 포함)
    prompt = (
        f"{selected_cuisine if selected_cuisine else ''} 스타일로 "
        f"{', '.join(ingredients)}를 사용한 레시피를 HTML 형식으로 작성해주세요. "
        "재료 목록(<h3>Ingredients</h3>)과 조리 순서(<ul> 또는 <ol>)만 포함하고, "
        f"{selected_language}({selected_language_code})로 반드시 작성해 주세요. "
        "추가 설명은 생략해주세요."
    )

    # 5) 식품 제한(dietary_restrictions)이 있으면 프롬프트에 추가
    if selected_restrictions and len(selected_restrictions) > 0:
        prompt += f" 레시피에는 다음 제한사항을 반드시 반영해주세요: {', '.join(selected_restrictions)}."

    # 6) Gemini API 호출
    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
    except Exception as e:
        raw = f"레시피 생성 중 오류 발생: {str(e)}"

    # 7) Markdown 코드 펜스 제거
    recipe_html = raw
    if recipe_html.startswith("```html"):
        lines = recipe_html.splitlines()
        recipe_html = "\n".join(lines[1:-1]).strip()
    elif recipe_html.startswith("```"):
        lines = recipe_html.splitlines()
        recipe_html = "\n".join(lines[1:-1]).strip()

    # 8) 결과 렌더링
    return render_template('recipe.html', recipe=recipe_html)

if __name__ == "__main__":
    app.run(debug=True)
