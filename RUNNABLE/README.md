# repy_v2

RepyV2 is a cross-platform, **Re**stricted **Py**thon environment and
is used most prominently in
[Seattle](https://github.com/SeattleTestbed), the open peer-to-peer
testbed. This README gives a quick conceptual overview. More detailed
information is available from the
[Seattle documentation](https://github.com/SeattleTestbed/docs/blob/master/UnderstandingSeattle/README.md)
and the source code in this repository.

Repy is "restricted" in several ways, and its restrictions revolve around
making it a **safe** sandbox inside of which **untrusted code** can be
executed with **minimal impact** to the system hosting the sandbox.
This means that a sandboxed program has limited resources to use,
is confined to a single directory on the file system, needs
explicit permission to use TCP/UDP ports, and so on; furthermore,
while Python-based, many useful *but dangerous* (or potentially
obscurer) features of Python are disabled in Repy. Lastly, the
RepyV2 sandbox exposes a safe [API](https://github.com/SeattleTestbed/docs/blob/master/Programming/RepyV2API.md)
that connects programs with the outside world, the user, and the
file system.



### Code Safety

Repy ensures code safety in the sense that buggy or deliberately destructive
code cannot harm the host machine. This is done in three ways: First, the code
is checked statically for constructs that we consider unsafe, see
[`safe.py`](https://github.com/SeattleTestbed/repy_v2/blob/master/safe.py).
This catches things like attempting to `import` a library, using the `print`
statement (instead of RepyV2'2 `log` function), and so on.

Second, the namespace wrapping layer in
[`namespace.py`](https://github.com/SeattleTestbed/repy_v2/blob/master/namespace.py)
performs checks on every call to the
[RepyV2 API functions](https://github.com/SeattleTestbed/docs/blob/master/Programming/RepyV2API.md).
This guarantees that only specific types of variables can be passed to and
returned from the API.

Third, the RepyV2 API also defends itself against attempts of otherwise abusing
call parameters. For example, the functions for accessing files will not accept
attempts to add directory names to filenames, and the networking functions
don't allow passing options to the actual socket objects used for data transfer.



### Resource Restrictions

Repy reads resource quotas for a sandbox from a restrictions file. The `nanny`
component tallies usage statistics for all resources, and intervenes (by
blocking resource consumption) so that the quotas are met.
A much more detailed description and evaluation of the concept can be found
in our paper
["Fence: Protecting Device Availability with Uniform Resource Control"](https://ssl.engineering.nyu.edu/papers/li-usenix-fence-2015.pdf).



### Directory And Interface Restrictions

These restrictions govern where the sandbox can read and write files,
and what IP addresses and interfaces the Repy sandbox may bind to.
They are set up via command-line arguments to the sandbox. See
[`repy.py`](https://github.com/SeattleTestbed/repy_v2/blob/master/repy.py)'s
usage string for details
