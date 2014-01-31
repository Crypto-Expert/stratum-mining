[ ![Codeship Status for ahmedbodi/php-mpos](https://www.codeship.io/projects/b3003a70-61a3-0131-231e-26f75a0c690d/status?branch=master)](https://www.codeship.io/projects/12274)
#Description
Stratum-mining is a pooled mining protocol. It is a replacement for *getwork* based pooling servers by allowing clients to generate work. The stratum protocol is described [here](http://mining.bitcoin.cz/stratum-mining) in full detail.

This is a implementation of stratum-mining for scrypt based coins. It is compatible with *MPOS* as it complies with the standards of *pushpool*. The end goal is to build on these standards to come up with a more stable solution.

The goal is to make a reliable stratum mining server for a wide range of coins unlike other forks where the code is limited to specific algorithm's. Over time I will develop this to be more feature rich and very stable. If you would like to see a feature please file a feature request. 

**NOTE:** This fork is still in development. Many features may be broken. Please report any broken features or issues.

#Features

* Stratum Mining Pool 
* Solved Block Confirmation
* Job Based Vardiff support
* Solution Block Hash Support
* Log Rotation
* Initial low difficulty share confirmation
* Multiple *coind* wallets
* On the fly addition of new *coind* wallets
* MySQL/PostGres/SQLite database support
* Adjustable database commit parameters
* Bypass password check for workers
* Proof Of Work and Proof of Stake Coin Support
* Transaction Messaging Support

#Donations 
* BTC:  18Xg4qP6RUvpeajanKPt5PDvvcqvU2pP6d
* BTE:  8UJLskr8eDYATvYzmaCBw3vbRmeNweT3rW
* DGC:  DSBb5KmGWYKMJjxk3rETtvpk9sPqgCCYAw
* LTC:  Lg4kXMqPsmMHrGr81LLe8oHpbsMiWiuMSB
* WDC:  WeVFgZQsKSKXGak7NJPp9SrcUexghzTPGJ
* Doge: DLtBRYtNCzfiZfcpUeEr8KPvy5k1aR7jca
* SRC:  sMP2wHN5H2ik7FQDPjhSzFZUWux75BYZGe
* ARG:  AQvXPWVqGzcpH2j2XSRG7X5R9nA3y9D9aQ
* Cryptsy Trade Key: ec13d183e304326ebd41258d6ae7188e303866fe


#Requirements
*stratum-mining* is built in python. I have been testing it with 2.7.3, but it should work with other versions. The requirements for running the software are below.
* Python 2.7+
* python-twisted
* stratum
* MySQL Server 
* SHA256 or Scrypt CoinDaemon

Other coins have been known to work with this implementation. I have tested with the following coins, but there may be many others that work. 

* Orbitcoin.
* FireFlyCoin.
* ByteCoin
* DigitalCoin
* Worldcoin
* Argentum
* Netcoin
* FlorinCoin
* CHNCoin
* Cubits v3
* OpenSourceCoin
* TekCoin
* Franko
* Quark
* Securecoin

#Installation

The installation of this *stratum-mining* can be found in the Repo Wiki. 

#Contact
I am available in the #MPOS, #crypto-expert, #digitalcoin, and #worldcoin channels on freenode. 
Although i am willing to provide support through IRC please file issues on the repo.
Issues as a direct result of stratum will be helped with as much as possible
However issues related to a coin daemon's setup and other non stratum issues, 
Please research and attempt to debug first.

#Credits

* Original version by Slush0 and ArtForz (original stratum code)
* More Features added by GeneralFault, Wadee Womersley, Viperaus, TheSeven and Moopless
* Multi Algo, Vardiff, DB and MPOS support done by Ahmed_Bodi, penner42 and Obigal

#License
This software is provides AS-IS without any warranties of any kind. Please use at your own risk. 

