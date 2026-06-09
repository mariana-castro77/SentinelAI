import streamlit as st
import base64

# Função robusta para ler o arquivo local
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return None

# --- CSS E ANIMAÇÕES PARA O ROBO E PARALLAX ---
st.markdown("""
<style>
    /* Animação de flutuação suave */
    @keyframes floating {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-25px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }
    
    .robo-animado {
        width: 280px; /* Tamanho otimizado para o seu layout */
        animation: floating 4.5s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(255, 30, 30, 0.6));
        transition: transform 0.3s ease;
    }
    
    .robo-animado:hover {
        transform: scale(1.05); /* Pequeno zoom ao passar o mouse */
    }

    /* Parallax aprimorado: movimento mais perceptível */
    .stApp {
        background: radial-gradient(circle at center, rgba(140,10,10,1) 0%, rgba(10,2,2,1) 70%, rgba(0,0,0,1) 100%) !important;
        background-attachment: fixed !important;
        background-size: cover;
    }
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DA PÁGINA (SUBSTITUA A PRIMEIRA PARTE DO SEU CÓDIGO) ---
if not st.session_state["termo_aceito"]:
    st.markdown("<style>[data-testid='stSidebar']{display:none;} header{display:none!important;}</style>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([0.5, 3, 0.5])
    with c2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Injeção da imagem animada
        img_data = get_image_base64("robo.png")
        if img_data:
            st.markdown(f"""
                <div style="display: flex; justify-content: center; margin-bottom: 30px;">
                    <img src="data:image/png;base64,{img_data}" class="robo-animado">
                </div>
            """, unsafe_allow_html=True)
        
        # Seu container principal do card continua abaixo...
        st.markdown('<div class="hud-container-soc">', unsafe_allow_html=True)
        # ... (insira o restante do seu HTML do termo aqui)
