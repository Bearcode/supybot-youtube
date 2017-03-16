# ##
# Copyright (c) 2009, James Scott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import apiclient
from urllib.parse import *


class Youtube(callbacks.Plugin):
    """Add the help for "@plugin help Youtube" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        super(Youtube, self).__init__(irc)
        self.__parent = super(Youtube, self)
        self.__parent.__init__(irc)
        self.developer_key = self.registryValue('developer_key')
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"

    def _video_id(self, value):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        #print value
        query = urlparse(value)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None

    def _lookup_youtube(self, irc, msg):
        (recipients, text) = msg.args
        yt_service = apiclient.discovery.build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                                               developerKey=self.developer_key)
        try:
            if "https" in text:
                url = text.split("https://")[1]
            else:
                url = text.split("http://")[1]
            url = url.split(" ")[0]
        except:
            url = text
        vid_id = self._video_id("http://" + url)
        entry = yt_service.videos().list(
            part="snippet, statistics",
            id=vid_id
        ).execute()
        title = ""
        try:
            title = ircutils.bold(entry['items'][0]['snippet']['title'])
        except:
            pass
        try:
            views = ircutils.bold(entry['items'][0]['statistics']['viewCount'])
        except:
            views = ircutils.bold('0')
        try:
            like_dislike_ratio = float(entry['items'][0]['statistics']['likeCount']) / (
                float(entry['items'][0]['statistics']['likeCount']) + float(
                    entry['items'][0]['statistics']['dislikeCount']))
            rating = ircutils.bold('{:.2%}'.format(like_dislike_ratio))
        except:
            rating = ircutils.bold("n/a")

        irc.reply('Title: %s  Views: %s  Rating: %s  ' % (title, views, rating), prefixNick=False)

    def doPrivmsg(self, irc, msg):
        (recipients, text) = msg.args
        #print text.find("youtube.com/watch?v=")
        if "youtube.com" in text:
            self._lookup_youtube(irc, msg)
        elif "youtu.be" in text:
            self._lookup_youtube(irc, msg)
        else:
            pass

    def search(self, irc, msg, args):
        yt_service = apiclient.discovery.build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION,
                                               developerKey=self.developer_key)
        search_response = yt_service.search().list(
            q=args,
            part="id,snippet",
            maxResults=3
        ).execute()
        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append("Title: %s  Url: https://www.youtube.com/watch?v=%s" %
                              (ircutils.bold(search_result["snippet"]["title"]),
                               search_result["id"]["videoId"]))
        for item in videos:
            irc.reply(format('%s' % item), notice='true', prefixNick='false', private='true')

Class = Youtube

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
