


class YouTubeAPI():
        def __init__(self):
                pass

        def query(self, search_query: str):
                '''
                Return a list of 10 of the following:
                [song name, artist name, views(?), total length]
                '''
                
                results = [
                        {'Name':'ZHU - Faded (Youtube Remix)', 'Views':300, 'Runtime':'0:30'},
                        {'Name':'ZHU - In The Morning (Seven Lions Remix)', 'Views':200, 'Runtime':'1:35'},
                        ]
                for result in results:
                        result['Downloader'] = self

                return results

        def toString(self):
                return "YouTube"
