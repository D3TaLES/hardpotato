class Test:
    '''
    '''
    def __init__(self):
        print('Test from Emstat Pico translator')


class Info:
    '''
        Pending:
        * Calculate dE, sr, dt, ttot, mins and max
    '''
    def __init__(self):
        self.tech = ['CV', 'CA', 'LSV', 'OCP']

        self.E_min = -1.7
        self.E_max = 2
        #self.sr_min = 0.000001
        #self.sr_max = 10
        #self.dE_min = 
        #self.sr_min = 
        #self.dt_min = 
        #self.dt_max = 
        #self.ttot_min = 
        #self.ttot_max = 

    def limits(self, val, low, high, label, units):
        if val < low or val > high:
            raise Exception(label + ' should be between ' + str(low) + ' ' +\
                            units  + ' and ' + str(high) + ' ' + units +\
                            '. Received ' + str(val) + ' ' + units)

    def techniques(self):
        print('Model: PalmSens Emstat Pico (emstatpico)')
        print('Techiques available:', self.tech)

    def specifications(self):
        print('Specifications list')




class CV:
    '''
    '''
    def __init__(self, Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens,
                 folder, fileName, header, path_lib=None, qt=2, resistance=0):
        '''
            Potential based variables need to be changed to mV int(Eini*100).
            For some reason Pico does not accept not having prefix 
        '''
        self.Eini = int(Eini*1000)
        self.Ev1 = int(Ev1*1000)
        self.Ev2 = int(Ev2*1000)
        self.Efin = int(Efin*1000)
        self.sr = int(sr*1000)
        self.dE = int(dE*1000)
        self.nSweeps = nSweeps
        self.text = ''

        self.validate(Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens)


        self.ini = 'e\nvar c\nvar p\nvar a\n'
        self.pre_body = 'set_pgstat_mode 4\nset_autoranging ba 100n 5m' +\
                        '\nset_e '+ str(self.Eini) + 'm\ncell_on\nwait 2\ntimer_start'
        self.body = '\nmeas_loop_cv p c ' + str(self.Eini) + 'm ' +\
                    str(self.Ev1) + 'm ' +\
                    str(self.Ev2) + 'm ' + str(self.dE) + 'm ' + str(self.sr) +\
                    'm nscans(' + str(self.nSweeps-1) + ')\n\tpck_start\n\ttimer_get a' +\
                    '\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_end\nendloop\n' + \
                    'on_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body

     def validate(self, Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens):
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, 'Eini', 'V')
        info.limits(Ev1, info.E_min, info.E_max, 'Ev1', 'V')
        info.limits(Ev2, info.E_min, info.E_max, 'Ev2', 'V')
        info.limits(Efin, info.E_min, info.E_max, 'Efin', 'V')
        #info.limits(sr, info.sr_min, info.sr_max, 'sr', 'V/s')
        #info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        #info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print('All the parameters are valid')

    def bipot(self, E, sens):
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, 'E2', 'V')
        #info.limits(sens2, info.sens_min, info.sens_max, 'sens', 'A/V')

        E = int(E*1000)
        self.pre_body = 'var b\nset_pgstat_chan 1' +\
                        '\nset_pgstat_mode 5' +\
                        '\nset_poly_we_mode 0' +\
                        '\nset_e '+ str(E) + 'm\nset_autoranging ba 100n 5m' +\
                        '\nset_pgstat_chan 0\nset_pgstat_mode 2' +\
                        '\nset_autoranging ba 100n 5m\nset_e ' + str(self.Eini) +\
                        'm\ntimer_start\ncell_on'
        self.body = '\nmeas_loop_cv p c ' + str(self.Eini) + 'm ' +\
                    str(self.Ev1) + 'm ' +\
                    str(self.Ev2) + 'm ' + str(self.dE) + 'm ' + str(self.sr) +\
                    'm nscans(' + str(self.nSweeps) + ') poly_we(1 b)\n\t' +\
                    'pck_start\n\ttimer_get a' +\
                    '\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t' +\
                    'pck_end\nendloop\non_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body
        #print(self.text)

        


class CA:
    '''
    '''
    def __init__(self, Estep, dt, ttot, sens, folder, fileName, header,
                 path_lib=None, qt=2):
        '''
        '''
        self.Estep = int(Estep*1000)
        self.dt = int(dt*1000)
        self.ttot = int(ttot*1000)
        self.text = ''

        self.validate(Estep, dt, ttot, sens)

        self.ini = 'e\nvar p\nvar c\nvar a\n'
        self.pre_body = 'set_pgstat_mode 3\nset_autoranging ba 100n 5m' +\
                        '\nset_e ' + str(self.Estep) + 'm\ncell_on\ntimer_start'
        self.body = '\nmeas_loop_ca p c ' + str(self.Estep) + 'm ' + str(self.dt) +\
                    'm ' + str(self.ttot) + 'm\n\tpck_start\n\ttimer_get a\n\t' +\
                    'pck_add a\n\t' +\
                    'pck_add p\n\tpck_add c\n\tpck_end\n\tendloop' +\
                    '\non_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body

    def validate(self, Estep, dt, ttot, sens):
        info = Info()
        info.limits(Estep, info.E_min, info.E_max, 'Estep', 'V')
        #info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        #info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        #info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print('All the parameters are valid')


    def bipot(self, E, sens):
        # Validate bipot:
        info = Info()
        info.limits(E, info.E_min, info.E_max, 'E2', 'V')
        #info.limits(sens2, info.sens_min, info.sens_max, 'sens2', 'A/V')

        E = int(E*1000)
        self.pre_body = 'var b\nset_pgstat_chan 1' +\
                        '\nset_pgstat_mode 5' +\
                        '\nset_poly_we_mode 0' +\
                        '\nset_e '+ str(E) + 'm\nset_autoranging ba 100n 5m' +\
                        '\nset_pgstat_chan 0\nset_pgstat_mode 2' +\
                        '\nset_autoranging ba 100n 5m\nset_e ' + str(self.Estep) +\
                        'm\ntimer_start\ncell_on'
        self.body = '\nmeas_loop_ca p c ' + str(self.Estep) + 'm ' +\
                    str(self.dt) + 'm ' +\
                    str(self.ttot) + 'm poly_we(1 b)\n\t' +\
                    'pck_start\n\ttimer_get a' +\
                    '\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t' +\
                    'pck_end\nendloop\non_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body

        pass


class LSV:
    '''
    '''
    def __init__(self, Eini, Efin, sr, dE, sens, folder, fileName, header, 
                 path_lib=None, qt=2):
        self.Eini = int(Eini*1000)
        self.Efin = int(Efin*1000)
        self.sr = int(sr*1000)
        self.dE = int(dE*1000)
        self.text = ''

        self.validate(Eini, Efin, sr, dE, sens)

        self.ini = 'e\nvar c\nvar p\nvar a\n'
        self.pre_body = 'set_pgstat_mode 4\nset_autoranging ba 100n 5m' +\
                        '\nset_e '+ str(self.Eini) + 'm\ncell_on\ntimer_start'
        self.body = '\nmeas_loop_lsv p c ' + str(self.Eini) + 'm ' + str(self.Efin) + 'm ' +\
                    str(self.dE) + 'm ' + str(self.sr) +\
                    'm\n\tpck_start\n\ttimer_get a' +\
                    '\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_end\nendloop\n' + \
                    'on_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body

    def bipot(self, E, sens):
        # Validate bipot:
        info.limits(E, info.E_min, info.E_max, 'E2', 'V')
        #info.limits(sens2, info.sens_min, info.sens_max, 'sens', 'A/V')

        E = int(E*1000)
        self.pre_body = 'var b\nset_pgstat_chan 1' +\
                        '\nset_pgstat_mode 5' +\
                        '\nset_poly_we_mode 0' +\
                        '\nset_e '+ str(E) + 'm\nset_autoranging ba 100n 5m' +\
                        '\nset_pgstat_chan 0\nset_pgstat_mode 2' +\
                        '\nset_autoranging ba 100n 5m\nset_e ' + str(self.Eini) +\
                        'm\ntimer_start\ncell_on'
        self.body = '\nmeas_loop_lsv p c ' + str(self.Eini) + 'm ' +\
                    str(self.Efin) + 'm ' +\
                    str(self.dE) + 'm ' + str(self.sr) +\
                    'm poly_we(1 b)\n\t' +\
                    'pck_start\n\ttimer_get a' +\
                    '\n\tpck_add a\n\tpck_add p\n\tpck_add c\n\tpck_add b\n\t' +\
                    'pck_end\nendloop\non_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body
        #print(self.text)

    def validate(self, Eini, Efin, sr, dE, sens):
        info = Info()
        info.limits(Eini, info.E_min, info.E_max, 'Eini', 'V')
        info.limits(Efin, info.E_min, info.E_max, 'Efin', 'V')
        #info.limits(sr, info.sr_min, info.sr_max, 'sr', 'V/s')
        #info.limits(dE, info.dE_min, info.dE_max, 'dE', 'V')
        #info.limits(sens, info.sens_min, info.sens_max, 'sens', 'A/V')
        print('All the parameters are valid')



class OCP:
    '''
    '''
    def __init__(self, ttot, dt, folder, fileName, header, path_lib=None):
        dt = int(dt*1000)
        ttot = int(ttot*1000)
        self.text = ''

        self.validate(ttot, dt)

        self.ini = 'e\nvar p\nvar a\n'
        self.pre_body = 'set_pgstat_mode 4\ncell_off\ntimer_start\n'
        self.body = 'meas_loop_ocp p ' + str(dt) + 'm ' + str(ttot) + 'm '+\
                    '\n\tpck_start\n\ttimer_get a\n\tpck_add a\n\tpck_add p' +\
                    '\n\tpck_end\nendloop\non_finished:\ncell_off\n\n'
        self.text = self.ini + self.pre_body + self.body
        
    def validate(self, ttot, dt):
        info = Info()
        #info.limits(dt, info.dt_min, info.dt_max, 'dt', 's')
        #info.limits(ttot, info.ttot_min, info.ttot_max, 'ttot', 's')
        print('All the parameters are valid')

