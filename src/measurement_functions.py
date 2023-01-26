"""Module which contains functions for controlling the measurements

    Usage:
    control_xy_table(progress_window, **measurement_configuration) -> move x-y-table with specific configuration
    make_measurement(**measurement_configuration) -> make measurement (is called in control_xy_table)
"""

import pyvisa
from pipython import GCSDevice, pitools, PILogger
import numpy as np
import math
import logging
import pandas as pd

# remove handlers from apis, so everything is logged by the one defined logger
PILogger.handlers = []
pyvisa.logger.handlers = []

_logger = logging.getLogger(__name__)

STAGES = ('L-406.20SD00')
REFMODES = ['FNL']

def control_xy_table(progress_window, **measurement_configuration):
    """This method controls the movement of the xy-table, starts mesurements and saves the results of
    measurement runs

    Args:
        measurement_configuration (dict): Dictonary with measurment configuration
    """

    # calculate number of x and y values
    quantity_of_y_values = int((measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"])
    quantity_of_x_values = int((measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"])

    # allocate memory space for arrays
    x_position_values = np.zeros(quantity_of_y_values * quantity_of_x_values, dtype=float)
    y_position_values = np.zeros(quantity_of_y_values * quantity_of_x_values, dtype=float)
    measurements = np.zeros(quantity_of_y_values * quantity_of_x_values, dtype=float)

    # make calculations for progress bar step size
    step_size = 100 / (quantity_of_x_values*quantity_of_y_values * measurement_configuration["number_of_measurement_runs"])
    progress = 0

    try:
        # create two gsc device instances for being able to control the two step motors
        with GCSDevice() as device_1, GCSDevice() as device_2:

            # establish the connections with the two controllers
            device_1.ConnectUSB('0017550026')
            device_2.ConnectUSB('0017550025')
            
            # a lot of initializing information
            _logger.info('Connected to devices with IDs')
            _logger.info('\n{}:\n{}'.format(device_1.GetInterfaceDescription(), device_1.qIDN()))
            _logger.info('\n{}:\n{}'.format(device_2.GetInterfaceDescription(), device_2.qIDN()))

            _logger.info('Initialization of axes...')

            # initialize axes
            pitools.startup(device_1, stages=STAGES, refmodes=REFMODES)
            pitools.startup(device_2, stages=STAGES, refmodes=REFMODES)

            _logger.info('Min y-axis:', device_1.qTMN())
            _logger.info('Max y-axis:', device_1.qTMX())

            _logger.info('Min x-axis:', device_2.qTMN())
            _logger.info('Max x-axis:', device_2.qTMX())

            # run the ammount of configured measuremnts
            for i in range(measurement_configuration["number_of_measurement_runs"]): 
                
                _logger.info('In {}. measurement run'.format(i))

                # reset the y axis to start point
                device_1.MOV(1, measurement_configuration["y_start_value"])
                
                # wait until y axis is at correct position
                pitools.waitontarget(device_1, axes=1)

                # reset the x axis to start point
                device_2.MOV(1, measurement_configuration["x_start_value"])

                # wait until x axis is at correct position
                pitools.waitontarget(device_2, axes=1)

                # wait so the table doesnt shake anymore
                progress_window.get_thread_flag().wait(timeout=measurement_configuration["wait_time"])

                # cycle through the amount of measurement points with measurementcounter
                measurement_counter = 0

                # cycle through the amount of measurement points on the y axis
                for current_y_step in range(0, quantity_of_y_values):

                    # cycle through the amount of measurement points on the x axis
                    for current_x_step in range(0, quantity_of_x_values):

                        # read out x and y position
                        current_y_position = device_1.qPOS(1)[1]
                        current_x_position = device_2.qPOS(1)[1]
                        
                        # save measured value, x and y position
                        measurements[measurement_counter] = make_measurement(**measurement_configuration)
                        x_position_values[measurement_counter] = current_x_position 
                        y_position_values[measurement_counter] = current_y_position
                        
                        _logger.info('Actual Data: x-pos: {:.2f} y-pos: {:.2f} reading: {:.2f}'.format(current_x_position, current_y_position, measurements[measurement_counter]))

                        # increment meausrement counter
                        measurement_counter = measurement_counter + 1

                        # exit when thread is set to be stopped
                        if(progress_window.get_thread_flag().is_set()):

                            _logger.info('Close daisy chain connection')
                            device_2.CloseDaisyChain()
                            device_1.CloseDaisyChain()
                            return

                        # as long as not last measurement
                        if current_x_step < quantity_of_x_values:
                            
                            # this instead of using currentposition avoids error propagation
                            delta_to_start = (current_x_step + 1) * measurement_configuration["delta_x_value"]
                            next_x_position = measurement_configuration["x_start_value"] + delta_to_start

                            # move to next x measurepoint
                            device_2.MOV(1, next_x_position)
                            
                            # wait until x axis is at correct position
                            pitools.waitontarget(device_2, axes=1)

                            # timer to wait so the table doesnt shake anymore
                            progress_window.get_thread_flag().wait(timeout=measurement_configuration["wait_time"])       

                        # update progress bar in gui
                        progress = progress + step_size
                        progress_window.update_progress_bar(math.ceil(progress))

                    # as long as not last measurement
                    if current_y_step < quantity_of_y_values:
                        
                        # this instead of using currentposition avoids error propagation
                        delta_to_start = (current_y_step + 1) * measurement_configuration["delta_y_value"]
                        next_y_position = measurement_configuration["y_start_value"] + delta_to_start
        
                        # move to next y Measurepoint
                        device_1.MOV(1, next_y_position)
                        
                        # wait until y axis is at correct position
                        pitools.waitontarget(device_1, axes=1)

                    # Reset to "beginning of line" for next measurement
                    device_2.MOV(1, measurement_configuration["x_start_value"])
                    
                    # wait until y axis is at correct position
                    pitools.waitontarget(device_2, axes=1)
                    
                    # timer to wait so the table doesnt shake anymore
                    progress_window.get_thread_flag().wait(timeout=measurement_configuration["wait_time"])      

                
                _logger.info('Saving measurement run results...')

                # Save measurement results
                df = pd.DataFrame({"xpos" : x_position_values, "ypos" : y_position_values, "measure" : measurements})
                df.to_csv(f"measurement_data/Measurement_run_{i}.csv", index=False)
            
        _logger.info("Close daisy chain connection")

        # close the daisy chain connection
        device_2.CloseDaisyChain()
        device_1.CloseDaisyChain()
        
        # close progress window
        progress_window.close_progress_window_after_finish()

    except Exception as e:

        # show error message and close the program
        progress_window.show_error_message(str(e))


def make_measurement(**measurement_configuration):
    """This function performs the local measurement. If more then one measurement is taken the mean of all saved values is returned.

    Args: 
        measurement_configuration (dict): Dictonary with measurment configuration

    Returns:
        float: power value of performed measurement
    """

    # connect to measurement device
    rm = pyvisa.ResourceManager()
    measuring_device = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
    voltage_measurement_values = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)

    # make specified number of measurements
    for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
        voltage_measurement_values[i] = measuring_device.query_ascii_values("Meas?", container=np.array, )

    # calculate power value from measurements
    measured_power_value = np.mean(measurement_configuration["conversion_factor"] * voltage_measurement_values)

    return measured_power_value