const PROCESS_NAME = "%s";
const AOB_PATTERN = "41 8B 44 80 18";

function hexToPattern(hexStr) {
    return hexStr.replace(/ /g, '');
}

function val(v) {
    return v == 0xFFFFFFFF ? null : v;
}

rpc.exports = {
    init: function () {
        var m = Process.enumerateModules()[0];
        var modules = Process.enumerateModules();
        for (var i = 0; i < modules.length; i++) {
            if (modules[i].name.toLowerCase() === PROCESS_NAME.toLowerCase()) {
                m = modules[i];
                break;
            }
        }
        var last_r8 = null;

        Memory.scan(m.base, m.size, hexToPattern(AOB_PATTERN), {
            onMatch: function (address, size) {
                console.log("[HOOK]已经写入: " + address.toString(16));
                Interceptor.attach(address, {
                    onEnter: function (args) {
                        if (this.context.rdx.toInt32() === 0) {
                            let r8 = this.context.r8.toString();
                            if (r8 === last_r8) {
                                return;
                            }
                            last_r8 = r8;
                            try {
                                let buff_offsets = [0x18, 0x1C, 0x20];
                                let debuff_offsets = [0x40, 0x44, 0x48];
                                let buff = [];
                                let debuff = [];
                                for (var i = 0; i < debuff_offsets.length; i++) {
                                    let buff_val = val(this.context.r8.add(buff_offsets[i]).readU32());
                                    if (buff_val !== null) {
                                        buff.push(buff_val);
                                    }
                                    let debuff_val = val(this.context.r8.add(debuff_offsets[i]).readU32());
                                    if (debuff_val !== null) {
                                        debuff.push(debuff_val);
                                    }
                                }
                                send({ "buff": buff, "debuff": debuff });
                            } catch (e) { }
                        }
                    }
                });
                return "stop";
            },
            onComplete: function () { }
        });
    }
};