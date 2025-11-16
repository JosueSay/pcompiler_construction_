from logs.logger import log

class FrameLayout:
    def __init__(self, func_name, saved_ra_offset=None, saved_fp_offset=None, frame_size=0):
        self.func_name = func_name

        # tamaño total del frame (en bytes)
        self.frame_size = frame_size

        # tablas de offsets (relativos a $fp una vez hecho el prólogo)
        self.param_offsets = {}    # nombre_param -> offset
        self.local_offsets = {}    # nombre_local -> offset
        self.temp_offsets = {}     # nombre_temp -> offset
        self.saved_reg_offsets = {}  # reg -> offset

        # offsets relativos a $sp al inicio del frame
        self.saved_ra_offset = saved_ra_offset
        self.saved_fp_offset = saved_fp_offset


class ActivationRecordBuilder:
    def __init__(self, machine_desc, scope_manager):
        self.machine_desc = machine_desc
        self.scope_manager = scope_manager

    def buildForFunction(self, func_symbol):
        """
        De momento: frame mínimo
          - 4 bytes para $fp guardado
          - 4 bytes para $ra guardado
        """
        func_name = getattr(func_symbol, "name", str(func_symbol))

        local_size = 0
        saved_fp_offset = 0       # fp[0] = old $fp
        saved_ra_offset = 4       # fp[4] = $ra
        frame_size = local_size + 16  # reservar 16 bytes mínimos


        layout = FrameLayout(
            func_name=func_name,
            saved_ra_offset=saved_ra_offset,
            saved_fp_offset=saved_fp_offset,
            frame_size=frame_size,
        )

        log(
            f"[cg] frame layout for {func_name}: "
            f"frame_size={frame_size}, saved_ra_offset={saved_ra_offset}, "
            f"saved_fp_offset={saved_fp_offset}",
            channel="cg"
        )
        return layout