# import random
from .subscriber import Subscribers, Subscriber
# from .constants import *

def generate_subscribers(subscribers: Subscribers,
                         msisdn_template,
                         imsi_template,
                         carrier_id,
                         n_subscribers):
    msisdn_min = int(msisdn_template)
    imsi_min = int(imsi_template)
    imsi = imsi_min
    msisdn_max = msisdn_min + n_subscribers
    imsi_max = imsi_min + n_subscribers
    for msisdn in range(msisdn_min, msisdn_max):
        subscriber = Subscriber(str(msisdn), str(msisdn), str(imsi), carrier_id)
        subscribers.add_subscriber(subscriber)
        imsi += 1
        if imsi > imsi_max:
            imsi = imsi_min
    return subscribers