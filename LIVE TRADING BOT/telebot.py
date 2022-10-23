import requests
from datetime import datetime, timedelta
# import plotly.graph_objs as go

class telegramBot:
    def __init__(self, botToken : str, chatID : str, graphDirectory : str = ""):
        """
        botToken : api bot token given by bot father @BotFather on telegram,
        chatTd : chat id as assigned by user, you can find your unique chatid at api.telegram.org/bot{bottoken}/getUpdates, send a message and refresh,
        graphDirectory : default value is an empty string, use if you intend to send plotly.graph_objs.Figure graphs
        """
        self.botToken = botToken
        self.chatID = chatID
        self.graphDirectory = graphDirectory

    def sendText(self, msg : str) -> bool : 
        """
        msg : message in string format
        """
        base_url = f'https://api.telegram.org/bot{self.botToken}/sendMessage?chat_id={self.chatID}&text={msg}'
        requests.post(base_url)  # Sending automated message
        return True

    def sendTextToChatID(self, msg : str, chatid : str) -> bool : 
        """
        msg : message in string format
        """
        base_url = f'https://api.telegram.org/bot{self.botToken}/sendMessage?chat_id={chatid}&text={msg}'
        requests.post(base_url)  # Sending automated message
        return True

    # def sendGraph(self, graph : go.Figure) -> bool :
    #     """
    #     graph : a graph of type plotly.graph_objs.Figure
    #     """
    #     graph.write_image(self.graphDirectory)
    #     return self.sendImage(self.graphDirectory)

    def sendImage(self, directory : str) -> bool :
        """
        directory : directory of image in png or jpeg
        """
        imgpath = {'photo': open(directory, 'rb')}
        requests.post(
            f'https://api.telegram.org/bot{self.botToken}/sendPhoto?chat_id={self.chatID}',
            files=imgpath)  # Sending Automated Image
        return True

    def pollResponse(self, specifity : bool, waittime : int) :
        """
        specifity : set to true if you want to listen ONLY to the chatid user, false if you want to listen to all users
        waittime : wait time in seconds
        """
        # assert '-' not in self.chatID, 'ChatID is that of a Channel, unable to poll for responses'
        site = f'https://api.telegram.org/bot{self.botToken}/getUpdates'
        data = requests.get(site).json()  # reads data from the url getUpdates
        chatid = ''
        try:
            lastMsg = len(data['result']) - 1
            updateIdSave = data['result'][lastMsg]['update_id']
        except:
            updateIdSave = ''
        time = datetime.now()
        waitTime = time + timedelta(seconds=waittime)

        while True:
            try:
                time = datetime.now()
                data = requests.get(site).json()  # reads data from the url getUpdates
                lastMsg = len(data['result']) - 1
                updateId = data['result'][lastMsg]['update_id']
                chatid = str(data['result'][lastMsg]['message']['chat']['id'])  # reads chat ID
                if specifity == True:
                    condition = self.chatID == chatid
                else:
                    condition = True
                if updateId != updateIdSave and condition:  # compares update ID
                    text = data['result'][lastMsg]['message']['text']  # reads what they have sent
                    requests.get(f'https://api.telegram.org/bot{self.botToken}/getUpdates?offset=' + str(updateId))
                    break
                    
                elif waitTime < time:
                    text = ''
                    chatid = ''
                    break
            except:
                text = ''
                break
        return text,chatid