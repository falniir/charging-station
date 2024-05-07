from sense_hat import SenseHat
import paho.mqtt.client as mqtt
from threading import Thread
from stmpy import Driver, Machine
import time
import random


broker, port = "test.mosquitto.org", 1883
mqtt_topic = "ttm4115/rats"

G = [0, 255, 0]
X = [255, 0, 0]
O = [0, 0, 0]
Y = [230, 200, 0]

green_checkmark = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, G,
    O, O, O, O, O, O, G, G,
    O, G, O, O, O, G, G, O,
    O, O, G, O, G, G, O, O,
    O, O, O, G, G, O, O, O,
    O, O, O, O, G, O, O, O
]


red_x = [
    X, O, O, O, O, O, O, X,
    O, X, O, O, O, O, X, O,
    O, O, X, O, O, X, O, O,
    O, O, O, X, X, O, O, O,
    O, O, O, X, X, O, O, O,
    O, O, X, O, O, X, O, O,
    O, X, O, O, O, O, X, O,
    X, O, O, O, O, O, O, X
]

yellow_triangle = [
    O, O, O, Y, Y, O, O, O,
    O, O, Y, O, O, Y, O, O,
    O, O, Y, O, O, Y, O, O,
    O, Y, O, O, O, O, Y, O,
    O, Y, O, O, O, O, Y, O,
    Y, O, O, O, O, O, O, Y,
    Y, Y, Y, Y, Y, Y, Y, Y,
    O, O, O, O, O, O, O, O,
]

charge_1 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    X, X, X, X, X, X, X, X
]

charge_2 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    X, X, X, X, X, X, X, X,
    X, X, X, X, X, X, X, X
]

charge_3 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    Y, Y, Y, Y, Y, Y, Y, Y,
    Y, Y, Y, Y, Y, Y, Y, Y,
    Y, Y, Y, Y, Y, Y, Y, Y
]

charge_4 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    Y, Y, Y, Y, Y, Y, Y, Y,
    Y, Y, Y, Y, Y, Y, Y, Y,
    Y, Y, Y, Y, Y, Y, Y, Y,
    Y, Y, Y, Y, Y, Y, Y, Y
]

charge_5 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G
]


charge_6 = [
    O, O, O, O, O, O, O, O,
    O, O, O, O, O, O, O, O,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G
]

charge_7 = [
    O, O, O, O, O, O, O, O,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G
]

charge_8 = [
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G,
    G, G, G, G, G, G, G, G
]

charge = [charge_1, charge_2, charge_3, charge_4, charge_5, charge_6, charge_7, charge_8]



class ChargerMQTT:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message


    def mqtt_on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("mqtt_on_connect(): {}".format(mqtt.connack_string(rc)))
        else:
            print("Failed to connect to MQTT broker")
            

    def mqtt_on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        print("mqtt_on_message(): topic: {}".format(msg.topic))
        print("mqtt_on_message(): payload: {}".format(message))
        if(message == "RESERVE"):
            self.stm_driver.send("message_reserve", "charger")
        elif(message == "MAINTANENCE"):
            self.stm_driver.send("message_fault", "charger")
        elif(message == "START"):
            self.stm_driver.send("message_car_connected", "charger")
        elif(message == "STOP"):
            self.stm_driver.send("message_car_disconnected", "charger")
        elif(message == "RESET"):
            self.stm_driver.send("message_reset", "charger")

    def mqtt_on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker. result code (rc): {}".format(rc))


    def start(self):
        print("Connecting to {}:{}".format(broker, port))


        self.client.connect(broker, port)
        self.client.subscribe(mqtt_topic, qos=1)

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except Exception as err:
            print("Interrupted {}".format(err))
            self.client.disconnect()






class Charger:

    def __init__(self):
        self.sensehat = SenseHat()
        self.charge_percentage = 0.0
        self.incr = 100 / 7

    def sensehat_vacant(self):
        self.sensehat.set_pixels(green_checkmark)

    def sensehat_reserved(self):
        self.sensehat.set_pixels(red_x)

    def sensehat_occupied(self):
        self.sensehat.set_pixels(red_x)

    def sensehat_fault(self):
        self.sensehat.set_pixels(yellow_triangle)
        
    def sensehat_charging(self):
        index = int((self.charge_percentage) // self.incr)

        if self.charge_percentage == 100.0:
            self.sensehat.set_pixels(charge[7])
            self.mqtt_client.publish(mqtt_topic, "100.00".format(self.charge_percentage), qos=1)
            return
        
        self.sensehat.set_pixels(charge[index])
        self.mqtt_client.publish(mqtt_topic, "{:.2f}".format(self.charge_percentage), qos=1)
        self.charge_percentage += self.incr
        self.charge_percentage = min(100.0, self.charge_percentage)


            


    def mqtt_send_vacant(self):
        self.mqtt_client.publish(mqtt_topic, "VACANT", qos=1)
        self.sensehat_vacant()

    def mqtt_send_reserved_ack(self):
        self.mqtt_client.publish(mqtt_topic, "RESERVED", qos=1)
        self.sensehat_reserved()

    def mqtt_send_occupied(self):
        self.mqtt_client.publish(mqtt_topic, "OCCUPIED", qos=1)
    
    def mqtt_send_fault(self):
        self.mqtt_client.publish(mqtt_topic, "FAULT", qos=1)
        self.sensehat_fault()


    def charging_on(self):
        self.mqtt_client.publish(mqtt_topic, "STARTED", qos=1)
        self.charge_percentage = random.randint(1, 40)
        self.sensehat.set_pixels(charge[int((self.charge_percentage) // self.incr)])
        self.sensehat_charging()

    def charging_off(self):
        self.mqtt_client.publish(mqtt_topic, "STOPPED", qos=1)


    
    






transition_initial_to_vacant = {
                                "source": "initial", 
                                "target": "state_vacant"
                                }
                                
transition_vacant_to_reserved = {
                                "trigger": "message_reserve", 
                                "source": "state_vacant", 
                                "target": "state_reserved", 
                                "effect": "start_timer('t1', 15000)"
                                }
                                
transition_vacant_to_fault = {
                            "trigger": "message_fault", 
                            "source": "state_vacant", 
                            "target": "state_fault"
                            }

transition_reserved_to_vacant_timeout = {
                                        "trigger": "t1", 
                                        "source": "state_reserved", 
                                        "target": "state_vacant"
                                        }
                                        
transition_reserved_to_vacant_stop = {
                                    "trigger": "message_car_disconnected", 
                                    "source": "state_reserved", 
                                    "target": "state_vacant", 
                                    "effect": "stop_timer('t1')"
                                    }
                                    
transition_reserved_to_occupied = {
                                    "trigger": "message_car_connected", 
                                    "source": "state_reserved", 
                                    "target": "state_occupied", 
                                    "effect": "stop_timer('t1'); charging_on;"
                                    }
                                    
transition_reserved_to_fault = {
                                "trigger": "message_fault", 
                                "source": "state_reserved", 
                                "target": "state_fault"
                                }

transition_occupied_to_vacant = {
                                "trigger": "message_car_disconnected", 
                                "source": "state_occupied", 
                                "target": "state_vacant"
                                }

transition_occupied_to_fault = {
                                "trigger": "message_fault", 
                                "source": "state_occupied", 
                                "target": "state_fault"
                                }
                                
transition_occupied_to_occupied = {
                                "trigger": "t2", 
                                "source": "state_occupied", 
                                "target": "state_occupied", 
                                "effect": "start_timer('t2', 2500); sensehat_charging"
                                }


transition_fault_to_vacant = {
                            "trigger": "message_reset", 
                            "source": "state_fault", 
                            "target": "state_vacant"
                            }



state_vacant = {'name': 'state_vacant',
                'entry': 'mqtt_send_vacant; sensehat_vacant'
}

state_reserved = {'name': 'state_reserved',
                'entry': 'mqtt_send_reserved_ack; sensehat_reserved'
}


state_occupied = {'name': 'state_occupied',
                'entry': 'mqtt_send_occupied; start_timer("t2", 3000)',
                'exit': 'stop_timer("t2")'
                
}


state_fault = {'name': 'state_fault',
                'entry': 'mqtt_send_fault; sensehat_fault; charging_off'
}











def main():
    charger = Charger()
    charger_machine = Machine(name='charger', 
                            transitions=[transition_initial_to_vacant,
                            
                                        transition_vacant_to_reserved,
                                        transition_vacant_to_fault,
                                        
                                        transition_reserved_to_vacant_timeout,
                                        transition_reserved_to_vacant_stop,
                                        transition_reserved_to_occupied,
                                        transition_reserved_to_fault,
                                        
                                        transition_occupied_to_vacant,
                                        transition_occupied_to_fault,
                                        transition_occupied_to_occupied,
                                        
                                        transition_fault_to_vacant], 
                                                            
                                obj=charger, 

                                states=[state_vacant, 
                                        state_reserved, 
                                        state_occupied,
                                        state_fault])


    charger.stm = charger_machine

    driver = Driver()
    driver.add_machine(charger_machine)

    charger_mqtt = ChargerMQTT()
    charger.mqtt_client = charger_mqtt.client
    charger_mqtt.stm_driver = driver

    driver.start()
    charger_mqtt.start()




if __name__ == '__main__':
    main()
