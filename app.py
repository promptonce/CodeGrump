from flask import Flask, request, jsonify
import logging
from zhipuai import ZhipuAI
import os

app = Flask(__name__)

# 初始化 ZhipuAI 客户端
client = ZhipuAI(api_key="")

# 设置日志
logging.basicConfig(level=logging.INFO)

# AI 点评代码的逻辑
def ai_comment_on_code(code):
    logging.info(f"Received code for review:\n{code}")
    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
{"role": "user", "content": f"你扮演一个暴躁，说话犀利的程序员老哥，你看见一个人正在写下面的代码：\n{code}, 请说出你的内心独白"}
            ]
        )
        ai_response = response.choices[0].message.content
        logging.info(f"AI review successful: {ai_response}")
        return ai_response
    except Exception as e:
        logging.error(f"Error during AI review: {e}")
        return "点评时出错了，请稍后再试。"

# API 端点：接收代码并返回 AI 点评
@app.route('/api/review', methods=['POST'])
def review_code():
    data = request.json
    if 'code' not in data:
        return jsonify({'error': 'No code provided'}), 400

    code = data['code']
    ai_review = ai_comment_on_code(code)
    return jsonify({'review': ai_review})

# Function to get AI review for code with language info
def ai_comment_on_code_with_language(code, language):
    logging.info(f"Received code for review in {language}:\n{code}")
    try:
        # Modify the prompt to include the language in the inner monologue
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {
                    "role": "user",
                    "content": f"你扮演一个暴躁，说话犀利的{language}程序员老哥，你看见一个人正在写下面的代码：\n{code}, 请说出你的内心独白"
                }
            ]
        )
        ai_response = response.choices[0].message.content
        logging.info(f"AI review successful: {ai_response}")
        return ai_response
    except Exception as e:
        logging.error(f"Error during AI review: {e}")
        return "点评时出错了，请稍后再试。"

# New API endpoint that accepts both code and language
@app.route('/api/v1.5/review_with_language', methods=['POST'])
def review_code_with_language():
    data = request.json
    if 'code' not in data or 'language' not in data:
        return jsonify({'error': 'Code and language must be provided'}), 400

    code = data['code']
    language = data['language']
    ai_review = ai_comment_on_code_with_language(code, language)
    return jsonify({'review': ai_review})

# 新的API：验证问题是否符合规定
@app.route('/api/project_name/validate_question', methods=['POST'])
def validate_question():
    data = request.json
    if 'question' not in data:
        return jsonify({'error': 'No question provided'}), 400

    question = data['question']

    # 优化后的AI提示：检查问题是否合理、相关且符合项目需求
    try:
        response = client.chat.completions.create(
            model="glm-4-plus",
            messages=[
                {"role": "user", "content": f"你是一个项目审核专家，请检查以下问题是否符合项目的业务需求和技术标准：\n{question}"}
            ]
        )
        ai_response = response.choices[0].message.content
        logging.info(f"AI response for question validation: {ai_response}")
        
        # 判断AI返回的内容是否指示该问题不符合项目要求
        if "不符合" in ai_response or "不相关" in ai_response or "无关紧要" in ai_response:
            return jsonify({'isValid': False, 'message': '问题不符合项目需求'}), 400
        else:
            return jsonify({'isValid': True, 'message': '问题符合项目需求'}), 200
    except Exception as e:
        logging.error(f"Error during question validation: {e}")
        return jsonify({'error': '验证问题时出错，请稍后再试'}), 500

# 运行应用程序
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)