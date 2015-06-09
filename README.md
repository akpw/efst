####Requirements:
- [Python 3.4.x](https://www.python.org/download/releases/3.4.1/) or later
- [EncFS](https://github.com/vgough/encfs) installed and available on the command line
- OS: Mac OSX or Linux (Windows TBD/maybe)


####Install:
- latest from source repository: `$ pip install git+https://github.com/akpw/efst.git`

####Blogs:

##Description

[EncFS](https://vgough.github.io/encfs/) is a free [FUSE-based](https://en.wikipedia.org/wiki/Filesystem_in_Userspace) cryptographic file system. It transparently encrypts files, using an arbitrary directory as back-end storage for the encrypted files. EncFS works on per-file basis, which makes it suitable for syncing files and a great fit for protecting cloud data.

The EFST project help manage EncFS-encrypted data, making it easy to create / register all necessary EncFS assets and then effectively operate it via a few simple commands. In addition to common operation such as mounting / un-mounting registered EncFS volumes, EFST simplifies and automates advanced EncFS features such as reverse encryption for encrypted backups or multiple interleaved EncFS file systems for plausible deniability.

The EFST project is written in [Python 3.4](https://www.python.org/download/releases/3.4.1/) and currently consists of two main command-line utilities.

[**EFSM**](https://github.com/akpw/efsm#efsm) enables creating / registering / operating EncFS backend stores and all its related assets such as target mountpoint folder, mount volume name, path to config/key file, etc.
One way to learn about available EFSM options would be via running:
```
    $ efsm -h

```

As a more hands on approach, lets just quickly create and handle a basic encrypted Dropbox folder:
```
    $ efsm create -en MySecrets -bp ~/Dropbox/.my_secret_folder
    $ Enter password:
    $ Confirm password:
    Creating EncFS backend store...
    Do you want to securely store the password for further use? [y/n]: y
    CipherText Entry registered: MySecrets
```

A single simple command did quite a few things there. A back-end directory for storing the encrypted files was created, an EncFS config/key file was generated, default values were figured out and finally the password was collected from input, set, and stored in OS-specific system keyring service. To review all of these in detail, let's take a look at the relevant EFST config entry:
```
    $ efsm show -en MyS
    Entry name: MySecrets
        Entry type: CipherText
        Password store entry: efst-entry-MySecrets
        Conf/Key file: /Users/AKPW/Dropbox/.my_secret_folder/.encfs6.xml
        Back-end store folder: /Users/AKPW/Dropbox/.my_secret_folder
        Mount folder: /Volumes/MySecrets
        Volume name: MySecrets
```

The ```-en, --entry-name``` parameter takes the name of a registered entry. Both full registered name and its unique shortcut would do, e,g, in the above it was sufficient to shortcut 'MySecrets' to 'Mys'.

The password store entry is the default name of automatically created OS-specific keychain entry. For Mac OS, this e.g. can be reviewed via the Keychain app:

![efst-keychain](https://lh3.googleusercontent.com/HXtJUhzr5Hiq8XNmofy0kF_VX4mtkd0CeA_4F_3oDqc=w532-h346-no)


From now on, working with the protected data is straightforward:
```
    $ efsm mount -en MyS
    Mounted: /Volumes/MySecrets
```

Now the mounted folder is where you put your plaintext data, with the encrypted version automatically stored in the backend "Dropbox/.my_secret_folder".

Un-mounting the plaintext folder is just as easy:
```
    $ efsm umount -en MyS
    Unmounted: /Volumes/MySecrets
```

Now the data are securely stored on the disk (and Dropbox) in encrypted form, readily accessible whenever needed via the above 'efsm mount' command.

Similar to creating a new EncFS ciphertext backend store, it is as easy to register an existing one.

```
    $ efsm register -en OtherSecrets -bp ~/path-to-existing-ciphertext_backend
    CipherText Entry registered: OtherSecrets

    $ efsm mount -en Other
    OtherSecrets
    $ Enter password:
    Mounted: /Volumes/OtherSecrets
    Do you want to securely store the password for later use? [y/n]: y

    $ efsm umount -en Other
    Unmounted: /Volumes/OtherSecrets
```

While there a few more commands / options supported by the ```efsm``` utility, this already should provide a decent starting point. A general recommendation would be to keep the EncFS config/key file separate from the encrypted backend data, which can be easily accomplished via the ```--conf-path``` switch for both ```efsm create``` and ```efsm register```:

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

This would keep the conf/key file in a dedicated local folder, further enhancing the cloud data security. As in the examples above we put both encrypted backends into a single directory (~/Dropbox/.my_secret_folder), another implication is that we now have a two interleaved encrypted file systems living in a single place. While generally it's a good idea to use dedicated backend storage folders, a configuration like that could be useful for e.g. various plausible deniablity scenarios.

I will follow up with more advanced examples and use-cases in some of the future blogs.


[**EFSC**](https://github.com/akpw/efsm#efsc) is a EFST configuration tool.
```
    $ efsc -h
```

##Full description of CLI Commands
###efsc

    Usage: efsc [-h]
      Commands:
        {info}
        $ efsc {command} -h  #run this for detailed help on individual commands

###efsm
    Usage: efsm [-h]
      Commands:
        {info}
        $ efsc {command} -h  #run this for detailed help on individual commands


##Installing Development version
- Clone the repo, then run: `$ python setup.py develop`

**Running Tests**
- TDB






