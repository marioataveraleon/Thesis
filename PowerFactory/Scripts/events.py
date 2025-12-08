
import powerfactory



def _get_events_folder(study_case):
    evt_folders = study_case.GetContents('IntEvt')
    if not evt_folders:
        raise Exception("This study case does not have an 'IntEvt' (Simulation Events/Fault) folder.")
    return evt_folders[0]

def create_3ph_fault(app, study_case, element,
                     t_start: float, t_clear: float,
                     r_fault: float = 0.0, x_fault: float = 0.0):
    """
    Create a 3 phase short circuit in an "element" contained in a studycase
    element: normalmente un ElmTerm (bus) pero podría ser otro objeto válido.
    t_start: tiempo de inicio de la falta [s]
    t_clear: tiempo de despeje [s]
    r_fault, x_fault: impedancia de la falta [ohm]
    """

    # 1) Obtener la carpeta de eventos (IntEvt) del study case
    evt_folders = study_case.GetContents('IntEvt')
    if not evt_folders:
        raise Exception("Este study case no tiene carpeta 'IntEvt'.")
    evt_folder = evt_folders[0]

    # 2) Crear un nuevo objeto de evento de tipo Short-Circuit (EvtShc)
    fault_event = evt_folder.CreateObject('EvtShc', 'auto_3ph_fault')

    # 3) Asignar el objetivo de la falta (el elemento pasado a la función)
    fault_event.p_target = element

    # 4) Tiempos de inicio y despeje
    fault_event.time = t_start
    fault_event.t_clear = t_clear

    # 5) Impedancia de la falta
    fault_event.R_f = r_fault
    fault_event.X_f = x_fault

    # (Opcional: si tu versión de PF tiene un campo para tipo de falta, revísalo
    # en la GUI y podríamos configurarlo aquí también.)

    # 6) Devolvemos el evento por si lo quieres usar después
    return fault_event
def create_load_step(app, study_case, load,
                     t_start: float,
                     dP_MW: float = 0.0,
                     dQ_MVAr: float = 0.0):
    """
    Create a load step event (Load Step) on a given load object.

    Parameters
    ----------
    app : powerfactory.Application
        PowerFactory application object (not heavily used here, but kept for consistency).
    study_case : IntCase
        Study case where the event will be created.
    load : ElmLod / ElmLodlv / similar
        Load object where the step is applied.
    t_start : float
        Time instant [s] when the step is applied.
    dP_MW : float, default 0.0
        Increment in active power [MW]. Positive = increase load.
    dQ_MVAr : float, default 0.0
        Increment in reactive power [MVAr]. Positive = increase reactive load.

    Returns
    -------
    load_event : EvtLod
        The created load event object.
    """

    # 1) Get the Events folder of this study case
    evt_folder = _get_events_folder(study_case)

    # 2) Create a new Load Event (EvtLod) under that folder
    #    'auto_load_step' is just a name; you can change it if you prefer.
    load_event = evt_folder.CreateObject('EvtLod', 'auto_load_step')

    # 3) Set the target of the event: the load you pass to the function
    load_event.p_target = load

    # 4) Set the time at which the step occurs
    load_event.time = t_start

    # 5) Set the size of the step
    #    NOTE: Check in the GUI that these attributes are indeed 'dP' and 'dQ'
    #    and confirm their units. In most RMS cases they're in MW/MVAr.
    load_event.dP = dP_MW
    load_event.dQ = dQ_MVAr

    return load_event

def create_loss_of_generation(app, study_case, generator,
                              t_start: float,
                              remaining_factor: float = 0.0,
                              event_name: str = "auto_loss_gen"):
    """
    Create a Loss of Generation event on a given generator/inverter.

    Parameters
    ----------
    app : powerfactory.Application
        PowerFactory application object (used only for logging here).
    study_case : IntCase
        Study case where the event will be created.
    generator :
        Generator / inverter object (ElmSym, ElmInfeeder, etc.) whose
        active power will be reduced.
    t_start : float
        Time instant [s] when the loss of generation occurs.
    remaining_factor : float, default 0.0
        Fraction of active power remaining after the event:
        0.0 = full trip, 0.5 = 50% remaining, 1.0 = no change.
    event_name : str, default "auto_loss_gen"
        Name of the event object created in PowerFactory.

    Returns
    -------
    loss_event :
        The created loss-of-generation event object (EvtGen or similar).
    """

    # 1) Get the Events folder of this study case
    evt_folder = _get_events_folder(study_case)

    # 2) Create a new generator event.
    #    In many PF versions the class name is 'EvtGen' for generator events.
    #    If in your GUI the class name is slightly different, just change 'EvtGen'.
    loss_event = evt_folder.CreateObject('EvtGen', event_name)

    # 3) Set the target: which generator/inverter is affected
    loss_event.p_target = generator

    # 4) Time of the event
    loss_event.time = t_start

    # 5) Set remaining power factor (0..1).
    #    The field name can vary slightly between PF versions,
    #    so we try a couple of common options.
    if hasattr(loss_event, "fact"):
        loss_event.fact = remaining_factor
    elif hasattr(loss_event, "pfact"):
        loss_event.pfact = remaining_factor
    else:
        app.PrintPlain(
            "[WARN] Loss-of-generation event has no attribute 'fact' or 'pfact'. "
            "Check in the GUI which attribute represents the remaining power factor "
            "and adapt this function accordingly."
        )

    return loss_event

def create_phase_jump(app, study_case, element,
                      t_start: float,
                      dphi_deg: float,
                      event_name: str = "auto_phase_jump"):
    """
    Create a phase-angle jump event on a given element (typically a bus).

    Parameters
    ----------
    app : powerfactory.Application
        PowerFactory application object (used for logging).
    study_case : IntCase
        Study case where the event will be created.
    element :
        Target element where the phase jump is applied, typically an ElmTerm bus
        (e.g. infinite bus in a SMIB).
    t_start : float
        Time instant [s] when the phase jump occurs.
    dphi_deg : float
        Phase-angle jump in degrees. Positive = increase angle, negative = decrease.
    event_name : str, default "auto_phase_jump"
        Name of the event object created in PowerFactory.

    Returns
    -------
    phase_event :
        The created phase-jump event object (EvtAng or similar).
    """

    # 1) Get the Events folder of this study case
    evt_folder = _get_events_folder(study_case)

    # 2) Create a new phase-angle event.
    #    In many PF versions the class name is 'EvtAng' for angle / phase jump events.
    phase_event = evt_folder.CreateObject('EvtAng', event_name)

    # 3) Set the target element (bus or other voltage reference)
    phase_event.p_target = element

    # 4) Set the time of the jump
    phase_event.time = t_start

    # 5) Set the angle step.
    #    Common attribute name is 'dph' (delta phi) in degrees.
    if hasattr(phase_event, "dph"):
        phase_event.dph = dphi_deg
    elif hasattr(phase_event, "phi"):
        # some versions may use 'phi' or similar
        phase_event.phi = dphi_deg
    else:
        app.PrintPlain(
            "[WARN] Phase-jump event has no attribute 'dph' or 'phi'. "
            "Check in the GUI which field corresponds to the angle step "
            "and adjust this function accordingly."
        )

    return phase_event

