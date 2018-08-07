# Home-Assistant-Luxtronik

A Luxtronik heatpump component for Home Assistant

This component is going to use the "old" binary protocol that Alpha Innotec, the manufacturer of the Luxtronik heatpumps, used in its Java based webinterface. They added a new, websockets based webinterface in newer versions, but in order to make this a useful component to as much users as possible we decided to stick with the binary protocol.
Maybe we implement the new protocol in the future and make it configurable which protocol the component is going to use.

## Binary protocol

A Luxtronik heatpump runs a TCP server that servers the binary protocol on port 8888 or 8889 depending on the firmware version. 

The binary protocol has 4 commands which are decribed in seperate files:

- [3002](3002.md) : Writing parameters to the heatpump
- [3003](3003.md) : Read parameters from the heatpump
- [3004](3004.md) : Read calculations from the heatpump (measurement values, etc.)
- [3005](3005.md) : Read visibilitys from  the heatpump (not clear at the Moment what the purpose of these is)
