import json, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN") or "COLA_AQUI"
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

async def start(update, context): await update.message.reply_text("🔥 V2 CLOUD ON")
async def recebi(update, context):
    txt=update.message.text.lower()
    if "+" in txt:
        valor=float(txt.split("+")[1]); d=load_data(); d["recebido"]+=valor; d["saldo_comida"]+=valor*0.13
    else:
        valor=float(txt.split()[1]); d=load_data(); d["recebido"]=valor; d["saldo_comida"]=valor*0.13; d["streak"]=0
    save_data(d); await update.message.reply_text(f"TOTAL {d['recebido']:.0f}€ | {d['saldo_comida']/30:.2f}€/dia")
async def gastei(update, context):
    valor=float(update.message.text.split()[1]); d=load_data(); d["saldo_comida"]-=valor; save_data(d)
    await update.message.reply_text(f"Saldo: {d['saldo_comida']:.2f}€")
async def saldo(update, context): d=load_data(); await update.message.reply_text(f"Saldo: {d.get('saldo_comida',0):.2f}€")
async def handle_text(update, context):
    txt=update.message.text.lower()
    if txt.startswith("recebi"): await recebi(update, context)
    elif txt.startswith("gastei"): await gastei(update, context)
async def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start)); app.add_handler(CommandHandler("saldo", saldo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)); app.run_polling()
if __name__=="__main__": main()
