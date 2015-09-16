Title: Bridged VPN with OpenWRT and SoftEther
Date: 2015-06-02
Category: Networking

I have been happily using OpenWRT as the main operating system for my networking
needs at home. More specifically, I have recently installed a TP-Link Archer V5
of which I am very satisfied. In this post, I will be running through the main
steps necessary to easily access the local network through VPN. We will be using
the open-source SoftEther software, from the University of Tsukuba in Japan.

## Why SoftEther and not OpenVpn

OpenVpn is the defacto solution for VPN under the Unix environment. However, I
decided to use another opensource software, SoftEther, for a variety of reasons:

1. Since SoftEther acts as an L2TP server, the VPN can be accessed with the
native clients included in Android, Windows, and OSX. This is a big usability
win in my books.

2. Did I mention I love VoIP? I have a VDSL/VoIP box (with ATA for old phones) 
kindly offered by my provider. It can be accessed within the local network
to place landline and cellular calls via SIP. I would love to be able to use
this when away from home, but SIP is notoriously picky about NATs and other
network magic, so that a standard OpenVPN L3 VPN would not work without
significant hand-holding.

3. In my experience, I have found that L2 (bridging) VPNs are more friendly
with a whole set of network services, i.e. discovery of Apple and Windows
services works out of the box. Unfortunately, OpenVPN recommends using routed
(L3) VPNs and L2 are a pain to configure correctly.

4. SoftEther has an integrated Dynamic DNS client (joking, but useful for
testing, and you can pick your favorite l2 domain)

For the reasons above, I decided to go with SoftEther and leave the trusty
OpenVPN this time.

## Setting up SoftEther

There are a couple of guides for setting up SofEther on OpenWRT. I followed
this one:

http://wordpress.tirlins.com/?p=63

For ar71xx devices (such as the Archer C5) it all boils down to installing a
couple of dependencies:

	opkg update
	opkg install zlib libpthread librt libreadline libncurses libiconv-full kmod-tun libopenssl

and downloading an *ipk* package from [a nice site](http://b.mikomoe.jp/) into /tmp and then
installing it with `opkg install`.

The rest of the procedure is straight forward and very similar to what you
would do on a standard Linux install. Just remember to open ports

- TCP 443 for the management interface
- UDP 500 and 4500 for the L2TP connection

You can easily do this with the admin interface on the Network -> Firewall ->
Traffic rules page.

## The tricky parts

SoftEther has a built-in system check feature that you can access by starting
up the server:

	/usr/bin/env LANG=en_US.UTF-8 /usr/bin/vpnserver start

and running the command-line management interface:

	/usr/bin/env LANG=en_US.UTF-8 /usr/bin/vpncmd

To access the built-in check:

1. Choose option 3
2. Write *check*
3. Wait for the test to complete
4. Write *exit*

My system would fail the check at the "network" step, but luckily this has not
impacted the functionality.

## Configuring the bridge

If you have a standard OpenWRT config, you want to bridge the VPN to the `br-lan`
interface, so that your remote clients can get an IP address from the router
and communicate freely with the rest of the network.

<img src="{filename}/images/mgmt_interface.png" alt="SoftEther management interface" width="80%"/>

Click on the "local bridge" button to configure the virtual TAP device that
we will be bridging later. The following window appears:

<img src="{filename}/images/local_bridge.png" alt="Virtual TAP configuration" width="60%"/>

Select the Virtual Hub you want to bridge with and be sure to *create a new TAP
device*. Once you confirm, you'll get a new device in your `ifconfig` output:

```
tap_sether Link encap:Ethernet  HWaddr 00:AC:64:55:EF:4E  
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:3744157 errors:0 dropped:0 overruns:0 frame:0
          TX packets:3653750 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:500 
          RX bytes:1197775990 (1.1 GiB)  TX bytes:1719054306 (1.6 GiB)
```

The last step involves actually bridging the newly created TAP interface with
the existing `br-lan` interface. To do this, edit the `/etc/config/network/`
file and look for the `lan` interface. My config looks like this:

```
config interface 'lan'
        option ifname 'eth1 tap_sether'
        option type 'bridge'
        option proto 'static'
        option netmask '255.255.255.0'
        option ipaddr '192.168.2.253'
```

Note the `bridge` type and the `tap_sether` interface added in.

To finish up, `/etc/init.d/networking/restart` so that the changes take effect,
and enjoy your remote connection.

## Performance
I am very satisfied with the final outcome: the uptime is great and the puny
CPU in the router saturates my 3mbit/s upload connection just fine. All
network services, including SIP, work brillianty across the VPN and require no special
configuration.

