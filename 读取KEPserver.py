from opcua import Client


class SubHandler(object):
    """
    客户端订阅。它将从服务器接收事件
    """

    def datachange_notification(self, node, val, data):
        # print("Python: New data change event", node, val)
        print("changed. new value is : ", val)

    def event_notification(self, event):
        print("Python: New event", event)


def test2():
    client = Client("opc.tcp://127.0.0.1:49321")
    client.connect()
    root = client.get_root_node()
    aa = client.get_node('ns=2;s=Channel8.Device1.aa')

    handler = SubHandler()
    sub = client.create_subscription(1000, handler)
    sub.subscribe_data_change(aa)


if __name__ == '__main__':
    test2()