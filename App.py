import streamlit as st
import datetime
import json
import urllib.parse
import requests

# Configurazione della pagina ottimizzata per smartphone
st.set_page_config(page_title="BioTalee AI Ultra", page_icon="🌵", layout="centered")

st.title("🌵 BioTalee AI Ultra")
st.subheader("Assistente Agronomico d'Avanguardia per la Campagna")

# CONFIGURAZIONE CHIAVE API GEMINI
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("⚠️ Chiave API di Gemini non configurata! Inseriscila nei Secrets di Streamlit.")
    API_KEY = None

# Funzione con vincolo strutturale nativo del server di Google
def analizza_pianta_con_ia(nome_pianta):
    if not API_KEY:
        return None
        
    url = f"https://googleapis.com{API_KEY}"
    
    prompt = f"Analizza la riproduzione tramite talea della pianta: {nome_pianta}"
    
    # Vincolo nativo del server: forza Gemini a rispondere solo in formato dati puro
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "nome_corretto": {"type": "STRING"},
                    "temp_ottima": {"type": "INTEGER"},
                    "umidita_ottima": {"type": "INTEGER"},
                    "giorni_base": {"type": "INTEGER"},
                    "tipo_bio": {"type": "STRING"},
                    "esposizione": {"type": "STRING"},
                    "innaffiamento": {"type": "STRING"},
                    "metodo_veloce": {"type": "STRING"},
                    "terreno_ideale": {"type": "STRING"},
                    "finestra_stagionale": {"type": "STRING"}
                },
                "required": ["nome_corretto", "temp_ottima", "umidita_ottima", "giorni_base", "tipo_bio", "esposizione", "innaffiamento", "metodo_veloce", "terreno_ideale", "finestra_stagionale"]
            }
        }
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()
        text = res_json['candidates'][0]['content']['parts'][0]['text'].strip()
        return json.loads(text)
    except Exception as e:
        st.error("I server di calcolo non hanno risposto correttamente. Verifica la connessione e riprova.")
        return None

# Funzione per generare il link di Google Calendar
def crea_link_google_calendar(titolo, data_radicazione, note):
    base_url = "https://google.com"
    data_formattata = data_radicazione.strftime("%Y%m%d")
    data_param = f"{data_formattata}/{data_formattata}"
    
    params = {
        "text": titolo,
        "dates": data_param,
        "details": note,
        "sf": "true",
        "output": "xml"
    }
    return f"{base_url}&{urllib.parse.urlencode(params)}"

# Inizializzazione del diario
if "diario_talee" not in st.session_state:
    st.session_state.diario_talee = []

# TABS DELL'APPLICAZIONE
tab1, tab2, tab3 = st.tabs(["🤖 Simulatore & Ricerca", "📔 Il mio Diario", "🧪 Substrato Fai-da-Te"])

# ================= TAB 1: SIMULATORE & RICERCA IA =================
with tab1:
    st.header("🔍 Analisi Biologica della Pianta")
    pianta_input = st.text_input("Scrivi il nome o la specie della pianta:", placeholder="Es: Fico d'India, Limone, Crassula...")
    
    if pianta_input:
        if st.button("🧠 Avvia Ricerca con Gemini IA"):
            with st.spinner("L'IA sta estraendo i dati biologici..."):
                risultato = analizza_pianta_con_ia(pianta_input)
                if risultato:
                    st.session_state.pianta_focus = risultato
                    st.success(f"Profilo caricato per: {risultato['nome_corretto']}")
    if "pianta_focus" in st.session_state:
        d = st.session_state.pianta_focus
        st.markdown("---")
        
        st.markdown(f"### 📋 Scheda Tecnica: *{d['nome_corretto']}*")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"☀️ **Esposizione:** {d['esposizione']}")
            st.write(f"💧 **Innaffiamento:** {d['innaffiamento']}")
        with col_b:
            st.write(f"🌱 **Terreno Ideale (Teorico):** {d['terreno_ideale']}")
            st.write(f"⚡ **Metodo più Veloce:** {d['metodo_veloce']}")
            
        st.markdown(f"🗓️ **Finestra Stagionale (Prossimi 3 mesi):** {d['finestra_stagionale']}")
        
        st.markdown("---")
        st.write("**⚙️ Adatta il simulatore alle tue condizioni attuali:**")
        temperatura = st.slider("Temperatura ambiente attuale (°C):", 5, 40, 22)
        umidita = st.slider("Umidità ambientale attuale (%):", 10, 100, 60)
        
        diff_temp = abs(temperatura - d["temp_ottima"])
        score_temp = max(0, 100 - (diff_temp * 6))
        
        if d["tipo_bio"] == "grassa":
            score_umi = max(0, 100 - (abs(umidita - d["umidita_ottima"]) * 3))
            if umidita > 75: score_umi -= 25
        else:
            score_umi = max(0, 100 - (max(0, d["umidita_ottima"] - umidita) * 3))
            
        chance = min(100, max(0, int((score_temp * 0.5) + (score_umi * 0.5))))
        giorni_totali = d["giorni_base"]
        if temperatura < d["temp_ottima"]:
            giorni_totali = int(giorni_totali * (1 + (diff_temp * 0.06)))
            
        st.markdown("### 📈 Previsione di Radicazione")
        if chance > 75: st.success(f"Probabilità di successo alta: {chance}%")
        elif chance > 45: st.warning(f"Probabilità di successo media: {chance}%")
        else: st.error(f"Probabilità di successo bassa: {chance}%")
        
        st.info(f"⏱️ **Tempo stimato:** circa **{giorni_totali} giorni**.")
        
        if st.button("💾 Salva ed emetti Codice di Tracciamento"):
            data_oggi = datetime.date.today()
            data_fine = data_oggi + datetime.timedelta(days=giorni_totali)
            nuovo_id = f"TL-{data_oggi.strftime('%y%m%d')}-{len(st.session_state.diario_talee)+1}"
            
            nuova_talea = {
                "id": nuovo_id,
                "pianta": d['nome_corretto'],
                "data_inizio": data_oggi.strftime("%d/%m/%Y"),
                "data_fine_obj": data_fine,
                "data_fine_str": data_fine.strftime("%d/%m/%Y"),
                "chance": chance,
                "stato": "In corso ⏳"
            }
            st.session_state.diario_talee.append(nuova_talea)
            st.session_state.ultimo_id = nuovo_id
            st.session_state.ultima_data_fine = data_fine
            st.rerun()
            
    if "ultimo_id" in st.session_state:
        st.success(f"🎉 **Talea Registrata!**")
        st.markdown(f"🏷️ Scrivi questo **Codice Identificativo** sul vasetto: **{st.session_state.ultimo_id}**")
        
        titolo_cal = f"🌱 Controllo Talea {st.session_state.ultimo_id}"
        note_cal = f"Verifica radicazione per la talea salvata nel tuo diario BioTalee."
        link_cal = crea_link_google_calendar(titolo_cal, st.session_state.ultima_data_fine, note_cal)
        
        st.markdown(f"[🗓️ Aggiungi Promemoria su Google Calendar]({link_cal})")

# ================= TAB 2: DIARIO DI TRACCIAMENTO =================
with tab2:
    st.header("📔 Registro delle Talee in Campagna")
    
    if not st.session_state.diario_talee:
        st.write("Nessuna talea attiva nel registro.")
    else:
        data_oggi = datetime.date.today()
        
        for idx, t in enumerate(st.session_state.diario_talee):
            avviso_notifica = ""
            if t["stato"] == "In corso ⏳" and data_oggi >= t["data_fine_obj"]:
                avviso_notifica = "🚨 **[PRONTA DA CONTROLLARE]** "
                
            with st.expander(f"{avviso_notifica}ID: {t['id']} - {t['pianta']} ({t['stato']})"):
                st.write(f"📅 **Inizio:** {t['data_inizio']} | **Fine Teorica:** {t['data_fine_str']}")
                st.write(f"📊 **Probabilità calcolata:** {t['chance']}%")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎉 Radicata!", key=f"rad_{idx}"):
                        st.session_state.diario_talee[idx]["stato"] = "Radicata con successo! 🥳"
                        st.rerun()
                with col2:
                    if st.button("❌ Marcita", key=f"morta_{idx}"):
                        st.session_state.diario_talee[idx]["stato"] = "Non riuscita 🪵"
                        st.rerun()

# ================= TAB 3: CREATORE DI SUBSTRATO FAI-DA-TE =================
with tab3:
    st.header("🧪 Calcolatore di Substrato Personalizzato")
    st.write("Inserisci gli inerti e i materiali che hai fisicamente a disposizione nella tua campagna:")
    
    materiali = st.multiselect(
        "Seleziona cosa hai a disposizione intorno a te:",
        ["Terra di campo comune", "Sabbia di fiume / Lavata", "Pietra pomice", "Lapillo vulcanico", "Compost autoprodotto", "Terriccio universale vecchio", "Argilla espansa", "Perlite"]
    )
    
    if materiali and "pianta_focus" in st.session_state:
        pianta_target = st.session_state.pianta_focus["nome_corretto"]
        terreno_teorico = st.session_state.pianta_focus["terreno_ideale"]
        
        if st.button("⚖️ Calcola Ricetta Volumetrica con i miei ingredienti"):
            with st.spinner("Gemini sta bilanciando le proporzioni..."):
                 if API_KEY:
                     url_sub = f"https://googleapis.com{API_KEY}"
                     prompt_sub = f"Devo fare il substrato per una talea di {pianta_target}. Il terreno ideale sarebbe: {terreno_teorico}. Ho solo questi materiali: {', '.join(materiali)}. Generami una ricetta in tazze o parti usando solo questi materiali, spiegando perché. Sii breve (max 80 parole)."
                     payload_sub = {"contents": [{"parts": [{"text": prompt_sub}]}]}
                     try:
                         response_sub = requests.post(url_sub, headers={'Content-Type': 'application/json'}, json=payload_sub)
                         st.markdown("### 🧑‍🔬 La tua Ricetta su Misura:")
                         st.info(response_sub.json()['candidates'][0]['content']['parts'][0]['text'])
                     except:
                         st.error("Errore nel calcolo del substrato.")
    elif not materiali:
        st.write("⚠️ Seleziona almeno un materiale per calcolare la ricetta.")
    else:
        st.write("⚠️ Cacciatori di piante: Cerca prima una pianta nel Tab 1 per poterne calcolare il substrato su misura.")
