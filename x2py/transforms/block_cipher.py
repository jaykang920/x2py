# Copyright (c) 2017, 2018 Jae-jun Kang
# See the file LICENSE for details.

import codecs

from x2py.buffer_transform import BufferTransform
from x2py.util.trace import Trace

# pycrypto
from Crypto import Random
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA

class BlockCipher(BufferTransform):
    """A simple example of BufferTransform that performs block encryption and
        decryption based on the keys exchanged by an asymmetric algorithm."""

    class SettingsBuilder(object):
        def __init__(self, block_size, key_size, rsa_key_size, \
                my_private_key, peer_public_key):
            self.block_size = block_size
            self.key_size = key_size
            self.rsa_key_size = rsa_key_size
            self.my_private_key = my_private_key
            self.peer_public_key = peer_public_key

        def build(self):
            settings = BlockCipher.Settings(self)
            settings.my_rsa = BlockCipher.SettingsBuilder._xml2rsa(self.my_private_key)
            settings.peer_rsa = BlockCipher.SettingsBuilder._xml2rsa(self.peer_public_key)
            return settings

        @staticmethod
        def _xml2rsa(xml):
            import base64
            import xml.etree.ElementTree as etree
            has_private = False
            root = etree.fromstring(xml.replace('\n', ''))
            if root.tag == 'RSAKeyValue':
                for node in root:
                    if node.tag == 'Modulus':
                        n = int(codecs.encode(base64.b64decode(node.text), 'hex'), 16)
                    elif node.tag == 'Exponent':
                        e = int(codecs.encode(base64.b64decode(node.text), 'hex'), 16)
                    elif node.tag == 'P':
                        p = int(codecs.encode(base64.b64decode(node.text), 'hex'), 16)
                    elif node.tag == 'Q':
                        q = int(codecs.encode(base64.b64decode(node.text), 'hex'), 16)
                    elif node.tag == 'DP':
                        pass
                    elif node.tag == 'DQ':
                        pass
                    elif node.tag == 'InverseQ':
                        pass
                    elif node.tag == 'D':
                        d = int(codecs.encode(base64.b64decode(node.text), 'hex'), 16)
                        has_private = True
                if has_private:
                    return RSA.construct((n, e, d, p, q))
                else:
                    return RSA.construct((n, e))
            else:
                raise ValueError()

    class Settings(SettingsBuilder):
        def __init__(self):
            raise AssertionError()

        def __init__(self, builder):
            super(BlockCipher.Settings, self).__init__(
                builder.block_size,
                builder.key_size,
                builder.rsa_key_size,
                builder.my_private_key,
                builder.peer_public_key
            )
            self.my_rsa = None
            self.peer_rsa = None

    def __init__(self, settings=None):
        if settings is not None:
            self.settings = settings
        else:
            # Default settings
            self.settings = BlockCipher.SettingsBuilder(
                block_size = 128,
                key_size = 256,
                rsa_key_size = 1024,
                # In a real-world client/server production, each peer should use
                # a different RSA key pair.
                my_private_key = '''
<RSAKeyValue><Modulus>xtU+mTT9tOES5vLZeSAEvuWaa+FX4jUtH5iVFGSULCaBR6TtQ2TYUz1Jnt
rUhA26OQBIcVzlMyarM8XVhZqk5RJDP64VFz3m+VMmghAgJLUPKDORmIPlc18FuaTsZjxoIwfuVojrDH
/12BoEHHmwb3CVq6dHGsxRLUKG0DYBWQk=</Modulus><Exponent>AQAB</Exponent><P>+3iHfNfD
ARBhnHQ33OyJudsOWkFPwqOG575nkCntjW8RhepXaKPNRqmEu/cYN/Fr/nCmxxgW8Fp5HEI+gI7xZw==
</P><Q>ymoD2gsEj0ksiph+UbkT3Amwx/SHOaRWTwWysL8xKicD0afqnGpHkUnoAUnEQFAnuDIB5D+rb
+6ulwsS6xCsDw==</Q><DP>2d2brJqV1PcnSlAaEepQjFfvwFwzSRM6Ds8UlH7u04k1qkrT/dFkSGMXn
229asJb6O4aYAVL4mLP6J6v3dt54w==</DP><DQ>kLRhtIuT4uupEBwckkgBzpiO7SP/WFIH8c5dBMZq
W3ww2r10mAXSzCdN2T3nMyMagjAd8hMieI7l+c1M5QeyOQ==</DQ><InverseQ>M+sgtHA0blhMUBdGG
IYboxSEvPwPxoX5ORwgL/Zl3TOgxN1oM9i5EkmwKFcazAHKfL5eArtlmfELOcqPMFiyzQ==</Inverse
Q><D>CBEw2AB5ZrRXEv25axusdZ5VNJlQ+oGT0htbuRcXl+78Ac8kPT7DNCVhbkuMocr4ykVDqy3MstW
XzqLxNdl/ZSV9KvP6u5bcDQQeC9KbKQ5PpzGoGmMJNsVtXC0voOA3sYx9P+vVtEqhxn9eAKPOPqX9wRo
9rMW9UZRtDcLiUj0=</D></RSAKeyValue>
''',
                peer_public_key = '''
<RSAKeyValue><Modulus>xtU+mTT9tOES5vLZeSAEvuWaa+FX4jUtH5iVFGSULCaBR6TtQ2TYUz1Jnt
rUhA26OQBIcVzlMyarM8XVhZqk5RJDP64VFz3m+VMmghAgJLUPKDORmIPlc18FuaTsZjxoIwfuVojrDH
/12BoEHHmwb3CVq6dHGsxRLUKG0DYBWQk=</Modulus><Exponent>AQAB</Exponent></RSAKeyVal
ue>
'''
            ).build()

        self.encryptor = None
        self.decryptor = None
        self.encryption_key = None
        self.encryption_iv = None
        self.decryption_key = None
        self.decryption_iv = None

    def cleanup(self):
        pass

    def clone(self):
        return BlockCipher(self.settings)

    @property
    def block_size_in_bytes(self):
        return (self.settings.block_size >> 3)

    @property
    def key_size_in_bytes(self):
        return (self.settings.key_size >> 3)

    def handshake_block_length(self):
        return (self.settings.rsa_key_size >> 3)

    def init_handshake(self):
        challenge_length = self.key_size_in_bytes + self.block_size_in_bytes
        challenge = Random.new().read(challenge_length)
        Trace.trace("challenge: {}", repr(challenge))

        n = self.key_size_in_bytes
        key = challenge[:n]
        iv = challenge[n:n + self.block_size_in_bytes]
        self.encryptor = AES.new(key, AES.MODE_CBC, iv)
        self.encryption_key = key
        self.encryption_iv = iv

        encrypted = self._rsa_encrypt(challenge)
        Trace.trace("encrypted challenge: {}", repr(encrypted))
        return encrypted

    def handshake(self, challenge):
        decrypted = self._rsa_decrypt(challenge)

        n = self.key_size_in_bytes
        key = decrypted[:n]
        iv = decrypted[n:n + self.block_size_in_bytes]
        self.decryptor = AES.new(key, AES.MODE_CBC, iv)
        self.decryption_key = key
        self.decryption_iv = iv

        encrypted = self._rsa_encrypt(decrypted)
        return encrypted

    def fini_handshake(self, response):
        expected = self.encryption_key + self.encryption_iv

        decrypted = self._rsa_decrypt(response)

        return (decrypted == expected)

    def transform(self, buffer):
        buffer = self._pad_pkcs7(buffer)
        return self.encryptor.encrypt(buffer)

    def inverse_transform(self, buffer):
        buffer = self.decryptor.decrypt(bytes(buffer))
        buffer = self._unpad_pkcs7(buffer)
        return buffer

    def _pad_pkcs7(self, buffer):
        length = len(buffer)
        val = self.block_size_in_bytes - (length % self.block_size_in_bytes)
        return bytes(buffer + bytearray([val] * val))

    def _unpad_pkcs7(self, buffer):
        val = buffer[-1]
        if (isinstance(val, str)):
            val = ord(val)
        if val > self.block_size_in_bytes:
            raise ValueError("Invalid PKCS#7 padding")
        length = len(buffer) - val
        return bytes(buffer[:length])

    def _rsa_decrypt(self, ciphertext):
        cipher = PKCS1_v1_5.new(self.settings.my_rsa)
        return cipher.decrypt(ciphertext, None)

    def _rsa_encrypt(self, plaintext):
        cipher = PKCS1_v1_5.new(self.settings.peer_rsa)
        return cipher.encrypt(plaintext)
