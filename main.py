import pygame
import sys
import random

pygame.init() # Configuração inicial do jogo: inicialização do pygame
LARGURA, ALTURA = 600, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Trabalho CG - Centopeia")

# Definição das cores
PRETO, BRANCO, VERDE, VERMELHO, AZUL, AMARELO = (0,0,0), (255,255,255), (0,255,0), (255,0,0), (0,150,255), (255,255,0)
MARROM = (139, 69, 19)

# e carregamento das fontes utilizadas na interface.
fps = pygame.time.Clock()
fonte_ui = pygame.font.SysFont("Arial", 25)
fonte_grande = pygame.font.SysFont("Arial", 50) 

class Gnomo: # Metodo construtor da classe Gnomo, como posição, velocidade e tamanho.(VETOR)
    def __init__(self):
        self.pos = pygame.Vector2(LARGURA // 2, ALTURA - 60)
        self.vel = 8
        self.tamanho = 10

    def mover(self, teclas): #Método responsável por mover o gnomo com as teclas do teclado
        if teclas[pygame.K_LEFT] and self.pos.x > 20: self.pos.x -= self.vel #ESQUERDA A
        if teclas[pygame.K_RIGHT] and self.pos.x < LARGURA - 20: self.pos.x += self.vel #DIREITA D
        if teclas[pygame.K_UP] and self.pos.y > ALTURA - 180: self.pos.y -= self.vel #CIMA
        if teclas[pygame.K_DOWN] and self.pos.y < ALTURA - 20: self.pos.y += self.vel #BAIXO

    def desenhar(self, superficie): # caracteristicas do Gnomo
        pontos = [(self.pos.x, self.pos.y - self.tamanho),
                  (self.pos.x - self.tamanho, self.pos.y + self.tamanho),
                  (self.pos.x + self.tamanho, self.pos.y + self.tamanho)]
        pygame.draw.polygon(superficie, AZUL, pontos)
        pygame.draw.polygon(superficie, BRANCO, pontos, 2)

class  Tiro: # classe Tiro, como posição, velocidade e tamanho.(VETOR)
    def __init__(self, x, y, vetor_vel):
        self.pos = pygame.Vector2(x, y)
        self.vel = vetor_vel

    def mover(self):
        self.pos += self.vel

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, BRANCO, (int(self.pos.x), int(self.pos.y)), 4)

class Inimigo: # classe Inimigo, metodo construtor da centopeia(VETOR)
    def __init__(self, x, y, direcao):
        self.pos = pygame.Vector2(x, y)
        self.direcao = direcao
        self.velocidade = 5
        self.raio = 10 

    def mover(self):
        self.pos.x += self.direcao * self.velocidade

class Jogo: # Classe principal responsável por controlar toda a lógica do jogo
    def __init__(self):
        self.resetar()

    def resetar(self): # Reinicia todas as variáveis do jogo
        self.gnomo = Gnomo()
        self.tiros = []
        self.corpo = [Inimigo(30 * i, 60, 1) for i in range(10)]
        self.cogumelos = [pygame.Vector2(random.randrange(40, 580, 20), random.randrange(120, 600, 20)) for _ in range(20)]
        
        #Tempo do jogo
        self.tempo_limite = 15
        self.tempo_inicio = pygame.time.get_ticks()
        self.tempo_acumulado = 0 
        self.tempo_vitoria = 0   
        self.inimigo_dividido = False #Estado 
        self.estado = "JOGANDO" 

    def disparar(self, direcao):   # Cria um tiro dependendo da direção do disparo
        if direcao == "cima": 
            vel = pygame.Vector2(0, -12)
        elif direcao == "esq": 
            vel = pygame.Vector2(-12, 0)
        elif direcao == "dir": 
            vel = pygame.Vector2(12, 0)
            
        self.tiros.append(Tiro(self.gnomo.pos.x, self.gnomo.pos.y, vel))

    def atualizar(self):
        if self.estado != "JOGANDO": 
            return

        # Verifica se todos os inimigos foram derrotados
        if len(self.corpo) == 0:
            tempo_atual_fase = (pygame.time.get_ticks() - self.tempo_inicio) // 1000   
            self.tempo_vitoria = self.tempo_acumulado + tempo_atual_fase
            self.estado = "VITORIA"

            return
        
        decorrido = (pygame.time.get_ticks() - self.tempo_inicio) // 1000
        restante = self.tempo_limite - decorrido

        if restante <= 0:
            if not self.inimigo_dividido:
              
                self.corpo.extend([Inimigo(30 * i, 100, -1) for i in range(10)]) # Cria mais um corpo da Centopeia

                # Fases
                self.inimigo_dividido = True
                self.tempo_acumulado = 20
                self.tempo_limite = 10 
                self.tempo_inicio = pygame.time.get_ticks() 
            else:
                self.estado = "GAMEOVER"

        for seg in self.corpo:
            seg.mover()

             # Colisão com as bordas da tela
            if seg.pos.x > LARGURA - 15 or seg.pos.x <  15:
                seg.direcao *= -1
                seg.pos.y += 25

            # Colisão entre inimigo e jogador
            if seg.pos.distance_to(self.gnomo.pos) < 25:
                self.estado = "GAMEOVER"

         # Colisão entre tiros e inimigos
            for t in self.tiros[:]:
                for seg in self.corpo[:]:

                    if t.pos.distance_to(seg.pos) < 20: # Cálculo de colisão distância vetorial
                        self.corpo.remove(seg)
        for t in self.tiros[:]:
            t.mover()

            if t.pos.y < 0 or t.pos.x < 0 or t.pos.x > LARGURA:

                self.tiros.remove(t)

        for seg in self.corpo:
            seg.mover()
           
            colidiu_cogumelo = False
            for cog in self.cogumelos:
               
                if seg.pos.distance_to(cog) < 20:
                    colidiu_cogumelo = True
                    break
            
            if seg.pos.x > LARGURA - 15 or seg.pos.x < 15 or colidiu_cogumelo:
                seg.direcao *= -1
                seg.pos.y += 25
                seg.pos.x += seg.direcao * seg.velocidade 
            

            if seg.pos.distance_to(self.gnomo.pos) < 25:# Verificando colisão com o “gnomo”
                self.estado = "GAMEOVER"

        for t in self.tiros[:]: #Percorrendo os tiros para checar colisões
            colidiu = False

            for i, seg in enumerate(self.corpo): # Colisão de cada tiro com o corpo do inimigo
                if t.pos.distance_to(seg.pos) < 20:
                 
                    for posterior in self.corpo[i+1:]:
                        posterior.direcao *= -1
                        posterior.pos.y += 10 
                    
                    self.corpo.remove(seg)
                    colidiu = True
                    break

            if colidiu:
                self.tiros.remove(t)


    def desenhos(self): #Desenha no fundo uma grade
        tela.fill(PRETO)
        desenhar_grade()
        
        #Tempo restante na tela
        if self.estado == "JOGANDO":
            decorrido = (pygame.time.get_ticks() - self.tempo_inicio) // 1000
            restante = max(0, self.tempo_limite - decorrido)
            cor_timer = VERMELHO if restante < 5 else BRANCO
            txt_timer = fonte_ui.render(f"RESTANTE: {restante}s", True, cor_timer)
            tela.blit(txt_timer, (LARGURA - 160, 20))
            
            #Tempo extra
            if self.inimigo_dividido:
                txt_aviso = fonte_ui.render("10 s EXTRAS", True, VERMELHO)
                tela.blit(txt_aviso, (LARGURA//2 - 120, 20))

        # Desenho dos cogumelos 
        for cog in self.cogumelos:
            pygame.draw.circle(tela, AMARELO, (int(cog.x), int(cog.y)), 10) 
            pygame.draw.rect(tela, VERMELHO, (cog.x-3, cog.y+5, 6, 8))

        # Desenha o corpo do inimigo
        for seg in self.corpo:
            pygame.draw.circle(tela,  VERDE, (int(seg.pos.x), int(seg.pos.y)), 14)
        
        # Desenha os tiros
        for t in self.tiros: t.desenhar(tela)
        #Gnomo /Jogador
        self.gnomo.desenhar(tela)

   
        if self.estado == "VITORIA":
        
            msg = fonte_grande.render("VOCÊ GANHOU!", True, VERDE)
            tempo_msg = fonte_ui.render(f"Tempo total: {self.tempo_vitoria} segundos", True, BRANCO)
            sub = fonte_ui.render("Pressione 'R' para reiniciar", True, BRANCO)
            
            tela.blit(msg, (LARGURA//2 - 160, ALTURA//2 - 50))
            tela.blit(tempo_msg, (LARGURA//2 - 130, ALTURA//2 + 20))
            tela.blit(sub, (LARGURA//2 - 125, ALTURA//2 + 80))

        elif self.estado == "GAMEOVER":
            msg = fonte_grande.render("GAMEOVER", True, VERMELHO)
            tela.blit(msg, (LARGURA//2 - 130, ALTURA//2))
            sub = fonte_ui.render("Pressione 'R' para tentar de novo", True, BRANCO)
            tela.blit(sub, (LARGURA//2 - 150, ALTURA//2 + 60))
def desenhar_grade():
    espacamento = 40
    for x in range(0, LARGURA, espacamento):
        pygame.draw.line(tela, (40,40,40), (x,0), (x,ALTURA))
    for y in range(0, ALTURA, espacamento):
        pygame.draw.line(tela, (40,40,40), (0,y), (LARGURA,y))


def main():
    gerenciador = Jogo()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:

                if gerenciador.estado == "JOGANDO":
                    if event.key == pygame.K_SPACE: 
                        gerenciador.disparar("cima")
                    if event.key == pygame.K_a:   
                        gerenciador.disparar("esq")
                    if event.key == pygame.K_d:   
                        gerenciador.disparar("dir")

                if event.key == pygame.K_r: 
                    gerenciador.resetar()

        if gerenciador.estado == "JOGANDO":
            teclas = pygame.key.get_pressed()
            gerenciador.gnomo.mover(teclas)
        
        gerenciador.atualizar()
        gerenciador.desenhos()
        pygame.display.flip()
        fps.tick(60)

if __name__ == "__main__":
    main()  
