from logs.logger import log

class FrameLayout:
    def __init__(self, func_name, saved_ra_offset=None, saved_fp_offset=None, frame_size=0):
        self.func_name = func_name

        # tamaño total del frame (en bytes)
        self.frame_size = frame_size

        # tablas de offsets
        self.param_offsets = {}
        self.local_offsets = {}
        self.temp_offsets = {}
        self.saved_reg_offsets = {}

        # offsets relativos a $sp al inicio del frame
        self.saved_ra_offset = saved_ra_offset
        self.saved_fp_offset = saved_fp_offset

        # si quieres mantener compatibilidad con nombres antiguos:
        self.return_addr_offset = saved_ra_offset
        self.old_fp_offset = saved_fp_offset


class ActivationRecordBuilder:
    def __init__(self, machine_desc, scope_manager):
        self.machine_desc = machine_desc
        self.scope_manager = scope_manager

    def buildForFunction(self, func_symbol):
        # por ahora no calculamos locales, solo el espacio mínimo:
        #  - 4 bytes para $fp guardado
        #  - 4 bytes para $ra guardado
        func_name = getattr(func_symbol, "name", str(func_symbol))

        local_size = 0
        saved_fp_offset = 0
        saved_ra_offset = 4
        frame_size = local_size + 8

        layout = FrameLayout(
            func_name=func_name,
            saved_ra_offset=saved_ra_offset,
            saved_fp_offset=saved_fp_offset,
            frame_size=frame_size,
        )
        log(f"[cg] frame layout for {func_name}: frame_size={frame_size}, "
            f"saved_ra_offset={saved_ra_offset}, saved_fp_offset={saved_fp_offset}",
            channel="cg")
        return layout
