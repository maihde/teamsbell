import esp
import webrepl
import machine
import network
import time

VERSION="0.0.0"

# Load configuration
try:
    import main_cfg
except ImportError:
    print("create main_cfg.py to configure application")
    main_cfg = None

try:
    import main
except ImportError:
    print("load main.py to setup application")
    main = None

##############################################################################

def do_connect(ssid, key):
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect(ssid, key)
        while not sta_if.isconnected():
            time.sleep(1)
        print("connected:", sta_if.ifconfig())


def boot():
    print("running boot:", VERSION)
    # The REPL PIN, when held down will skip launching the main application
    # and instead allow the device to enter the micropython REPL
    repl_pin = machine.Pin(
        14,
        machine.Pin.IN,
        machine.Pin.PULL_UP,
    )

    # The LED PIN is used to monitor the boot status, the LED lights
    # inverted to value, since it sinks rather than sources current
    led_pin = machine.Pin(
        32,
        machine.Pin.OUT,
        value=1
    )
    led_pin.value(0)

    if main_cfg:
        do_connect(main_cfg.NETWORK_SSID, main_cfg.NETWORK_KEY)

    # Blink for three seconds quickly to show network has configured
    for _ in range(30):
        led_pin.value((led_pin.value() + 1) % 2)
        time.sleep_ms(100)

    # If the REPL button is held down at this point we enter the REPL instead
    # of executing main
    if repl_pin.value() and (main is not None) and (main_cfg is not None):
        print("executing main:", getattr(main, "VERSION", ""))
        # Set LED on to indicate we are in main
        led_pin.value(0)
        main.main(main_cfg)
    else:
        print("entering repl...")
        # Set LED off to indicate we are not in main
        led_pin.value(1)

##############################################################################
# Run BOOT 
boot()


