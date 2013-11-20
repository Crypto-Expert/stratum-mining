#Description
Stratum-mining is a pooled mining protocol. It is a replacement for *getwork* based pooling servers by allowing clients to generate work. The stratum protocol is described [here](http://mining.bitcoin.cz/stratum-mining) in full detail.

This is a implementation of stratum-mining for scrypt based coins. It is compatible with *MPOS* as well as *mmcfe*, as it complies with the standards of *pushpool*. The end goal is to build on these standards to come up with a more stable solution.

The goal is to make a reliable stratum mining server for scrypt based coins. Over time I will develop this to be more feature rich and very stable. If you would like to see a feature please file a feature request. 

**NOTE:** This fork is still in development. Many features may be broken. Please report any broken features or issues.

#Features

* Stratum Mining Pool 
* Solved Block Confirmation
* Vardiff support
* Solution Block Hash Support
* *NEW* SHA256 and Scrypt Algo Support 
* Log Rotation
* Initial low difficulty share confirmation
* Multiple *coind* wallets
* On the fly addition of new *coind* wallets
* MySQL database support
* Adjustable database commit parameters
* Bypass password check for workers


#Requirements
*stratum-mining* is built in python. I have been testing it with 2.7.3, but it should work with other versions. The requirements for running the software are below.

* Python 2.7+
* python-twisted
* stratum
* MySQL Server 
* SHA256 or Scrypt CoinDaemon

Other coins have been known to work with this implementation. I have tested with the following coins, but there may be many others that work. 

*Orbitcoin
*FireFlyCoin

#Installation

The installation of this *stratum-mining* can be found in the INSTALL.md file. 

#Contact
I am available in the #MPOS, #crypto-expert, #digitalcoin, #bytecoin and #worldcoin channels on freenode. Although i am willing to provide support through IRC please file issues on the repo 

#Credits

* Original version by Slush0 (original stratum code)
* More Features added by GeneralFault, Wadee Womersley and Moopless
* Scrypt conversion from work done by viperaus 
* PoS conversion done by TheSeven
* Modifications to make it more user friendly and easier to setup for multiple coins  done by Ahmed_Bodi


#License
This software is provides AS-IS without any warranties of any kind. Please use at your own risk. 

