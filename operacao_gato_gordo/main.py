import pygame
import random
import sys
import config # Importa nossas constantes!

# 1. Inicialização do Motor
pygame.init()
tela = pygame.display.set_mode((config.LARGURA, config.ALTURA))
pygame.display.set_caption("Operação Gato Gordo 🐱")
relogio = pygame.time.Clock()
fonte = pygame.font.Font(None, 36)

# 2. Estado Inicial do Jogo
estado_jogo = "INTRO" # Começa na historinha
score = 0
angulo_rotacao = 0

# Variáveis do Gato
tamanho_gato = 30
gato_x, gato_y = config.LARGURA // 2, config.ALTURA // 2
velocidade = 5

# Função para spawnar os sachês
def gerar_comida():
    return pygame.Rect(
        random.randint(0, config.LARGURA - 20), 
        random.randint(0, config.ALTURA - 20), 
        20, 20
    )

comida = gerar_comida()

# Móveis para a fase BOLOTA
def gerar_moveis(quantidade):
    moveis = []
    for _ in range(quantidade):
        # Cria retângulos marrons aleatórios para representar os móveis
        moveis.append(pygame.Rect(random.randint(50, config.LARGURA - 50), random.randint(50, config.ALTURA - 50), 40, 40))
    return moveis

moveis_destrutiveis = gerar_moveis(5) # Spawna 5 móveis pela casa

# Função para fatiar o sprite sheet - ATUALIZADA!
def carregar_sprites(caminho, colunas, linhas, fatiar_cheio=False):
    """
    Carrega e fatia um spritesheet.
    'fatiar_cheio' define se corta o topo (padrão) ou fatia o frame inteiro (para rotação).
    """
    # Carrega a imagem principal
    sheet = pygame.image.load(caminho).convert_alpha()
    
    # Descobre o tamanho exato de cada frame fatiado
    frame_largura = sheet.get_width() // colunas
    frame_altura = sheet.get_height() // linhas
    
    frames = []
    for linha in range(linhas):
        linha_frames = []
        for coluna in range(colunas):
            
            # Calcula a posição X do corte
            x = coluna * frame_largura
            
            if fatiar_cheio:
                # ==========================================
                # O SEGREDO DO CORTE INTEIRO (Para Fase 4)
                # Fatia o frame inteiro, sem corte no topo. Preserva o giro.
                # ==========================================
                y = linha * frame_altura
                rect = pygame.Rect(x, y, frame_largura, frame_altura)
            else:
                # ==========================================
                # O SEGREDO DO CORTE ANTI-SUJEIRA (Fases 1, 2, 3)
                # Vamos ignorar os 15 primeiros pixels do topo de cada frame.
                # ==========================================
                corte_topo = 15 
                y = (linha * frame_altura) + corte_topo
                # Recorta descontando o pedaço que pulamos no topo
                rect = pygame.Rect(x, y, frame_largura, frame_altura - corte_topo)
            
            # O .copy() é crucial aqui para gerar uma imagem independente e limpa
            imagem_frame = sheet.subsurface(rect).copy()
            
            # Pega a cor do primeiro pixel (0,0) e a torna transparente
            cor_fundo = imagem_frame.get_at((0, 0))
            imagem_frame.set_colorkey(cor_fundo)
            
            linha_frames.append(imagem_frame)
        frames.append(linha_frames)
        
    # Retorna uma matriz onde:
    # frames[0] = Baixo, frames[1] = Esquerda, frames[2] = Direita, frames[3] = Cima
    return frames

# Carrega e fatia as imagens das 4 fases evolutivas do gato!
animacoes_gato_magro = carregar_sprites("assets/sprites/gato_primeira_fase.jpg", 3, 4)
animacoes_gato_gordinho = carregar_sprites("assets/sprites/gato_segunda_fase.jpg", 3, 4)
animacoes_gato_obeso = carregar_sprites("assets/sprites/gato_terceira_fase.jpg", 3, 4)

# ==========================================
# Carregamento do Asset da Fase 4 (NOVO MÉTODO)
# ==========================================
# Carrega apenas UMA imagem do gato gordo para a fase BOLOTA
imagem_bolota_base = pygame.image.load("assets/sprites/gato03.png").convert_alpha()
velocidade_giro = 15 # Define a velocidade que ele vai rolar

# Carrega a foto de vocês para o final
foto_casal = pygame.image.load("assets/sprites/foto_casal.jpg").convert()
foto_casal = pygame.transform.scale(foto_casal, (400, 300))

# Variáveis para controlar a animação
direcao_atual = 0  # Começa olhando para baixo
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
    # ESTADO 0: INTRODUÇÃO (A História)
    # ==========================================
    if estado_jogo == "INTRO":
        pygame.draw.rect(tela, config.COR_GATO, (gato_x, gato_y, tamanho_gato, tamanho_gato))
        pygame.draw.rect(tela, config.COR_COMIDA, comida)

        # Caixa de Texto
        caixa_x, caixa_y = 50, config.ALTURA - 150
        caixa_largura, caixa_altura = config.LARGURA - 100, 100
        pygame.draw.rect(tela, config.COR_CAIXA, (caixa_x, caixa_y, caixa_largura, caixa_altura))
        pygame.draw.rect(tela, config.COR_TEXTO, (caixa_x, caixa_y, caixa_largura, caixa_altura), 3)

        texto_fala = fonte.render("Vocês: 'Fique bonzinho, deixamos um sachê pra você.'", True, config.COR_TEXTO)
        texto_dica = fonte.render("[Pressione ENTER para fechar a porta]", True, (150, 150, 150))
        
        tela.blit(texto_fala, (caixa_x + 20, caixa_y + 20))
        tela.blit(texto_dica, (caixa_x + 20, caixa_y + 60))

        if teclas[pygame.K_RETURN]:
            estado_jogo = "JOGANDO"

    # ==========================================
    # ESTADO 1: O CAOS COMEÇA (JOGANDO)
    # ==========================================
    elif estado_jogo == "JOGANDO":
        andando = False
        
        # Movimentação e atualização da direção
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            gato_x -= velocidade
            direcao_atual = 1 # Linha 1 do Sprite: Esquerda
            andando = True
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            gato_x += velocidade
            direcao_atual = 2 # Linha 2 do Sprite: Direita
            andando = True
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: 
            gato_y -= velocidade
            direcao_atual = 3 # Linha 3 do Sprite: Cima
            andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
            gato_y += velocidade
            direcao_atual = 0 # Linha 0 do Sprite: Baixo
            andando = True

        # Controle da velocidade da animação (troca de frame)
        if andando:
            contador_animacao += 1
            if contador_animacao >= 10: # A cada 10 ticks, muda o passinho
                frame_atual = (frame_atual + 1) % 3 # Fica variando entre 0, 1 e 2
                contador_animacao = 0
        else:
            # Se não estiver andando, volta para o frame 0 (parado)
            frame_atual = 0

        # LÓGICA DE COLISÃO E CRESCIMENTO
        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)

        if hitbox_gato.colliderect(comida):
            score += 10
            tamanho_gato += 2
            comida = gerar_comida()
            
            # Transição APÓS 1 COMIDA
            if tamanho_gato >= 32:
                estado_jogo = "GORDINHO"
                velocidade = 4

        pygame.draw.rect(tela, config.COR_COMIDA, comida)
        
        imagem_atual = animacoes_gato_magro[direcao_atual][frame_atual]
        
        # ==========================================
        # LIFTING VISUAL (CORRIGIDO)
        # ==========================================
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        # Centraliza o gato no hitbox invisível
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 2: GATO GORDINHO
    # ==========================================
    elif estado_jogo == "GORDINHO":
        andando = False
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            gato_x -= velocidade; direcao_atual = 1; andando = True
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            gato_x += velocidade; direcao_atual = 2; andando = True
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: 
            gato_y -= velocidade; direcao_atual = 3; andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
            gato_y += velocidade; direcao_atual = 0; andando = True

        if andando:
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
            comida = gerar_comida()
            
            # Transição APÓS 2 COMIDAS (Tamanho vai para 34)
            if tamanho_gato >= 34:
                estado_jogo = "OBESO"
                velocidade = 2 

        pygame.draw.rect(tela, config.COR_COMIDA, comida)
        
        imagem_atual = animacoes_gato_gordinho[direcao_atual][frame_atual] 
        
        # LIFTING VISUAL (CORRIGIDO)
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 3: GATO OBESO (Quase explodindo)
    # ==========================================
    elif estado_jogo == "OBESO":
        andando = False
        
        # --- Ajuste das direções invertidas ---
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            gato_x -= velocidade; direcao_atual = 2; andando = True # Esquerda agora é 2
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            gato_x += velocidade; direcao_atual = 1; andando = True # Direita agora é 1
        elif teclas[pygame.K_UP] or teclas[pygame.K_w]: 
            gato_y -= velocidade; direcao_atual = 3; andando = True
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
            gato_y += velocidade; direcao_atual = 0; andando = True

        if andando:
            contador_animacao += 1
            if contador_animacao >= 12: # <-- Diminuído de 18 para 12! Passos mais rápidos
                frame_atual = (frame_atual + 1) % 3
                contador_animacao = 0
        else:
            frame_atual = 0

        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        if hitbox_gato.colliderect(comida):
            score += 20 
            tamanho_gato += 2
            comida = gerar_comida()
            
            # Transição APÓS 3 COMIDAS (Tamanho vai para 36)
            if tamanho_gato >= 36:
                estado_jogo = "BOLOTA"

        pygame.draw.rect(tela, config.COR_COMIDA, comida)
        
        imagem_atual = animacoes_gato_obeso[direcao_atual][frame_atual] 
        
        # LIFTING VISUAL (CORRIGIDO E CENTRALIZADO)
        proporcao = imagem_atual.get_width() / imagem_atual.get_height()
        nova_altura = int(tamanho_gato * 2.2) 
        nova_largura = int(nova_altura * proporcao)
        imagem_atual = pygame.transform.scale(imagem_atual, (nova_largura, nova_altura))
        
        # Centraliza perfeitamente o gato no hitbox para ele crescer a partir do meio
        pos_x = gato_x + (tamanho_gato // 2) - (nova_largura // 2)
        pos_y = gato_y + (tamanho_gato // 2) - (nova_altura // 2)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # === ESTADO 4: BOLOTA (Rotação Nativa Direcional Perfeita) ===
    # ==========================================
    elif estado_jogo == "BOLOTA":
        andando = False
        andando_horizontal = False # Flag para prioridade de giro
        
        # MOVIMENTAÇÃO E LÓGICA DE GIRO
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            gato_x -= velocidade
            andando = True
            andando_horizontal = True
            # === GIRAR PARA ESQUERDA ===
            # Incrementa o ângulo (anti-horário)
            angulo_rotacao += velocidade_giro
            
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            gato_x += velocidade
            andando = True
            andando_horizontal = True
            # === GIRAR PARA DIREITA ===
            # Decrementa o ângulo (horário)
            angulo_rotacao -= velocidade_giro

        # Se não estiver andando para os lados, mas estiver subindo/descendo, 
        # ele continua girando (vamos manter o giro anti-horário padrão aqui)
        if not andando_horizontal:
            if teclas[pygame.K_UP] or teclas[pygame.K_w]: 
                gato_y -= velocidade; andando = True; angulo_rotacao += velocidade_giro
            elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
                gato_y += velocidade; andando = True; angulo_rotacao += velocidade_giro

        # Mantém o ângulo entre 0 e 359
        if angulo_rotacao >= 360: angulo_rotacao -= 360
        if angulo_rotacao < 0: angulo_rotacao += 360

        # Lógica de Colisão com Móveis
        hitbox_bolota = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        for movel in moveis_destrutiveis[:]: 
            if hitbox_bolota.colliderect(movel):
                moveis_destrutiveis.remove(movel)
                score += 50
                velocidade += 1 
                
        # Desenha os Móveis restantes
        for movel in moveis_destrutiveis:
            pygame.draw.rect(tela, (139, 69, 19), movel) 

        # ==========================================
        # DESENHO DA BOLOTA GIRANDO CENTRALIZADA
        # ==========================================
        proporcao = imagem_bolota_base.get_width() / imagem_bolota_base.get_height()
        nova_altura = int(tamanho_gato * 2.2) # Escala proporcional da fase bolota
        nova_largura = int(nova_altura * proporcao)
        imagem_escalada = pygame.transform.scale(imagem_bolota_base, (nova_largura, nova_altura))
        
        # Gira a imagem redimensionada
        imagem_girada = pygame.transform.rotate(imagem_escalada, angulo_rotacao)
        
        # Centraliza exatamente no hitbox invisível do gato
        centro_x = gato_x + (tamanho_gato // 2)
        centro_y = gato_y + (tamanho_gato // 2)
        rect_girado = imagem_girada.get_rect(center=(centro_x, centro_y))
        
        # Desenha na tela!
        tela.blit(imagem_girada, rect_girado.topleft)

        texto_alerta = fonte.render("ALERTA: MASSA CRÍTICA! [Aperte ESPAÇO para quebrar tudo]", True, config.COR_TEXTO)
        tela.blit(texto_alerta, (20, 20))

        if teclas[pygame.K_SPACE]:
            estado_jogo = "FIM"

    # ==========================================
    # ESTADO 3: TELA FINAL
    # ==========================================
    elif estado_jogo == "FIM":
        tela.fill(config.COR_CAIXA) 
        
        # 1. Posiciona e desenha a foto bem no centro da tela
        foto_rect = foto_casal.get_rect(center=(config.LARGURA // 2, config.ALTURA // 2))
        tela.blit(foto_casal, foto_rect.topleft)

        # 2. Textos (Ajustados para ficar acima e abaixo da foto)
        texto_final = fonte.render("Você quebrou o universo...", True, config.COR_TEXTO)
        texto_sub = fonte.render("Feliz Dia dos Namorados pra nós, gatos gordos ❤️", True, (255, 105, 180))
        
        # Texto em cima
        tela.blit(texto_final, (config.LARGURA//2 - texto_final.get_width()//2, foto_rect.top - 40))
        # Texto embaixo
        tela.blit(texto_sub, (config.LARGURA//2 - texto_sub.get_width()//2, foto_rect.bottom + 20))

    pygame.display.flip()
    relogio.tick(config.FPS)