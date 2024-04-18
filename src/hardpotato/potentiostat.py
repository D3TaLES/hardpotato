import os
import numpy as np
import matplotlib.pyplot as plt
import softpotato as sp

import hardpotato.palmsens.serial as pico_serial
import hardpotato.palmsens.mscript as pico_mscript
import hardpotato.palmsens.instrument as pico_instrument
from hardpotato import chi, load_data, save_data, emstatpico

# Potentiostat models available: 
AVAILABLE_MODELS = ['chi1205b', 'chi1242b', 'chi601e', 'chi620e', 'chi760e', 'emstatpico']
BIPOT_TECHNIQUES = ['CV', 'CA', 'IT', 'LSV', 'NPV']


class Test:
    """
    Class for testing
    """

    def __init__(self):
        print('Test from potentiostat module')


class Info:
    """
    Class for storing information about potentiostat and technique in use
    """

    def __init__(self, model: str):
        self.model = model
        if "chi" in self.model:
            self.info = chi.ChiInfo(model=model)
        elif self.model == 'emstatpico':
            self.info = emstatpico.PicoInfo()
        else:
            print('Potentiostat model ' + model + ' not available in the library.')
            print('Available models:', AVAILABLE_MODELS)

    def specifications(self):
        self.info.specifications()


class SetupInstrument:
    """
    Class for setting up potentiostat and filing system
    """

    def __init__(self, model: str = None, path: str = '.', folder: str = '.', port: str = None, verbose: int = 1):
        self.folder = folder
        self.model_pstat = model
        self.path_lib = path
        self.port_ = port
        if verbose:
            self.info()

    def info(self):
        print('\n----------')
        print('Potentiostat model: ' + self.model_pstat)
        print('Potentiostat path: ' + self.path_lib)
        print('Save folder: ' + self.folder)
        print('----------\n')


class Technique:
    """
    Base class for operating chosen potentiostat technique
    """

    def __init__(self, instrument: SetupInstrument, text: str = '', fileName: str = 'CV'):
        self.model_pstat = instrument.model_pstat
        self.path_lib = instrument.path_lib
        self.port = instrument.port_

        self.folder = instrument.folder
        self.fileName = fileName
        self.text = text  # text to write as macro
        self.header = ""

        self.technique = 'Technique'
        self.bpot = False
        self.tech = None
        self.data = []

    def writeToFile(self):
        if self.model_pstat[0:3] == 'chi':
            file = open(self.folder + '/' + self.fileName + '.mcr', 'wb')
            file.write(self.text.encode('ascii'))
            file.close()
        elif self.model_pstat == 'emstatpico':
            file = open(self.folder + '/' + self.fileName + '.mscr', 'wb')
            file.write(self.text.encode('ascii'))
            file.close()

    def run(self):
        if self.model_pstat[0:3] == 'chi':
            self.message()
            # Write macro:
            self.writeToFile()
            # Run command:
            param = ' /runmacro:\"{}\"'.format(os.path.join(self.folder, self.fileName + '.mcr'))
            os.system(self.path_lib + param)
            self.message(start=False)
            self.plot()
        elif self.model_pstat == 'emstatpico':
            self.message()
            self.writeToFile()
            if self.port is None:
                self.port = pico_serial.auto_detect_port()
            with pico_serial.Serial(self.port, 1) as comm:
                dev = pico_instrument.Instrument(comm)
                dev.send_script(os.path.join(self.folder, self.fileName + '.mscr'))
                result = dev.readlines_until_end()
            self.data = pico_mscript.parse_result_lines(result)
            fileName = os.path.join(self.folder, self.fileName + '.txt')
            save_data.Save(self.data, fileName, self.header, self.model_pstat,
                           self.technique, bpot=self.bpot)
            self.message(start=False)
            self.plot()
        else:
            print('\nNo potentiostat selected. Aborting.')

    def plot(self):
        figNum = np.random.randint(100)  # To prevent rewriting the same plot
        if self.technique == 'CV':
            cv = load_data.CV(self.fileName + '.txt', self.folder, self.model_pstat)
            sp.plotting.plot(cv.E, cv.i, show=False, fig=figNum,
                             fileName=self.folder + '/' + self.fileName)
        elif self.technique == 'LSV':
            lsv = load_data.LSV(self.fileName + '.txt', self.folder, self.model_pstat)
            sp.plotting.plot(lsv.E, lsv.i, show=False, fig=figNum,
                             fileName=self.folder + '/' + self.fileName)
        elif self.technique == 'IT':
            ca = load_data.IT(self.fileName + '.txt', self.folder, self.model_pstat)
            sp.plotting.plot(ca.t, ca.i, show=False, fig=figNum,
                             xlab='$t$ / s', ylab='$i$ / A',
                             fileName=self.folder + '/' + self.fileName)
        elif self.technique == 'OCP':
            ocp = load_data.OCP(self.fileName + '.txt', self.folder, self.model_pstat)
            sp.plotting.plot(ocp.t, ocp.E, show=False, fig=figNum,
                             xlab='$t$ / s', ylab='$E$ / V',
                             fileName=self.folder + '/' + self.fileName)
        plt.close()

    def message(self, start=True):
        if start:
            print('----------\nStarting ' + self.technique)
            if self.bpot:
                print('Running in bipotentiostat mode')
        else:
            print(self.technique + ' finished\n----------\n')

    def bipot(self, E=-0.2, sens=1e-6):
        if self.technique in BIPOT_TECHNIQUES:
            self.tech.bipot(E, sens)
            self.text = self.tech.text
            self.bpot = True
        else:
            print(self.technique + ' does not have bipotentiostat mode')


class CV(Technique):
    """
    Class for running CV Technique
    """

    def __init__(self, instrument: SetupInstrument, Eini: float = -0.2, Ev1: float = 0.2, Ev2: float = -0.2,
                 Efin: float = -0.2, sr: float = 0.1, dE: float = 0.001, nSweeps: float = 2, sens: float = 1e-6,
                 fileName: str = 'CV', header: str = 'CV', **kwargs):
        self.header = header
        self.technique = 'CV'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiCV(Eini=Eini, Ev1=Ev1, Ev2=Ev2, Efin=Efin, sr=sr, dE=dE, nSweeps=nSweeps, sens=sens,
                                  fileName=fileName, header=header, folder=self.folder, model=self.model_pstat,
                                  **kwargs)
        elif self.model_pstat == 'emstatpico':
            self.tech = emstatpico.CV(Eini=Eini, Ev1=Ev1, Ev2=Ev2, Efin=Efin, sr=sr, dE=dE, nSweeps=nSweeps, sens=sens,
                                      folder=self.folder, fileName=fileName, header=header, path_lib='',
                                      **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have CV.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class LSV(Technique):
    """
    Class for running LSV Technique
    """

    def __init__(self, instrument: SetupInstrument, Eini: float = -0.2, Efin: float = 0.2, sr: float = 0.1,
                 dE: float = 0.001, sens: float = 1e-6, fileName: str = 'LSV', header: str = 'LSV', **kwargs):
        self.header = header
        self.technique = 'LSV'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiLSV(Eini=Eini, Efin=Efin, sr=sr, dE=dE, sens=sens, folder=self.folder,
                                   fileName=fileName, model=self.model_pstat, **kwargs)
        elif self.model_pstat == 'emstatpico':
            self.tech = emstatpico.LSV(Eini=Eini, Efin=Efin, sr=sr, dE=dE, sens=sens, folder=self.folder,
                                       fileName=fileName, header=header, **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have LSV.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class IT(Technique):
    """
    Class for running IT Technique
    """

    def __init__(self, instrument: SetupInstrument, Estep: float = 0.2, dt: float = 0.001, ttot: float = 2, sens=1e-6,
                 fileName: str = 'IT', header: str = 'IT', **kwargs):
        self.header = header
        self.technique = 'IT'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiIT(Estep, dt, ttot, sens, fileName=fileName, model=self.model_pstat,
                                  folder=self.folder, **kwargs)
        elif self.model_pstat == 'emstatpico':
            self.tech = emstatpico.IT(Estep=Estep, dt=dt, ttot=ttot, sens=sens, folder=self.folder,
                                      fileName=fileName, header=header, **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have IT.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class CA(Technique):
    """
    Class for running CA experiment to determine conductivity
    """

    def __init__(self, instrument: SetupInstrument, Eini: float = -0.025, Ev1: float = 0.025, Ev2: float = -0.025,
                 dE: float = 1e-6, nSweeps: int = 200, pw: float = 1e-4, sens: float = 1e-4,
                 fileName: str = 'CA', header: str = 'CA', **kwargs):
        self.header = header
        self.technique = 'CA'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiCA(Eini=Eini, Ev1=Ev1, Ev2=Ev2, dE=dE, nSweeps=nSweeps, pw=pw, sens=sens,
                                  header=header, fileName=fileName, model=self.model_pstat, folder=self.folder,
                                  **kwargs)
        # elif self.model_pstat == 'emstatpico':
        #     self.tech = emstatpico.CA(Estep, dt, ttot, sens, self.folder_save, fileName, header, **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have IT.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class OCP(Technique):
    """
    Class for running OCP Technique
    """

    def __init__(self, instrument: SetupInstrument, ttot: float = 2, dt: float = 0.01,
                 fileName: str = 'OCP', header: str = 'OCP', **kwargs):
        self.header = header
        self.technique = 'OCP'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiOCP(ttot=ttot, dt=dt, header=header, fileName=fileName, folder=self.folder,
                                   model=self.model_pstat, **kwargs)
        elif self.model_pstat == 'emstatpico':
            self.tech = emstatpico.OCP(ttot=ttot, dt=dt, folder=self.folder, fileName=fileName, header=header, **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have OCP.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class NPV(Technique):
    """
    Class for running NPV Technique
    """

    def __init__(self, instrument: SetupInstrument, Eini: float = 0.5, Efin: float = -0.5, dE: float = 0.01,
                 tsample: float = 0.1, twidth: float = 0.05, tperiod: float = 10, sens: float = 1e-6,
                 fileName: str = 'NPV', header: str = 'NPV performed with CHI760', **kwargs):
        self.technique = 'NPV'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiNPV(Eini=Eini, Efin=Efin, dE=dE, tsample=tsample, twidth=twidth, tperiod=tperiod,
                                   sens=sens, header=header, fileName=fileName, model=self.model_pstat,
                                   folder=self.folder, **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have NPV.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)


class EIS(Technique):
    """
    Class for running ESI Technique for determining solution resistance
    """

    def __init__(self, instrument: SetupInstrument, Eini: float = 0, low_freq: float = 1, high_freq: float = 1000,
                 amplitude: float = 0.01, sens: float = 1e-6, fileName: str = 'EIS', header: str = 'EIS', **kwargs):
        self.header = header
        self.technique = 'EIS'
        if "chi" in self.model_pstat:
            self.tech = chi.ChiEIS(Eini=Eini, low_freq=low_freq, high_freq=high_freq, amplitude=amplitude, sens=sens,
                                   header=header, fileName=fileName, model=self.model_pstat, folder=self.folder,
                                   **kwargs)
        else:
            raise Exception('Potentiostat model ' + self.model_pstat + ' does not have EIS.')
        Technique.__init__(self, instrument, text=self.tech.text, fileName=fileName)
