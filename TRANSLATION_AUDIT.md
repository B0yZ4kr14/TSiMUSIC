# Relatório de Auditoria de Tradução – TSi MUSIC Frontend

**Arquivos analisados:**
- `en.json`: 1405 chaves
- `pt_BR.json`: 1419 chaves

---

## Resumo Global

| Métrica | Valor |
|---------|-------|
| Total de chaves em `en.json` | 1405 |
| Total de chaves em `pt_BR.json` | 1419 |
| Chaves faltantes em `pt_BR.json` | 0 |
| Chaves extras em `pt_BR.json` | 14 |
| Chaves idênticas (não traduzidas) | 248 |
| Chaves com texto misturado pt/en | 294 |
| Chaves com placeholders mal formatados | 2 |

---

## Login

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 182 |
| Chaves em pt_BR.json | 182 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 32 |
| Texto misturado pt/en | 65 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **97** |

### Exemplos de não traduzidas (idênticas)
- `auth.manage_your_profile_info` → `Manage your profile information and settings`
- `remote.sign_in` → `Sign In`
- `auth.role` → `Role`
- `remote.remote_id_placeholder` → `e.g., MA-X7K9-P2M4`
- `auth.long_lived_tokens` → `Long-lived access tokens`
- `login.remote_id_placeholder` → `e.g., MA-X7K9-P2M4`
- `auth.logout` → `Sign out`
- `auth.revoke` → `Revoke`
- `remote.recent_connections` → `Recent Connections`
- `login.server_address_placeholder` → `http://192.168.1.100:8095`
- ... e mais 22 chaves

### Exemplos de texto misturado pt/en
- `auth.session_revoked` → `pt_BR: Sessão revoked com sucesso` (en: `Session revoked successfully`)
- `auth.user_management` → `pt_BR: Usuário management` (en: `User management`)
- `auth.player_filter_hint` → `pt_BR: Restrict this user to access only the selecionado players. Leave empty for full access to all players.` (en: `Restrict this user to access only the selected players. Leave empty for full access to all players.`)
- `auth.user_create_failed` → `pt_BR: Falhou to create user` (en: `Failed to create user`)
- `remote.subtitle_oauth` → `pt_BR: Complete o login in your browser` (en: `Complete sign-in in your browser`)
- `remote.oauth_waiting_title` → `pt_BR: Completar Sign-in` (en: `Complete Sign-in`)
- `auth.player_filter` → `pt_BR: Player filtro` (en: `Player filter`)
- `auth.token_revoke_failed` → `pt_BR: Falhou to revoke token` (en: `Failed to revoke token`)
- `auth.field_required` → `pt_BR: This campo is required` (en: `This field is required`)
- `remote.connect_locally` → `pt_BR: Conectar to local server instead` (en: `Connect to local server instead`)
- ... e mais 55 chaves

---

## Settings

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 492 |
| Chaves em pt_BR.json | 492 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 76 |
| Texto misturado pt/en | 129 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **205** |

### Exemplos de não traduzidas (idênticas)
- `settings.proud_part_of` → `Proud part of`
- `settings.core_module.webserver.description` → `Configuration of the webserver and API`
- `settings.unsaved_changes` → `Unsaved changes`
- `settings.players_count` → `{0} player{1}`
- `settings.remote_access_qr_code` → `QR Code`
- `settings.language.options.lt_LT` → `Lithuanian`
- `settings.remote_access_qr_code_description` → `Scan with your phone camera to connect instantly.`
- `settings.profile_description` → `Manage your personal account settings and preferences`
- `settings.bug_reports` → `Bug Reports`
- `settings.stage.options.experimental` → `Experimental`
- ... e mais 66 chaves

### Exemplos de texto misturado pt/en
- `settings.onboarding_player_desc` → `pt_BR: Conectar your speakers and devices like Sonos, Chromecast, or AirPlay.` (en: `Connect your speakers and devices like Sonos, Chromecast, or AirPlay.`)
- `settings.scan_triggered` → `pt_BR: Gênero scan started com sucesso.` (en: `Genre scan started successfully.`)
- `settings.mobile_sidebar_side.description` → `pt_BR: Which side the navigation menu (sheet) opens from on mobile. Padrão is left.` (en: `Which side the navigation menu (sheet) opens from on mobile. Default is left.`)
- `settings.volume_control.description` → `pt_BR: Define/substitui o comportamento do controle de volume desse reprodutor. Permite, por exemplo, redirecionar os comandos de controle de volume para um dispositivo diferente ou desativá-lo completamente.` (en: `Define/override the volume control behavior for this player.
It allows you for example to redirect the volume control commands to a different appliance, or disable it completely.`)
- `settings.music_sources` → `pt_BR: Música sources` (en: `Music sources`)
- `settings.remote_access_mode_basic` → `pt_BR: Running in Básico Moda` (en: `Running in Basic Mode`)
- `settings.remote_access_feature_encrypted` → `pt_BR: End-to-end criptografado - your data stays private` (en: `End-to-end encrypted - your data stays private`)
- `settings.dsp.configure_on` → `pt_BR: Configuração do DSP em: {name}` (en: `Configuring DSP on: {name}`)
- `settings.library_stats` → `pt_BR: Biblioteca Statistics` (en: `Library Statistics`)
- `settings.total_genres` → `pt_BR: Total Gêneros` (en: `Total Genres`)
- ... e mais 119 chaves

---

## Player

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 88 |
| Chaves em pt_BR.json | 88 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 6 |
| Texto misturado pt/en | 11 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **17** |

### Exemplos de não traduzidas (idênticas)
- `player_options.dimmer` → `Dimmer`
- `player_options.surround_3d` → `Surround 3D`
- `player_options.enhancer` → `Enhancer`
- `player_options.pure_direct` → `Pure direct`
- `volume_normalization_gain_correction` → `{0} dB`
- `streamdetails.file_info.codec` → `Codec: {0}`

### Exemplos de texto misturado pt/en
- `player_options.link_audio_quality` → `pt_BR: Qualidade de áudio do link` (en: `Link audio quality`)
- `streamdetails.dsp_disabled_by_unsupported_group` → `pt_BR: Esse provedor de player não é compatível com DSP com reprodução sincronizada` (en: `This player provider does not support DSP with synchronized playback`)
- `sync_player_with` → `pt_BR: Sincronizar com outro player` (en: `Synchronize with another player`)
- `player_options.extra_bass` → `pt_BR: Grave extra` (en: `Extra bass`)
- `streamdetails.output_format_pcm_info` → `pt_BR: O áudio é transmitido como PCM para o provedor do reprodutor. O provedor do reprodutor pode então converter o áudio em um formato diferente antes de enviá-lo ao player.` (en: `Audio is passed as PCM to the player provider. The player provider may then convert the audio to a different format before sending it to the player.`)
- `player_options.surround_decoder_type` → `pt_BR: Tipo de decoder surround` (en: `Surround decoder type`)
- `player_options.subwoofer_volume` → `pt_BR: Volume do subwoofer` (en: `Subwoofer Volume`)
- `player_options.link_audio_delay` → `pt_BR: Atraso de áudio do link` (en: `Link audio delay`)
- `powered_off_players` → `pt_BR: Desligar players` (en: `Unpowered players`)
- `player_options.link_control` → `pt_BR: Controle do link` (en: `Link control`)
- ... e mais 1 chaves

---

## Queue

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 24 |
| Chaves em pt_BR.json | 24 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 4 |
| Placeholders mal formatados | 1 |
| **Total de problemas** | **5** |

### Exemplos de texto misturado pt/en
- `queue_delete` → `pt_BR: Excluir item` (en: `Delete item`)
- `music_assistant_source` → `pt_BR: Fila de espera do TSi MUSIC` (en: `TSi MUSIC Queue`)
- `music_assistant_library` → `pt_BR: Biblioteca do TSi MUSIC` (en: `TSi MUSIC Library`)
- `save_queue_as_playlist` → `pt_BR: Salvar fila como playlist` (en: `Save queue as playlist`)

### Exemplos de placeholders mal formatados
- `queue_radio_based_on` → en: `set()` | pt: `{'{0}'}`

---

## Library

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 37 |
| Chaves em pt_BR.json | 37 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 6 |
| Texto misturado pt/en | 7 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **13** |

### Exemplos de não traduzidas (idênticas)
- `recommendations.recent_series` → `Recent series`
- `recommendations.libraries` → `Libraries`
- `recommendations.trending_podcasts` → `Trending podcasts`
- `recommendations.listen_again` → `Listen again`
- `recommendations.newest_episodes` → `Newest episodes`
- `recommendations.newest_authors` → `Newest authors`

### Exemplos de texto misturado pt/en
- `in_progress_items` → `pt_BR: Continue ouvindo...` (en: `Continue listening...`)
- `confirm_library_remove` → `pt_BR: Tem certeza de que deseja excluir esse item da biblioteca? Todos os itens dependentes desse item também serão removidos recursivamente. Observe que isso removerá apenas esse item da biblioteca. Se for um arquivo de música no disco, ele poderá retornar na próxima sincronização.` (en: `Are you sure you want to delete this item from the library? Any items depending on this item will also be recursively removed. Note that this will only remove this item from the library. If this is a music file on disk, it may return on the next sync.`)
- `item_in_library` → `pt_BR: Esse item está disponível na biblioteca` (en: `This item is available in the library`)
- `recommendations.in_progress_series` → `pt_BR: Continuar series...` (en: `Continue series...`)
- `recommendations.in_progress_items` → `pt_BR: Continue ouvindo...` (en: `Continue listening...`)
- `recommendations.favorite_playlists` → `pt_BR: Playlists favoritas` (en: `Favorite playlists`)
- `recommendations.episodes_recently_added` → `pt_BR: Adicionado recentemente episodes` (en: `Recently added episodes`)

---

## Artists

**Status:** ✅ completo

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 4 |
| Chaves em pt_BR.json | 4 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **0** |

---

## Albums

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 12 |
| Chaves em pt_BR.json | 12 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 3 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **3** |

### Exemplos de não traduzidas (idênticas)
- `album_type.single` → `Single`
- `album_type.podcast` → `Podcast`
- `album_type.ep` → `EP`

---

## Tracks

**Status:** ✅ completo

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 3 |
| Chaves em pt_BR.json | 3 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **0** |

---

## Playlists

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 19 |
| Chaves em pt_BR.json | 19 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 9 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **9** |

### Exemplos de texto misturado pt/en
- `export_playlist` → `pt_BR: Exportar playlist` (en: `Export playlist`)
- `import_playlist` → `pt_BR: Importar playlist` (en: `Import playlist`)
- `add_playlist` → `pt_BR: Adicionar à playlist...` (en: `Add to playlist...`)
- `create_playlist` → `pt_BR: Criar nova playlist em {0}` (en: `Create new playlist on {0}`)
- `playlist_created` → `pt_BR: Playlist criada` (en: `Playlist created`)
- `open_playlist` → `pt_BR: Abrir playlist` (en: `Open playlist`)
- `import_playlist_invalid_file` → `pt_BR: Arquivo de playlist inválido` (en: `Invalid playlist file`)
- `playlist_mix_not_allowed` → `pt_BR: Este provedor não suporta a mistura de tipos de mídia em playlists. Selecione para qual tipo de mídia você deseja criar uma playlist:` (en: `This provider does not support mixing media types in playlists. Please select for which media type you would like to create a playlist:`)
- `import_playlist_title` → `pt_BR: Importar playlist` (en: `Import playlist`)

---

## Radio

**Status:** ✅ completo

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 10 |
| Chaves em pt_BR.json | 10 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **0** |

---

## Podcasts

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 4 |
| Chaves em pt_BR.json | 4 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 2 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **2** |

### Exemplos de não traduzidas (idênticas)
- `podcast` → `Podcast`
- `podcasts` → `Podcasts`

---

## Audiobooks

**Status:** ✅ completo

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 10 |
| Chaves em pt_BR.json | 10 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **0** |

---

## Search

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 8 |
| Chaves em pt_BR.json | 8 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 2 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **2** |

### Exemplos de texto misturado pt/en
- `global_search` → `pt_BR: Pesquisa global` (en: `Global search`)
- `try_global_search` → `pt_BR: Tentar busca global` (en: `Try global search`)

---

## Notifications

**Status:** ✅ completo

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 1 |
| Chaves em pt_BR.json | 1 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 0 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **0** |

---

## Errors

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 28 |
| Chaves em pt_BR.json | 28 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 12 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **12** |

### Exemplos de texto misturado pt/en
- `background_tasks.toast.history_clear_failed` → `pt_BR: Falhou to limpar finished tarefas.` (en: `Failed to clear finished tasks.`)
- `promote_alias_failed` → `pt_BR: Falha ao promover alias` (en: `Failed to promote alias`)
- `link_alias_failed` → `pt_BR: Falha ao vincular alias` (en: `Failed to link alias`)
- `background_tasks.schedule_dialog.invalid_every` → `pt_BR: Please enter a válido repeat interval.` (en: `Please enter a valid repeat interval.`)
- `background_tasks.schedule_dialog.invalid_hour` → `pt_BR: Please enter a válido hour.` (en: `Please enter a valid hour.`)
- `add_alias_failed` → `pt_BR: Falha ao adicionar alias` (en: `Failed to add alias`)
- `background_tasks.toast.schedule_update_failed` → `pt_BR: Falhou to atualizar the agendamento for {0}.` (en: `Failed to update the schedule for {0}.`)
- `providers.party.guest_access_toggle_failed` → `pt_BR: Falhou to alternar guest access` (en: `Failed to toggle guest access`)
- `remove_alias_failed` → `pt_BR: Falha ao remover alias` (en: `Failed to remove alias`)
- `background_tasks.toast.run_failed` → `pt_BR: Falhou to start {0}.` (en: `Failed to start {0}.`)
- ... e mais 2 chaves

---

## Actions

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 47 |
| Chaves em pt_BR.json | 47 |
| Faltantes | 0 |
| Extras | 0 |
| Não traduzidas (idênticas) | 0 |
| Texto misturado pt/en | 9 |
| Placeholders mal formatados | 1 |
| **Total de problemas** | **10** |

### Exemplos de texto misturado pt/en
- `add_alias` → `pt_BR: Adicionar alias` (en: `Add alias`)
- `map_provider_mapping` → `pt_BR: Mapear esta entrada do provedor para o item atual` (en: `Map this provider entry to the current item`)
- `delete_db` → `pt_BR: Excluir item do banco de dados` (en: `Delete item from database`)
- `add_url_item` → `pt_BR: Adicionar item a partir de uma URL` (en: `Add item from URL`)
- `refresh_item` → `pt_BR: Atualizar item` (en: `Refresh item`)
- `link_alias` → `pt_BR: Vincular alias` (en: `Link alias`)
- `remove_alias` → `pt_BR: Remover alias` (en: `Remove alias`)
- `perform_action` → `pt_BR: Realizar ação em {0} item(ns)` (en: `Perform action on {0} item(s)`)
- `edit_playlist` → `pt_BR: Editar playlist` (en: `Edit playlist`)

### Exemplos de placeholders mal formatados
- `sync_now` → en: `set()` | pt: `{'{0}'}`

---

## Common

**Status:** ⚠️ parcial

| Métrica | Valor |
|---------|-------|
| Chaves em en.json | 436 |
| Chaves em pt_BR.json | 436 |
| Faltantes | 0 |
| Extras | 14 |
| Não traduzidas (idênticas) | 123 |
| Texto misturado pt/en | 46 |
| Placeholders mal formatados | 0 |
| **Total de problemas** | **183** |

### Exemplos de não traduzidas (idênticas)
- `genre_names.dance` → `Dance`
- `genre_names.jazz` → `Jazz`
- `genre_names.pop` → `Pop`
- `genre_descriptions.ragtime` → `Ragtime, also spelled rag-time or rag time, is a musical style noted for its syncopated or "ragged" rhythm. It originated in African American communities in the late 19th century and was propelled to popularity in the 1890s to 1910s by composers such as James Scott, Joseph Lamb, and particularly Scott Joplin. Known as the "King of Ragtime", Joplin gained fame through compositions like "Maple Leaf Rag" and "The Entertainer".`
- `genre_names.chanson` → `Chanson`
- `genre_descriptions.childrens_music` → `Children's music or kids' music is music composed and performed for children. In European-influenced contexts this means music, usually songs, written specifically for a juvenile audience. The composers are usually adults.`
- `genre_descriptions.field_recording` → `Field recording is the production of audio recordings outside recording studios, and the term applies to recordings of both natural and human-produced sounds. It can also include the recording of electromagnetic fields or vibrations using different microphones like a passive magnetic antenna for electromagnetic recordings or contact microphones, or underwater field recordings made with hydrophones to capture the sounds and/or movements of whales, or other sealife. These recordings are often regarded as being very useful for sound designers and foley artists.`
- `genre_descriptions.folk` → `Folk music is a music genre that includes traditional folk music and the contemporary genre that evolved from the former during the 20th-century folk revival. Some types of folk music may be called world music. Traditional folk music has been defined in several ways: as music transmitted orally, music with unknown composers, music that is played on traditional instruments, music about cultural or national identity, music that changes between generations, music associated with a people's folklore, or music performed by custom over a long period of time. It has been contrasted with commercial and classical styles. The term originated in the 19th century, but folk music extends beyond that.`
- `genre_descriptions.musical` → `Musical theatre is a form of theatrical performance that combines songs, spoken dialogue, acting and dance. The story and emotional content of a musical – humor, pathos, love, anger – are communicated through words, music, movement and technical aspects of the entertainment as an integrated whole. Although musical theatre overlaps with other theatrical forms like opera and dance, it may be distinguished by the equal importance given to the music as compared with the dialogue, movement and other elements. Since the early 20th century, musical theatre stage works have generally been called, simply, musicals.`
- `genre_names.blues` → `Blues`
- ... e mais 113 chaves

### Exemplos de texto misturado pt/en
- `merge_genres_description` → `pt_BR: Selecione um gênero de destino para mesclar. Todos os aliases e mídias mapeadas dos gêneros de origem serão transferidos para o destino.` (en: `Select a target genre to merge into. All aliases and mapped media from the source genres will be transferred to the target.`)
- `background_task.refresh_playlist_metadata` → `pt_BR: Atualizar metadados da playlist` (en: `Refresh playlist metadata`)
- `items_selected` → `pt_BR: {0} item(ns) selecionado(s)` (en: `{0} item(s) selected`)
- `background_task.add_playlist_tracks` → `pt_BR: Adicionar itens à playlist {0}` (en: `Add items to playlist {0}`)
- `background_tasks.toast.removed` → `pt_BR: Removed {0} from tarefa history.` (en: `Removed {0} from task history.`)
- `background_tasks.schedule_dialog.select_weekday` → `pt_BR: Selecionar at least one weekday.` (en: `Select at least one weekday.`)
- `tooltip.open_provider_link` → `pt_BR: Abrir esse item no site do provedor` (en: `Open this item on the provider's website`)
- `providers.party.guest_page.boost_available` → `pt_BR: Boost disponível` (en: `Boost available`)
- `confirm_delete_genre` → `pt_BR: Tem certeza de que deseja excluir este gênero? O gênero em si será removido, juntamente com seus mapeamentos de alias.` (en: `Are you sure you want to delete this genre? The genre itself will be removed, along with its alias mappings.`)
- `providers.party.confirm_disable_guest_access` → `pt_BR: Are you sure you want to desativar guest access? Guests will no longer be able to juntar the party, browse music, or add songs to the fila.` (en: `Are you sure you want to disable guest access? Guests will no longer be able to join the party, browse music, or add songs to the queue.`)
- ... e mais 36 chaves

### Exemplos de chaves extras (não existem em en.json)
- `providers.party.stop_party` → `Parar Festa`
- `background_tasks.schedule_dialog.cancel` → `Cancelar`
- `background_tasks.schedule_dialog.specific_time` → `Horário específico`
- `background_tasks.schedule_dialog.cron_description` → `Insira uma expressão cron válida.`
- `background_tasks.schedule_dialog.interval_days` → `A cada X dias`
- `background_tasks.schedule_dialog.cron_example` → `Exemplo: 0 4 * * * (todos os dias às 04:00)`
- `background_tasks.schedule_dialog.specific_time_description` → `Executar diariamente no horário especificado.`
- `background_tasks.schedule_dialog.interval_hours` → `A cada X horas`
- `providers.party.show_qr` → `Mostrar Código QR`
- `background_tasks.schedule_dialog.cron` → `Expressão Cron`
- ... e mais 4 chaves

---

## Detalhes Completos

### Todas as chaves extras em pt_BR.json
- `background_tasks.schedule_dialog.cancel`
- `background_tasks.schedule_dialog.cron`
- `background_tasks.schedule_dialog.cron_description`
- `background_tasks.schedule_dialog.cron_example`
- `background_tasks.schedule_dialog.interval`
- `background_tasks.schedule_dialog.interval_days`
- `background_tasks.schedule_dialog.interval_hours`
- `background_tasks.schedule_dialog.save`
- `background_tasks.schedule_dialog.specific_time`
- `background_tasks.schedule_dialog.specific_time_description`
- `providers.party.scan_qr`
- `providers.party.show_qr`
- `providers.party.start_party`
- `providers.party.stop_party`

### Todas as chaves idênticas
- `album_type.ep` → `EP`
- `album_type.podcast` → `Podcast`
- `album_type.single` → `Single`
- `alias` → `Alias`
- `aliases` → `Aliases`
- `auth.active_sessions_description` → `These are sessions created when you sign in. They automatically renew when used and expire after 30 days of inactivity.`
- `auth.admin_required` → `Administrator access required`
- `auth.admin_role` → `Administrator`
- `auth.avatar_url_hint` → `Enter URL to avatar image`
- `auth.disabled` → `Disabled`
- `auth.enabled` → `Enabled`
- `auth.ingress_password_note` → `When accessing TSi MUSIC outside of Home Assistant, you will need this password to sign in.`
- `auth.login` → `Sign in`
- `auth.login_error` → `An error occurred during login`
- `auth.logout` → `Sign out`
- `auth.long_lived_tokens` → `Long-lived access tokens`
- `auth.manage_active_sessions` → `View and manage your active login sessions`
- `auth.manage_tokens` → `Manage access tokens`
- `auth.manage_your_profile_info` → `Manage your profile information and settings`
- `auth.no_long_lived_tokens` → `No long-lived access tokens`
- `auth.no_players_selected` → `All players (no restrictions)`
- `auth.no_providers_selected` → `All providers (no restrictions)`
- `auth.no_tokens` → `No tokens yet`
- `auth.password_optional_hint` → `Leave blank to keep current password`
- `auth.revoke` → `Revoke`
- `auth.revoke_session` → `Revoke session`
- `auth.revoke_token` → `Revoke token`
- `auth.role` → `Role`
- `auth.setup_error` → `An error occurred during setup`
- `auth.token_name_hint` → `e.g., 'Home Assistant', 'Mobile App'`
- `background_tasks.download` → `Download`
- `background_tasks.failure.issue` → `issue`
- `background_tasks.failure.issues` → `issues`
- `background_tasks.failure.summary` → `{0} {1}`
- `background_tasks.failure.summary_with_message` → `{0} {1} • {2}`
- `background_tasks.no_value` → `n/a`
- `background_tasks.schedule_dialog.browser_timezone` → `Browser timezone: {0}.`
- `background_tasks.schedule_dialog.daily` → `Daily`
- `background_tasks.schedule_dialog.every_days` → `Run every (days)`
- `background_tasks.schedule_dialog.every_hours` → `Run every (hours)`
- `background_tasks.schedule_dialog.hour` → `Hour`
- `background_tasks.schedule_dialog.hourly` → `Hourly`
- `background_tasks.schedule_dialog.minute` → `Minute`
- `background_tasks.schedule_dialog.weekdays` → `Weekdays`
- `background_tasks.schedule_dialog.weekly` → `Weekly`
- `background_tasks.toast.added` → `The requested action is running in the background.`
- `background_tasks.toast.cancel_requested` → `Cancellation requested for {0}.`
- `background_tasks.toast.log_loaded` → `Loaded log for {0}.`
- `genre_descriptions.afrobeats` → `Afrobeats, not to be confused with Afrobeat or Afroswing, is an umbrella term to describe popular music from West Africa and the diaspora that initially developed in Nigeria, Ghana, and the UK in the 2000s and 2010s. Afrobeats is less of a style per se, and more of a descriptor for the fusion of sounds flowing out of Nigeria and Ghana. Genres such as hiplife, jùjú music, highlife, azonto music, and naija beats, among others, were amalgamated under the "Afrobeats" umbrella.`
- `genre_descriptions.ambient` → `Ambient music is a genre of music that emphasizes tone and atmosphere over traditional musical structure or rhythm. Often "peaceful" sounding and lacking composition, beat, and/or structured melody, ambient music uses textural layers of sound that can reward both passive and active listening, and encourage a sense of calm or contemplation. The genre evokes an "atmospheric", "visual", or "unobtrusive" quality. Nature soundscapes may be included, and some works use sustained or repeated notes, as in drone music. Bearing elements associated with new-age music, instruments such as the piano, strings and flute may be emulated through a synthesizer.`
- `genre_descriptions.anime_and_video_game_music` → `Video game music (VGM) is the soundtrack that accompanies video games. Early video game music was once limited to sounds of early sound chips, such as programmable sound generators (PSG) or FM synthesis chips. These limitations have led to the style of music known as chiptune, which became the sound of the early video games.`
- `genre_descriptions.asian_music` → `Asian music encompasses numerous musical styles, diverse cultural and religious traditions, and forms originating on the Asian continent.`
- `genre_descriptions.bluegrass` → `Bluegrass music is a genre of American roots music that developed in the 1940s in the Appalachian region of the United States. The genre derives its name from the band Bill Monroe and the Blue Grass Boys. Bluegrass has roots in African American genres like blues and jazz and North European genres, such as Irish ballads and dance tunes. Unlike country, it is traditionally played exclusively on acoustic instruments such as the fiddle, mandolin, banjo, guitar and upright bass. It was further developed by musicians who played with Monroe, including 5-string banjo player Earl Scruggs and guitarist Lester Flatt. Bill Monroe once described bluegrass music as, "It's a part of Methodist, Holiness and Baptist traditions. It's blues and jazz, and it has a high lonesome sound."`
- `genre_descriptions.blues` → `Blues is a music genre and musical form that originated among African Americans in the Deep South of the United States around the 1860s. Blues has incorporated spirituals, work songs, field hollers, shouts, chants, and rhymed simple narrative ballads from the African-American culture. The blues form is ubiquitous in jazz, rhythm and blues, and rock and roll, and is characterized by the call-and-response pattern, the blues scale, and specific chord progressions, of which the twelve-bar blues is the most common. Blue notes, usually thirds, fifths or sevenths flattened in pitch, are also an essential part of the sound. Blues shuffles or walking bass reinforce the trance-like rhythm and form a repetitive effect known as the groove.`
- `genre_descriptions.brazilian_music` → `The music of Brazil encompasses various regional musical styles influenced by European, American, African and Amerindian forms. Brazilian music developed some unique and original styles such as forró, repente, coco de roda, axé, sertanejo, samba, bossa nova, MPB, gaucho music, pagode, tropicália, choro, maracatu, embolada, frevo, brega, modinha and Brazilian versions of foreign musical styles, such as rock, pop music, soul, hip-hop, disco music, country music, ambient, industrial and psychedelic music, rap, classical music, fado, and gospel.`
- `genre_descriptions.chanson` → `A chanson is generally any lyric-driven French song. The term is most commonly used in English to refer either to the secular polyphonic French songs of late medieval and Renaissance music or to a specific style of French pop music which emerged in the 1950s and 1960s. The genre had origins in the monophonic songs of troubadours and trouvères, though the only polyphonic precedents were 16 works by Adam de la Halle and one by Jehan de Lescurel. Not until the ars nova composer Guillaume de Machaut did any composer write a significant number of polyphonic chansons.`
- `genre_descriptions.childrens_music` → `Children's music or kids' music is music composed and performed for children. In European-influenced contexts this means music, usually songs, written specifically for a juvenile audience. The composers are usually adults.`
- `genre_descriptions.christmas_music` → `Christmas music comprises a variety of genres of music regularly performed or heard around the Christmas season. Music associated with Christmas may be purely instrumental, or in the case of carols, may employ lyrics about the nativity of Jesus Christ, traditions such as gift-giving and merrymaking, cultural figures such as Santa Claus, or other topics. Many songs simply have a winter or seasonal theme, or have been adopted into the canon for other reasons.`
- `genre_descriptions.church_music` → `Church music is a genre of Christian music written for performance in church, or any musical setting of ecclesiastical liturgy, or music set to words expressing propositions of a sacred nature, such as a hymn.`
- `genre_descriptions.classical` → `Art music is music considered to be of high phonoaesthetic value. It typically implies advanced structural and theoretical considerations or a written musical tradition. In this context, the terms "serious" or "cultivated" are frequently used to present a contrast with ordinary, everyday music. Many cultures have art music traditions; in the Western world, the term typically refers to Western classical music.`
- `genre_descriptions.comedy` → `Comedy music or musical comedy is a genre of music that is comedic in nature. Its history can be traced back to the first century in ancient Greece and Rome, moving forward in time to the Medieval Period, Classical and Romantic eras, and the 20th century. Various forms of comedic musical theatre, including "musical play", "musical comedy", "operetta" and "light opera", evolved from the comic operas first developed in late 17th-century Italy. Popular music artists in the 20th century interested in comedy include Allan Sherman, Frank Zappa, Tiny Tim, Barenaked Ladies, Randy Newman, and "Weird Al" Yankovic. Artists in the 21st century include Tenacious D, Flight of the Conchords, The Lonely Island, Ninja Sex Party and The Axis of Awesome.`
- `genre_descriptions.country` → `Country music, also known as country and western or simply country, is a music genre known for its ballads and dance tunes, identifiable by both traditional lyrics and harmonies accompanied by banjos, mandolins, fiddles, harmonicas, and many types of guitar; either acoustic, electric, steel, or resonator guitars. Once called hillbilly music, the term country music was popularized in the 1940s to give it a correct term.`
- `genre_descriptions.dance` → `Dance music is music composed specifically to facilitate or accompany dancing. It can be either a whole piece or part of a larger musical arrangement. In terms of performance, the major categories are live dance music and recorded dance music. While there exist attestations of the combination of dance and music in ancient history, the earliest Western dance music that we can still reproduce with a degree of certainty are old-fashioned dances. In the Baroque period, the major dance styles were noble court dances. In the classical music era, the minuet was frequently used as a third movement, although in this context it would not accompany any dancing. The waltz also arose later in the classical era. Both remained part of the romantic music period, which also saw the rise of various other nationalistic dance forms like the barcarolle, mazurka, ecossaise, ballade and polonaise.`
- `genre_descriptions.dark_ambient` → `Dark ambient is a subgenre of post-industrial music, that originally emerged in the mid-1980s. It draws primary influence from ambient music and is characterized by ominous, dark drones, discordant overtones and a gloomy, monumental or catacomb-inspired atmosphere. Although mostly an electronic genre, artists frequently sample traditional instruments and make use of semi-acoustic recording procedures.`
- `genre_descriptions.dark_wave` → `Dark wave is a music genre that emerged from the new wave and post-punk movement of the late 1970s. Dark wave compositions are largely based on minor key tonality and introspective lyrics and have been perceived as being dark, romantic and bleak, with an undertone of sorrow. Common features include the use of chordophones such as electric and acoustic guitar, violin and piano, as well as electronic instruments such as synthesizer, sampler and drum machine. Like new wave, dark wave is not a "unified genre but rather an umbrella term" that encompasses a variety of musical styles, including cold wave, ethereal wave, gothic rock, neoclassical dark wave and neofolk.`
- `genre_descriptions.disco` → `Disco is a genre of dance music and a subculture that emerged in the late 1960s from the United States' urban nightlife scene, particularly in African-American, Italian-American, Latino and queer communities. Its sound is typified by four-on-the-floor beats, syncopated basslines, string sections, brass and horns, electric pianos, synthesizers, and electric rhythm guitars.`
- `genre_descriptions.electronic` → `Electronic music broadly is a group of music genres that employ electronic musical instruments, circuitry-based music technology and software, or general-purpose electronics in its creation. It includes both music made using electronic and electromechanical means. Pure electronic instruments depend entirely on circuitry-based sound generation, for instance using devices such as an electronic oscillator, theremin, or synthesizer: no acoustic waves need to be previously generated by mechanical means and then converted into electrical signals. On the other hand, electromechanical instruments have mechanical parts such as strings or hammers that generate the sound waves, together with electric elements including magnetic pickups, power amplifiers and loudspeakers that convert the acoustic waves into electrical signals, process them and convert them back into sound waves. Such electromechanical devices include the telharmonium, Hammond organ, electric piano and electric guitar.`
- `genre_descriptions.experimental` → `Experimental music is a general label for any music or music genre that pushes existing boundaries and genre definitions. Experimental compositional practice is defined broadly by exploratory sensibilities radically opposed to, and questioning of, institutionalized compositional, performing, and aesthetic conventions in music. Elements of experimental music include indeterminacy, in which the composer introduces the elements of chance or unpredictability with regard to either the composition or its performance. Artists may approach a hybrid of disparate styles or incorporate unorthodox and unique elements.`
- `genre_descriptions.field_recording` → `Field recording is the production of audio recordings outside recording studios, and the term applies to recordings of both natural and human-produced sounds. It can also include the recording of electromagnetic fields or vibrations using different microphones like a passive magnetic antenna for electromagnetic recordings or contact microphones, or underwater field recordings made with hydrophones to capture the sounds and/or movements of whales, or other sealife. These recordings are often regarded as being very useful for sound designers and foley artists.`
- `genre_descriptions.folk` → `Folk music is a music genre that includes traditional folk music and the contemporary genre that evolved from the former during the 20th-century folk revival. Some types of folk music may be called world music. Traditional folk music has been defined in several ways: as music transmitted orally, music with unknown composers, music that is played on traditional instruments, music about cultural or national identity, music that changes between generations, music associated with a people's folklore, or music performed by custom over a long period of time. It has been contrasted with commercial and classical styles. The term originated in the 19th century, but folk music extends beyond that.`
- `genre_descriptions.funk` → `Funk is a music genre that originated in African-American communities in the mid-1960s when musicians created a rhythmic, danceable new form of music through a mixture of various music genres that were popular among African-Americans in the mid-20th century. It deemphasizes melody and chord progressions and focuses on a strong rhythmic groove of a bassline played by an electric bassist and a drum part played by a percussionist, often at slower tempos than other popular music. Funk typically consists of a complex percussive groove with rhythm instruments playing interlocking grooves that create a "hypnotic" and "danceable" feel. Early funk, specifically James Brown, fused jazz and blues, and added a syncopated drum groove.`
- `genre_descriptions.gangsta_rap` → `Gangsta or gangster rap, initially called reality rap, is a subgenre of hip-hop that conveys the culture, values, and experiences of urban gangs and street hustlers, frequently discussing unpleasant realities of the world in general through an urban lens. Emerging in the late 1980s, gangsta rap's pioneers include Schoolly D and Ice-T, later expanding with artists such as N.W.A. In 1992, via record producer and rapper Dr. Dre, rapper Snoop Dogg, and their G-funk sound, gangster rap broadened to mainstream popularity.`
- `genre_descriptions.gospel` → `Gospel music is a traditional genre of Christian music and a cornerstone of Christian media, characterized by dominant vocals and lyrics that reflect Christian teachings and values. The creation, performance, significance, and even the definition of gospel music vary according to culture and social context. Gospel music is composed and performed for many purposes, including aesthetic pleasure, and also religious or ceremonial purposes, and as an entertainment product for the marketplace. Gospel music can be traced to the early 17th century.`
- `genre_descriptions.hip_hop` → `Hip-hop is a genre of popular music that emerged in the early 1970s alongside an associated subculture in the African-American and Caribbean immigrants communities of New York City. The musical style is characterized by the synthesis of a wide range of techniques, but rapping is frequent enough that it has become a defining characteristic. Other key markers of the genre are the disc jockey (DJ), turntablism, scratching, beatboxing, and instrumental tracks. Cultural interchange has always been central to the hip-hop genre; it simultaneously borrows from its social environment while commenting on it.`
- `genre_descriptions.indian_classical` → `Indian classical music is the classical music of the Indian subcontinent. It is generally described using terms like Shastriya Sangeet and Marg Sangeet. It has two major traditions: the North Indian classical music known as Hindustani and the South Indian expression known as Carnatic. Hindustani music emphasizes improvisation and exploration of all aspects of a raga, while Carnatic performances tend to be short composition-based. However, the two systems continue to have more common features than differences. Another unique classical music tradition from the eastern part of India is Odissi music, which has evolved over the last two thousand years.`
- `genre_descriptions.industrial` → `Industrial music is a subgenre of experimental music inspired by post-industrial society, initially drawing influences from avant-garde and early electronic music genres such as musique concrète, tape music, noise and sound collage. The term was coined in 1976 by Monte Cazazza and adopted by Throbbing Gristle with the founding of Industrial Records. Other early industrial musicians include NON and Cabaret Voltaire. By the late 1970s, additional artists emerged such as Clock DVA, Nocturnal Emissions, Einstürzende Neubauten, SPK, Nurse with Wound, and Z’EV, alongside Whitehouse who coined the subgenre "power electronics".`
- `genre_descriptions.jazz` → `Jazz is a music genre that originated in the African-American communities of New Orleans, Louisiana, in the late 19th and early 20th centuries. Its roots are in blues, ragtime, European harmony, African rhythmic rituals, spirituals, hymns, marches, vaudeville song, and dance music. Since the 1920s Jazz Age, it has been recognized as a major form of musical expression in traditional and popular music. Jazz is characterized by swing and blue notes, complex chords, call and response vocals, polyrhythms and improvisation.`
- `genre_descriptions.klezmer` → `Klezmer is an instrumental musical tradition of the Ashkenazi Jews of Central and Eastern Europe. The essential elements of the tradition include dance tunes, ritual melodies, and virtuosic improvisations played for listening; these would have been played at weddings and other social functions. The musical genre incorporated elements of many other musical genres including Ottoman music, Baroque music, German and Slavic folk dances, and religious Jewish music. As the music arrived in the United States, it lost some of its traditional ritual elements and adopted elements of American big band and popular music. Among the European-born klezmers who popularized the genre in the United States in the 1910s and 1920s were Dave Tarras and Naftule Brandwein; they were followed by American-born musicians such as Max Epstein, Sid Beckerman and Ray Musiker.`
- `genre_descriptions.latin` → `Latin music is a term used by the music industry as a catch-all category for various styles of music from Ibero-America, which encompasses Latin America, Spain, Portugal, and the Latino population in Canada and the United States, as well as music that is sung in either Spanish or Portuguese. It may also include music from other territories where Spanish- and Portuguese-language music is made.`
- `genre_descriptions.marching_band` → `Marching band is a performance-based, visual-musical genre featuring musicians playing brass, woodwind, and percussion instruments while moving in synchronized, choreographed formations, usually at 120-160+ beats per minute. It blends musical performance with athletic, high-speed marching, often incorporating pop, rock, and classical music alongside traditional military-style marches.`
- `genre_descriptions.metal` → `umbrella category of music genres of metal branch, derived from heavy metal music while not necessarily being its subgenre`
- `genre_descriptions.middle_eastern_music` → `The various nations of the region include the Arabic-speaking countries of the Middle East, the traditional Persian ritual music, the Jewish music of Israel and the diaspora, Kurdish music, Armenian music. Azeri Music, the varied traditions of Cypriot music, the Turkish music of Turkey, traditional Assyrian music, Coptic ritual music in Egypt as well as other genres of Egyptian music in general. It is widely regarded that some Middle-Eastern musical styles have influenced Central Asia, as well as the Balkans, Southern Italy, and Spain.`
- `genre_descriptions.musical` → `Musical theatre is a form of theatrical performance that combines songs, spoken dialogue, acting and dance. The story and emotional content of a musical – humor, pathos, love, anger – are communicated through words, music, movement and technical aspects of the entertainment as an integrated whole. Although musical theatre overlaps with other theatrical forms like opera and dance, it may be distinguished by the equal importance given to the music as compared with the dialogue, movement and other elements. Since the early 20th century, musical theatre stage works have generally been called, simply, musicals.`
- `genre_descriptions.new_age` → `New age is a genre of music intended to create artistic inspiration, relaxation, and optimism. It is used by listeners for yoga, massage, meditation, and reading as a method of stress management to bring about a state of ecstasy rather than trance, or to create a peaceful atmosphere in homes or other environments. It is sometimes associated with environmentalism and New Age spirituality; however, most of its artists have nothing to do with "New Age spirituality", and some even reject the term.`
- `genre_descriptions.poetry` → `Poetry as a musical genre merges spoken-word or recited verse with musical accompaniment, creating a hybrid form focused on emotional expression, storytelling, and rhythm. Often featuring acoustic instruments (piano, guitar) or experimental soundscapes, this genre blurs the line between literature and song,, highlighting the inherent melody and cadence in spoken words.`
- `genre_descriptions.polka` → `Polka is a dance style and genre of dance music in 24 originating in nineteenth-century Bohemia, now part of the Czech Republic. Though generally associated with Czech and Central European culture, polka is popular throughout Europe and the Americas.`
- `genre_descriptions.pop` → `Pop music, or simply pop, is a genre of popular music that originated in its modern form during the mid-1950s in the United States and the United Kingdom. During the 1950s and 1960s, pop music encompassed rock and roll and the youth-oriented styles it influenced. Rock and pop music remained roughly synonymous until the late 1960s, after which pop became associated with music that was more commercial, ephemeral, and accessible.`
- `genre_descriptions.psychedelic` → `Psychedelic music is a wide range of popular music styles and genres influenced by 1960s psychedelia, a subculture of people who used psychedelic drugs such as DMT, LSD, mescaline, and psilocybin mushrooms, to experience synesthesia and altered states of consciousness. Psychedelic music may also aim to enhance the experience of using these drugs and has been found to have a significant influence on psychedelic therapy.`
- `genre_descriptions.punk` → `umbrella category of music genres related to punk subculture, derived from punk rock music scene while not necessarily being its subgenre`
- `genre_descriptions.r_b` → `Rhythm and blues, frequently abbreviated as R&B or R'n'B, is a genre of popular music that originated within African American communities in the 1940s. The term was originally used by record companies to describe recordings marketed predominantly to African Americans, at a time when "rocking, jazz based music ... [with a] heavy, insistent beat" was starting to become more popular.
In the commercial rhythm and blues music typical of the 1950s through the 1970s, the bands usually consisted of a piano, one or two guitars, bass, drums, one or more saxophones, and sometimes background vocalists. R&B lyrical themes often encapsulate the African-American history and experience of pain and the quest for freedom and joy, as well as triumphs and failures in terms of societal racism, oppression, relationships, economics, and aspirations.`
- `genre_descriptions.ragtime` → `Ragtime, also spelled rag-time or rag time, is a musical style noted for its syncopated or "ragged" rhythm. It originated in African American communities in the late 19th century and was propelled to popularity in the 1890s to 1910s by composers such as James Scott, Joseph Lamb, and particularly Scott Joplin. Known as the "King of Ragtime", Joplin gained fame through compositions like "Maple Leaf Rag" and "The Entertainer".`
- `genre_descriptions.rai` → `Raï, sometimes written rai, is a form of Algerian folk music that dates back to the 1920s. Singers of Raï are called cheb (شاب) or cheba (شابة), i.e. 'young', as opposed to sheikh, i.e. 'old', the name given to Chaabi singers. The tradition arose in the city of Oran, primarily among the poor. Traditionally sung by men, by the end of the 20th century, female singers became common. The lyrics have concerned social issues such as disease and the policing of European colonies that affected native populations.`
- `genre_descriptions.reggae` → `Reggae is a music genre that originated in Jamaica in the late 1960s. The term also refers to the modern popular music of Jamaica and its diaspora. The 1968 single by Toots and the Maytals titled "Do the Reggay" was the first popular song to use the word reggae, effectively naming the genre and introducing it to a global audience.`
- `genre_descriptions.reggaeton` → `Reggaeton is a style of popular and electronic music that originated in Panama during the late 1980s. It has been popularized and dominated by artists from Puerto Rico since the early 1990s.`
- `genre_descriptions.rock` → `Rock music is a genre of popular music that originated in the United States as "rock and roll" in the late 1940s and early 1950s, developing into a range of styles from the mid-1960s, primarily in the United States and United Kingdom. It has its roots in rock and roll, a style that drew from the African-American musical genres of blues and rhythm and blues, as well as from country music. Rock also drew strongly from genres such as electric blues and folk, and incorporated influences from jazz and other styles. Rock is typically centered on the electric guitar, usually as part of a rock group with electric bass guitar, drums, and one or more singers.`
- `genre_descriptions.salsa` → `Salsa music is a style of Latin American music, combining elements of Cuban and Puerto Rican influences. Because most of the basic musical components predate the labeling of salsa, there have been many controversies regarding its origin. Most songs considered as salsa are primarily based on son montuno and son cubano, with elements of cha-cha-chá, bolero, rumba, mambo, jazz, R&B, bomba, and plena. All of these elements are adapted to fit the basic Son montuno template when performed within the context of salsa.`
- `genre_descriptions.singer_songwriter` → `group of musical genres that emerged in the mid-20th century, referring to the music of singer-songwriters, often characterised by political or personal lyrics and minimal acoustic accompaniment`
- `genre_descriptions.ska` → `Ska is a music genre that originated in Jamaica in the late 1950s and was the precursor to rocksteady and reggae. It combined elements of Caribbean mento and calypso with American jazz and rhythm and blues. Ska is characterized by a walking bass line accented with rhythms on the off beat. It was developed in Jamaica in the 1960s when Stranger Cole, Prince Buster, Clement "Coxsone" Dodd, and Duke Reid formed sound systems to play American rhythm and blues and then began recording their own songs. In the early 1960s, ska was the dominant music genre of Jamaica and was popular with British mods and with many skinheads.`
- `genre_descriptions.soul` → `Soul music is a popular music genre that originated in African-American communities throughout the United States in the late 1950s and early 1960s. Catchy rhythms, stressed by handclaps and extemporaneous body movements, are an important hallmark of soul. Other characteristics are a call and response between the lead and backing vocalists, an especially tense vocal sound, and occasional improvisational additions, twirls, and auxiliary sounds. Soul music is known for reflecting African-American identity and stressing the importance of African-American culture.`
- `genre_descriptions.sound_effects` → `Sound effects as a musical genre—often encompassing soundscape composition, musique concrète, and noise music—utilize environmental noises, mechanical sounds, and Foley recordings as primary musical elements rather than traditional melodies or harmonies. This avant-garde approach creates immersive, narrative, and textured auditory experiences.`
- `genre_descriptions.soundtrack` → `A film score is original music written specifically to accompany a film or a television program. The score consists of a number of orchestral, instrumental, or choral pieces called cues, which are timed to begin and end at specific points during the film to enhance the dramatic narrative and emotional impact of scenes. Scores are written by one or more composers under the guidance of or in collaboration with the film's director or producer and are then most often performed by an ensemble of musicians – usually including an orchestra or band, instrumental soloists, and choir or vocalists – known as playback singers – and recorded by a sound engineer. The term is less frequently applied to music written for media such as live theatre, television and radio programs, and video games, and that music is typically referred to as either the soundtrack or incidental music.`
- `genre_descriptions.spoken_word` → `Spoken word is a performance-based genre combining spoken poetry, storytelling, or monologue with musical accompaniment or rhythmic delivery, focusing on the voice as the primary instrument. Rooted in oral traditions and the Beat Generation, it merges literary artistry with music, commonly featuring themes of social justice, politics, and personal narrative, often accompanied by jazz, rock, or folk elements.`
- `genre_descriptions.swing` → `Swing music is a style of jazz that developed in the United States during the late 1920s and early 1930s. It became nationally popular from the mid-1930s. Swing represents the most famous era of jazz as a genre of entertainment, before the emergence of modern jazz. Swing bands usually featured soloists who would improvise on the melody over the arrangement. The danceable swing style of big bands and bandleaders such as Fletcher Henderson and Benny Goodman was the dominant form of American popular music from 1935 to 1946, known as the swing era, when people were dancing the Lindy Hop. The verb "to swing" is also used as a term of praise for playing that has a strong groove or drive. Big band leaders of the swing era include Benny Goodman, Duke Ellington, Count Basie, Jimmie Lunceford, Cab Calloway, Benny Carter, Jimmy Dorsey, Tommy Dorsey, Earl Hines, Bunny Berigan, Harry James, Lionel Hampton, Glenn Miller, and Artie Shaw.`
- `genre_descriptions.tango` → `Tango is a style of music in 24 or 44 time that originated in Uruguay and Argentina among European immigrants in the late 19th and early 20th centuries. It has mainly Spanish, Italian, Gaucho, African, and French cultural roots. It is traditionally played on a solo guitar, guitar duo, or an ensemble, known as the orquesta típica, which includes at least two violins, flute, piano, double bass, and at least two bandoneóns. Sometimes guitars and a clarinet join the ensemble. Tango may be purely instrumental or may include a vocalist. Tango music and dance have become popular throughout the world.`
- `genre_descriptions.trap` → `Trap music, also known simply as trap, is a subgenre of hip-hop music that originated in the Southern United States. Lyrical references to trap started in 1991 but the modern sound of trap appeared in 1999. The genre gets its name from the Atlanta term "trap house", a drug house. Trap music features simple, rhythmic, minimalistic productions that use synthesized drums and is characterized by complex hi-hat drum beats, snare drums, bass drums, some tuned with a long decay to emit a bass frequency. Lyrics often focus on drug use and urban violence.`
- `genre_descriptions.waltz` → `A waltz, probably deriving from German Ländler, is dance music in triple metre, often written in 34 time. A waltz typically sounds one chord per measure, and the accompaniment style particularly associated with the waltz is to play the root of the chord on the first beat, the upper notes on the second and third beats.`
- `genre_descriptions.wellness` → `Meditation music is music performed to aid in the practice of meditation. It can have a specific religious content, but also more recently has been associated with modern composers who use meditation techniques in their process of composition, or who compose such music with no particular religious group as a focus. The concept also includes music performed as an act of meditation.`
- `genre_names.ambient` → `Ambient`
- `genre_names.bluegrass` → `Bluegrass`
- `genre_names.blues` → `Blues`
- `genre_names.chanson` → `Chanson`
- `genre_names.country` → `Country`
- `genre_names.dance` → `Dance`
- `genre_names.dark_ambient` → `Dark ambient`
- `genre_names.dark_wave` → `Dark wave`
- `genre_names.disco` → `Disco`
- `genre_names.experimental` → `Experimental`
- `genre_names.field_recording` → `Field recording`
- `genre_names.folk` → `Folk`
- `genre_names.funk` → `Funk`
- `genre_names.gangsta_rap` → `Gangsta rap`
- `genre_names.gospel` → `Gospel`
- `genre_names.hip_hop` → `Hip hop`
- `genre_names.industrial` → `Industrial`
- `genre_names.jazz` → `Jazz`
- `genre_names.klezmer` → `Klezmer`
- `genre_names.metal` → `Metal`
- `genre_names.musical` → `Musical`
- `genre_names.new_age` → `New age`
- `genre_names.polka` → `Polka`
- `genre_names.pop` → `Pop`
- `genre_names.punk` → `Punk`
- `genre_names.ragtime` → `Ragtime`
- `genre_names.rai` → `Raï`
- `genre_names.reggae` → `Reggae`
- `genre_names.reggaeton` → `Reggaeton`
- `genre_names.rock` → `Rock`
- `genre_names.salsa` → `Salsa`
- `genre_names.ska` → `Ska`
- `genre_names.soul` → `Soul`
- `genre_names.spoken_word` → `Spoken word`
- `genre_names.swing` → `Swing`
- `genre_names.tango` → `Tango`
- `genre_names.trap` → `Trap`
- `login.remote_id_placeholder` → `e.g., MA-X7K9-P2M4`
- `login.server_address_placeholder` → `http://192.168.1.100:8095`
- `loudness_measurement` → `{0} LUFS`
- `mass` → `TSi MUSIC`
- `player_options.dimmer` → `Dimmer`
- `player_options.enhancer` → `Enhancer`
- `player_options.pure_direct` → `Pure direct`
- `player_options.surround_3d` → `Surround 3D`
- `podcast` → `Podcast`
- `podcasts` → `Podcasts`
- `providers.party.boost` → `Boost`
- `providers.party.powered_by` → `Powered by`
- `recommendations.libraries` → `Libraries`
- `recommendations.listen_again` → `Listen again`
- `recommendations.newest_authors` → `Newest authors`
- `recommendations.newest_episodes` → `Newest episodes`
- `recommendations.recent_series` → `Recent series`
- `recommendations.trending_podcasts` → `Trending podcasts`
- `remote.recent_connections` → `Recent Connections`
- `remote.remember_me` → `Remember me on this device`
- `remote.remote_id` → `Remote ID`
- `remote.remote_id_placeholder` → `e.g., MA-X7K9-P2M4`
- `remote.sign_in` → `Sign In`
- `settings.about` → `About`
- `settings.about_description` → `Version information, credits and more`
- `settings.bug_reports` → `Bug Reports`
- `settings.category.options` → `Player options`
- `settings.category.web_player` → `Web Player`
- `settings.confirm_full_restore` → `This will DELETE ALL existing genres and aliases, recreate only the defaults, and remap all existing media items to the new genres. All custom genres, alias mappings, and media associations will be lost.`
- `settings.core_module.cache.name` → `Cache`
- `settings.core_module.player_queues.name` → `Player Queues`
- `settings.core_module.players.name` → `Players`
- `settings.core_module.remote_access.description` → `Enables remote access to your TSi MUSIC server`
- `settings.core_module.streams.name` → `Streams`
- `settings.core_module.webserver.description` → `Configuration of the webserver and API`
- `settings.discard` → `Discard changes`
- `settings.discussion_forums` → `Discussion Forums`
- `settings.dsp.parametric_eq.filter_types.notch` → `Notch`
- `settings.excluded_genres` → `Excluded genres`
- `settings.frontend_description` → `Customize the user interface theme and appearance`
- `settings.full_restore_genres_description` → `Deletes all genres and aliases, recreates the defaults, and remaps all existing media items. Use with caution!`
- `settings.genre_table_page_info` → `{0}–{1} of {2}`
- `settings.language.options.lt_LT` → `Lithuanian`
- `settings.language.options.lv_LV` → `Latvian`
- `settings.last_scan` → `Last Scan`
- `settings.last_scan_mapped` → `Items Mapped (Last Scan)`
- `settings.links` → `Links`
- `settings.log_level.options.global` → `Global`
- `settings.metadata_providers_description` → `Manage metadata providers for artwork and additional info`
- `settings.missing_players_hint` → `Missing players? {0}`
- `settings.mobile_sidebar_side.label` → `Mobile sidebar side`
- `settings.mobile_sidebar_side.options.left` → `Left`
- `settings.mobile_sidebar_side.options.right` → `Right`
- `settings.onboarding_footer` → `You can always add more providers later from this settings page.`
- `settings.onboarding_player_title` → `Players`
- `settings.onboarding_title` → `Welcome to TSi MUSIC!`
- `settings.one_player` → `1 player`
- `settings.player_needs_setup` → `This player requires setup`
- `settings.players_count` → `{0} player{1}`
- `settings.players_total` → `{0} total player{1}`
- `settings.plugin_providers_description` → `Manage plugins that extend TSi MUSIC functionality`
- `settings.plugins` → `Plugins`
- `settings.profile_description` → `Manage your personal account settings and preferences`
- `settings.proud_part_of` → `Proud part of`
- `settings.provider_codeowners` → `This provider is contributed/maintained by`
- `settings.provider_requires_attention` → `This provider requires attention`
- `settings.providers_description` → `Manage your music sources, player providers and plugins`
- `settings.reconfigure` → `Reconfigure`
- `settings.remote_access_description` → `Securely access TSi MUSIC from anywhere`
- `settings.remote_access_explanation_ha_cloud` → `For the best experience and reliability, a Home Assistant Cloud subscription is required.`
- `settings.remote_access_feature_no_port_forwarding` → `No port forwarding or VPN required`
- `settings.remote_access_feature_webrtc` → `Based on WebRTC technology for peer-to-peer connections`
- `settings.remote_access_mode_optimized_description` → `Using STUN/TURN servers from Home Assistant Cloud for optimal performance. Works reliably in all network configurations.`
- `settings.remote_access_protocol_basic` → `WebRTC with public STUN servers (may not work in complex network setups).`
- `settings.remote_access_protocol_optimized` → `WebRTC with optimized STUN/TURN servers from Home Assistant Cloud (works in all network setups).`
- `settings.remote_access_qr_code` → `QR Code`
- `settings.remote_access_qr_code_description` → `Scan with your phone camera to connect instantly.`
- `settings.remote_access_signaling_server_description` → `Signaling server in the cloud.`
- `settings.restore_all_present` → `All default genres are already present.`
- `settings.restore_missing_defaults_description` → `Adds any missing default genres without affecting your existing genres or custom mappings.`
- `settings.restore_success` → `Restored {0} missing genre(s).`
- `settings.scan_ago` → `{0} ago`
- `settings.scan_never` → `Never`
- `settings.scan_now` → `Scan Now`
- `settings.scanner_running` → `Running...`
- `settings.scanner_status` → `Scanner Status`
- `settings.sendspin_static_delay.label` → `Static playback delay (ms)`
- `settings.server_as_addon` → `Home Assistant add-on`
- `settings.stage.options.beta` → `Beta`
- `settings.stage.options.experimental` → `Experimental`
- `settings.stay` → `Stay`
- `settings.system_logging_description` → `View and download server logs for troubleshooting`
- `settings.unsaved_changes` → `Unsaved changes`
- `settings.unsaved_changes_message` → `You have unsaved changes. Are you sure you want to leave without saving?`
- `settings.users_description` → `Manage user accounts, roles, and permissions`
- `settings.version_info` → `Version Information`
- `settings.view_documentation` → `View documentation`
- `settings.view_players` → `View players`
- `settings.web_player_enabled.description` → `Allow playback to this device/browser using the built-in Sendspin web player.`
- `sort.original` → `Original`
- `streamdetails.file_info.codec` → `Codec: {0}`
- `tooltip.in_provider_library` → `This item is in the provider's library`
- `view.discovery` → `Discovery`
- `volume_normalization_gain_correction` → `{0} dB`

### Todas as chaves com texto misturado
- `alias_added_successfully` → pt: `Alias adicionado com sucesso` | en: `Alias added successfully`
- `alias_linked_successfully` → pt: `Alias vinculado com sucesso` | en: `Alias linked successfully`
- `background_task.add_playlist_tracks` → pt: `Adicionar itens à playlist {0}` | en: `Add items to playlist {0}`
- `background_task.refresh_playlist_metadata` → pt: `Atualizar metadados da playlist` | en: `Refresh playlist metadata`
- `background_task.remove_playlist_tracks` → pt: `Remover itens da playlist {0}` | en: `Remove items from playlist {0}`
- `background_task.sync_provider_playlists` → pt: `Sincronizar Playlists para {0}` | en: `Sync Playlists for {0}`
- `background_task.sync_provider_podcasts` → pt: `Sincronizar Podcasts para {0}` | en: `Sync Podcasts for {0}`
- `background_tasks.schedule_dialog.select_weekday` → pt: `Selecionar at least one weekday.` | en: `Select at least one weekday.`
- `background_tasks.schedule_dialog.unsupported` → pt: `This tarefa agendamento can not be edited here.` | en: `This task schedule can not be edited here.`
- `background_tasks.toast.history_cleared` → pt: `Finalizado tarefa history limpo.` | en: `Finished task history cleared.`
- `background_tasks.toast.log_download_started` → pt: `Tarefa log download started.` | en: `Task log download started.`
- `background_tasks.toast.removed` → pt: `Removed {0} from tarefa history.` | en: `Removed {0} from task history.`
- `background_tasks.toast.schedule_updated` → pt: `Updated agendamento for {0}.` | en: `Updated schedule for {0}.`
- `background_tasks.total` → pt: `{0} tarefa{1} em segundo plano no total` | en: `{0} total background task{1}`
- `confirm_delete_genre` → pt: `Tem certeza de que deseja excluir este gênero? O gênero em si será removido, juntamente com seus mapeamentos de alias.` | en: `Are you sure you want to delete this genre? The genre itself will be removed, along with its alias mappings.`
- `confirm_delete_genres` → pt: `Tem certeza de que deseja excluir {0} gêneros? Os gêneros serão removidos, juntamente com seus mapeamentos de alias.` | en: `Are you sure you want to delete {0} genres? The genres will be removed, along with their alias mappings.`
- `confirm_promote_alias` → pt: `Promover "{0}" para um gênero independente? Isso criará um novo gênero e removerá o alias do gênero atual.` | en: `Promote "{0}" to a standalone genre? This will create a new genre and remove the alias from the current genre.`
- `confirm_remove_alias` → pt: `Tem certeza de que deseja remover o alias "{0}" deste gênero?` | en: `Are you sure you want to remove the alias "{0}" from this genre?`
- `genre_names.afrobeats` → pt: `Afrobeats (música urbana/pop da África Ocidental)` | en: `Afrobeats (west african urban/pop music)`
- `genre_names.anime_and_video_game_music` → pt: `Anime & música de videogame` | en: `Anime & video game music`
- `item_fully_played` → pt: `Este item foi totalmente reproduzido` | en: `This item has been fully played`
- `item_in_progress` → pt: `Este item foi parcialmente reproduzido` | en: `This item has been partially played`
- `items_selected` → pt: `{0} item(ns) selecionado(s)` | en: `{0} item(s) selected`
- `items_total` → pt: `{0} item(ns) no total` | en: `{0} total item(s)`
- `mapped_aliases` → pt: `Aliases Mapeados` | en: `Mapped Aliases`
- `merge_genres_description` → pt: `Selecione um gênero de destino para mesclar. Todos os aliases e mídias mapeadas dos gêneros de origem serão transferidos para o destino.` | en: `Select a target genre to merge into. All aliases and mapped media from the source genres will be transferred to the target.`
- `not_found_headline` → pt: `Ops, esta página saiu da setlist.` | en: `Oops, this page is off the setlist.`
- `promote_alias_successfully` → pt: `Alias promovido com sucesso` | en: `Alias promoted successfully`
- `providers.party.confirm_disable_guest_access` → pt: `Are you sure you want to desativar guest access? Guests will no longer be able to juntar the party, browse music, or add songs to the fila.` | en: `Are you sure you want to disable guest access? Guests will no longer be able to join the party, browse music, or add songs to the queue.`
- `providers.party.confirm_enable_guest_access` → pt: `Are you sure you want to ativar guest access? This allows anyone with the link or QR code to juntar the party, browse music, and add songs to the fila.` | en: `Are you sure you want to enable guest access? This allows anyone with the link or QR code to join the party, browse music, and add songs to the queue.`
- `providers.party.guest_page.boost_available` → pt: `Boost disponível` | en: `Boost available`
- `providers.party.guest_page.boost_disabled` → pt: `Boost está desativado pelo anfitrião.` | en: `Boost is disabled by the host.`
- `providers.party.guest_page.boost_limit_reached` → pt: `Limite de Boost atingido. Próximo uso disponível em {0} minutos.` | en: `Boost limit reached. Next use available in {0} minutes.`
- `providers.party.link_copy_fail` → pt: `Falhou to copiar link` | en: `Failed to copy link`
- `providers.party.link_copy_success` → pt: `Link copiado!` | en: `Link copied!`
- `remove_provider_mapping_confirm` → pt: `Tem certeza de que deseja remover este mapeamento do provedor? Isso desvinculará o item dos detalhes atuais. Ele pode reaparecer se você executar uma nova verificação de todas as correspondências do provedor.` | en: `Are you sure you want to remove this provider mapping? This will unlink the item from the current item details. It may come back if you perform a rescan for all provider matches.`
- `sort.album_sort_name` → pt: `Álbum (ordenar name)` | en: `Album (sort name)`
- `tooltip.filter_genre` → pt: `Filtrar por genre` | en: `Filter by genre`
- `tooltip.filter_provider` → pt: `Filtrar por music provider` | en: `Filter by music provider`
- `tooltip.hide_empty_genres` → pt: `Ocultar empty genres` | en: `Hide empty genres`
- `tooltip.linked` → pt: `Esse item do provedor está vinculado aos detalhes do item atual` | en: `This provideritem is linked to the current itemdetails`
- `tooltip.open_provider_link` → pt: `Abrir esse item no site do provedor` | en: `Open this item on the provider's website`
- `tooltip.show_all_genres` → pt: `Mostrar all genres` | en: `Show all genres`
- `tooltip.show_empty_genres` → pt: `Mostrar empty genres` | en: `Show empty genres`
- `tooltip.show_only_default_genres` → pt: `Mostrar only default genres` | en: `Show only default genres`
- `view.panel_compact` → pt: `Visão compacta dos thumbs` | en: `Compact thumbs view`

### Todas as chaves com placeholders mal formatados
- `queue_radio_based_on` → en: `set()` | pt: `{'{0}'}`
- `sync_now` → en: `set()` | pt: `{'{0}'}`
