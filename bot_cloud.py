
[19/07/2026 02:28] Josuas: import os
import json
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "financas_dono.json"

# --- BANCO DE DADOS SIMPLES ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"salario": 0, "renda": 350, "gastos": [], "mes": datetime.datetime.now().strftime("%m/%Y")}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def get_divisao_milionaria(salario, renda):
    # Mente Milionaria - 6 potes adaptado pra ti
    if salario == 0:
        return None
    # 55% necessidades (ja inclui renda)
    necessidades = salario * 0.55
    liberdade = salario * 0.10  # investir, bot, carta
    educacao = salario * 0.10   # cursos, livros
    diversao = salario * 0.10   # helicoptero, aviao Portimao
    longo_prazo = salario * 0.10 # reserva, emergencia
    doacao = salario * 0.05

    gasto_fixo = renda
    sobra_necessidades = necessidades - renda

    return {
        "necessidades": necessidades,
        "sobra_necessidades": max(0, sobra_necessidades),
        "liberdade": liberdade,
        "educacao": educacao,
        "diversao": diversao,
        "longo_prazo": longo_prazo,
        "doacao": doacao,
        "renda": renda
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Recebi Salário", callback_data='set_salario')],
        [InlineKeyboardButton("🏠 Minha Renda 350€", callback_data='ver_renda'), InlineKeyboardButton("💸 Gastei Agora", callback_data='add_gasto')],
        [InlineKeyboardButton("📊 Ver Saldo MASTIGADO", callback_data='saldo')],
        [InlineKeyboardButton("🛒 Lista de Compras Inteligente", callback_data='lista')],
        [InlineKeyboardButton("🏪 Onde Comprar Mais Barato?", callback_data='loja')],
        [InlineKeyboardButton("📄 Relatório PDF Fim do Mês", callback_data='pasta')],
        [InlineKeyboardButton("🗑️ RESETAR - Começar do Zero", callback_data='reset1')]
    ]
    await update.message.reply_text("👑 **BOT DO DONO - MODO MINIMALISTA**\n\nFala 'recebi 1010' ou clica abaixo. Eu divido tudo na mente milionária e faço sobrar.", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    data = load_data()
    
    # Recebi salario
    if "recebi" in text:
        try:
            valor = float(text.replace("recebi","").replace("€","").strip().split()[0])
            data["salario"] = valor
            data["mes"] = datetime.datetime.now().strftime("%m/%Y")
            data["gastos"] = [] # limpa gastos do mes novo
            save_data(data)
            div = get_divisao_milionaria(valor, data["renda"])
            msg = f"✅ Salário {valor:.2f}€ guardado - Mês {data['mes']}\n\n"
            msg += f"🧠 **DIVISÃO MENTE MILIONÁRIA (Mastigado):**\n"
            msg += f"🏠 RENDA FIXA: {div['renda']:.2f}€ (já separado)\n"
            msg += f"🛒 MERCADO + NECESSIDADES: {div['sobra_necessidades']:.2f}€ (o que sobra dos 55%)\n"
            msg += f"🚀 LIBERDADE FINANCEIRA (investir/bot): {div['liberdade']:.2f}€ - NÃO TOCA\n"
            msg += f"📚 EDUCAÇÃO: {div['educacao']:.2f}€\n"
            msg += f"✈️ DIVERSÃO SONHOS (helicóptero/avião): {div['diversao']:.2f}€\n"
            msg += f"🏦 LONGO PRAZO/RESERVA: {div['longo_prazo']:.2f}€\n"
            msg += f"❤️ DOAÇÃO: {div['doacao']:.2f}€\n\n"
            msg += f"👉 Agora me fala cada gasto: 'gastei 15 lidl' ou 'gastei 20 renda' e eu desconto certo."
            await update.message.reply_text(msg, parse_mode='Markdown')
            return
        except:
            await update.message.reply_text("Escreve assim: recebi 1010")
            return

    # Gastei
    if "gastei" in text:
        try:
            partes = text.
[19/07/2026 02:28] Josuas: replace("gastei","").strip().split()
            valor = float(partes[0].replace("€",""))
            loja = " ".join(partes[1:]) if len(partes)>1 else "geral"
            data["gastos"].append({"valor": valor, "onde": loja, "data": datetime.datetime.now().strftime("%d/%m %H:%M")})
            save_data(data)
            
            total_gasto = sum(g["valor"] for g in data["gastos"])
            sobra = data["salario"] - total_gasto - data["renda"] if data["salario"] else 0
            
            div = get_divisao_milionaria(data["salario"], data["renda"])
            
            await update.message.reply_text(f"✅ Gasto {valor:.2f}€ em {loja} anotado.\nTotal gasto esse mês (sem renda): {total_gasto:.2f}€\n💰 Sobra real até agora: {sobra:.2f}€\n\nLimite de mercado que te sobra: {div['sobra_necessidades']:.2f}€ - Gastaste {total_gasto:.2f}€ = FALTA {div['sobra_necessidades']-total_gasto:.2f}€", parse_mode='Markdown')
            return
        except Exception as e:
            await update.message.reply_text(f"Escreve: gastei 20 pingo doce (erro: {e})")
            return

    # Outros textos -> saldo
    if text in ["saldo","slm","s"]:
        await mostrar_saldo(update)
        return

async def mostrar_saldo(update_or_query):
    data = load_data()
    if data["salario"] == 0:
        msg = "❌ Tu ainda não me disse quanto recebeste. Escreve: recebi 1010"
        if isinstance(update_or_query, Update):
            await update_or_query.message.reply_text(msg)
        else:
            await update_or_query.edit_message_text(msg)
        return
    
    div = get_divisao_milionaria(data["salario"], data["renda"])
    total_gasto = sum(g["valor"] for g in data["gastos"])
    gastos_lista = "\n".join([f"- {g['data']}: {g['valor']:.2f}€ em {g['onde']}" for g in data["gastos"][-10:]])
    
    sobra_final = data["salario"] - data["renda"] - total_gasto
    tem_que_sobrar = div["liberdade"]+div["educacao"]+div["longo_prazo"]+div["diversao"]+div["doacao"]

    msg = f"📊 **MÊS {data['mes']} - MASTIGADO**\n\n"
    msg += f"💵 Entrou: {data['salario']:.2f}€\n"
    msg += f"🏠 Renda: -{data['renda']:.2f}€\n"
    msg += f"🛒 Gastos: -{total_gasto:.2f}€\n"
    msg += f"-----------------------\n"
    msg += f"💰 **SOBRA REAL: {sobra_final:.2f}€**\n"
    msg += f"🎯 Tinha que sobrar mínimo: {tem_que_sobrar:.2f}€ (potes)\n\n"
    
    if sobra_final < 0:
        msg += f"🚨 ALERTA DONO: Tu já estourou! Para de comprar. Vai ficar sem reserva.\n\n"
    elif sobra_final < tem_que_sobrar:
        msg += f"⚠️ ATENÇÃO: Tá gastando potes que eram pra liberdade/diversão. Ajusta.\n\n"
    else:
        msg += f"✅ PARABÉNS DONO: Vai sobrar! Tu guardou potes.\n\n"

    msg += f"**Tua divisão:**\nNecessidades sobra p/ mercado: {div['sobra_necessidades']:.2f}€\nLiberdade: {div['liberdade']:.2f}€\nEducação: {div['educacao']:.2f}€\nDiversão: {div['diversao']:.2f}€\nLongo Prazo: {div['longo_prazo']:.2f}€\n\n"
    msg += f"**Últimos gastos:**\n{gastos_lista if gastos_lista else 'Nenhum ainda'}"

    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update_or_query.edit_message_text(msg, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    d = query.data

    if d == 'set_salario':
        await query.edit_message_text("Escreve: recebi 1010 (ou quanto recebeste)")
    elif d == 'ver_renda':
        await query.edit_message_text(f"🏠 Tua renda fixa é {data['renda']:.2f}€\nPara mudar escreve: renda 400")
    elif d == 'add_gasto':
        await query.edit_message_text("Escreve: gastei 12.50 lidl\nOu: gastei 20 mercado\nOu: gastei 5 bolt")
    elif d == 'saldo':
        await mostrar_saldo(query)
    elif d == 'lista':
        msg = "🛒 **LISTA DE COMPRAS INTELIGENTE DONO - 50€ SEMANA**\n\n"
        msg += "Pingo Doce/Lidl (Portimão):\n- Ovos 1.89€\n- Arroz 1.20€\n- Frango 3.
[19/07/2026 02:28] Josuas: 50€\n- Pão 1€\n- Legumes 4€\n- Iogurte 2€\n- Azeite 3€\nTotal ~20€\n\n"
        msg += "NÃO COMPRA: refrigerante, bolacha recheada, delivery. Isso rouba teu pote liberdade."
        await query.edit_message_text(msg, parse_mode='Markdown')
    elif d == 'loja':
        msg = "🏪 **ONDE COMPRAR EM PORTIMÃO - MODO DONO**\n\n"
        msg += "1. Lidl - mais barato pra base (arroz, ovo, frango)\n2. Pingo Doce - promoção 50% carne\n3. Continente - só se for com cupom\n\nRegra: Entra com lista, sai com lista. Sem lista = escravo do marketing."
        await query.edit_message_text(msg)
    elif d == 'pasta':
        # PDF simples
        total_gasto = sum(g["valor"] for g in data["gastos"])
        sobra = data["salario"] - data["renda"] - total_gasto
        msg = f"📄 **RELATÓRIO PASTA MINIMALISTA - {data['mes']}**\n\n"
        msg += f"Recebi: {data['salario']:.2f}€\nRenda: -{data['renda']:.2f}€\nGastos: -{total_gasto:.2f}€\nSobra: {sobra:.2f}€\n\n"
        msg += f"Gastos detalhados:\n" + "\n".join([f"{g['valor']}€ {g['onde']}" for g in data["gastos"]])
        msg += f"\n\nMente milionária: Tu guardaste ou gastaste? Ajusta próximo mês."
        await query.edit_message_text(msg)
    elif d == 'reset1':
        kb = [[InlineKeyboardButton("❌ Cancelar", callback_data='cancel'), InlineKeyboardButton("✅ SIM APAGAR", callback_data='reset2')]]
        await query.edit_message_text("⚠️ Vai apagar SALÁRIO e GASTOS do mês e começar do zero?", reply_markup=InlineKeyboardMarkup(kb))
    elif d == 'reset2':
        save_data({"salario": 0, "renda": 350, "gastos": [], "mes": datetime.datetime.now().strftime("%m/%Y")})
        await query.edit_message_text("✅ Tudo apagado. Pasta limpa. Escreve 'recebi 1010' pra começar. /start")
    elif d == 'cancel':
        await query.edit_message_text("Cancelado. /start")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot Dono 24h rodando...")
    app.run_polling()

if name == "__main__":
    main()
