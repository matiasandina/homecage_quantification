# This script will automate key generation
# -------------------------------------------------

# Example below:
# yes "y" | ssh-keygen -o -a 100 -t ed25519 -C "Bla Bla" -f /mypath/bla -N ""

# here

# -o OpenSSH key format instead of older PEM (needs OpenSSH 6.5+)

# -a Number of primality test while screening DH-GEX candidates

# -t Type of key (ed25519, RSA, DSA etc.)

# -f /mypath/bla The output file path and name

# -N "" Use empty passphase

# -C comment

# and yes "y" for no interaction.

# It will generate two files

# /mypath/bla
# /mypath/bla.pub
# where the bla file is private and bla.pub is public.

# See more info here  https://stackoverflow.com/questions/3659602/automating-enter-keypresses-for-bash-script-generating-ssh-keys

# -------------------------------------------------
#              GENERATE KEYS
# -------------------------------------------------

# navigate home
cd
# example was not working as expected but figured it out
mkdir .ssh
yes ".ssh/id_rsa" | ssh-keygen -o -a 100 -t RSA -N ""

# -------------------------------------------------
#              COPY KEYS
# -------------------------------------------------

ssh-copy-id choilab@10.93.6.88


