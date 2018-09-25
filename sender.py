class Sender(object):

    senderIP 
    senderPort
    windowSize
    maxFrameSize
    # sequence number bits
    path # path to take the file from

    handler = PackageHandler()
    ack_handler = AckHandler()
    handler.start()
    ack_handler.start()

    handler.join()
    


class PackageHandler(Thread):

    def run():
        # do something