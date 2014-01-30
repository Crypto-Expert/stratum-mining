import hashlib
import struct
import skein

def skeinhash(msg):
    return hashlib.sha256(skein.Skein512(msg[:80]).digest()).digest()

def skeinhashmid(msg):
    s = skein.Skein512(msg[:64] + '\x00') # hack to force Skein512.update()
    return struct.pack('<8Q', *s.tf.key.tolist())

if __name__ == '__main__':
    mesg = "dissociative1234dissociative4567dissociative1234dissociative4567dissociative1234"
    h = skeinhashmid(mesg)
    print h.encode('hex')
    print 'ad0d423b18b47f57724e519c42c9d5623308feac3df37aca964f2aa869f170bdf23e97f644e81511df49c59c5962887d17e277e7e8513345137638334c8e59a4' == h.encode('hex')

    h = skeinhash(mesg)
    print h.encode('hex')
    print '764da2e768811e91c6c0c649b052b7109a9bc786bce136a59c8d5a0547cddc54' == h.encode('hex')
