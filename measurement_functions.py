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
import time

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

    # Calculate number of x and y values
    Anzahl_Y = int((measurement_configuration["y_end_value"] - measurement_configuration["y_start_value"]) / measurement_configuration["delta_y_value"])
    Anzahl_X = int((measurement_configuration["x_end_value"] - measurement_configuration["x_start_value"]) / measurement_configuration["delta_x_value"])

    # Allocate memory space for arrays
    xpositionvalues = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)
    ypositionvalues = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)
    measurements = np.zeros(Anzahl_Y * Anzahl_X, dtype=float)

    # make calculations for progress bar step size
    stepsize = 100/(Anzahl_X*Anzahl_Y*measurement_configuration["number_of_measurement_runs"])
    progress = 0

    # create two gsc device instances for being able to control the two step motors
    with GCSDevice() as Device1, GCSDevice() as Device2:
        
        # Fist setup of the master device which is connected via pc
        Device1.OpenUSBDaisyChain(description='0017550026')
        daisychainid = Device1.dcid
        Device1.ConnectDaisyChainDevice(1, daisychainid)
        _logger.info('Connection to DaisyChain-Master established')
        
        # Secondly enable connection to the next device in daisy chain
        Device2.ConnectDaisyChainDevice(2, daisychainid)
        _logger.info('Connection to DaisyChain-Slave established')
        
        # A lot of initializing information
        _logger.info('Connected to devices with IDs')
        _logger.info('\n{}:\n{}'.format(Device1.GetInterfaceDescription(), Device1.qIDN()))
        _logger.info('\n{}:\n{}'.format(Device2.GetInterfaceDescription(), Device2.qIDN()))


        _logger.info('Initialization of axes...')

        # initialize axes
        pitools.startup(Device1, stages=STAGES, refmodes=REFMODES)
        pitools.startup(Device2, stages=STAGES, refmodes=REFMODES)

        _logger.info('Min y-axis:', Device1.qTMN())
        _logger.info('Max y-axis:', Device1.qTMX())

        _logger.info('Min x-axis 2:', Device2.qTMN())
        _logger.info('Max x-axis 2:', Device2.qTMX())


        # run the ammount of configured measuremnts
        for i in range(measurement_configuration["number_of_measurement_runs"]): 
            
            _logger.info('In {}. measurement run'.format(i))

            # reset of the y and x axis to start point
            Device1.MOV(1, measurement_configuration["y_start_value"])
            
            # wait a little, so the response is correctly received
            time.sleep(0.1)
            
            pitools.waitontarget(Device1, axes=1)

            # wait a little, so the response is correctly received
            time.sleep(0.1)

            Device2.MOV(1, measurement_configuration["x_start_value"])
            
            # wait a little, so the response is correctly received
            time.sleep(0.1)

            pitools.waitontarget(Device2, axes=1)
            
            # wait a little, so the response is correctly received
            time.sleep(0.1)

            # wait so the table doesnt shake anymore
            progress_window.get_thread_flag().wait(timeout=5)

            # cycle through the amount of measurement points with measurementcounter
            measurementcounter = 0

            for currentystep in range(0, Anzahl_Y):

                # cycle through the amount of meassurement points on the x axis
                for currentxstep in range(0, Anzahl_X):
                    
                    currentyposition = Device1.qPOS(1)[1]
                    currentxposition = Device2.qPOS(1)[1]
                    
                    # Measurement save to array
                    measurements[measurementcounter] = make_measurement(**measurement_configuration)
                    xpositionvalues[measurementcounter] = currentxposition 
                    ypositionvalues[measurementcounter] = currentyposition
                    
                    _logger.debug('Actual Data: x-pos: {:.2f} y-pos: {:.2f} reading: {:.2f}'.format(currentyposition, currentxposition, measurements[measurementcounter]))

                    measurementcounter = measurementcounter + 1

                    if(progress_window.get_thread_flag().is_set()):

                        # todo check whether that works
                        _logger.info('Close daisy chain connection')
                        Device2.CloseDaisyChain()
                        Device1.CloseDaisyChain()
                        return

                    # as long as not last measurement
                    if currentxstep < (Anzahl_X - 1 ):
                        
                        # this instead of using currentposition avoids error propagation
                        theoreticalposition = (currentxstep + 1) * measurement_configuration["delta_x_value"] 
                        nextxposition = theoreticalposition + measurement_configuration["delta_x_value"]

                        # Move to next X Meassurepoint
                        Device2.MOV(1, nextxposition)
                        
                        # wait a little, so the response is correctly received
                        time.sleep(0.1)
                        
                        pitools.waitontarget(Device2, axes=1)
                        
                        # wait a little, so the response is correctly received
                        time.sleep(0.1)

                        # timer to wait so the table doesnt shake anymore
                        progress_window.get_thread_flag().wait(timeout=5)       

                    # update progress bar in gui
                    progress = progress + stepsize
                    progress_window.update_progress_bar(math.ceil(progress))

                # as long as not last measurement
                if currentystep < (Anzahl_Y - 1 ):
                    
                    # this instead of using currentposition avoids error propagation
                    theoreticalposition = (currentystep + 1) * measurement_configuration["delta_y_value"] 
                    nextyposition = theoreticalposition + measurement_configuration["delta_y_value"]

                    # Move to next Y Meassurepoint
                    Device1.MOV(1, nextyposition)
                    
                    # wait a little, so the response is correctly received
                    time.sleep(0.1)
                    
                    pitools.waitontarget(Device1, axes=1)
                    
                    # wait a little, so the response is correctly received
                    time.sleep(0.1)

                # Reset to "beginning of line" for next measurement
                Device2.MOV(1, measurement_configuration["x_start_value"])
                
                # wait a little, so the response is correctly received
                time.sleep(0.1)
                
                pitools.waitontarget(Device2, axes=1)
                
                # wait a little, so the response is correctly received
                time.sleep(0.1)

            
            _logger.info('Saving measurement run results...')

            # Save measurement results
            df = pd.DataFrame({"xpos" : xpositionvalues, "ypos" : ypositionvalues, "measure" : measurements})
            df.to_csv(f"Measurement_run_{i}.csv", index=False)
        
        _logger.info("Close daisy chain connection")

        # close the daisy chain connection
        Device2.CloseDaisyChain()
        Device1.CloseDaisyChain()
        
        # close progress window
        progress_window.close_progress_window_after_finish()

def make_measurement(**measurement_configuration):
    """This function performs the local measurement. If more then one measurement is taken the mean of all saved values is returned.

    Args: 
        measurement_configuration (dict): Dictonary with measurment configuration

    Returns:
        float: power value of performed measurement
    """

    # connect to measurement device
    rm = pyvisa.ResourceManager()
    Messinstrument = rm.open_resource('TCPIP0::141.47.75.77::inst0::INSTR')
    Spannungsmeasurements = np.zeros(measurement_configuration["number_of_measurements_in_one_position"], dtype=float)

    # make specified number of measurements
    for i in range(measurement_configuration["number_of_measurements_in_one_position"]):
        Spannungsmeasurements[i] = Messinstrument.query_ascii_values("Meas?", container=np.array, )

    # calculate mean value from measurements
    Leistungsmesswert = np.mean(measurement_configuration["conversion_factor"] * Spannungsmeasurements)

    return Leistungsmesswert