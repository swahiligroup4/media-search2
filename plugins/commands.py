from pyrogram import Client
import uuid
import io
from plugins.database import db
from info import filters
from utils import save_file,add_user,Media,User,is_user_exist,get_filter_results,upload_group
from pyrogram.types import CallbackQuery,InlineKeyboardMarkup,InlineKeyboardButton
from plugins.helper_funcs import (
    generate_button,
    upload_photo,
    split_quotes
)  
import os
import logging
logger = logging.getLogger(__name__)

@Client.on_message(filters.command('total') & filters.owner)
async def total(bot, message):
    """Show total files in database"""
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')


@Client.on_message(filters.command('logger') & filters.owner)
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('add'))
async def new_filter(client: Client, message):
    status= await db.is_admin_exist(message.from_user.id)
    if not status:
        return
    strid = str(uuid.uuid4())
    args = message.text.html.split(None, 1)
    user_id = message.from_user.id
    if len(args) < 2:
        await message.reply_text("Use Correct format 😐", quote=True)
        return
    
    extracted = split_quotes(args[1])
    text = extracted[0].lower()
    msg_type = 'Text'
   
    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text("Add some content to save your filter!", quote=True)
        return

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = generate_button(extracted[1], strid)
        fileid = None
        if not reply_text:
            await message.reply_text("You cannot have buttons alone, give some text to go with it!", quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        reply_text = ""
        btn = []
        fileid = None
        alert = None
        msg_type = 'Text'
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            replied = message.reply_to_message
            msg = replied.document or replied.video or replied.audio or replied.animation or replied.sticker or replied.voice or replied.video_note or None
            if msg:
                fileid = msg.file_id
                if replied.document:
                    msg_type = 'Document'
                elif replied.video:
                    msg_type = 'Video'
                elif replied.audio:
                    msg_type = 'Audio'
                elif replied.animation:
                    msg_type = 'Animation'
                elif replied.sticker:
                    msg_type = 'Sticker'
                elif replied.voice:
                    msg_type = 'Voice'
                elif replied.video_note:
                    msg_type = 'Video Note'

                reply_text = message.reply_to_message.caption.html
            
            elif replied.photo:
                fileid = await upload_photo(replied)
                msg_type = 'Photo'
                if not fileid:
                    return
                reply_text = message.reply_to_message.caption.html
            
                    
            elif replied.text:
                reply_text = message.reply_to_message.text.html
                msg_type = 'Text'
                fileid = None
            else:
                await message.reply('Not Supported..!')
                return
            alert = None
        except:
            pass
            

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            fileid = await upload_photo(message.reply_to_message)
            if not fileid:
                return
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Photo'

    elif message.reply_to_message and message.reply_to_message.video:
        try:
            fileid = message.reply_to_message.video.file_id
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Video'

    elif message.reply_to_message and message.reply_to_message.audio:
        try:
            fileid = message.reply_to_message.audio.file_id
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Audio'
   
    elif message.reply_to_message and message.reply_to_message.document:
        try:
            fileid = message.reply_to_message.document.file_id
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Document'

    elif message.reply_to_message and message.reply_to_message.animation:
        try:
            fileid = message.reply_to_message.animation.file_id
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Animation'

    elif message.reply_to_message and message.reply_to_message.sticker:
        try:
            fileid = message.reply_to_message.sticker.file_id
            reply_text, btn, alert =  generate_button(extracted[1], strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Sticker'

    elif message.reply_to_message and message.reply_to_message.voice:
        try:
            fileid = message.reply_to_message.voice.file_id
            reply_text, btn, alert = generate_button(message.reply_to_message.caption.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Voice'
    elif message.reply_to_message and message.reply_to_message.video_note:
        try:
            fileid = message.reply_to_message.video_note.file_id
            reply_text, btn, alert = generate_button(extracted[1], strid)
        except Exception as a:
            reply_text = ""
            btn = []
            alert = None
        msg_type = 'Video Note'
    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = generate_button(message.reply_to_message.text.html, strid)
        except:
            reply_text = ""
            btn = []
            alert = None
    else:
        await message.reply('Not Supported..!')
        return
    
    try:
        if fileid:
            if msg_type == 'Photo':
                await message.reply_photo(
                    photo = fileid,
                    caption = reply_text,
                    reply_markup = InlineKeyboardMarkup(btn) if len(btn) != 0 else None
                )
            else:
                await message.reply_cached_media(
                    file_id = fileid,
                    caption = reply_text,
                    reply_markup = InlineKeyboardMarkup(btn) if len(btn) != 0 else None
                )
        else:
            await message.reply(
                text = reply_text,
                disable_web_page_preview = True,
                reply_markup = InlineKeyboardMarkup(btn) if len(btn) != 0 else None
            )
    except Exception as a:
        try:
            await message.reply(text = f"<b>❌ Error</b>\n\n{str(a)}\n\n<i>Join @CodeXBotzSupport for Support</i>")
        except:
            pass
        return

    await save_file(text, reply_text, btn, fileid, alert, msg_type, strid,user_id)
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text = 'Share filter', switch_inline_query = text),
                InlineKeyboardButton(text = 'Try Here', switch_inline_query_current_chat = text)
            ]
        ]
    )
    await message.reply_text(f"<code>{text}</code> Added", quote = True, reply_markup = reply_markup)

@Client.on_message(filters.command('delete'))
async def del_filter(client: Client, message):
    status= await db.is_admin_exist(message.from_user.id)
    if not status:
        return
    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            "<i>Mention the filtername which you wanna delete!</i>\n\n"
            f"<code>/delete filtername</code>\n\n"
            "Use /filters to view all available filters",
            quote=True
        )
        return

    query = text.lower()
    filter={'text': query}
    filter['group_id'] = message.from_user.id
    found = Media.find(filter)
    if found:
        await Media.collection.delete_one(filter)
        await message.reply_text(
            f"<code>{text}</code>  deleted.",
            quote=True
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)
@Client.on_message(filters.command('filters'))
async def get_all(client: Client, message):
    status= await db.is_admin_exist(message.from_user.id)
    if not status:
        return
    text = ''
    texts = await get_filter_results(text,message.from_user.id)
    count = await Media.count_documents({'group_id':message.from_user.id})
    if count:
        filterlist = f"<b>Bot have total {count} filters</b>\n\n"

        for text in texts:
            keywords = f" ○  <code>{text.text}</code>\n"
            filterlist += keywords

        if len(filterlist) > 4096:
            with io.BytesIO(str.encode(filterlist.replace("<code>", "").replace("</code>","").replace('<b>', '').replace('</b>', ''))) as keyword_file:
                sts = await message.reply('<i>Please wait..</i>')
                keyword_file.name = "filters.txt"
                await message.reply_document(
                    document=keyword_file
                )
                await sts.delete()
            return
    else:
        filterlist = f"<b>Bot have no filters.!</b>"

    await message.reply_text(
        text=filterlist,
        quote=True
    )
    
@Client.on_message(filters.command('delall') & filters.owner)
async def delallconfirm(Client, message):
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Yes', callback_data = 'delall'),
                InlineKeyboardButton('No', callback_data = 'delallclose')
            ]
        ]
    )
    await message.reply_text(
        f"This will delete all of your filters.\nAre you sure you want do this.?",
        reply_markup = reply_markup,
        quote=True
    )
@Client.on_message((filters.private | filters.group) & filters.command('niunge'))
async def addconnection(client,message):
    status= await db.is_admin_exist(message.from_user.id)
    if not status:
        return
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"Samahan wewe ni anonymous(bila kujulikana) admin tafadhali nenda kweny group lako edit **admin permission** remain anonymouse kisha disable jaribu tena kutuma /niunge.Kisha ka enable tena")
    chat_type = message.chat.type
    if chat_type == "private":
        await message.reply_text(
                "Samahan add hii bot kama admin kwenye group lako kisha tuma command hii <b>/niunge </b>kwenye group lako",
                quote=True
            )
        return

    elif chat_type in ["group", "supergroup"]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
            st.status != "administrator"
            and st.status != "creator"
            and str(userid) not in ADMINS
        ):
            await message.reply_text("lazima uwe  admin kwenye group hili!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!",
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == "administrator":
            group_details= await is_user_exist(group_id)
            for file in group_details:
                user_id2=file.group_id
            if not group_details :
                await add_user(group_id,userid,'group',message.chat.title)
                aski = await client.get_chat(group_id)
                photo = await upload_group(client,aski.photo,message)
                photo_id =aski.photo.big_file_id if photo else None
                await User.collection.update_one({'_id':group_id},{'$set':{'title':aski.title,'link': photo ,'inv_link':aski.invite_link,'total_m':aski.members_count,'photo_id':photo_id}})
                await message.reply_text(
                    f"Tumeliunganisha kikamilifu Sasa unaweza kuendelea kuongezea muv/series posters audio video n.k ukiwa private kwa kureply ujumbe wako kisha /add kisha jina LA text,movie,series n.k !",
                    quote=True,
                    parse_mode="md"
                )
                if chat_type in ["group", "supergroup","private"]:
                    await client.send_message(
                        userid,
                        f"Asante kwa kutuamini umefanikiwa kuunganisha group lako tuma /help kupata muongozo!",
                        parse_mode="md"
                    )
                    return
           
            else:
                ttli = await client.get_users(user_id2)
                await message.reply_text(
                    f"Samahan hili group tayar limeshaunganishwa na admin **{ttli.first_name}** Msimaiz wangu kanikataza ku add wasimaz wawili kwenye group moja kama mnahitaj mabadiliko mcheki @hrm45!",
                    quote=True
                )
        else:
            await message.reply_text("Ni add admin kwenye group lako kisha jaribu tena", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Kuna tatizo tafadhali jaribu badae!!!.', quote=True)
        return
@Client.on_message(filters.private & filters.command("add_admin") & filters.owner)
async def ban(c,m):
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to add access to any user from the bot.\n\n"
            f"Usage:\n\n"
            f"`/add_admin admin_id duration_in days ofa_given`\n\n"
            f"Eg: `/add_admin 1234567 28 Umepata ofa ya Siku 3 zaidi.`\n"
            f"This will add user with id `1234567` for `28` days for the reason `ofa siku 3 zaidi`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Adding user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"Asante kwa uaminifu wako kwetu \n\n **🧰🧰 KIFURUSHI CHAKO 🧰🧰** \n\n🗓🗓**siku___siku{ban_duration}(+ofa)**\n\n🎁🎁ofa ___ ** __{ban_reason}__**\n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nNmeshindwa kumtaarifu tafadhali jaribu tena! \n\n`{traceback.format_exc()}`"
        adminexist=await db.is_admin_exist(user_id)
        if not adminexist :
            await db.add_admin(user_id)
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )
@Client.on_message(filters.private & filters.command("admin"))
async def get_status(bot,message):
    status= await db.is_admin_exist(message.from_user.id)
    if not status:
        return
    filters = await get_filter_results('',message.from_user.id)
    filters_no = 0
    text = 0
    photo = 0
    video = 0
    audio = 0
    document = 0
    animation = 0
    sticker = 0
    voice = 0 
    videonote = 0 
    
    for filter in filters:
        type = filter['type']
        if type == 'Text':
            text += 1 
        elif type == 'Photo':
            photo += 1 
        elif type == 'Video':
            video += 1 
        elif type == 'Audio':
            audio += 1 
        elif type == 'Document':
            document += 1
        elif type == 'Animation':
            animation += 1
        elif type == 'Sticker':
            sticker += 1 
        elif type == 'Voice':
            voice += 1
        elif type == 'Video Note':
            videonote += 1 

        filters_no += 1
    
    user_collection = await User.count_documents({'group_id': message.from_user.id})
    
    stats_text = f"""<b>Statistics</b>
    
Total groups: {user_collection}
Total filters: {filters_no}
Text filters: {text}
Photo filters: {photo}
Video filters: {video}
Audio filters: {audio}
Document filters: {document}
Animation filters: {animation}
Sticker filters: {sticker}
Voice filters: {voice}
Video Note filters: {videonote}"""
    await message.reply_text(stats_text)
    
@Client.on_callback_query(filters.regex("^delall$") & filters.owner)
async def delall(client: Client, query):
    await del_all(query.message)

@Client.on_callback_query(filters.regex("^delallclose$") & filters.owner)
async def delcancel(client: Client, query):
    await query.edit_message_text(
        text = 'Process Cancelled',
        reply_markup = None
    )
    return
