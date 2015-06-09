####Requirements:
- [Python 3.4.x](https://www.python.org/download/releases/3.4.1/) or later
- [EncFS](https://github.com/vgough/encfs) installed and available on the command line
- OS: Mac OSX or Linux (Windows TBD/maybe)


####Install:
- latest from source repository: `$ pip install git+https://github.com/akpw/efst.git`

####Blogs:

##Description

[EncFS](https://github.com/vgough/encfs) is a free [FUSE-based](https://en.wikipedia.org/wiki/Filesystem_in_Userspace) cryptographic file system. It transparently encrypts files, using a selected directory as back-end storage for the encrypted files. EncFS works on per-file basis, which makes it suitable for syncing files and a great fit for protecting cloud data.

EFST help manage EncFS-encrypted data, making it easy to create / register all nessesery EncFS assets and then effectively operate it via a few simple commands. In addition to common operation such as mounting / unmounting EncFS volumes, EFST simplifies and automates advanced EncFS features such as reverse encryption for encrypted backups or multiple interleaved EncFS file systems for plausible deniablity.

The EFST project is written in [Python 3.4](https://www.python.org/download/releases/3.4.1/) and currently consists of two main command-line utilities.

[**EFSM**](https://github.com/akpw/efsm#efsm) enables creating / registering / operating EncFS back-end stores and all its related assests such as target mountpoint path, mount volume name, path to config/key file, etc. 
One way to learn about available EFSM optons would obviously be via running:
```
    $ efsm -h

```

As a more practical approach, lets just quickly create and handle a basic encrypted Dropbox folder:
```
    $ efsm create -en SecretDropBoxFolder -bp ~/Dropbox/.my_secret_folder
    Enter password: 
    Confirm password:
    Creating EncFS backend store...
    Do you want to securily store the password for further use? [y/n]: y
    CipherText Entry registered: SecretDropBoxFolder
```

A single simple command did quite a few things there. A backend directory for storing the encrypted files has been created, an EncFS config/key file was generated, default values has been figured out and finally a password was collected from input, set, and stored in your OS-specific secure keychain.
To review all of these in detail, let's take a look at the relevant EFST config entry:
```
    $ efsm show -en Se
    Entry name: SecretDropBoxFolder
        Entry type: CipherText
        Password store entry: efst-entry-SecretDropBoxFolder
        Conf/Key file: /Users/AKPW/Dropbox/.my_secret_folder/.encfs6.xml
        Back-end store folder: /Users/AKPW/Dropbox/.my_secret_folder
        Mount folder: /Volumes/SecretDropBoxFolder
        Volume name: SecretDropBoxFolder
```

The password store entry here is the name of the automatically created OS-specific keychain entry. Since I ran the ````efsm create```` command on my Mac, here is the relevant Mac OS keychain entry:
![efst-keychain](https://lh3.googleusercontent.com/HXtJUhzr5Hiq8XNmofy0kF_VX4mtkd0CeA_4F_3oDqc=w532-h346-no)


From now on, working with the protected data is straightforward:
```
    $ efsm mount -en Secret
    Mounted: /Volumes/SecretDropBoxFolder
```

The mounted folder is where you put your plaintext data, with the encrypted version automatically stored in the backend "Dropbox/.my_secret_folder".

Unmounting the plaintext view is just as easy:
```
    $ efsm umount -en Se
    Unmounted: /Volumes/SecretDropBoxFolder
```

Now the data are stored on your computer (and Dropbox) in encrypted form, readily accessible whenever needed via the above 'efsm mount' command.


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






