import pygame
import sys
import random

pygame.init()
LARGURA, ALTURA = 600, 800
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Trabalho CG - Centopeia")


PRETO, BRANCO, VERDE, VERMELHO, AZUL, AMARELO = (0,0,0), (255,255,255), (0,255,0), (255,0,0), (0,150,255), (255,255,0)
MARROM = (139, 69, 19)

fps = pygame.time.Clock()
fonte_ui = pygame.font.SysFont("Arial", 25)
fonte_grande = pygame.font.SysFont("Arial", 50) 

class Gnomo:
    def __init__(self):
        self.pos = pygame.Vector2(LARGURA // 2, ALTURA - 60) # Definição da posição como um vetor
        self.vel = 8
        self.tamanho = 10

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.pos.x > 20: self.pos.x -= self.vel
        if teclas[pygame.K_RIGHT] and self.pos.x < LARGURA - 20: self.pos.x += self.vel
        if teclas[pygame.K_UP] and self.pos.y > ALTURA - 180: self.pos.y -= self.vel
        if teclas[pygame.K_DOWN] and self.pos.y < ALTURA - 20: self.pos.y += self.vel

    def desenhar(self, superficie):
        pontos = [(self.pos.x, self.pos.y - self.tamanho),
                  (self.pos.x - self.tamanho, self.pos.y + self.tamanho),
                  (self.pos.x + self.tamanho, self.pos.y + self.tamanho)]
        pygame.draw.polygon(superficie, AZUL, pontos)
        pygame.draw.polygon(superficie, BRANCO, pontos, 2)

class Projetil:
    def __init__(self, x, y, vetor_vel):
        self.pos = pygame.Vector2(x, y)
        self.vel = vetor_vel

    def mover(self):
        self.pos += self.vel

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, BRANCO, (int(self.pos.x), int(self.pos.y)), 4)

class Segmento:
    def __init__(self, x, y, direcao):
        self.pos = pygame.Vector2(x, y)
        self.direcao = direcao
        self.velocidade = 5
        self.raio = 10 

    def mover(self):
        self.pos.x += self.direcao * self.velocidade

class Jogo:
    def __init__(self):
        self.resetar()

    def resetar(self):
        self.gnomo = Gnomo()
        self.tiros = []
        self.corpo = [Segmento(30 * i, 60, 1) for i in range(10)]
        self.cogumelos = [pygame.Vector2(random.randrange(40, 580, 20), random.randrange(120, 600, 20)) for _ in range(20)]
        
        self.tempo_limite = 15
        self.tempo_inicio = pygame.time.get_ticks()
        self.tempo_acumulado = 0 
        self.tempo_vitoria = 0   
        self.inimigo_dividido = False
        self.estado = "JOGANDO" 

    def disparar(self, direcao):
        if direcao == "cima": 
            vel = pygame.Vector2(0, -12)
        elif direcao == "esq": 
            vel = pygame.Vector2(-12, 0)
        elif direcao == "dir": 
            vel = pygame.Vector2(12, 0)
            
        self.tiros.append(Projetil(self.gnomo.pos.x, self.gnomo.pos.y, vel))

    def atualizar(self):
        if self.estado != "JOGANDO": return

      
        if len(self.corpo) == 0:
            tempo_atual_fase = (pygame.time.get_ticks() - self.tempo_inicio) // 1000   
            self.tempo_vitoria = self.tempo_acumulado + tempo_atual_fase
            self.estado = "VITORIA"

            return

        decorrido = (pygame.time.get_ticks() - self.tempo_inicio) // 1000
        restante = self.tempo_limite - decorrido

        if restante <= 0:
            if not self.inimigo_dividido:
              
                self.corpo.extend([Segmento(30 * i, 100, -1) for i in range(10)])
                self.inimigo_dividido = True
                self.tempo_acumulado = 20
                self.tempo_limite = 10 
                self.tempo_inicio = pygame.time.get_ticks() 
            else:
                self.estado = "GAMEOVER"

        for seg in self.corpo:
            seg.mover()
            if seg.pos.x > LARGURA - 15 or seg.pos.x <  15:
                seg.direcao *= -1
                seg.pos.y += 25
            
            if seg.pos.distance_to(self.gnomo.pos) < 25:
                self.estado = "GAMEOVER"

        for t in self.tiros[:]:

            for seg in self.corpo[:]:

                if t.pos.distance_to(seg.pos) < 20: # Cálculo de colisão usando distância vetorial

                    self.corpo.remove(seg)

                    if t in self.tiros: self.tiros.remove(t)
                    break


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
            

            if seg.pos.distance_to(self.gnomo.pos) < 25:
                self.estado = "GAMEOVER"

        for t in self.tiros[:]:
            colidiu = False

            for i, seg in enumerate(self.corpo):
                if t.pos.distance_to(seg.pos) < 20:
                 
                    for posterior in self.corpo[i+1:]:
                        posterior.direcao *= -1
                        posterior.pos.y += 10 
                    
                    self.corpo.remove(seg)
                    colidiu = True
                    break
            if colidiu:
                self.tiros.remove(t)


    def desenhos(self):
        tela.fill(PRETO)
        desenhar_grade()
        
        if self.estado == "JOGANDO":
            decorrido = (pygame.time.get_ticks() - self.tempo_inicio) // 1000
            restante = max(0, self.tempo_limite - decorrido)
            cor_timer = VERMELHO if restante < 5 else BRANCO
            txt_timer = fonte_ui.render(f"RESTANTE: {restante}s", True, cor_timer)
            tela.blit(txt_timer, (LARGURA - 160, 20))
            
            if self.inimigo_dividido:
                txt_aviso = fonte_ui.render("10 s EXTRAS", True, VERMELHO)
                tela.blit(txt_aviso, (LARGURA//2 - 120, 20))

        for cog in self.cogumelos:
            pygame.draw.circle(tela, AMARELO, (int(cog.x), int(cog.y)), 10) 
            pygame.draw.rect(tela, VERMELHO, (cog.x-3, cog.y+5, 6, 8))
            
        for seg in self.corpo:
            pygame.draw.circle(tela,  VERDE, (int(seg.pos.x), int(seg.pos.y)), 12)
        
        for t in self.tiros: t.desenhar(tela)
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
