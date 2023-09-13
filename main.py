const { Client, MessageActionRow, MessageButton, MessageEmbed, Permissions } = require('discord.js');
const client = new Client({ intents: ["GUILDS", "GUILD_MESSAGES", "GUILD_MEMBERS", "DIRECT_MESSAGES"] });
const { token } = require('./config.json');

let ticketID = 1;
let supportCategory;

client.once('ready', async () => {
    console.log('Bot tá online!');

    for (const guild of client.guilds.cache.values()) {
        if (!guild.channels.cache.find(ch => ch.name === "Suportes" && ch.type === "GUILD_CATEGORY")) {
            await guild.channels.create('Suportes', { type: 'GUILD_CATEGORY' });
        }
        if (!guild.channels.cache.find(ch => ch.name === "Tickets fechados" && ch.type === "GUILD_CATEGORY")) {
            await guild.channels.create('Tickets fechados', { type: 'GUILD_CATEGORY' });
        }
    
        let supportChannel = guild.channels.cache.find(ch => ch.name === "dúvidas e suporte");
        if (!supportChannel) {
            supportChannel = await guild.channels.create('dúvidas e suporte', { type: 'GUILD_TEXT' });
            
            const embed = new MessageEmbed()
                .setColor('#FF0000')
                .setTitle('Caso queira falar com um Moderador ou esteja com algum problema no jogo ou dúvidas!')
                .setAuthor({ name: 'Navegantes do BG3 - Astarion Bot', iconURL: 'https://i.imgur.com/W6JeE0C.jpg'})
                .setThumbnail('https://i.imgur.com/W6JeE0C.jpg')
                .setDescription(`Este canal é destinado somente a dúvidas e suporte em geral do jogo e servidor, caso esteja procurando atualização ou baixar você encontrará em <#728732030568890439>!`)    
                .setFooter({ text: 'Clique no botão abaixo 📩' });
            const row = new MessageActionRow()
                .addComponents(
                    new MessageButton()
                        .setCustomId('open_ticket')
                        .setLabel('📩 Abrir Ticket 📩')
                        .setStyle('PRIMARY')
                );
    
            supportChannel.send({ embeds: [embed], components: [row] });
        }
    }
});

client.on('interactionCreate', async interaction => {
    if (interaction.isButton()) {
        switch(interaction.customId) {
            case 'open_ticket':
                supportCategory = interaction.guild.channels.cache.find(ch => ch.name === "Suportes" && ch.type === "GUILD_CATEGORY");
                const channel = await interaction.guild.channels.create(`ticket-${ticketID++}`, {
                    parent: supportCategory,
                    permissionOverwrites: [
                        { id: interaction.guild.roles.everyone, deny: ['VIEW_CHANNEL'] },
                        { id: '1140334770623094906', allow: ['VIEW_CHANNEL'] },
                        { id: interaction.user.id, allow: ['VIEW_CHANNEL'] }
                    ]
                });

                const openEmbed = new MessageEmbed()
                    .setColor('#FF0000')
                    .setTitle('Olá, sem mais surpresas. Você tem minha atenção, vou chamar um ajudante.')
                    .setAuthor({ name: 'Navegantes do BG3 - Astarion Bot', iconURL: 'https://i.imgur.com/W6JeE0C.jpg'})
                    .setDescription(`__Astarion parece sincero. Ele coloca a mão em seu coração e aguarda você__`)
                    .setThumbnail('https://i.imgur.com/W6JeE0C.jpg')
                    .setFooter({ text: `Caso queira fechar o ticket clique no botão abaixo Fechar Ticket!` });

                const openRow = new MessageActionRow()
                    .addComponents(
                        new MessageButton()
                            .setCustomId('close_ticket')
                            .setLabel('Fechar Ticket')
                            .setStyle('DANGER')
                    );
                await channel.send({ content: `<@&1140334770623094906>`, embeds: [openEmbed], components: [openRow] });
                await interaction.reply({ content: 'Ticket aberto!', ephemeral: true });
                break; 

            case 'close_ticket':
                if (interaction.channel && interaction.channel.name.startsWith('ticket-')) {
                    const closedTicketsCategory = interaction.guild.channels.cache.find(ch => ch.name === "Tickets fechados" && ch.type === "GUILD_CATEGORY");
                    if (closedTicketsCategory) {
                        await interaction.channel.setParent(closedTicketsCategory);
                        await interaction.channel.setName(`fechado-${interaction.channel.name.split('-')[1]}`);

                        const closeEmbed = new MessageEmbed()
                            .setColor('#FF0000')
                            .setDescription(`Ticket fechado por ${interaction.user.username}`)
                            .setFooter({ text: `Astarion Bot - ${interaction.user.username}` });

                        const closeRow = new MessageActionRow()
                            .addComponents(
                                new MessageButton()
                                    .setCustomId('send_dm')
                                    .setLabel('Enviar ticket para DM')
                                    .setStyle('SECONDARY'),
                                new MessageButton()
                                    .setCustomId('reopen_ticket')
                                    .setLabel('Reabrir Ticket')
                                    .setStyle('SUCCESS')
                            );

                        await interaction.channel.send({ embeds: [closeEmbed], components: [closeRow] });
                        await interaction.reply({ content: 'Ticket fechado com sucesso!', ephemeral: true });
                    } else {
                        await interaction.reply({ content: 'Categoria "Tickets fechados" não encontrada!', ephemeral: true });
                    }
                } else {
                    await interaction.reply({ content: 'Este comando só pode ser usado em canais de ticket.', ephemeral: true });
                }
                break;

            case 'send_dm':
                const ticketContent = interaction.channel.messages.cache.map(message => `[${message.author.tag}] ${message.content}`).join('\n');
                interaction.user.send(`Aqui está o conteúdo do ticket:\n\n${ticketContent}`);
                break;

            case 'reopen_ticket':
                supportCategory = interaction.guild.channels.cache.find(ch => ch.name === "Suportes" && ch.type === "GUILD_CATEGORY");
                await interaction.channel.send('Reabrindo o ticket...'); 
                
                supportCategory = interaction.guild.channels.cache.find(ch => ch.name === "Suportes" && ch.type === "GUILD_CATEGORY");
                if (supportCategory) {
                    await interaction.channel.setParent(supportCategory);
                    const ticketNumber = interaction.channel.name.split('-')[1];
                    await interaction.channel.setName(`ticket-${ticketNumber}`);
                    await interaction.channel.send(`Ticket ${ticketNumber} re-aberto.`);
                } else {
                    await interaction.channel.send('Não foi possível reabrir o ticket. Categoria de suporte não encontrada.');
                }
                break;

            case 'delete_ticket':
                await interaction.channel.send('Deletando o ticket...');
                await interaction.channel.delete();
                break;
        }
    } else if (interaction.isCommand()) {
        const { commandName } = interaction;

        if (commandName === 'add') {
            const member = interaction.options.getMember('membro');
            if (member && interaction.channel.name.startsWith('ticket-')) {
                interaction.channel.permissionOverwrites.edit(member, { VIEW_CHANNEL: true });
                interaction.channel.send(`${member} foi adicionado ao ticket.`);
            }
        } else if (commandName === 'remover') {
            const member = interaction.options.getMember('membro');
            if (member && interaction.channel.name.startsWith('ticket-')) {
                interaction.channel.permissionOverwrites.edit(member, { VIEW_CHANNEL: false });
                interaction.channel.send(`${member} foi removido do ticket.`);
            }
        } else if (commandName === 'fechar') {
            if (interaction.channel && interaction.channel.name.startsWith('ticket-')) {
                const closedTicketsCategory = interaction.guild.channels.cache.find(ch => ch.name === "Tickets fechados" && ch.type === "GUILD_CATEGORY");
                if (closedTicketsCategory) {
                    await interaction.channel.setParent(closedTicketsCategory);
                    await interaction.channel.setName(`fechado-${interaction.channel.name.split('-')[1]}`);

                    const embed = new MessageEmbed()
                        .setColor('#FF0000')
                        .setDescription(`Ticket Fechado por ${interaction.user.tag}`)
                        .setFooter({ text: 'Astarion Bot' });

                    const row = new MessageActionRow()
                        .addComponents(
                            new MessageButton()
                                .setCustomId('send_dm')
                                .setLabel('Enviar ticket para DM')
                                .setStyle('SECONDARY'),
                            new MessageButton()
                                .setCustomId('reopen_ticket')
                                .setLabel('Reabrir Ticket')
                                .setStyle('SUCCESS')
                        );

                    await interaction.channel.send({ embeds: [embed], components: [row] });
                    await interaction.reply({ content: 'Ticket fechado com sucesso!', ephemeral: false });
                }
            }
        } else if (commandName === 'dm') {
            if (interaction.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) {
                const user = interaction.options.getUser('usuario');
                const ticketContent = interaction.channel.messages.cache.map(message => `[${message.author.tag}] ${message.content}`).join('\n');
                user.send(`Aqui está o conteúdo do ticket:\n\n${ticketContent}`);
            } else {
                interaction.reply('Você não tem permissão para usar este comando!');
            }
        } else if (commandName === 'abrir') {
            if (interaction.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) {
                const ticketNumber = interaction.channel.name.split('-')[1];
                const supportCategory = interaction.guild.channels.cache.find(ch => ch.name === "Suportes" && ch.type === "GUILD_CATEGORY");
                if (supportCategory) {
                    await interaction.channel.setParent(supportCategory);
                }
                await interaction.channel.setName(`ticket-${ticketNumber}`);
                await interaction.channel.send(`Ticket ${ticketNumber} reaberto por ${interaction.user.tag}.`);
            } else {
                interaction.reply('Você não tem permissão para usar este comando.');
            }
        } else if (commandName === 'excluir') {
            if (interaction.member.permissions.has(Permissions.FLAGS.ADMINISTRATOR)) {
                await interaction.channel.delete();
            } else {
                interaction.reply('Você não tem permissão para usar este comando.');
            }
        }
    }
});

client.login(token);
