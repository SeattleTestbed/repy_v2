"""
   Author: Justin Cappos, Armon Dadgar

   Start Date: 27 June 2008
   V.2 Start Date: January 14th 2009

   Description:

   This is a collection of functions, etc. that need to be emulated in order
   to provide the programmer with a reasonable environment.   This is used
   by repy.py to provide a highly restricted (but usable) environment.
"""

import nanny

# Used for path and file manipulation
import os 
import os.path

# Used to handle a fatal exception
import tracebackrepy

# Used to force Garbage collection to free resources
import gc

# Used to get a lock object
import threading

# Get access to the current working directory
import repy_constants

# Import all the exceptions
from exception_hierarchy import *

# Store a reference to open, so that we retain access
# after the builtin's are disabled
safe_open = open

##### Constants

# This restricts the number of characters in filenames
MAX_FILENAME_LENGTH = 120

# This is the set of characters which are allowed in a file name
ALLOWED_FILENAME_CHAR_SET = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-')

# This is the set of filenames which are forbidden.
ILLEGAL_FILENAMES = set(["", ".", ".."])


##### Module data

# This set contains the filenames of every file which is open
# Access to this set should be serialized via the OPEN_FILES_LOCK
OPEN_FILES_LOCK = threading.Lock()
OPEN_FILES = set([])


##### Public Functions

def listfiles():
  """
   <Purpose>
      Allows the user program to get a list of files in their vessel.

   <Arguments>
      None

   <Exceptions>
      None

   <Side Effects>
      None

  <Resource Consumption>
    Consumes 4K of fileread.

   <Returns>
      A list of strings (file names)
  """
  # Wait for available fileread resources
  nanny.tattle_quantity('fileread',0)

  # Get the list of files from the current directory
  files = os.listdir(repy_constants.REPY_CURRENT_DIR)

  # Consume 4K
  nanny.tattle_quantity('fileread', 4096)

  # Return the files
  return files


def removefile(filename):
  """
   <Purpose>
      Allows the user program to remove a file in their area.

   <Arguments>
      filename: the name of the file to remove.   It must not contain 
      characters other than 'a-zA-Z0-9.-_' and cannot be '.', '..' or
      the empty string.

   <Exceptions>
      FileNotFoundError is raised if the file does not exist
      RepyArgumentError is raised if the filename is invalid.
      FileInUseError is raised if the file is already open.

   <Side Effects>
      None

  <Resource Consumption>
      Consumes 4K of fileread, and 4K of filewrite if successful.

   <Returns>
      None
  """
  OPEN_FILES_LOCK.acquire()
  try:
    # Check that the filename can be used
    filename, exists = check_can_use_filename(filename, True)

    # Wait for available filewrite resources
    nanny.tattle_quantity('filewrite',0)

    # Try to remove the file
    os.remove(filename)

    # Consume the filewrite resources
    nanny.tattle_quantity('filewrite',4096)
  
  except RepyException:
    # We can raise the exceptions that are expected
    raise

  except Exception, e:
    # We should not get an exception. Log this...
    tracebackrepy.handle_internalerror(str(e), 75)

  finally:
    OPEN_FILES_LOCK.release()


def emulated_open(filename, create):
  """
   <Purpose>
      Allows the user program to open a file safely. This function is meant
      to resemble the builtin "open".

   <Arguments>
      filename:
        The file that should be operated on. It must not contain 
        characters other than 'a-zA-Z0-9.-_' and cannot be '.', '..' or
        the empty string.

      create:
         A Boolean flag which specifies if the file should be created
         if it does not exist.

   <Exceptions>
      RepyArgumentError is raised if the filename is invalid.
      FileNotFoundError is raised if the filename is not found, and create is False.
      FileInUseError is raised if a handle to the file is already open.
      ResourceExhaustedError is raised if there are no available file handles.

   <Side Effects>
      Opens a file on disk, uses a file descriptor.

   <Resource Consumption>
      Consumes 4K of fileread. If the file is created, then 4K of filewrite is used.
      If a handle to the object is created, then a file descriptor is used.

   <Returns>
      A file-like object.
  """
  # Check the  type of create
  if type(create) is not bool:
    raise RepyArgumentError, "Create argument type is invalid! Must be a Boolean!"
  
  OPEN_FILES_LOCK.acquire()
  try:
    # Check that the filename can be used
    abs_filename, exists = check_can_use_filename(filename, False)

    # Here is where we try to allocate a "file" resource from the
    # nanny system. If that fails, we garbage collect and try again
    # (this forces __del__() methods to be called on objects with
    # no references, which is how we automatically free up
    # file resources).
    try:
      nanny.tattle_add_item('filesopened', abs_filename)
    except ResourceExhaustedError:
      # Ok, maybe we can free up a file by garbage collecting.
      gc.collect()
      nanny.tattle_add_item('filesopened', abs_filename)

    # If the file does not exist, and we should create or through an exception
    if not exists:
      if create:
        # Wait for available filewrite resources, then create
        nanny.tattle_quantity('filewrite',0)
        safe_open(abs_filename, "w").close()
        nanny.tattle_quantity('filewrite', 4096)
      else:
        raise FileNotFoundError, 'File "'+filename+'" does not exist and "create" flag is False!'

    # Create an emulated file object
    # Mode is always "rw" in binary, and the file can be assumed to exist.
    return emulated_file(filename, abs_filename)

  except RepyException:
    # We can raise the exceptions that are expected
    raise

  except Exception, e:
    # We should not get an exception. Log this...
    tracebackrepy.handle_internalerror(str(e), 76)

  finally:
    OPEN_FILES_LOCK.release()



##### Private functions

def check_can_use_filename(filename, err_no_exist):
  """
  <Purpose>
    Private method to check:
      1) If a filename is allowed
      2) If this filename is already in use
      3) If a file with the given name exists

    The OPEN_FILES_LOCK should be acquired prior to
    calling this method.

  <Arguments>
    filename:
      The filename to check.

    err_no_exist:
      A boolean flag, which specifies if it is an error
      if the file does not exist.

  <Exceptions>
    Raises RepyArgumentError if the filename is not allowed.
    Raises FileNotFoundError if the filename does not exist and err_no_exist is True.
    Raises FileInUseError if the file is in use.

  <Resource Consumption>
    Consumes 4K worth of fileread.

  <Returns>
    A tuple of ( The absolute path to the file , (BOOL) If the file exists )
  """
  # Check that the filename is allowed
  assert_is_allowed_filename(filename)
  
  # Check if the file is in use
  if filename in OPEN_FILES:
    raise FileInUseError, 'File "'+filename+'" is in use!'

  # Get the absolute file path
  absolute_path = os.path.abspath(os.path.join(repy_constants.REPY_CURRENT_DIR, filename))

  # Wait for available fileread resources, then check if the file exists
  nanny.tattle_quantity('fileread',0)
  exists = os.path.isfile(absolute_path)
  nanny.tattle_quantity('fileread', 4096)

  if not exists and err_no_exist:
    raise FileNotFoundError, 'File "'+filename+'" does not exist!'

  # Return the absolute path and if the file exists
  return absolute_path,exists


def assert_is_allowed_filename(filename):
  """
  <Purpose>
    Private method to check if a filename is allowed.

  <Arguments>
    filename:
      The filename to check.

  <Exceptions>
    Raises a RepyArgumentError if the filename is not allowed.

  <Returns>
    None
  """

  # Check the type
  if type(filename) is not str:
    raise RepyArgumentError, "Filename is not a string!"

  # Check the length of the filename
  if len(filename) > MAX_FILENAME_LENGTH:
    raise RepyArgumentError, "Filename exceeds maximum length! Maximum: "+str(MAX_FILENAME_LENGTH)

  # Check if the filename is forbidden
  if filename in ILLEGAL_FILENAMES:
    raise RepyArgumentError, "Illegal filename provided!"

  # Check that each character in the filename is allowed
  for char in filename:
    if char not in ALLOWED_FILENAME_CHAR_SET:
      raise RepyArgumentError, "Filename has disallowed character '"+char+"'"



##### Class Definitions


class emulated_file:
  """
    A safe class which enables a very primitive file interaction.
    We only allow reading and writing at a provided index.
  """

  # We use the following instance variables.
  # filename is the name of the file we've opened,
  # abs_filename is the absolute path to the file we've opened,
  # and is the unique handle used to tattle the "filesopened" to nanny.
  #
  # fobj is the actual underlying file-object from python.
  # seek_lock is a Lock object to serialize seeking
  __slots__ = ["filename", "abs_filename", "fobj", "seek_lock"]

  def __init__(self, filename, abs_filename):
    """
     <Purpose>
        This is an internal initializer. The OPEN_FILES_LOCK should be
        acquired prior to calling this method. Additionally,
        a "filesopened" resource should be acquired using the abs_filename.

     <Arguments>
        filename:
           The name of the file, non-absolute.

        abs_filename:
           The absolute path to a file that should be opened with
           read/write privileges in binary mode. This file must
           exist.

           This should be verified as valid prior to calling,
           since it is assumed to be valid.

     <Exceptions>
        None.

     <Side Effects>
        Opens a file on disk, using a file descriptor.

     <Returns>
        A file-like object 
    """

    # Store the filename we are given
    self.filename = filename
    self.abs_filename = abs_filename

    # Store a file handle
    # Always open in mode r+b, this avoids Windows text-mode
    # quirks, and allows reading and writing
    self.fobj = safe_open(abs_filename, "r+b")

    # Add the filename to the open files
    OPEN_FILES.add(filename)

    # Store a seek lock
    self.seek_lock = threading.Lock()



  def close(self):
    """
    <Purpose>
      Allows the user program to close the handle to the file.

    <Arguments>
      None.

    <Exceptions>
      FileClosedError is raised if the file is already closed.

    <Resource Consumption>
      Releases a file handle.

    <Returns>
      None.
    """

    # Acquire the lock to the set 
    OPEN_FILES_LOCK.acquire()

    # Tell nanny we're gone.
    nanny.tattle_remove_item('filesopened', self.abs_filename)
    
    # Acquire the seek lock
    self.seek_lock.acquire()
  
    try:
      # Release the file object
      fobj = self.fobj
      if fobj is not None:
        fobj.close()
        self.fobj = None
      else:
        raise FileClosedError, "File '"+self.filename+"' is already closed!" 

      # Remove this file from the list of open files
      OPEN_FILES.remove(self.filename)

    finally:
      # Release the two locks we hold
      self.seek_lock.release()
      OPEN_FILES_LOCK.release()


  def readat(self,sizelimit,offset):
    """
    <Purpose>
      Reads from a file handle. Reading 0 bytes informs you if you have read
      pas the end-of-file, but returns no data.

    <Arguments>
      sizelimit: 
        The maximum number of bytes to read from the file. Reading EOF will read less.
      offset:
        Seek to a specific absolute offset before reading.

    <Exceptions>
      RepyArgumentError is raised if the offset or size is negative.
      FileClosedError is raised if the file is already closed.
      SeekPastEndOfFileError is raised if trying to read past the end of the file.

    <Resource Consumption>
      Consumes 4K of fileread for each 4K aligned-block of the file read.
      All reads will consume at least 4K.

    <Returns>
      The data that was read. This may be the empty string if we have reached the
      end of the file, or if the sizelimit was 0.
    """
    # Check the arguments
    if sizelimit < 0:
      raise RepyArgumentError, "Negative sizelimit specified!"
    if offset < 0:
      raise RepyArgumentError, "Negative read offset speficied!"

    # Get the underlying file object
    fobj = self.fobj
    if fobj is None:
      raise FileClosedError, "File '"+self.filename+"' is already closed!"

    # Get the seek lock
    self.seek_lock.acquire()

    try:
      # Get the file's size, seek to the end.
      fobj.seek(0, os.SEEK_END)
      filesize = fobj.tell()

      # Check the provided offset
      if offset > filesize:
        raise SeekPastEndOfFileError, "Seek offset extends past the EOF!"
      
      # Seek to the correct location
      fobj.seek(offset)

      # Wait for available file read resources
      nanny.tattle_quantity('fileread',0)

      # Read the data
      data = fobj.read(sizelimit)

    finally:
      # Release the seek lock
      self.seek_lock.release()

    # Check how much we've read, in terms of 4K "blocks"
    end_offset = len(data) + offset
    disk_blocks_read = end_offset / 4096 - offset / 4096
    if end_offset % 4096 > 0:
      disk_blocks_read += 1

    # Charge 4K per block
    nanny.tattle_quantity('fileread', disk_blocks_read*4096)

    # Return the data
    return data


  def writeat(self,data,offset):
    """
    <Purpose>
      Allows the user program to write data to a file.

    <Arguments>
      data: The data to write
      offset: An absolute offset into the file to write

    <Exceptions>
      FileClosedError is raised if the file is already closed.
      SeekPastEndOfFileError is raised if trying to write past the EOF.
      RepyArgumentError is raised if the offset is negative.

    <Side Effects>
      Writes to persistent storage.

    <Resource Consumption>
      Consumes 4K of filewrite for each 4K aligned-block of the file written.
      All writes consume at least 4K.

    <Returns>
      Nothing
    """
    # Check the arguments
    if offset < 0:
      raise RepyArgumentError, "Negative read offset speficied!"

    # Get the underlying file object
    fobj = self.fobj
    if fobj is None:
      raise FileClosedError, "File '"+self.filename+"' is already closed!"

    # Get the seek lock
    self.seek_lock.acquire()

    try:
      # Get the file's size, seek to the end.
      fobj.seek(0, os.SEEK_END)
      filesize = fobj.tell()

      # Check the provided offset
      if offset > filesize:
        raise SeekPastEndOfFileError, "Seek offset extends past the EOF!"
      
      # Seek to the correct location
      fobj.seek(offset)

      # Wait for available file write resources
      nanny.tattle_quantity('filewrite',0)

      # Write the data and flush to disk
      fobj.write(data)
      fobj.flush()

    finally:
      # Release the seek lock
      self.seek_lock.release()

    # Check how much we've written, in terms of 4K "blocks"
    end_offset = len(data) + offset
    disk_blocks_written = end_offset / 4096 - offset / 4096
    if end_offset % 4096 > 0:
      disk_blocks_written += 1

    # Charge 4K per block
    nanny.tattle_quantity('filewrite', disk_blocks_written*4096)


  def __del__(self):
    # Make sure we are closed
    try:
      self.close()
    except FileClosedError:
      pass # Good, we are already closed.


# End of emulated_file class
