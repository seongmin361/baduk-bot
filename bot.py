from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# 데이터 저장 구조
# buyins: { "이름": 총 바이인 금액 }
# outchips: { "이름": 아웃칩 금액 }
buyins = {}
outchips = {}

# 1. 바이인 등록 (/buy 이름 금액) - 중복 입력 시 금액 합산
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("사용법: /buy [이름] [금액]\n예시: /buy 성민 100000")
        return
    
    name = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("금액은 숫자로 입력해주세요!")
        return

    # 기존 바이인이 있으면 합산
    buyins[name] = buyins.get(name, 0) + amount
    await update.message.reply_text(f"✅ 바이인 등록: {name} ({buyins[name]:,})")

# 2. 아웃칩 등록 (/out 이름 금액)
async def out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("사용법: /out [이름] [아웃칩 금액]\n예시: /out 성민 350000")
        return
    
    name = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        await update.message.reply_text("금액은 숫자로 입력해주세요!")
        return

    outchips[name] = amount
    await update.message.reply_text(f"✅ 아웃칩 등록: {name} ({amount:,})")

# 3. 현재 현황 출력 (/list)
async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not buyins:
        await update.message.reply_text("현재 등록된 바이인 내역이 없습니다.")
        return

    # 바이인 금액이 높은 순으로 정렬
    sorted_buyins = sorted(buyins.items(), key=lambda x: x[1], reverse=True)
    total_buyin = sum(buyins.values())
    
    text = "🃏 **바둑 정산**\n\n```text\n"
    for name, amount in sorted_buyins:
        text += f"{name:<8} {amount:>9,}\n"
    text += f"```\n총 바이인 : {total_buyin:,}"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# 4. 최종 결과 출력 (/result)
async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not buyins:
        await update.message.reply_text("현재 등록된 바이인 내역이 없습니다.")
        return

    all_names = set(buyins.keys()).union(set(outchips.keys()))
    
    result_list = []
    for name in all_names:
        b_amount = buyins.get(name, 0)
        o_amount = outchips.get(name, 0)
        profit = o_amount - b_amount
        result_list.append((name, b_amount, o_amount, profit))

    # 손익이 높은 순으로 정렬
    result_list.sort(key=lambda x: x[3], reverse=True)

    text = "🏆 **최종 정산**\n\n```text\n"
    text += f"{'이름':<4} {'바이인':<9} {'아웃칩':<9} {'손익':<8}\n\n"
    
    for name, b, o, p in result_list:
        p_str = f"+{p:,}" if p > 0 else f"{p:,}"
        text += f"{name:<4} {b:>7,} {o:>9,} {p:>9}\n"
        
    text += "```"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# 5. 초기화 (/reset)
async def reset_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buyins.clear()
    outchips.clear()
    await update.message.reply_text("🔄 모든 정산 데이터가 초기화되었습니다.")

def main():
    # 텔레그램 BotFather에서 받은 본인의 봇 토큰을 아래 따옴표 사이에 넣어주세요
    TOKEN = "8969540703:AAFlCIFEz4ZfYSQ8oE_OWab66O6ng_iXfco"  
    
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("out", out))
    app.add_handler(CommandHandler("list", show_list))
    app.add_handler(CommandHandler("result", show_result))
    app.add_handler(CommandHandler("reset", reset_data))

    print("바둑 정산 봇이 실행 중입니다...")
    app.run_polling()

if __name__ == "__main__":
    main()