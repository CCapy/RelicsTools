const PROCESS_NAME = "%s";
const AOB_PATTERN = "41 8B 44 80 18";

function hexToPattern(hexStr) {
    return hexStr.replace(/ /g, '');
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

        Memory.scan(m.base, m.size, hexToPattern(AOB_PATTERN), {
            onMatch: function (address, size) {
                console.log("HOOK已经写入: " + address.toString(16));
                Interceptor.attach(address, {
                    onEnter: function (args) {
                        var rdx = this.context.rdx.toInt32();
                        var r8 = this.context.r8;

                        if (rdx === 0) {
                            try {
                                var offsets = [0x18, 0x40, 0x1C, 0x44, 0x20, 0x48];
                                var raw_entries = [];
                                for (var i = 0; i < offsets.length; i++) {
                                    raw_entries.push(r8.add(offsets[i]).readU32());
                                }
                                send({ "ptr": r8.toString(16), "raw_entries": raw_entries });
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