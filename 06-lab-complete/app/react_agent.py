import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from openai import OpenAI
from app.tools import tools
from app.config import settings

# Đảm bảo Windows Terminal / PowerShell hiển thị được ký tự UTF-8 (Emoji) mà không bị lỗi mã hóa
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

MODEL_NAME = settings.llm_model
API_KEY = settings.openai_api_key

MAX_ITERATIONS = 6
SIMULATE_ERROR = False
tools.SIMULATE_ERROR = SIMULATE_ERROR

class ModelOutput:
    def __init__(self, output_type: str, content: str = None, name: str = None, args: dict = None, raw_message = None):
        self.type = output_type        # "final_answer" hoặc "tool_call"
        self.content = content          # Câu trả lời cuối cùng cho user
        self.name = name                # Tên Tool cần gọi
        self.args = args                # Tham số truyền vào Tool
        self.raw_message = raw_message  # Đối tượng message thô từ OpenAI

    def as_message(self) -> dict:
        return self.raw_message

_latest_tool_call_id = None

def call_model(system: str, messages: list, tools_list: list) -> ModelOutput:
    global _latest_tool_call_id
    client = OpenAI(api_key=API_KEY)
    
    full_messages = [{"role": "system", "content": system}] + messages
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=full_messages,
        tools=tools_list,
        tool_choice="auto",
        temperature=0.2
    )
    
    assistant_message = response.choices[0].message
    
    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        _latest_tool_call_id = tool_call.id
        
        try:
            tool_args = json.loads(tool_call.function.arguments)
        except ValueError:
            tool_args = {}
            
        thought = assistant_message.content
        if thought:
            print(f"🧠 [Thought]:\n{thought}")
        else:
            print("🧠 [Thought]: (Đang chuẩn bị gọi công cụ kế tiếp...)")
            
        print(f"🎬 [Action] -> Gọi Tool: '{tool_call.function.name}'")
        print(f"   └─ Tham số đầu vào: {json.dumps(tool_args, ensure_ascii=False)}")
        
        return ModelOutput(
            output_type="tool_call",
            name=tool_call.function.name,
            args=tool_args,
            raw_message=assistant_message
        )
    else:
        thought = assistant_message.content
        if thought:
            print(f"🧠 [Thought]:\n{thought}")
            
        return ModelOutput(
            output_type="final_answer",
            content=assistant_message.content,
            raw_message=assistant_message
        )

def run_tool(name: str, args: dict) -> str:
    observation = ""
    try:
        if name == "search_flights":
            dep_city = args.get("departure_city")
            dest_city = args.get("destination_city")
            dep_date = args.get("departure_date")
            result = tools.search_flights(dep_city, dest_city, dep_date)
            observation = json.dumps(result, ensure_ascii=False)
            
        elif name == "hotel":
            dest_city = args.get("destination_city")
            rate = args.get("rate")
            result = tools.hotel(dest_city, rate)
            observation = json.dumps(result, ensure_ascii=False)
            
        elif name == "get_weather":
            dest_city = args.get("destination_city")
            dep_date = args.get("departure_date")
            result = tools.get_weather(dest_city, dep_date)
            observation = json.dumps(result, ensure_ascii=False)
            
        elif name == "calculate_total_price":
            flight_id = args.get("flight_id")
            hotel_id = args.get("hotel_id")
            result = tools.calculate_total_price(flight_id, hotel_id)
            observation = json.dumps(result, ensure_ascii=False)
            
        else:
            observation = f"Lỗi: Không tìm thấy công cụ nào có tên là '{name}'."
            
    except Exception as tool_error:
        observation = f"Lỗi phát sinh từ công cụ: {str(tool_error)}"

    print(f"👁️‍🗨️ [Observation] -> Kết quả thực tế thu được:")
    print(f"   └─ {observation}")
    return observation

def tool_message(name: str, result: str) -> dict:
    global _latest_tool_call_id
    return {
        "role": "tool",
        "tool_call_id": _latest_tool_call_id,
        "name": name,
        "content": result
    }

SYSTEM_PROMPT = """Bạn là một AI Agent thông minh lập kế hoạch du lịch hoạt động theo mô hình ReAct (Reasoning and Acting).
Mục tiêu của bạn là giúp người dùng lên kế hoạch chuyến đi trọn vẹn thông qua việc kết hợp giữa suy luận (Thought) và hành động (Action - gọi tool).

Bạn có quyền truy cập vào 4 công cụ:
1. `search_flights(departure_city, destination_city, departure_date)`: Tìm danh sách chuyến bay. Trả về flight_id và price.
2. `hotel(destination_city, rate)`: Tìm danh sách khách sạn tại điểm đến dựa vào số sao (rate). Trả về hotel_id và price.
3. `get_weather(destination_city, departure_date)`: Kiểm tra thời tiết tại điểm đến vào ngày khởi hành. Trả về temp và rain_prob.
4. `calculate_total_price(flight_id, hotel_id)`: Tính toán tổng chi phí dựa trên mã chuyến bay và khách sạn đã chọn.

QUY TRÌNH HÀNH ĐỘNG NGHIÊM NGẶT ĐỐI VỚI BẠN:
1. [Thought]: Suy nghĩ xem bạn đang ở bước nào, cần thêm thông tin gì để lên kế hoạch và gọi tool nào tiếp theo.
2. [Action]: Gọi tool phù hợp với các tham số tương ứng đã phân tích được.
3. [Observation]: Xem kết quả trả về từ tool (Observation) để làm cơ sở cho bước tiếp theo.
4. [Final Answer]: Sau khi đã thu thập trọn vẹn đầy đủ thông tin (chuyến bay phù hợp, khách sạn phù hợp, thời tiết điểm đến, và tính tổng chi phí bằng tool), hãy đưa ra câu trả lời chi tiết, mạch lạc và thân thiện nhất cho người dùng.

⚠️ YÊU CẦU CỰC KỲ QUAN TRỌNG:
1. Bạn phải hoàn thành tất cả các bước tra cứu: Tìm chuyến bay -> Tìm khách sạn -> Kiểm tra thời tiết -> Tính tổng chi phí trước khi đưa ra câu trả lời cuối cùng.
2. KHÔNG ĐƯỢC tự bịa ra thông tin mã chuyến bay, mã khách sạn, thời tiết hoặc giá tiền. Mọi thông tin phải đến từ kết quả của các công cụ.
3. Khi tính tổng chi phí, bắt buộc phải sử dụng công cụ `calculate_total_price` với mã flight_id và hotel_id thực tế đã tìm thấy được qua tool.
"""

def run_react_agent(user_query: str):
    if not API_KEY or not API_KEY.startswith("s" "k" "-"):
        print("\n" + "!"*80)
        print("⚠️ CẢNH BÁO CỦA HỆ THỐNG: Bạn chưa cấu hình 'OPENAI_API_KEY' hợp lệ.")
        print("!"*80 + "\n")
        return "Lỗi: Không tìm thấy OPENAI_API_KEY hợp lệ của OpenAI."

    print("\n" + "="*80)
    print(f"🎬 BẮT ĐẦU CHẠY AGENT - CÂU HỎI: \"{user_query}\"")
    print("="*80)

    messages = [{"role": "user", "content": user_query}]

    for step in range(MAX_ITERATIONS):
        print(f"\n--- [VÒNG LẶP REACT BƯỚC {step + 1}/{MAX_ITERATIONS}] ---")
        
        output = call_model(
            system=SYSTEM_PROMPT,
            messages=messages,
            tools_list=tools.TOOLS,
        )
        
        if output.type == "final_answer":
            print("\n✨ [Final Answer]:")
            print(output.content)
            print("="*80)
            return output.content

        result = run_tool(output.name, output.args)
        
        messages += [
            output.as_message(),
            tool_message(output.name, result),
        ]

    print("\n🛑 Stopped: max iterations reached! Vòng lặp bị ngắt để tránh lặp vô hạn.")
    print("="*80)
    return "Stopped: max iterations reached"

if __name__ == "__main__":
    test_question = "Tôi muốn bay từ Hà Nội đến Paris vào ngày mai. Hãy giúp tôi tìm chuyến bay phù hợp, tìm khách sạn 4 sao tại điểm đến, kiểm tra thời tiết ở điểm đến và tính tổng chi phí chuyến đi giúp tôi nhé!"
    run_react_agent(test_question)
