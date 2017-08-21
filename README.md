#### Requirements:
- [Python 3.4.x](https://www.python.org/download/releases/3.4.1/) or later
- [EncFS](https://vgough.github.io/encfs/) installed and available on the command line
    * [EncFS v1.8.1](https://github.com/vgough/encfs/releases/tag/v1.8.1) or later is recommended
- OSs:
    * Mac OSX
    * Linux
    * Windows: TBD / maybe


#### Install:
- from [PyPI](https://pypi.python.org/pypi/efst): `$ pip install efst`
- latest from source repository: `$ pip install git+https://github.com/akpw/efst.git`

#### Blog:
   * [EFST tips & tricks](http://www.akpdev.com/tags.html#EFST)

## Description

[EncFS](https://vgough.github.io/encfs/) is a free [FUSE-based](https://en.wikipedia.org/wiki/Filesystem_in_Userspace) cryptographic file system. It transparently encrypts files, using an arbitrary directory as backend storage for the encrypted files. EncFS works on per-file basis, which makes it suitable for syncing files and protecting cloud data.

The EFST project help manage EncFS-encrypted data, making it easy to organize various EncFS assets and then effectively operate it via a few simple commands. In addition to common operations such as mounting / un-mounting registered EncFS volume entries, EFST simplifies and automates advanced EncFS features such as e.g. reverse encryption for encrypted backups or multiple interleaved EncFS file systems for plausible deniability.

The EFST project is written in [Python 3.4](https://www.python.org/download/releases/3.4.1/) and currently consists of three main command-line utilities.

[**EFSM**](https://github.com/akpw/efst#efsm) enables creating / registering / operating EncFS backend store directories and related assets such as target mountpoint folder, mount volume name, path to EncFS config/key file, etc.
One way to learn about available EFSM options would be via running:
```
    $ efsm -h

```

As a more hands on approach, lets just quickly create and handle a basic encrypted Dropbox folder (examples below are from Mac OS terminal, for Linux some details such as mountpoint folders, etc. might be a bit different):
```
    $ efsm create -en MySecrets -bp ~/Dropbox/.my_secret_folder
    $ Enter password:
    $ Confirm password:
    Creating EncFS backend store...
    $ Do you want to securely store the password for further use? [y/n]: y
    CipherText Entry registered: MySecrets
```

A single ```efsm create``` command there did quite a few things. A backend directory for storing the encrypted files was created, an EncFS config/key file was generated, default values were figured out and finally the password was collected, set, and safely stored in OS-specific system keyring service. To review all of these in details, let's take a look at the relevant EFST config entry:
```
    $ efsm show -en MyS
    Entry name: MySecrets
      Entry type: CipherText
      Password store entry: efst-entry-MySecrets
      Conf/Key file: /Users/AKPW/Dropbox/.my_secret_folder/.encfs6.xml
      Back-end store folder (CipherText): /Users/AKPW/Dropbox/.my_secret_folder
      Mount folder (Plaintext): /Volumes/MySecrets
      Un-mount on idle: Disabled
      Volume name: MySecrets
```

The ```-en, --entry-name``` parameter takes the name of a registered entry. Both full registered name and its unique shortcut would do, e.g. in the above example it was sufficient to shortcut 'MySecrets' to 'MyS'.

The "Password store entry" is the default name of automatically created OS-specific keychain entry. For Mac OS, this can be reviewed via the Keychain app:

![efst-keychain](https://lh3.googleusercontent.com/BMmxK-sWF-vJY6vrfBl5SqecbtQTbqWsBmnbxKXmZeA=w533-h348-no)


From now on, working with the protected data is straightforward:
```
    $ efsm mount -en MyS
    Mounted: /Volumes/MySecrets
```

The mounted folder is where you put your plaintext data, with the encrypted version automatically stored in the backend ```Dropbox/.my_secret_folder```.

Un-mounting the plaintext folder is just as easy:
```
    $ efsm umount -en MyS
    Unmounted: /Volumes/MySecrets
```

Now the data are securely stored on the disk (and Dropbox) in encrypted form, readily accessible whenever needed via the 'efsm mount' command.

Similar to creating a new EncFS ciphertext backend store, it is as easy to register an existing one.

```
    $ efsm register -en OtherSecrets -bp ~/path-to-existing-ciphertext_backend
    CipherText Entry registered: OtherSecrets

    $ efsm mount -en Other
    OtherSecrets
    $ Enter password:
    Mounted: /Volumes/OtherSecrets
    $ Do you want to securely store the password for later use? [y/n]: y

    $ efsm umount -en Other
    Unmounted: /Volumes/OtherSecrets
```

Creating or registering a reversed EFST entry can be done with the ``` -r, --reverse``` switch:
```
    $ efsm create -r -en BackupDocuments -bp ~/Documents/
    $ Enter password:
    $ Confirm password:
    Creating EncFS backend store...
    $ Do you want to securely store the password for later use? [y/n]: y
    Reversed CipherText Entry registered: BackupDocuments

    $ efsm show -en Bac
    Entry name: BackupDocuments
      Entry type: Reversed CipherText
      Password store entry: efst-entry-BackupDocuments
      Conf/Key file: /Users/AKPW/Documents/.encfs6.xml
      Back-end store folder (Plaintext): /Users/AKPW/Documents
      Mount folder (CipherText): /Volumes/BackupDocuments
      Un-mount on idle: Disabled
      Volume name: BackupDocuments
```

Now whenever a secure backup of the /Documents folder is needed, just do:
```
    $ efsm mount -en Bac
```

and then use your favorite file system backup utility on the encrypted ```/Volumes/BackupDocuments``` folder.


While there are more commands and options supported by the ```efsm``` utility, this already should give a decent starting point. A general recommendation would be to keep the EncFS config/key file separate from the encrypted backend data, which can be done via the ```--conf-path``` switch of both ```efsm create``` and ```efsm register``` commands:

```
    $ efsm create -en LayeredSecrets -cp ~/.myKeys/se_key -bp ~/Dropbox/.my_secret_folder
    $ Enter password:
    $ Confirm password:
    Creating EncFS backend store...
    Do you want to securely store the password for later use? [y/n]: y
    CipherText Entry registered: LayeredSecrets

    $ efsm mount -en Layered
    Mounted: /Volumes/LayeredSecrets
```

This would keep the conf/key file in a dedicated local folder, further enhancing the cloud data security. As we put the ```LayeredSecrets``` encrypted backend into the same ```~/Dropbox/.my_secret_folder``` that was already used in a prior example, another interesting implication is that now two interleaved encrypted file systems are living alongside in a single place. While generally it's a good idea to use dedicated backend storage folders, a configuration like that could actually be useful for various plausible deniablity scenarios.



[**EFSC**](https://github.com/akpw/efst#efsc) is a EFST configuration tool for managing EncFS preset configurations that could be used for creating EncFS config files. Out of the box, EFST provide a default built-in configuration that can be viewed with the ```efsc show``` command:

```
    $ efsc show -h
    usage: EFSM show [-h] -ce ['EFSTConfigDefault']

    Shows a registered EFST Config entry

    Required Arguments:
        -ce, --config-entry ['EFSTConfigDefault']
                        Name of EFST Config entry to show
```

Additional EncFS presets could be added with ```efsc register``` command. For example, to create a EncFS configuration for ciphertext backend storage with plaintext file names:

```
    $ efsc register -ce PlainFileNames -na Plain # creates a EncFS preset configuration entry
                                                 # with no encryption for file names
```

Once registered, that now can be used by the ```efsm``` utility instead of the default ('EFSTConfigDefault') configuration:
```
    $ efsm create -en PlainNamesSecret -cp ~/.myKeys/pn_key \
                        -bp ~/Dropbox/.my_secret_folder -ce PlainF

    $ efsm mount -en PlainNamesSecret
    Mounted: /Volumes/PlainNamesSecret
```

Similar to the above example, a unique shortcut ("PlainF") is sufficient for the ```-ce``` parameter as it is automatically expanded to its full version ("PlainFileNames") under the hood.

Since we stubbornly keep using the same backend folder ```~/Dropbox/.my_secret_folded```, this will add a thrid layered file system which would have encrypted files content without encrypting the actual file names.

To keep things simple here, I'll be off-loading more advanced used-cases to a later blog. In the meantime, all the details could be revealed via reading the individual commands description below or just using the ```-h``` switch in the command line.

[**EFSB**](https://github.com/akpw/efst#efsb) is a EFST configuration tool for managing EncFS backend stores folders. It can show registered EncFS File Systems info, retrieve plaintext EncFS key values, change EncFS passwords, list encrypted files, encode / decode file names, show EncFS
cruft info, etc.
For example, to see a detailed info for the previously created `MySecrets` folder:

```
$ efsb show -en MyS -sk -cs
CipherText Volume Info:
  Backend Store Path (CipherText):
    /Users/AKPower/Dropbox/.my_secret_folder
  Conf/Key Path:
    /Users/AKPower/Dropbox/.my_secret_folder/.encfs6.xml
  The Key (PlainText Value):
    9VW3vyb1WatB6MCGh51I-K6IBru9wSdeR97wYPac-x41Hf352mcTcBqLBgB4ub9LHbMTz
  General Info:
    Version 6 configuration; created by EncFS 1.8.1 (revision 20100713)
    Filesystem cipher: "ssl/aes", version 3:0:0 (using 3:0:2)
    Filename encoding: "nameio/stream", version 2:1:0 (using 2:1:2)
    Key Size: 256 bits
    Using PBKDF2, with 153491 iterations
    Salt Size: 160 bits
    Block Size: 1024 bytes
    File holes passed through to ciphertext.
  Un-decodable filenames:
    Found 1 invalid file.
    Use the <-cf, --cruft-file> parameter to store detailed cruft info to a file

```


## Full description of CLI Commands
### efsm

    EFSM enables creating new and registering existing EncFS backends, to then
    easily manipulate corresponding ciphertext / plaintext views.
      . action commands:
        .. create       Sets up and register a new EncFS backend along with its related assets
        .. register     Registers an existing EncFS backend along with its related assets
        .. unregister   Un-registers an EncFS backend
        .. show         Shows info about a registered EncFS backend
        .. mount        Mounts a data-access view for a registered EncFS backend
        .. umount       Un-Mounts a data-access view for a registered EncFS backend
        .. info         Shows info about the EFSM utility
        .. version      Shows EFST version

    Usage: $ efsm [-h]
                    {create, register, unregister, show, mount, umount, info, version}
      Commands:
        {create, register, unregister, show, mount, umount, info, version}

        $ efsc {command} -h  #run this for detailed help on individual commands


### efsb

    EFSB helps manage backened stores for registered EFST entries
      . action commands:
        .. show         Shows info about a registered EncFS entry backend
        .. encode       Encodes a file entry name to its CipherText version
        .. decode       Decodes a file entry name to its PlainText version
        .. info         Shows info about the EFSB utility
        .. version      Shows EFST version

    Usage: $ efsb [-h]
                    {show, encode, decode}
      Commands:
         {show, encode, decode}

        $ efsb {command} -h  #run this for detailed help on individual commands


### efsc

    EFSC helps create EncFS conf/key files and manage related EFST config. entries
      . action commands:
        .. create-key   Creates EncFS conf/key file at a specified location
        .. register     Registers an EFST config entry
        .. unregister   Un-registers an EFST config entry
        .. show         Shows info about a registered EFST config entry
        .. info         Shows info about the EFSC utility
        .. version      Shows EFST version

    Usage: $ efsc [-h]
                    {create-key, register, show, unregister, info, version}
      Commands:
        {create-key, register, show, unregister, info, version}

        $ efsc {command} -h  #run this for detailed help on individual commands

## Installing Development version
- Clone the repo, then run: `$ python setup.py develop`

** Running Tests**
- Run via: `$ python setup.py test`






