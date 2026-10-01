import { CONTROL_CENTER_ACTUATORS } from "@/lib/control-center/config";

const DEFAULT_RELAY_STATE: Record<string, boolean> = {
  "aerator-main": true,
  "pump-feed": false,
  "hvac-lobby": true,
  "light-greenhouse": false,
  "deck-relay": true,
  "drone-pad-light": false,
  "amr-charger": true,
};

export function buildInitialRelayState(): Record<string, boolean> {
  const state = { ...DEFAULT_RELAY_STATE };
  for (const actuator of CONTROL_CENTER_ACTUATORS) {
    if (!(actuator.id in state)) state[actuator.id] = false;
  }
  return state;
}

export function allRelaysOff(prev: Record<string, boolean>): Record<string, boolean> {
  return Object.fromEntries(Object.keys(prev).map((k) => [k, false]));
}
