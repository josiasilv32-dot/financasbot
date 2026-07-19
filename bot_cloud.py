import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- FUNÇÕES GENIAIS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💸 Adicionar Gasto", callback_data='add')],
        [InlineKeyboardButton("💰 Saldo Atual", callback_data='saldo'), InlineKeyboardButton("📊 Modo Dono", callback_data='dono')],
        [InlineKeyboardButton("📄 Pasta Minimalista (PDF)", callback_data='pasta')],
        [InlineKeyboardButton("🗑️ RESETAR TUDO", callback_data='reset_step1')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Bem-vindo, Dono. O que vamos resolver hoje?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'reset_step1':
        # Trava 1
        keyboard = [
            [InlineKeyboardButton("❌ NÃO, cancelar", callback_data='cancel')],
            [InlineKeyboardButton("✅ SIM, quero apagar tudo", callback_data='reset_step2')]
        ]
        await query.edit_message_text("⚠️ TEM CERTEZA? Vai apagar TUDO e começar do zero. Isso não tem volta.", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == 'reset_step2':
        # AQUI TU COLOCA TUA LÓGICA DE APAGAR DB/JSON
        # Ex: os.remove('financas.db') ou zerar dict
        # context.user_data.clear()
        await query.edit_message_text("✅ Feito. Tudo apagado. Pasta limpa. Começando do zero como dono minimalista. /start")

    elif data == 'dono':
        # Botão gênio 1
        await query.edit_message_text("👑 MODO DONO:\n\nEsse mês:\n- Trabalhou 60% pra JMR\n- 25% pra contas\n- 15% pra ti (Dono)\n\nMeta: Chegar em 50% pra ti. Quer ajustar?")

    elif data == 'pasta':
        # Botão gênio 2
        await query.edit_message_text("📄 Gerando tua Pasta Minimalista... (aqui vai gerar PDF limpo só com o essencial, igual tu entrando no jato)")
        # aqui entra função gera_pdf()

    elif data == 'cancel':
        await query.edit_message_text("Ufa, cancelado. Nada apagado. /start")

# --- START DO BOT ---
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()
