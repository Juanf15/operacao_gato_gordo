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

# Função para fatiar o sprite sheet
def carregar_sprites(caminho, colunas, linhas):
    # Carrega a imagem principal
    sheet = pygame.image.load(caminho).convert_alpha()
    
    # Descobre o tamanho exato de cada frame fatiado
    frame_largura = sheet.get_width() // colunas
    frame_altura = sheet.get_height() // linhas
    
    frames = []
    for linha in range(linhas):
        linha_frames = []
        for coluna in range(colunas):
            # Calcula a posição X e Y do corte
            x = coluna * frame_largura
            y = linha * frame_altura
            
            # Recorta aquele quadradinho específico
            rect = pygame.Rect(x, y, frame_largura, frame_altura)
            imagem_frame = sheet.subsurface(rect)
            
            # Pega a cor do primeiro pixel (0,0) e a torna transparente (tira o fundo preto/branco)
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

# Carrega e fatia a imagem da Bolota rolando (Fase 4)
# Como é uma bolota rolando, pegamos apenas o primeiro frame (ele já é redondo)
animacoes_bolota = carregar_sprites("assets/sprites/gato_quarta_fase.png", 3, 4)
imagem_bolota = animacoes_bolota[0][0]
imagem_bolota.set_colorkey((255, 255, 255)) # Remove o fundo branco se houver

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

        # ==========================================
        # LÓGICA DE COLISÃO E CRESCIMENTO
        # ==========================================
        # 1. Cria o hitbox invisível do gato acompanhando a posição dele
        hitbox_gato = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)

        # 2. Verifica se o hitbox do gato se sobrepôs ao hitbox da comida
        if hitbox_gato.colliderect(comida):
            score += 10              # Aumenta a pontuação
            tamanho_gato += 2        # O gato começa a engordar visualmente!
            comida = gerar_comida()  # Reposiciona a comida na tela
            
            # Transição APÓS 1 COMIDA (Tamanho inicial é 30, vai para 32)
            if tamanho_gato >= 32:
                estado_jogo = "GORDINHO"
                velocidade = 4

        pygame.draw.rect(tela, config.COR_COMIDA, comida)
        
        imagem_atual = animacoes_gato_magro[direcao_atual][frame_atual]
        # Faz a imagem inchar e engordar em tempo real baseada no tamanho_gato!
        imagem_atual = pygame.transform.scale(imagem_atual, (tamanho_gato * 2, tamanho_gato * 2))
        
        pos_x = gato_x - (imagem_atual.get_width() // 4)
        pos_y = gato_y - (imagem_atual.get_height() // 4)
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
        imagem_atual = pygame.transform.scale(imagem_atual, (tamanho_gato * 2, tamanho_gato * 2))
        
        pos_x = gato_x - (imagem_atual.get_width() // 4)
        pos_y = gato_y - (imagem_atual.get_height() // 4)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 3: GATO OBESO (Quase explodindo)
    # ==========================================
    elif estado_jogo == "OBESO":
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
            if contador_animacao >= 18: # Passos muito pesados e lentos
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
        imagem_atual = pygame.transform.scale(imagem_atual, (tamanho_gato * 2, tamanho_gato * 2))
        
        pos_x = gato_x - (imagem_atual.get_width() // 4)
        pos_y = gato_y - (imagem_atual.get_height() // 4)
        tela.blit(imagem_atual, (pos_x, pos_y))

    # ==========================================
    # ESTADO 4: MODO BOLOTA 
    # ==========================================
    elif estado_jogo == "BOLOTA":
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
            gato_x -= velocidade; angulo_rotacao += 10
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
            gato_x += velocidade; angulo_rotacao -= 10
        if teclas[pygame.K_UP] or teclas[pygame.K_w]: 
            gato_y -= velocidade; angulo_rotacao += 10
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: 
            gato_y += velocidade; angulo_rotacao -= 10

        # Lógica de Colisão com Móveis
        hitbox_bolota = pygame.Rect(gato_x, gato_y, tamanho_gato, tamanho_gato)
        for movel in moveis_destrutiveis[:]: # Copia a lista para remover itens com segurança
            if hitbox_bolota.colliderect(movel):
                moveis_destrutiveis.remove(movel) # O móvel é esmagado!
                score += 50
                velocidade += 1 # Ele gira/anda mais rápido a cada móvel destruído!
                
        # Desenha os Móveis restantes
        for movel in moveis_destrutiveis:
            pygame.draw.rect(tela, (139, 69, 19), movel) # Cor de madeira (Marrom)

        # ==========================================
        # DESENHO DO GATO BOLOTA (A ESFERA)
        # ==========================================
        # Redimensiona a imagem_bolota para o tamanho gigante atual do gato
        bolota_escala = pygame.transform.scale(imagem_bolota, (tamanho_gato * 2, tamanho_gato * 2))
        
        gato_rotacionado = pygame.transform.rotate(bolota_escala, angulo_rotacao)
        rect_rotacionado = gato_rotacionado.get_rect(center=(gato_x + tamanho_gato//2, gato_y + tamanho_gato//2))
        tela.blit(gato_rotacionado, rect_rotacionado.topleft)

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