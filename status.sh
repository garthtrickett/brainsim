#!/bin/bash
# What is running / done / queued in the brainsim experiment chain.
cd /tmp/brainsim || exit 1
declare -A DESC=(
  [D2]="#4 multi-timescale eligibility traces (rerun)"
  [E2]="#2 clone merging (rerun)"
  [F]="#5 pretrained sensory encoder"
  [G]="#3 prioritised replay vs forgetting"
  [H]="#6 gradient descent in the sleep phase"
  [I]="#4 follow-up: combination lock with slow trace"
  [E3]="#2 follow-up: merge with headroom (250 trials/agent)"
  [G2]="#3 follow-up: replay across 12 seeds"
  [H2]="#6 follow-up: gradient vs matched local replay"
)
ORDER=(D2 E2 F G H I E3 G2 H2)
declare -A SCRIPT=([D2]=D2_traces [E2]=E2_merge [F]=F_encoder [G]=G_replay [H]=H_sleepgrad [I]=I_lock_trace [E3]=E3_merge [G2]=G2_replay [H2]=H2_sleepgrad)

echo "=============================================="
echo " brainsim queue    $(date '+%H:%M:%S')"
echo "=============================================="
for k in "${ORDER[@]}"; do
  s="${SCRIPT[$k]}.py"
  if [ -f "$k.done" ]; then
    printf " [DONE]    %-3s %s\n" "$k" "${DESC[$k]}"
  elif ps -eo comm,etime,args --no-headers | awk -v s="$s" '$1=="python3" && $4==s' | grep -q .; then
    el=$(ps -eo comm,etime,args --no-headers | awk -v s="$s" '$1=="python3" && $4==s {print $2}' | head -1)
    printf " [RUNNING] %-3s %s   (%s elapsed)\n" "$k" "${DESC[$k]}" "$el"
  else
    printf " [QUEUED]  %-3s %s\n" "$k" "${DESC[$k]}"
  fi
done
echo "----------------------------------------------"
echo " results so far:"
for k in "${ORDER[@]}"; do
  [ -s "$k.out" ] && echo "   $k.out  ($(wc -l < "$k.out") lines)"
done
echo "----------------------------------------------"
echo " see a result:   cat /tmp/brainsim/<NAME>.out"
echo " watch live:     watch -n30 /tmp/brainsim/status.sh"
echo " stop it all:    pkill -f 'python3 [A-Z]_' ; pkill -f 'python3 [A-Z][0-9]_'"
