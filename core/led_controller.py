import gpiod
import time

# !!! REPLACE THESE VALUES WITH YOUR ROCK 5B's specific chip and line number !!!
# Example for a hypothetical setup:
# CHIP_NAME = "gpiochip4" 
# LED_LINE_OFFSET = 21 

CHIP_NAME = "gpiochip4"  # Replace with your Rock 5B's GPIO chip name
LED_LINE_OFFSET = 21     # Replace with the GPIO line offset connected to the LED strip

try:
    chip = gpiod.Chip(CHIP_NAME)
    line = chip.get_line(LED_LINE_OFFSET)

    # Request the line as output, setting initial value to 0 (off)
    line.request(consumer='led_strip', type=gpiod.LINE_REQ_DIR_OUT, default_val=0)

    print(f"Blinking LED on {CHIP_NAME}, line {LED_LINE_OFFSET}...")
    for _ in range(10):
        line.set_value(1)  # Turn on
        time.sleep(0.5)
        line.set_value(0)  # Turn off
        time.sleep(0.5)

except Exception as e:
    print(f"An error occurred: {e}")
    print("Please verify your CHIP_NAME and LED_LINE_OFFSET values using gpiodetect and the Radxa pinout documentation.")

finally:
    # Ensure the line is released when done
    if 'line' in locals() and line.is_requested():
        line.release()

