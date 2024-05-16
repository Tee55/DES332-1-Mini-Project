import os
import rsa

publickey, privatekey = rsa.newkeys(1024)
def main():
    # Tee's Public Key, Tee's Private Key
    if not os.path.exists('tee_publickey.pem') or os.path.exists('tee_privatekey.pem'):
        with open('tee_publickey.pem', 'w') as f:
            f.write(publickey._save_pkcs1_pem().decode())
            f.close()
        with open('tee_privatekey.pem', 'w') as f:
            f.write(privatekey._save_pkcs1_pem().decode())
            f.close()

    # John's Public Key, John's Private Key
    if not os.path.exists('john_publickey.pem') or os.path.exists('john_privatekey.pem'):
        with open('john_publickey.pem', 'w') as f:
            f.write(publickey._save_pkcs1_pem().decode())
            f.close()
        with open('john_privatekey.pem', 'w') as f:
            f.write(privatekey._save_pkcs1_pem().decode())
            f.close() 

if __name__ == "__main__":
    main()