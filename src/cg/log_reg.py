from logs.logger import log

def dump_reg_desc(reg_desc):
    estado = {
        reg: sorted(list(vals))
        for reg, vals in reg_desc.reg_contents.items()
    }
    log(f"[REG_DESC] {estado}", channel="regalloc")

def dump_addr_desc(addr_desc):
    log(f"[ADDR_DESC] {addr_desc.locations}", channel="regalloc")

