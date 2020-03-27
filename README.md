# Forked from here:
https://github.com/mrwnwttk/scdl
Added wrapper to download and specifify title

## Usage
```
(base) fourbolt@veldin:~/Desktop/scdl$ python dl.py 
Search terms: for you simon ray
*** Querying SoundCloud...
*** Getting HTML: https://soundcloud.com/search?q=for%20you%20simon%20ray
*** Querying sub-results: https://www.soundcloud.com/manyfewofficial/for-you-simon-ray-extended
*** Got HTML
*** Decoding HTML
*** Querying sub-results: https://www.soundcloud.com/manyfewofficial/for-you-simon-ray-remix-feat
*** Got HTML
*** Decoding HTML
*** Querying sub-results: https://www.soundcloud.com/matthew_marquez/all-for-you-video-games-remix
*** Got HTML
*** Decoding HTML
*** Querying sub-results: https://www.soundcloud.com/cida-fernandes/01-ray-charles-song-for-you-1994
*** Got HTML
*** Decoding HTML
*** Querying sub-results: https://www.soundcloud.com/arda-demir-469553643/these-for-you
*** Got HTML
*** Decoding HTML
*** Querying YouTube...
+-----+-----------------+----------------+----------+-------------+------------+
| Idx | Name            | Artist         | Duration | Plays/Views | DL         |
+-----+-----------------+----------------+----------+-------------+------------+
| 1   | For You (Simon  | ManyFew        |  5:25    | 382         | SoundCloud |
|     | Ray Extended    |                |          |             |            |
|     | Remix) [feat.   |                |          |             |            |
|     | Hayley May]     |                |          |             |            |
+-----+-----------------+----------------+----------+-------------+------------+
| 2   | For You (Simon  | ManyFew        |  4:01    | 884         | SoundCloud |
|     | Ray Remix)      |                |          |             |            |
|     | [feat. Hayley   |                |          |             |            |
|     | May]            |                |          |             |            |
+-----+-----------------+----------------+----------+-------------+------------+
| 3   | French Montana  | matthewmarquez |  4:38    | 182,191     | SoundCloud |
|     | - All For You   |                |          |             |            |
|     | (feat. Lana Del |                |          |             |            |
|     | Ray, Wiz        |                |          |             |            |
|     | Khalifa, and    |                |          |             |            |
|     | Snoop Dogg)     |                |          |             |            |
+-----+-----------------+----------------+----------+-------------+------------+
| 4   | 01 Ray Charles  | &quot;Cida Fer |  5:24    | 159,888     | SoundCloud |
|     | - Song For You  | nandes&quot;   |          |             |            |
|     | (1994)          |                |          |             |            |
+-----+-----------------+----------------+----------+-------------+------------+
| 5   | These For You   | RAY-D          |  4:00    | 198         | SoundCloud |
+-----+-----------------+----------------+----------+-------------+------------+
Song pick: 
```

## Requirements

pip install texttable
pip install beautifulsoup4

# Install ffmpeg
mac: brew install ffmpeg
ubuntu: apt-get install ffmpeg

