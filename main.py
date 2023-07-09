import machine
import time
import urequests
import ujson

VERSION="0.0.0"

def sendwebhook(url):
    data = ujson.dumps(
        {
            "text": "Doorbell Rung"
        }
    )

    res = None
    try:
        res = urequests.post(
            url,
            headers={
                'Content-Type': 'application/json'
            },
            data=data
        )

        print('sent webhook...')
        print(res)
    finally:
        # You must close RES otherwise memory will run out quickly
        if res:
            res.close()


def main(cfg):
    
    # Setup PINS
    led_pin = machine.Pin(
        32,
        machine.Pin.OUT,
        value=1
    )

    bell_pin = machine.Pin(
        27,
        machine.Pin.IN,
        None,
        value=1
    )

    # Track last time webhook was sent and last time we did a blink
    webhook_last_ticks = None
    last_blink = time.ticks_ms()

    while True:
        # See if we want to check for a doorbell ring
        if (webhook_last_ticks is None) or time.ticks_diff(time.ticks_ms(), webhook_last_ticks) > 60000:
            # Slow Blink during time period where we want bell rings
            if time.ticks_diff(time.ticks_ms(), last_blink) > 1000:
                last_blink = time.ticks_ms()
                led_pin.value((led_pin.value() + 1) % 2)

            if bell_pin.value():
                led_pin.value(1)
                webhook_last_ticks = time.ticks_ms()
                print("sending webhook...")
                sendwebhook(cfg.WEBHOOK_URL)
                led_pin.value(0)
        else:
            # Fast Blink during time period where we ignore bell rings
            if time.ticks_diff(time.ticks_ms(), last_blink) > 100:
                last_blink = time.ticks_ms()
                led_pin.value((led_pin.value() + 1) % 2)

        # Sleep for 1 ms
        time.sleep_ms(1)