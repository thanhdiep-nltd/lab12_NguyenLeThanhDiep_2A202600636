# Deployment Information

## Public URL
https://day12ha-tang-cloudvadeployment-production-f1a1.up.railway.app

## Platform
Railway

## Test Commands

### Health Check
```bash
curl https://day12ha-tang-cloudvadeployment-production-f1a1.up.railway.app/health
# Expected: {"status": "ok", ...}
```

### API Test (with authentication)
```bash
echo '{"question": "Tôi muốn bay từ Hà Nội đến Paris vào ngày mai. Hãy tìm chuyến bay phù hợp, tìm khách sạn 4 sao tại điểm đến, kiểm tra thời tiết ở Paris ngày mai và tính tổng chi phí chuyến đi giúp tôi."}' | curl -X POST https://day12ha-tang-cloudvadeployment-production-f1a1.up.railway.app/ask \
  -H "X-API-Key: agent_5b2d8e4f1a7c93d6e5f8b0c2a4d6e8f0" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @-
```
###Kết quả: ```bash
{"question":"Tôi muốn bay từ Hà Nội đến Paris vào ngày mai. Hãy tìm chuyến bay phù hợp, tìm khách sạn 4 sao tại điểm đến, kiểm tra thời tiết ở Paris ngày mai và tính tổng chi phí chuyến đi giúp tôi.","answer":"Dưới đây là thông tin chi tiết cho chuyến đi của bạn từ Hà Nội đến Paris vào ngày mai:\n\n### Chuyến bay:\n- **Chuyến bay**: VN18\n- **Giá**: 15,000,000 VNĐ\n\n### Khách sạn:\n- **Khách sạn**: IBIS PARIS (4 sao)\n- **Giá**: 2,500,000 VNĐ\n\n### Thời tiết tại Paris vào ngày mai:\n- **Nhiệt độ**: 18°C\n- **Xác suất mưa**: 30%\n\n### Tổng chi phí chuyến đi:\n- **Tổng giá**: 17,500,000 VNĐ\n\nNếu bạn cần thêm thông tin hoặc muốn đặt chuyến đi, hãy cho tôi biết nhé!","model":"gpt-4o-mini","timestamp":"2026-06-12T14:51:05.520197+00:00"}
```


### Rate Limiting Test
Gửi 15 requests liên tiếp đến API sử dụng API Key. Từ request thứ 11 trở đi sẽ nhận mã lỗi 429:
```bash
for i in {1..15}; do 
  curl -X POST https://day12ha-tang-cloudvadeployment-production-f1a1.up.railway.app/ask \
    -H "X-API-Key: agent_5b2d8e4f1a7c93d6e5f8b0c2a4d6e8f0" \
    -H "Content-Type: application/json" \
    -d '{"user_id": "test_rate", "question": "test"}'
done
```

## Environment Variables Set
- `PORT` (được gán tự động bởi Railway)
- `AGENT_API_KEY`: agent_5b2d8e4f1a7c93d6e5f8b0c2a4d6e8f0
- `OPENAI_API_KEY`: (OpenAI Key hoạt động)
- `RATE_LIMIT_PER_MINUTE`: 10
- `DAILY_BUDGET_USD`: 5.0
