// One of each port, side by side on an 18 mm panel: a blank std pin, a probe port with its flex
// collet for a pH probe, and a thermocouple port carrying a 1/8 NPT mount. Each is drawn in the
// port's own datum, z = 0 at the panel's outer face, +z outward.

include <../custom/bayonet_interfaces.scad>
include <../purchased/atlas_probes.scad>
include <../utils/npt_threads.scad>
use <../custom/bayonet_port.scad>

panel = 18;

bayonet_port(type=bayonet_std, part="pin", panel_thickness=panel, text_labels=true, label="BLANK");
translate([40, 0, 0]) bayonet_probe_port(type=bayonet_std, probe=ph_lab_g2, panel_thickness=panel);
translate([80, 0, 0]) bayonet_thermocouple_port(type=bayonet_std, panel_thickness=panel, thread=npt_1_8);
