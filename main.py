import can, time, sys, threading, math
start = time.time()
BUS = can.interface.Bus(interface='socketcan', channel='vcan0')
BUS2 = can.interface.Bus(interface='socketcan', channel='vcan0')
#bus = can.interface.Bus(interface='virtual')
#printer = can.Printer()
#notifier = can.Notiier(bus, [printer])

class ECU:
    isTransmitter = False
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

    def transmitPeriodic(self, targetBus=BUS, speed=1):
        self.isTransmitter = True
        def sendMsg(busToUse, speedToUse):
            try:
                BUS.send(self.msg)
                #print(f"Message sent on {BUS.channel_info}")
            except can.CanError:
                print("Message NOT sent!")
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

    def __broadcastError(self):
        print("broadcastError")

    def printErrorRegs(self):
        def repeat():
            print(f"\rTEC, REC: {self.TEC},{self.REC}", end='')
            threading.Timer(0.0001, repeat).start()
        repeat()

    def decrementTEC(self):
        if self.TEC > 0:
            self.TEC = self.TEC - 1
        
    def decrementREC(self):
        if self.REC > 0:
            self.REC = self.REC - 1

    def error(self):
        #print("error")
        if (self.isTransmitter):
            self.TEC = self.TEC + 8
        else:
            self.REC = self.REC + 1

        if (self.TEC > 127 and self.TEC < 255) or (self.REC > 127 and self.REC < 255):
            self.state = 0b10 # error passive
        elif self.TEC < 128 and self.REC < 128:
            self.state = 0b01 # error active
        elif self.TEC >= 255:
            self.state = 0b11 # bus-off
            print("~~BUS OFF~~")
            sys.exit(11)
   

def busRecv(bus=BUS):
    def repeat():
        msgOut = bus.recv()
        try:
            if msgOut.data == victim.getMsg().data:
                victim.decrementTEC()
            else:
                victim.decrementREC()
        except:
            pass
        #print(f"msg: {msgOut}")
        threading.Timer(0.000001, repeat).start()
        return msgOut
    return repeat()

if __name__ == "__main__":
    victim = ECU(0x70, [0, 0, 0, 1, 0, 0, 0, 0])
    attacker = ECU(0x70, [0, 0, 0, 0, 1, 0, 1, 0])

    print("Beginning transmission...")
    victim.transmitPeriodic(BUS, 0.050)
    victim.printErrorRegs()
    attacker.transmitPeriodic(BUS, 0.0001)
    
    pastTimestamp = -1
    count = 0
    while True:
        #print(f"rcvd: {busRecv(BUS2).timestamp}")
        timestamp = busRecv(BUS2).timestamp
        #print(round(timestamp, 6), round(pastTimestamp, 6))
        # print(f"\r{math.ceil((timestamp*1000))/1000}\t{math.ceil((pastTimestamp*1000))/1000}", end='')
        if math.ceil((timestamp*1000))/1000 == math.ceil((pastTimestamp*1000))/1000:
            #count = count + 1
            #print(f"\r{count}", end='')
            victim.error()
            #print("\n\nSAME TIME!\n\n")
            #sys.exit(1)
        pastTimestamp = timestamp
        # print(f"\r{timestamp}", end='')
    #while True:
    #    busRecv(BUS)
    #        print(BUS.recv())
    # listener = can.Listener(bus)
    # print(listener(msgReceived))
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

