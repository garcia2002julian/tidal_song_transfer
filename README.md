# tidal_song_transfer
transfer playlists from spotify to tidal

Fellas, I just wanted to come in here and say that it's bullshit that there's no free option to transfer playlists considering that the tidal api is open source and I believe spotify's is as well. Therefore I did research and found this github that someoene created https://github.com/Maverick565/Tidal-library-data-transfer for tidal transfer within itself and just piggybacked on it and changed the code to fit my needs. (note you do not have to change the limit like the read me says unless you have playlists over 1000 songs long, if you dont need to, just install the tidalapi regularly through pip: pip install tidalapi in python). 
Next you have to get your spotify csv backup to use with my code using this link https://www.tunemymusic.com/transfer/spotify-to-file
this is the following code that worked great enough for me

Make sure to read the comments to understand what is going on or if you want to change something yourself. The application is simple enough.
The only 2 things you will have to change is the 'YOUR PATH' with your path you want to read the csv file from and store the log files and the name of the playlist you want to add to in tidal:
![image](https://github.com/user-attachments/assets/69a1a635-86a0-449c-a222-8a7cf9cf82c9)

![image](https://github.com/user-attachments/assets/2408cb97-5091-4444-99b3-21bed62e401b)


This is the image of the github link I posted in case it ever goes away:

![image](https://github.com/user-attachments/assets/6f9c28e0-fa8d-4883-b74f-f02492d2bae4)
