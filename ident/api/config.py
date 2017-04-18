import os

class config:
    fun_facts = {
        'fav_text_editor': os.environ['FAV_TEXT_EDITOR'] if 'FAV_TEXT_EDITOR' in os.environ else 'Emacs with evil (Vim) mode (aka Spacemacs)',
        'fav_os': os.environ['FAV_OS'] if 'FAV_OS' in os.environ else 'Ubuntu with the Gnome 3 shell'
    }
