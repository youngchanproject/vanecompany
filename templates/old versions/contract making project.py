from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# 대화 상태를 저장하는 전역 변수
conversation_state = {
    "step": 1,
    "responses": {}
}

valid_answers = {
    "Q3": ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "대전광역시"],
    "Q4": ["월세", "전세"],
    "Q5": ["보증금+월세", "보증금 없는 월세", "전액 보증금", "반전세"]
}

@app.route("/")
def home():
    # 초기 메시지 전달
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "메시지를 입력해주세요."})

    step = conversation_state["step"]
    response = ""
    options = None

    try:
        if step == 1:
            response = "1. 임대인/임차인 여부를 선택해 주세요 (임대인 / 임차인)"
            options = ["임대인", "임차인"]
            conversation_state["step"] += 1

        elif step == 2:
            response = "2. 임대인/임차인의 성명을 입력해주세요."
            conversation_state["responses"]["Q1"] = user_message
            conversation_state["step"] += 1

        elif step == 3:
            response = "3. 부동산 소재지는 어떻게 되나요? (서울특별시 / 부산광역시 / 대구광역시 / 인천광역시 / 대전광역시)"
            options = valid_answers["Q3"]
            conversation_state["responses"]["Q2"] = user_message
            conversation_state["step"] += 1

        elif step == 4:
            if user_message not in valid_answers["Q3"]:
                return jsonify({"response": "잘못된 입력입니다. 다음 중에서 선택해 주세요: 서울특별시, 부산광역시, 대구광역시, 인천광역시, 대전광역시"})
            response = "4. 월세 또는 전세 여부를 선택해 주세요 (월세 / 전세)"
            options = valid_answers["Q4"]
            conversation_state["responses"]["Q3"] = user_message
            conversation_state["step"] += 1

        elif step == 5:
            if user_message == "월세":
                response = "5. 계약금 납부의 방식을 선택해 주세요 (보증금+월세 / 보증금 없는 월세)"
                options = ["보증금+월세", "보증금 없는 월세"]
            elif user_message == "전세":
                response = "5. 계약금 납부의 방식을 선택해 주세요 (전액 보증금 / 반전세)"
                options = ["전액 보증금", "반전세"]
            else:
                return jsonify({"response": "잘못된 입력입니다. '월세' 또는 '전세'를 선택해 주세요."})
            conversation_state["responses"]["Q4"] = user_message
            conversation_state["step"] += 1

        elif step == 6:
            if user_message not in valid_answers["Q5"]:
                return jsonify({"response": "잘못된 입력입니다. 올바른 계약금 납부 방식을 선택해 주세요."})
            if user_message in ["보증금+월세", "전액 보증금", "반전세"]:
                response = "보증금의 금액을 적어주세요."
            elif user_message == "보증금 없는 월세":
                response = "월세의 금액을 적어주세요."
            conversation_state["responses"]["Q5"] = user_message

            # 결과값 반환
            final_response = f"감사합니다! 입력이 완료되었습니다.\n입력 내용: {conversation_state['responses']}"
            conversation_state["step"] = 1  # 초기화
            conversation_state["responses"] = {}
            return jsonify({"response": final_response})

    except Exception as e:
        response = f"오류가 발생했습니다: {str(e)}. 다시 시도해주세요."
        conversation_state["step"] = 1  # 초기화

    return jsonify({"response": response, "options": options})

if __name__ == "__main__":
    app.run(debug=True)
