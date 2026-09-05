from flask import Flask, request, jsonify, render_template_string, send_file
import re
from datetime import datetime
import os

app = Flask(__name__)

# 🔑 Chave de acesso
CHAVE_ACESSO = "5411"
NOME_ARQUIVO = "resultados_busca.txt"

# 📦 Analisa o arquivo e separa por URL → email:senha
def carregar_base():
    base = {}
    try:
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                padrao = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+):(.+)$'
                match = re.search(padrao, linha)
                if match:
                    email = match.group(1).strip().lower()
                    senha = match.group(2).strip()
                    url_parte = linha[:match.start()].strip()
                    nome_site = extrair_dominio(url_parte)
                    if nome_site not in base:
                        base[nome_site] = []
                    base[nome_site].append({"email": email, "senha": senha})
    except FileNotFoundError:
        pass
    return base

# 🌐 Extrai o nome do site/domínio de qualquer URL
def extrair_dominio(url):
    url = url.lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    partes = url.split('/')[0].split('.')
    if len(partes) >= 2:
        return f"{partes[-2]}.{partes[-1]}"
    return partes[0]

# 🔍 Busca na base pela URL digitada
def buscar_por_url(url_digitada):
    nome_site_alvo = extrair_dominio(url_digitada)
    base = carregar_base()
    for site, lista in base.items():
        if nome_site_alvo in site or site in nome_site_alvo:
            return lista, site
    return None, nome_site_alvo

# 💾 Salva o resultado em arquivo TXT
def salvar_resultado(site, lista, url_busca):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(NOME_ARQUIVO, "a", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write(f"📅 DATA/HORA: {agora}\n")
        f.write(f"🌐 SITE: {site}\n")
        f.write(f"🔍 URL BUSCADA: {url_busca}\n")
        f.write("-" * 50 + "\n")
        for i, item in enumerate(lista, 1):
            f.write(f"REGISTRO {i}:\n")
            f.write(f"   E-MAIL: {item['email']}\n")
            f.write(f"   SENHA:  {item['senha']}\n")
            f.write("-" * 50 + "\n")
        f.write(f"✅ TOTAL: {len(lista)} registro(s)\n")
        f.write("=" * 50 + "\n\n")
    return NOME_ARQUIVO

# 📄 Interface — MG — Terminal Hacker
@app.route('/')
def pagina_inicial():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MG — Sistema de Credenciais</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #050505;
                color: #00ff41;
                font-family: 'Courier New', 'Consolas', monospace;
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
                position: relative;
            }
            body::before {
                content: "";
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: repeating-linear-gradient(transparent, transparent 2px, rgba(0,255,65,0.03) 2px, rgba(0,255,65,0.03) 4px);
                pointer-events: none; z-index: 100;
            }
            .container { max-width: 850px; margin: 0 auto; }
            .banner {
                border: 2px solid #00ff41; border-radius: 6px; padding: 20px; margin-bottom: 25px;
                background: rgba(0,255,65,0.03); box-shadow: 0 0 20px rgba(0,255,65,0.15);
                text-align: center;
            }
            .banner pre { color: #00ff41; font-size: 10px; line-height: 1.1; margin: 0; }
            .titulo {
                text-align: center; margin: 15px 0 5px; font-size: 32px; letter-spacing: 8px;
                text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41; font-weight: bold;
            }
            .subtitulo { text-align: center; font-size: 12px; color: #00cc33; opacity: 0.8; margin-top: 5px; }
            .aviso { text-align: center; font-size: 11px; color: #ffcc00; margin-top: 8px; animation: piscar 1.5s infinite; }
            @keyframes piscar { 0%,100%{opacity:1} 50%{opacity:0.3} }
            .terminal {
                border: 2px solid #00ff41; border-radius: 8px; background: rgba(0,0,0,0.85);
                padding: 25px; box-shadow: 0 0 30px rgba(0,255,65,0.2);
            }
            .linha { margin-bottom: 18px; }
            .prompt { color: #00ff41; font-weight: bold; margin-bottom: 6px; }
            .prompt span { color: #00ccff; }
            input, textarea {
                width: 100%; background: #0a0a0a; border: 1px solid #00ff41;
                border-radius: 4px; color: #00ff41; padding: 12px 15px;
                font-family: 'Courier New', monospace; font-size: 14px; outline: none;
                transition: all 0.2s;
            }
            input:focus, textarea:focus { border-color: #00ffaa; box-shadow: 0 0 12px rgba(0,255,65,0.4); }
            textarea { min-height: 100px; resize: vertical; }
            input::placeholder, textarea::placeholder { color: #006622; }
            
            /* BOTÃO PRINCIPAL */
            .btn {
                width: 100%; padding: 14px; background: transparent;
                border: 2px solid #00ff41; color: #00ff41;
                font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold;
                text-transform: uppercase; letter-spacing: 2px; cursor: pointer;
                transition: all 0.3s; margin-top: 5px;
            }
            .btn:hover { background: #00ff41; color: #000; box-shadow: 0 0 25px #00ff41; }
            
            /* BOTÃO DE DOWNLOAD — ABAIXO DO INICIAR BUSCA */
            .btn-download {
                border: 2px solid #00ff41; color: #00ff41;
                margin-top: 12px; display: none;
            }
            .btn-download:hover { background: #00ff41; color: #000; box-shadow: 0 0 25px #00ff41; }
            .btn-download.visivel { display: block; }
            
            .saida {
                margin-top: 25px; border: 1px dashed #00ff41; border-radius: 6px;
                padding: 18px; background: rgba(0,20,5,0.6); min-height: 120px;
            }
            .saida-titulo {
                color: #00ccff; font-size: 13px; margin-bottom: 15px;
                border-bottom: 1px solid #003311; padding-bottom: 8px;
                display: flex; justify-content: space-between;
            }
            .codigo { font-size: 13px; line-height: 1.8; }
            .sucesso { color: #00ff41; }
            .erro { color: #ff3333; }
            .aviso-txt { color: #ffcc00; }
            .email { color: #00ccff; }
            .senha { color: #ff33ff; text-shadow: 0 0 4px #ff33ff; }
            .barra-progresso {
                height: 8px; background: #0a0a0a; border: 1px solid #00ff41;
                border-radius: 4px; margin: 10px 0; overflow: hidden;
            }
            .barra-preenchida {
                height: 100%; width: 0%;
                background: linear-gradient(90deg, #00ff41, #00ffaa);
                animation: carregar 1.2s ease-out forwards;
            }
            @keyframes carregar { 0%{width:0%} 100%{width:100%} }
            .piscar { animation: blink 0.8s infinite; }
            @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="banner">
                <pre>
  ███╗   ███╗ ██████╗ 
  ████╗ ████║██╔════╝ 
   ██╔████╔██║██║  ███╗ 
    ██║╚██╔╝██║██║   ██║  
 ██║ ╚═╝ ██║╚██████╔╝
 ╚═╝     ╚═╝ ╚═════╝ 
                </pre>
                <h1 class="titulo">MG</h1>
                <p class="subtitulo">SISTEMA DE BUSCA DE CREDENCIAIS — VERSÃO 2.6</p>
                <p class="aviso">⚠️ ACESSO RESTRITO — SISTEMA PRIVADO ⚠️</p>
            </div>
            <div class="terminal">
                <div class="linha">
                    <div class="prompt">[<span>ADMIN@MG</span>:~]# CHAVE_ACESSO</div>
                    <input type="password" id="chave" placeholder="Insira a chave de acesso...">
                </div>
                <div class="linha">
                    <div class="prompt">[<span>ADMIN@MG</span>:~]# URL_ALVO</div>
                    <textarea id="urlBusca" placeholder="Cole a URL alvo...&#10;Ex: https://accounts.google.com/signin"></textarea>
                </div>
                <!-- BOTÃO PRINCIPAL -->
                <button class="btn" onclick="executarBusca()">▶ INICIAR BUSCA</button>
                <!-- BOTÃO DE DOWNLOAD — FICA AQUI EMBAIXO, APARECE DEPOIS DA BUSCA -->
                <button id="btnDownload" class="btn btn-download" onclick="window.location.href='/download'">💾 BAIXAR RESULTADO .TXT</button>
                <!-- ÁREA DE SAÍDA -->
                <div class="saida">
                    <div class="saida-titulo">
                        <span>► SAÍDA_DO_SISTEMA</span>
                        <span id="hora">--/--/---- --:--</span>
                    </div>
                    <div class="codigo" id="conteudo">
                        <span class="aviso-txt">Aguardando comando...<span class="piscar">_</span></span>
                    </div>
                </div>
            </div>
        </div>
        <script>
            function atualizarHora() {
                document.getElementById('hora').textContent = new Date().toLocaleString('pt-BR');
            }
            atualizarHora();
            function executarBusca() {
                const chave = document.getElementById('chave').value;
                const url = document.getElementById('urlBusca').value.trim();
                const conteudo = document.getElementById('conteudo');
                const btnDownload = document.getElementById('btnDownload');
                // ESCONDE o botão de download antes de buscar
                btnDownload.classList.remove('visivel');
                if (!chave) {
                    conteudo.innerHTML = '<span class="erro">❌ ERRO: Chave de acesso não fornecida!</span>';
                    return;
                }
                if (!url) {
                    conteudo.innerHTML = '<span class="erro">❌ ERRO: URL alvo não informada!</span>';
                    return;
                }
                conteudo.innerHTML = `
                    ⏳ INICIANDO BUSCA...<br>
                    ⏳ ANALISANDO URL ALVO...<br>
                    <div class="barra-progresso"><div class="barra-preenchida"></div></div>
                    ⏳ LOCALIZANDO CORRESPONDÊNCIAS...<br>
                    <span class="piscar">PROCESSANDO...</span>
                `;
                setTimeout(() => {
                    fetch(`/buscar?chave=${encodeURIComponent(chave)}&url=${encodeURIComponent(url)}`)
                        .then(r => r.json())
                        .then(dados => {
                            if (dados.status === 'sucesso') {
                                // ✅ MOSTRA o botão de download ABAIXO do botão INICIAR BUSCA
                                btnDownload.classList.add('visivel');
                                let html = `<span class="sucesso">✅ ${dados.quantidade} REGISTRO(S) ENCONTRADO(S)</span><br><br>`;
                                dados.lista.forEach((item, i) => {
                                    html += `──────────────────────────────<br>`;
                                    html += `<b>REGISTRO ${i+1}:</b> ${dados.site}<br>`;
                                    html += `📧 <span class="email">USUÁRIO: ${item.email}</span><br>`;
                                    html += `🔑 <span class="senha">SENHA: ${item.senha}</span><br>`;
                                });
                                conteudo.innerHTML = html;
                            } else if (dados.status === 'erro_chave') {
                                conteudo.innerHTML = `<span class="erro">❌ ACESSO NEGADO — ${dados.mensagem}</span>`;
                            } else {
                                conteudo.innerHTML = `<span class="aviso-txt">⚠️ ${dados.mensagem}</span>`;
                            }
                            atualizarHora();
                        })
                        .catch(() => {
                            conteudo.innerHTML = '<span class="erro">❌ FALHA NA CONEXÃO</span>';
                        });
                }, 1400);
            }
        </script>
    </body>
    </html>
    """)

# 🔍 Rota de busca
@app.route('/buscar', methods=['GET'])
def buscar():
    chave = request.args.get('chave')
    url_digitada = request.args.get('url', '').strip()

    if chave != CHAVE_ACESSO:
        return jsonify({"status": "erro_chave", "mensagem": "Chave de acesso inválida!"}), 403

    if not url_digitada:
        return jsonify({"status": "erro", "mensagem": "URL alvo não informada!"}), 400

    logins, nome_site = buscar_por_url(url_digitada)

    if logins:
        salvar_resultado(nome_site, logins, url_digitada)
        return jsonify({
            "status": "sucesso",
            "site": nome_site,
            "quantidade": len(logins),
            "lista": logins
        })
    else:
        return jsonify({
            "status": "nao_encontrado",
            "mensagem": f"Nenhum registro encontrado para: {nome_site}"
        })

# 📥 Rota de Download do Arquivo
@app.route('/download')
def download():
    if os.path.exists(NOME_ARQUIVO):
        return send_file(NOME_ARQUIVO, as_attachment=True)
    return "Arquivo não encontrado. Faça uma busca primeiro.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
