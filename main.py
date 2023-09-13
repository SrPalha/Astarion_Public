from asyncio.base_events import constants
import discord
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

sorteio_participantes = set()
sorteio_iniciado = False
message_sorteio = None
premio = ""
imagem_url = ""
tempo_sorteio = 0
numero_participantes = 0
preco_jogo = 0

class SorteioView(discord.ui.View):
    def __init__(self, tempo, message):
        super().__init__(timeout=tempo)
        self.tempo_restante = tempo
        self.message = message
        self.add_item(EntrarSorteioButton())

    async def on_timeout(self):
        if sorteio_iniciado:
            await self.sortear()
    
    async def sortear(self):
        if sorteio_participantes:
            vencedor_id = random.choice(list(sorteio_participantes))
            sorteio_participantes.discard(vencedor_id)  # Remova o vencedor da lista de participantes
            await self.message.channel.send(f"Parabéns <@{vencedor_id}>, você ganhou o sorteio!")

            # Remova o botão da view
            self.clear_items()

            # Defina sorteio_iniciado como False
            sorteio_iniciado = False
        else:
            await self.message.channel.send("Ninguém entrou no sorteio. O sorteio foi cancelado.")
            
    async def atualizar_tempo(self):
        while self.tempo_restante > 0:
            self.tempo_restante -= 60
            minutos, segundos = divmod(self.tempo_restante, 60)
            horas, minutos = divmod(minutos, 60)
            dias, horas = divmod(horas, 24)
            
            tempo_formatado = f"{dias} dias, {horas} horas, {minutos} minutos e {segundos} segundos" if dias else \
                              f"{horas} horas, {minutos} minutos e {segundos} segundos" if horas else \
                              f"{minutos} minutos e {segundos} segundos" if minutos else \
                              f"{segundos} segundos"

            embed = discord.Embed(
                title="Sorteio",
                description=f"Prêmio: {premio}\nPreço do Jogo: {preco_jogo}\nTempo Restante: {dias} dias, {horas} horas, {minutos} minutos \nClique no Botão abaixo para participar do Sorteio!"
            )

            embed.set_image(url=imagem_url)
            embed.add_field(name="🎉 Participantes 🎉", value=f"Já temos {len(sorteio_participantes)} pessoas participando! Vamos lá, junte-se a nós! 🎉", inline=False)
            
            try:
                await self.message.edit(embed=embed)
            except discord.errors.NotFound:
                print("A mensagem foi excluída antes de poder ser editada.")
                break

            await asyncio.sleep(60)  # Pausa o loop por 60 segundos antes da próxima atualização

class EntrarSorteioButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='Entrar no Sorteio', style=discord.ButtonStyle.green)
    
    async def callback(self, interaction: discord.Interaction):
        global sorteio_participantes, sorteio_iniciado, numero_participantes
        if sorteio_iniciado and interaction.user.id not in sorteio_participantes:
            sorteio_participantes.add(interaction.user.id)
            numero_participantes += 1
            await interaction.response.send_message(f"Você entrou no sorteio, {interaction.user.mention}!", ephemeral=True)
        else:
            await interaction.response.send_message("Você já está no sorteio ou o sorteio não foi iniciado.", ephemeral=True)

@client.event
async def on_ready():
    print(f'Conectado como {client.user}')

@client.event
async def on_message(message):
    global sorteio_participantes, sorteio_iniciado, message_sorteio, premio, imagem_url, tempo_sorteio, preco_jogo
    if message.content.startswith('!iniciar'):
        args = message.content.split()[1:]

        if len(args) < 4:
            await message.channel.send("Argumentos insuficientes. Uso correto: !iniciar <prêmio> <tempo em minutos> <URL da imagem> <preço do jogo>")
            return

        premio = args[0]
        
        try:
            tempo_sorteio = int(args[1]) * 60  # Converte minutos em hora, ou seja 60 igual 1hora.
            if tempo_sorteio <= 0:
                raise ValueError("O tempo do sorteio deve ser maior que zero.")
        except ValueError as e:
            await message.channel.send(str(e))
            return
        
        imagem_url = args[2]
        preco_jogo = args[3]
        
        embed = discord.Embed(
            title="Sorteio",
            description=f"Prêmio: {premio}\nClique no Botão abaixo para participar do Sorteio!"
        )
        await message.channel.send("🎉🎉🎉 Estamos começando um novo sorteio! 🎉🎉🎉")  # Sem @everyone
        
        embed.set_image(url=imagem_url)
        embed.add_field(name="🎉 Participantes 🎉", value=f"Já temos {len(sorteio_participantes)} pessoas participando! Vamos lá, junte-se a nós! 🎉", inline=False)
        message_sorteio = await message.channel.send(embed=embed)

        view = SorteioView(tempo_sorteio, message_sorteio)
        message_sorteio = await message_sorteio.edit(embed=embed, view=view)
        sorteio_iniciado = True
        asyncio.create_task(view.atualizar_tempo()) 
        await message.channel.send("<@&1149687935319412848>")
