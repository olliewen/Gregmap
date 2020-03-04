# Gregmap
WARNING: I don't have a check for dependencies yet.

I'm hoping to have caught any exception generated and have the script just skip over any tests that use dependencies you don't have.
Have you ever looked at your nmap scan results and thought:

"Damn, a lot of what I'm going to be doing for the next couple of hours could be automated"?
Well you're in luck. Basic testing of FTP, RPC, NFS, SMB, and HTTP services has never been easier. GregMap is here!
GregMap is part wrapper, part not wrapper. It will use command line utilities like nc, cURL, wget...
and I know that if you have installed ncat (nmap's netcat utility) then my port scanner, and therefore GregMap, will not work.
You should be warned, GregMap can launch enum4linux and dirb as background processes, which can sometimes generate a lot of noise.

I don't have a flag to turn these off, so for now, just use the -P flag if you don't want enum4linux and dirb to run.
Additionally, Greg will attempt to download all files from an FTP server, which is arguably a bad idea, should one exist.
If you want to avoid this, again, use the -P flag.

Test everything quickly with -H [host] or include a -P in your command line for a nice little prompt so you can choose what to test.
Find the help page with '-h'.

Disclaimer: My code is garbage. For your own safety, you shouldn't try to review it.

GregMap. Powered by Greg.

(this tool is not good. use AutoRecon instead.)
