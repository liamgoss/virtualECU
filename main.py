import can, time, sys, threading
start = time.time()
#bus = can.interface.Bus(interface='socketcan', channel='vcan1')
bus = can.interface.Bus(interface='virtual')

class ecu:

    TEC = 0
    REC = 0
    # 01 = error active
    # 10 = error passive,
    # 11 = bus-off
    '''
When TEC or REC is greater than 127 and less than 255, a Passive Error frame
    will be transmitted on the bus.
When TEC and REC is less than 128, an Active Error frame will be
    transmitted on the bus.
When TEC is greater than 255, then the node enters into Bus Off state,
    where no frames will be transmitted.

    '''
    state = 0b01
    def __init__(self, arb, msgData=[0, 0, 0, 0, 0, 0, 0, 0]):
        self.arb_id = arb
        self.msg = can.Message(arbitration_id=arb, data=msgData, is_extended_id=False)
    
    def transmitPeriodic(self, targetBus=bus, speed=1):
        def sendMsg(busToUse, speedToUse):
            busToUse.send(self.msg)
            threading.Timer(speedToUse, sendMsg, args=[busToUse, speedToUse]).start()
        sendMsg(targetBus, speed)

    def setArb(self, arb):
        self.arb_id = arb

    def getArb(self):
        return self.arb_id

    def setMsg(self, msgData):
        self.msg = can.Message(arbitration_id=self.arb_id, data=msgData)

    def getMsg(self):
        return self.msg

    def broadcastError(self):
        print("broadcastError")
   

    def error(self):
        if (self.isTransmitter):
            self.TEC = self.TEC + 8
        else:
            self.REC = self.REC + 9

        if (self.TEC > 127 and self.TEC < 255) or (self.REC > 127 and self.REC < 255):
            self.state = 0b10 # error passive
        elif self.TEC < 128 and self.REC < 128:
            self.state = 0b01 # error active
        elif self.TEC >= 255:
            self.state = 0b11 # bus-off
            print("~~BUS OFF~~")
            sys.exit(11)


if __name__ == "__main__":
    test = ecu(0x69, [0, 0, 0, 1, 0, 0, 0, 0])
    
    test.transmitPeriodic(bus, 1)
    print("Beginning transmission")
    for msg in bus:
        print(msg)
    
    '''
    bg1 = ecu(0x14, [0xFF, 0xA8, 0x56, 0x13, 0x7C, 0x34, 0x99, 0xBA])
    bg2 = ecu(0x14, [0x01, 0xEE, 0x32, 0xA3, 0xCB, 0x00, 0x91, 0xA4])
    victim = ecu(0x70, [0, 1, 0, 1, 0, 0, 0, 1])
    attacker = ecu(0x70, [0, 1, 0, 1, 0, 0, 0, 0])
    
    # I have adjusted these periods a lot, not sure if the issue is simply timing?
    bg1.transmitPeriodic(bus, 0.5)
    bg2.transmitPeriodic(bus, 0.25)
    victim.transmitPeriodic(bus, 0.0001)
    attacker.transmitPeriodic(bus, 0.0000001)
    
    while bus.state == can.bus.BusState.ACTIVE:
        if time.time() - start >= 30: break # 30 second failsafe, my VM likes to freeze
        print(f"\r{bus.state}",end='')


    print()
    print(bus.state)
    '''

