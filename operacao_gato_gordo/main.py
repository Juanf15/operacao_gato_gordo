import pygame
import random
import sys
import config # Importa as nossas constantes!

# 1. Inicialização do Motor
pygame.init()
tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
pygame.display.set_caption("Operação Gato Gordo 🐱")
relogio = pygame.time.Clock()


# --- NOVO: Variáveis para o Flash ---
tempo_inicio_flash = 0
duracao_flash = 2500  # Aumentado para 2.5 segundos para o efeito Flashbang completo

# FONTES DO JOGO
fonte_titulo = pygame.font.Font(None, 72) 
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 28) 

# ==========================================
# CARREGANDO OS EFEITOS SONOROS E MÚSICA
# ==========================================

# 1. Som de Destruição
try:
    som_destruicao = pygame.mixer.Sound("assets/sounds/destruicao.wav")
    som_destruicao.set_volume(0.7)
except Exception as e:
    print(f"Aviso: Não achou destruicao.wav - {e}")

# 2. Som do Flashbang
try:
    som_flashbang = pygame.mixer.Sound("assets/sounds/flashbang.wav")
    som_flashbang.set_volume(1.0)
except Exception as e:
    print(f"Aviso: Não achou flashbang.wav - {e}")

# 3. Música de Fundo
try:
    pygame.mixer.music.load("assets/sounds/musica_fundo.mp3") 
    pygame.mixer.music.set_volume(0.4) 
    pygame.mixer.music.play(-1) 
except Exception as e:
    print(f"Aviso: Não achou musica_fundo.mp3 - {e}")

# ==========================================
# CARREGANDO AS TEXTURAS (SPRITES)
# ==========================================
# --- NOVO: ATUM AUMENTADO E RETANGULAR (120x90) ---
img_comida = pygame.image.load("assets/sprites/sache.png").convert_alpha()
img_comida = pygame.transform.scale(img_comida, (120, 90)) # Ajustado para não perder legibilidade

img_sofa = pygame.image.load("assets/sprites/sofa.png").convert_alpha()
img_sofa = pygame.transform.scale(img_sofa, (240, 120)) 

img_mesa = pygame.image.load("assets/sprites/mesa.png").convert_alpha()
img_mesa = pygame.transform.scale(img_mesa, (160, 120)) 

# Cadeira da Esquerda
img_cadeira_esq = pygame.image.load("assets/sprites/cadeira_esquerda.png").convert_alpha()
img_cadeira_esq = pygame.transform.scale(img_cadeira_esq, (100, 100)) # Mudou para 100, 100

# Cadeira da Direita
img_cadeira_dir = pygame.image.load("assets/sprites/cadeira_direita.png").convert_alpha()
img_cadeira_dir = pygame.transform.scale(img_cadeira_dir, (100, 100)) # Mudou para 100, 100

img_tv = pygame.image.load("assets/sprites/tv.png").convert_alpha()
# Aumentamos a altura de 80 para 160
img_tv = pygame.transform.scale(img_tv, (200, 160))

img_planta = pygame.image.load("assets/sprites/planta.png").convert_alpha()
img_planta = pygame.transform.scale(img_planta, (80, 80)) 

# 2. Estado Inicial do Jogo
estado_jogo = "MENU" 
score = 0
angulo_rotacao = 0
mensagem_sistema = ""
comidas_comidas = 0 # --- NOVO: Contador de quantas vezes o gato comeu ---

# Variáveis do Gato
tamanho_gato = 30
gato_x, gato_y = (config.LARGURA // 2) - 15, (config.ALTURA // 2) + 150
velocidade = 5

# ==========================================
# 1. MÓVEIS FIXOS 
# ==========================================
def gerar_moveis():
    moveis = []
    # (Rect(x, y, largura, altura), Textura_Imagem)
    moveis.append((pygame.Rect(100, 190, 240, 120), img_sofa))    # Sofá movido para baixo!
    moveis.append((pygame.Rect(400, 300, 160, 120), img_mesa))    # Mesa
    
# Agora cada uma recebe a sua imagem específica
    moveis.append((pygame.Rect(290, 310, 100, 100), img_cadeira_esq))  # Cadeira 1 Esquerda
    moveis.append((pygame.Rect(570, 310, 100, 100), img_cadeira_dir))  # Cadeira 2 Direita
    
    # Aumentamos o último número (altura) de 80 para 160
    moveis.append((pygame.Rect(550, 80, 200, 160), img_tv))      # TV/Estante
    
    # Vasos de Planta (80x80)
    moveis.append((pygame.Rect(30, 40, 80, 80), img_planta))       # Planta Topo Esquerda
    moveis.append((pygame.Rect(680, 440, 80, 80), img_planta))     # Planta Baixo Direita
    moveis.append((pygame.Rect(30, 440, 80, 80), img_planta))      # Planta Baixo Esquerda
    return moveis

moveis_destrutiveis = gerar_moveis() 
moveis_voando = [] 

# ==========================================
# 2. COMIDA (Spawn e Hitbox ajustados para o tamanho novo)
# ==========================================
def gerar_comida():
    while True:
        # --- Hitbox físico atualizado para o tamanho retangular (120x90) ---
        novo_rect = pygame.Rect(
            random.randint(0, config.LARGURA - 120), 
            random.randint(50, config.ALTURA - 90), 
            120, 90 # Nova Largura e Altura
        )
        colidiu = False
        for movel in moveis_destrutiveis:
            if novo_rect.colliderect(movel[0]):
                colidiu = True
                break
        if not colidiu:
            return novo_rect

comida = gerar_comida() 

# Função para fatiar o sprite sheet
def carregar_sprites(caminho, colunas, linhas, fatiar_cheio=False):
    sheet = pygame.image.load(caminho).convert_alpha()
    frame_largura = sheet.get_width() // colunas
    frame_altura = sheet.get_height() // linhas
    frames = []
    for linha in range(linhas):
        linha_frames = []
        for coluna in range(colunas):
            x = coluna * frame_largura
            if fatiar_cheio:
                y = linha * frame_altura
                rect = pygame.Rect(x, y, frame_largura, frame_altura)
            else:
                corte_topo = 15 
                y = (linha * frame_altura) + corte_topo
                rect = pygame.Rect(x, y, frame_largura, frame_altura - corte_topo)
            
            imagem_frame = sheet.subsurface(rect).copy()
            cor_fundo = imagem_frame.get_at((0, 0))
            imagem_frame.set_colorkey(cor_fundo)
            linha_frames.append(imagem_frame)
        frames.append(linha_frames)
    return frames

# Carrega e fatia as imagens dos gatos
animacoes_gato_magro = carregar_sprites("assets/sprites/gato_primeira_fase.jpg", 3, 4)
animacoes_gato_gordinho = carregar_sprites("assets/sprites/gato_segunda_fase.jpg", 3, 4)
animacoes_gato_obeso = carregar_sprites("assets/sprites/gato_terceira_fase.jpg", 3, 4)

# Imagem Fase 4
imagem_bolota_base = pygame.image.load("assets/sprites/gato03.png").convert_alpha()
velocidade_giro = 15 

# Foto do casal (Final)
foto_casal = pygame.image.load("assets/sprites/foto_casal.jpg").convert()
foto_casal = pygame.transform.scale(foto_casal, (400, 300))

# Sprite do casal (Intro TELA CHEIA)
sprite_casal = pygame.image.load("assets/sprites/sprite_casal.png").convert() 
sprite_casal = pygame.transform.scale(sprite_casal, (config.LARGURA, config.ALTURA)) 

# Carregamento do cenário
fundo_sala = pygame.image.load("assets/sprites/fundo_sala_limpa.png").convert()
fundo_sala = pygame.transform.scale(fundo_sala, (config.LARGURA, config.ALTURA))

# Variáveis para controlar a animação
direcao_atual = 0  
frame_atual = 0
contador_animacao = 0

# 3. O Game Loop Principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()
    tela.fill(config.COR_FUNDO)

    # ==========================================
    # DESENHANDO O CENÁRIO E OBJETOS FIXOS
    # ==========================================
    if estado_jogo in ["JOGANDO", "GORDINHO", "OBESO", "BOLOTA"]:
        tela.blit(fundo_sala, (0, 0))
        
        for movel in moveis_destrutiveis:
            tela.blit(movel[1], movel[0].topleft)

    # ==========================================
    # ESTADO -1: MENU INICIAL
    # ==========================================
    if estado_jogo == "MENU":
        tela.fill((20, 20, 30)) 
        
        txt_titulo = fonte_titulo.render("OPERAÇÃO GATO GORDO", True, (255, 215, 0)) 
        txt_sub = fonte.render("Especial de Dia dos Namorados ❤️", True, (255, 105, 180)) 
        
        tela.blit(txt_titulo, (config.LARGURA//2 - txt_titulo.get_width()//2, config.ALTURA//2 - 80))
        tela.blit(txt_sub, (config.LARGURA//2 - txt_sub.get_width()//2, config.ALTURA//2 - 10))

        if pygame.time.get_ticks() % 1000 < 500:
            txt_start = fonte.render("[ Pressione ENTER para Começar ]", True, (200, 200, 200))
            tela.blit(txt_start, (config.LARGURA//2 - txt_start.get_width()//2, config.ALTURA//2 + 80))

        if teclas[pygame.K_RETURN]:
            estado_jogo = "INTRO"

    # ==========================================
    # ESTADO 0: INTRODUÇÃO (CUTSCENE TELA CHEIA)
    # ==========================================
    elif estado_jogo == "INTRO":
        tela.blit(sprite_casal, (0, 0))

        caixa_x, caixa_y = 50, config.ALTURA - 150
        caixa_largura, caixa_altura = config.LARGURA - 100, 100
        
        pygame.draw.rect(tela, config.COR_CAIXA, (caixa_x, caixa_y, caixa_largura, caixa_altura))
        pygame.draw.rect(tela, config.COR_TEXTO, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        texto_fala = fonte.render("Vocês: 'Vamos sair. Coma a sua ração e se comporte!'", True, config.COR_TEXTO)
        texto_dica = fonte.render("[Pressione ESPAÇO para fechar a porta]", True, (150, 150, 150))
        
        tela.blit(texto_fala, (caixa_x + 20, caixa_y + 20))
        tela.blit(texto_dica, (caixa_x + 20, caixa_y + 60))

        if teclas[pygame.K_SPACE]: 
            estado_jogo = "JOGANDO"
            mensagem_sistema = "OBJETIVO: coma sua ração"

    # ==========================================
    # ESTADO 1: JOGANDO
    # ==========================================
    elif estado_jogo == "JOGANDO":
        andando = False
        dx, dy = 0, 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx = -velocidade; direcao_atual = 1; andando = True
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx = velocidade; direcao_atual = 2; andando = True
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: dy = -velocidade; direcao_atual = 3; andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy = velocidade; direcao_atual = 0; andando = True

        if andando:
            hitbox_teste = pygame.Rect(gato_x + dx, gato_y + dy, tamanho_gato, tamanho_gato)
            bateu_parede = False
            
            if hitbox_teste.left < 0 or hitbox_teste.right > config.LARGURA or hitbox_teste.top < 40 or hitbox_teste.bottom > config.ALTURA:
                bateu_parede = True
            for movel in moveis_destrutiveis:
                if hitbox_teste.colliderect(movel[0]):
                    bateu_parede = True
                    break
            
            if not bateu_parede:
                gato_x += dx
                gato_y += dy

            contador_animacao += 1
            if contador_animacao >= 10: 
                frame_atual = (frame_atual + 1) % 3
                contador_animacao = 0
        else:
            frame_atual = 0

        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        # Colisão com a comida (agora maior)
        if hitbox_gato.colliderect(comida):
            score += 10
            tamanho_gato += 2
            comidas_comidas += 1 # Aumenta o contador!
            comida = gerar_comida()
            
            if comidas_comidas == 1:
                mensagem_sistema = "não é o suficiente, coma mais,"
            elif comidas_comidas == 2:
                mensagem_sistema = "Ainda não é o bastante, coma mais"
            elif comidas_comidas == 3:
                estado_jogo = "GORDINHO"
                velocidade = 4
                mensagem_sistema = "Você ganhou uns quilinhos, mas a fome é imparável, coma mais"

        # Desenha a imagem do sachê
        tela.blit(img_comida, comida.topleft)
        
        imagem_atual = animacoes_gato_magro[direcao_atual][frame_atual]
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 2: GATO GORDINHO
    # ==========================================
    elif estado_jogo == "GORDINHO":
        andando = False
        dx, dy = 0, 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx = -velocidade; direcao_atual = 1; andando = True
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx = velocidade; direcao_atual = 2; andando = True
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: dy = -velocidade; direcao_atual = 3; andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy = velocidade; direcao_atual = 0; andando = True

        if andando:
            hitbox_teste = pygame.Rect(gato_x + dx, gato_y + dy, tamanho_gato, tamanho_gato)
            bateu_parede = False
            
            if hitbox_teste.left < 0 or hitbox_teste.right > config.LARGURA or hitbox_teste.top < 40 or hitbox_teste.bottom > config.ALTURA:
                bateu_parede = True
            for movel in moveis_destrutiveis:
                if hitbox_teste.colliderect(movel[0]):
                    bateu_parede = True
                    break
            
            if not bateu_parede:
                gato_x += dx
                gato_y += dy

            contador_animacao += 1
            if contador_animacao >= 12: 
                frame_atual = (frame_atual + 1) % 3
                contador_animacao = 0
        else:
            frame_atual = 0

        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        if hitbox_gato.colliderect(comida):
            score += 15 
            tamanho_gato += 2
            comidas_comidas += 1
            comida = gerar_comida()
            
            if comidas_comidas == 4:
                mensagem_sistema = "CONSUMA MAIS"
            elif comidas_comidas == 5:
                estado_jogo = "OBESO"
                velocidade = 2 
                mensagem_sistema = "COMA MAIS, MAIS, MAIS E MAIS"

        tela.blit(img_comida, comida.topleft)
        
        imagem_atual = animacoes_gato_gordinho[direcao_atual][frame_atual] 
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 3: GATO OBESO
    # ==========================================
    elif estado_jogo == "OBESO":
        andando = False
        dx, dy = 0, 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: dx = -velocidade; direcao_atual = 2; andando = True 
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx = velocidade; direcao_atual = 1; andando = True 
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: dy = -velocidade; direcao_atual = 3; andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: dy = velocidade; direcao_atual = 0; andando = True

        if andando:
            hitbox_teste = pygame.Rect(gato_x + dx, gato_y + dy, tamanho_gato, tamanho_gato)
            bateu_parede = False
            
            if hitbox_teste.left < 0 or hitbox_teste.right > config.LARGURA or hitbox_teste.top < 40 or hitbox_teste.bottom > config.ALTURA:
                bateu_parede = True
            for movel in moveis_destrutiveis:
                if hitbox_teste.colliderect(movel[0]):
                    bateu_parede = True
                    break
            
            if not bateu_parede:
                gato_x += dx
                gato_y += dy

            contador_animacao += 1
            if contador_animacao >= 12: 
                frame_atual = (frame_atual + 1) % 3
                contador_animacao = 0
        else:
            frame_atual = 0

        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        if hitbox_gato.colliderect(comida):
            score += 20 
            tamanho_gato += 2
            comidas_comidas += 1
            comida = gerar_comida()
            
            if comidas_comidas == 6:
                estado_jogo = "BOLOTA"
                velocidade = 6 
                mensagem_sistema = "DESTRUA TUDO!!!!!" 

        tela.blit(img_comida, comida.topleft)
        
        imagem_atual = animacoes_gato_obeso[direcao_atual][frame_atual] 
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2.2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 4: BOLOTA
    # ==========================================
    elif estado_jogo == "BOLOTA":
        andando = False
        andando_horizontal = False 
        dx, dy = 0, 0
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            dx = -velocidade; andando = True; andando_horizontal = True; angulo_rotacao += velocidade_giro
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            dx = velocidade; andando = True; andando_horizontal = True; angulo_rotacao -= velocidade_giro

        if not andando_horizontal:
            if teclas[pygame.K_UP] or teclas[pygame.K_w]: 
                dy = -velocidade; andando = True; angulo_rotacao += velocidade_giro
            elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
                dy = velocidade; andando = True; angulo_rotacao += velocidade_giro

        if angulo_rotacao >= 360: angulo_rotacao -= 360
        if angulo_rotacao < 0: angulo_rotacao += 360

        hitbox_teste = pygame.Rect(gato_x + dx, gato_y + dy, tamanho_gato, tamanho_gato)
        if not (hitbox_teste.left < 0 or hitbox_teste.right > config.LARGURA or hitbox_teste.top < 40 or hitbox_teste.bottom > config.ALTURA):
            gato_x += dx
            gato_y += dy

        hitbox_bolota = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        
        for movel in moveis_destrutiveis[:]: 
            if hitbox_bolota.colliderect(movel[0]): 
                rect_movel, textura_movel = movel 
                moveis_destrutiveis.remove(movel)
                score += 50
                tamanho_gato += 2 
                velocidade += 1 

                try:
                    som_destruicao.play()
                except:
                    pass

                surf_movel = textura_movel.copy()
                vx_explosao = random.choice([-20, -15, 15, 20])
                vy_explosao = random.choice([-20, -15, 15, 20])
                forca_giro = random.choice([-30, -25, 25, 30])
                
                moveis_voando.append({
                    'surface': surf_movel,
                    'x': rect_movel.centerx,
                    'y': rect_movel.centery,
                    'vx': vx_explosao,
                    'vy': vy_explosao,
                    'angulo': 0,
                    'giro': forca_giro
                })
                
        for voando in moveis_voando[:]:
            voando['x'] += voando['vx']
            voando['y'] += voando['vy']
            voando['angulo'] += voando['giro']
            
            surf_girada = pygame.transform.rotate(voando['surface'], voando['angulo'])
            rect_girado = surf_girada.get_rect(center=(voando['x'], voando['y']))
            tela.blit(surf_girada, rect_girado.topleft)
            
            if (voando['x'] < -200 or voando['x'] > config.LARGURA + 200 or 
                voando['y'] < -200 or voando['y'] > config.ALTURA + 200):
                moveis_voando.remove(voando)
                
        if len(moveis_destrutiveis) == 0 and len(moveis_voando) == 0:
                    estado_jogo = "FLASH_EXPLOSAO" 
                    tempo_inicio_flash = pygame.time.get_ticks() 
                    
                    # --- NOVO: Toca a granada de luz! ---
                    try:
                        som_flashbang.play()
                    except:
                        pass

        proporcao = imagem_bolota_base.get_width() / imagem_bolota_base.get_height()
        nova_altura = int(tamanho_gato * 2.2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_escalada = pygame.transform.scale(imagem_bolota_base, (nova_largura, nova_altura))
        
        imagem_girada = pygame.transform.rotate(imagem_escalada, angulo_rotacao)
        centro_x = gato_x + (tamanho_gato // 2)
        centro_y = gato_y + (tamanho_gato // 2)
        rect_girado = imagem_girada.get_rect(center=(centro_x, centro_y))
        tela.blit(imagem_girada, rect_girado.topleft)

    # ==========================================
    # ESTADO 5: CORRUPÇÃO
    # ==========================================
    elif estado_jogo == "CORRUPCAO":
        cor_glitch = (random.randint(150, 255), random.randint(50, 255), random.randint(50, 255))
        tela.fill(cor_glitch)
        
        txt1 = fonte.render("Você ficou TÃO GORDO E GRANDE...", True, (0, 0, 0))
        txt2 = fonte.render("Que rompeu um terço do ESPAÇO-TEMPO!", True, (255, 255, 255))
        txt3 = fonte.render("[Aperte ESPAÇO para seu destino final]", True, (50, 50, 50))
        
        tela.blit(txt1, (config.LARGURA//2 - txt1.get_width()//2, config.ALTURA//2 - 50))
        tela.blit(txt2, (config.LARGURA//2 - txt2.get_width()//2, config.ALTURA//2))
        tela.blit(txt3, (config.LARGURA//2 - txt3.get_width()//2, config.ALTURA//2 + 60))

        if teclas[pygame.K_SPACE]:
            estado_jogo = "FIM"

    # ==========================================
    # --- NOVO ESTADO: FLASH EXPLOSÃO ---
    # ==========================================
    elif estado_jogo == "FLASH_EXPLOSAO":
        tela.blit(fundo_sala, (0, 0))
        
        # Mantém o Gato Bolota desenhado no mesmo lugar
        proporcao = imagem_bolota_base.get_width() / imagem_bolota_base.get_height()
        nova_altura = int(tamanho_gato * 2.2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_escalada = pygame.transform.scale(imagem_bolota_base, (nova_largura, nova_altura))
        
        imagem_girada = pygame.transform.rotate(imagem_escalada, angulo_rotacao)
        centro_x = gato_x + (tamanho_gato // 2)
        centro_y = gato_y + (tamanho_gato // 2)
        rect_girado = imagem_girada.get_rect(center=(centro_x, centro_y))
        tela.blit(imagem_girada, rect_girado.topleft)

        # Lógica do clarão branco
        tempo_atual = pygame.time.get_ticks()
        tempo_passado = tempo_atual - tempo_inicio_flash

        if tempo_passado < duracao_flash:
            # Cria a tela branca de cegueira
            flash_surf = pygame.Surface((config.LARGURA, config.ALTURA))
            flash_surf.fill((255, 255, 255))
            
            # Matemática do Flashbang: 
            # Começa no Alpha 255 (totalmente branco/opaco) e vai caindo até 0 (transparente)
            alpha = int(255 * (1 - (tempo_passado / duracao_flash)))
            
            # Impede que o alpha fique negativo (evita travamentos)
            if alpha < 0: alpha = 0
                
            flash_surf.set_alpha(alpha)
            tela.blit(flash_surf, (0,0))
        else:
            # Acabou o flash, a poeira baixa e a realidade quebrou!
            estado_jogo = "CORRUPCAO"

    # ==========================================
    # ESTADO 6: TELA FINAL
    # ==========================================
    elif estado_jogo == "FIM":
        tela.fill(config.COR_CAIXA) 
        
        foto_rect = foto_casal.get_rect(center=(config.LARGURA // 2, config.ALTURA // 2))
        tela.blit(foto_casal, foto_rect.topleft)

        texto_final = fonte.render("Você destruiu o espaço-tempo e foi parar em outra dimensão...", True, config.COR_TEXTO)
        texto_sub = fonte.render("Onde vocês são dois gatos gordos! ❤️", True, (255, 105, 180))
        
        tela.blit(texto_final, (config.LARGURA//2 - texto_final.get_width()//2, foto_rect.top - 40))
        tela.blit(texto_sub, (config.LARGURA//2 - texto_sub.get_width()//2, foto_rect.bottom + 20))

    # ==========================================
    # DESENHO DA BARRA DE MENSAGEM
    # ==========================================
    if estado_jogo in ["JOGANDO", "GORDINHO", "OBESO", "BOLOTA"]:
        pygame.draw.rect(tela, (20, 20, 20), (0, 0, config.LARGURA, 40)) 
        txt_obj = fonte_pequena.render(mensagem_sistema, True, (255, 215, 0)) 
        tela.blit(txt_obj, (config.LARGURA//2 - txt_obj.get_width()//2, 10))

    pygame.display.flip()
    relogio.tick(config.FPS)