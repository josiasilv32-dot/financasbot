import json, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# PEGA TOKEN DA NUVEM (seguro)
TOKEN = os.getenv("BOT_TOKEN") or "COLA_SEU_TOKEN_AQUI_LOCAL"
DATA_FILE = "financas_guerra.json"

CONFIG = {"fixo_percent":0.40,"comida_percent":0.13,"lazer_percent":0.10,"guerra_percent":0.30,"curso_percent":0.07}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,'r',encoding='utf-8') as f: return json.load(f)
        except: pass
    return {"saldo_comida":0,"recebido":0,"streak":0,"nivel":"RECRUTA"}

def save_data(d):
    clean={"saldo_comida":float(d.get("saldo_comida",0)),"recebido":float(d.get("recebido",0)),"streak":int(d.get("streak",0)),"nivel":str(d.get("nivel","RECRUTA"))}
    with open(DATA_FILE,'w',encoding='utf-8') as f: json.dump(clean,f)

async def start(update, context): await update.message.reply_text("🔥 V2 CLOUD ON\nrecebi 1050 | gastei 12 | /saldo | /lojas | /bonus")

async def recebi(update, context):
    try:
        txt=update.message.text.lower()
        if "+" in txt:
            valor=float(txt.split("+")[1])
            d=load_data()
            d["recebido"]+=valor
            d["saldo_comida"]+=valor*CONFIG["comida_percent"]
        else:
            valor=float(txt.split()[1].replace('€',''))
            d=load_data()
            d["recebido"]=valor
            d["saldo_comida"]=valor*CONFIG["comida_percent"]
            d["streak"]=0
        save_data(d)
        por_dia=d["saldo_comida"]/30
        await update.message.reply_text(f"💰 TOTAL MÊS: {d['recebido']:.0f}€\n🍱 COMIDA: {d['saldo_comida']:.0f}€ -> {por_dia:.2f}€/dia\nUsa: recebi +100 se for extra")
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}\nUsa: recebi 950 ou recebi +100")

async def gastei(update, context):
    try:
        valor=float(update.message.text.split()[1])
        d=load_data()
        d["saldo_comida"]=d.get("saldo_comida",0)-valor
        media=(d.get("recebido",0)*CONFIG["comida_percent"]/30) or 4
        d["streak"]=d.get("streak",0)+1 if valor<=media else 0
        save_data(d)
        msg=f"GASTO {valor}€\nSaldo: {d['saldo_comida']:.2f}€\nStreak {d['streak']}"
        if d["streak"]>=3: msg+="\n🏆 BONUS +10€ lazer!"
        await update.message.reply_text(msg)
    except: await update.message.reply_text("Usa: gastei 12")

async def saldo(update, context): d=load_data(); await update.message.reply_text(f"Saldo: {d.get('saldo_comida',0):.2f}€ Streak:{d.get('streak',0)}")
async def lojas(update, context): await update.message.reply_text("🛒 Faro: Lidl 2ª, Aldi, Pingo Doce promo")
async def bonus(update, context): d=load_data(); await update.message.reply_text(f"Streak {d.get('streak',0)}/3")

async def handle_text(update, context):
    txt=update.message.text.lower().strip()
    if txt.startswith("recebi"): await recebi(update, context)
    elif txt.startswith("gastei"): await gastei(update, context)

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(CommandHandler("lojas", lojas))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("BOT CLOUD RODANDO...")
    app.run_polling()

if __name__=="__main__": main()
