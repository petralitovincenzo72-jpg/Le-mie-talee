import streamlit as st
import datetime

# Configurazione della pagina
st.set_page_config(page_title="BioTalee - Diario & Simulatore", page_icon="🌱", layout="centered")

st.title("🌱 BioTalee")
st.subheader("Diario di Propagazione & Simulatore di Microclima")

# DATI BIOLOGICI DELLE PIANTE (Database di calcolo)
PIANTE_DATA = {
    "Rosmarino": {"temp_ottima": 21, "umidita_ottima": 85, "giorni_base": 20, "difficolta": "Facile"},
    "Olivo": {"temp_ottima": 24, "umidita_ottima": 90, "giorni_base": 45, "difficolta": "Media"},
    "Ficus": {"temp_ottima": 25, "umidita_ottima": 95, "giorni_base": 30, "difficolta": "Media"}
}

# Inizializzazione del database nello stato della pagina per non perdere i dati durante la sessione
if "diario_talee" not in st.session_state:
    st.session_state.diario_talee = []

# TABS PER NAVIGARE NELL'APP
tab1, tab2 = st.tabs(["📊 Simulatore di Radicazione", "📔 Il mio Diario"])

# ================= TAB 1: SIMULATORE =================
with tab1:
    st.header("Calcola la probabilità di successo")
    
    # Input dell'utente
    pianta_scelta = st.selectbox("Seleziona la pianta da riprodurre:", list(PIANTE_DATA.keys()))
    tipo_talea = st.radio("Tipo di talea:", ["Erbacea / Tenera", "Semilegnosa", "Legnosa"])
    
    st.markdown("---")
    st.write("**Condizioni del tuo microclima attuale (Serra o Casa):**")
    temperatura = st.slider("Temperatura dell'aria (°C):", min_value=5, max_value=40, value=20)
    umidita = st.slider("Umidità ambientale (%):", min_value=20, max_value=100, value=70)
    ormone = st.checkbox("Usi un ormone radicante? (Naturale o chimico)")

    # ALGORITMO DI SIMULAZIONE BOTANICA
    dati = PIANTE_DATA[pianta_scelta]
    
    # 1. Calcolo penalità Temperatura
    diff_temp = abs(temperatura - dati["temp_ottima"])
    score_temp = max(0, 100 - (diff_temp * 6)) # Perde il 6% di chance per ogni grado di distanza dall'ottimo
    
    # 2. Calcolo penalità Umidità
    diff_umi = max(0, dati["umidita_ottima"] - umidita)
    score_umi = max(0, 100 - (diff_umi * 3)) # L'aria secca è letale per le talee
    
    # 3. Calcolo finale combinato
    chance_successo = (score_temp * 0.5) + (score_umi * 0.5)
    
    # Bonus ormone e modificatori tipo talea
    if ormone:
        chance_successo += 15
    if tipo_talea == "Semilegnosa":
        chance_successo += 5
        
    chance_successo = min(100, max(0, int(chance_successo)))
    
    # Calcolo giorni stimati
    giorni_stimati = dati["giorni_base"]
    if temperatura < dati["temp_ottima"]:
        giorni_stimati = int(giorni_stimati * (1 + (diff_temp * 0.05))) # Il freddo rallenta il metabolismo

    # MOSTRA I RISULTATI DELLA SIMULAZIONE
    st.markdown("### 📈 Resoconto Previsionale")
    
    if chance_successo > 75:
        st.success(f"**Probabilità di successo alta: {chance_successo}%**")
    elif chance_successo > 45:
        st.warning(f"**Probabilità di successo media: {chance_successo}%**")
    else:
        st.error(f"**Probabilità di successo bassa: {chance_successo}%**")
        
    st.info(f"⏱️ **Tempo stimato per le prime radici:** circa **{giorni_stimati} giorni**.")
    
    # Suggerimenti agronomici dinamici
    st.markdown("**💡 Consiglio dell'IA:**")
    if umidita < (dati["umidita_ottima"] - 10):
        st.write("⚠️ *L'umidità è troppo bassa! Copri la talea con un sacchetto di plastica trasparente o usa un propagatore per creare l'effetto serra.*")
    if temperatura < (dati["temp_ottima"] - 4):
        st.write("⚠️ *Il freddo sta rallentando la radicazione. Se puoi, usa un tappetino riscaldante sotto il vaso.*")
    if chance_successo >= 80:
        st.write("✅ *Le condizioni sono ottimali. Mantieni il substrato umido ma non inzuppato per evitare marciumi.*")

    # Bottone per salvare direttamente nel diario
    if st.button("💾 Salva questa configurazione nel Diario"):
        nuova_talea = {
            "pianta": pianta_scelta,
            "tipo": tipo_talea,
            "data": datetime.date.today().strftime("%d/%m/%Y"),
            "chance": chance_successo,
            "giorni": giorni_stimati,
            "stato": "In corso ⏳"
        }
        st.session_state.diario_talee.append(nuova_talea)
        st.toast("Salvato nel diario con successo!")

# ================= TAB 2: DIARIO =================
with tab2:
    st.header("📔 Le tue Talee Attive")
    
    if not st.session_state.diario_talee:
        st.write("Non hai ancora salvato nessuna talea. Usa il simulatore per registrare il tuo primo esperimento!")
    else:
        for idx, t in enumerate(st.session_state.diario_talee):
            with st.expander(f"🌱 {t['pianta']} ({t['tipo']}) - Iniziata il {t['data']}"):
                st.write(f"**Probabilità iniziale stimata:** {t['chance']}%")
                st.write(f"**Attesa stimata:** {t['giorni']} giorni")
                st.write(f"**Stato attuale:** {t['stato']}")
                
                # Bottoni di aggiornamento stato
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎉 Radicata!", key=f"rad_{idx}"):
                        st.session_state.diario_talee[idx]["stato"] = "Radicata con successo! 🥳"
                        st.rerun()
                with col2:
                    if st.button("❌ Marcita/Morta", key=f"morta_{idx}"):
                        st.session_state.diverse_talee[idx]["stato"] = "Non riuscita 🪵"
                        st.rerun()
