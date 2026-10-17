# One-attempt future owner S0/S1 RT2 hardware packet

PREPARED / NOT_EXECUTED. Controller is stopped after ONE d30e CYAN/OFF/OFF attempt.
No source agent may operate it. This source-work turn authorizes no new RT2.
First require separate profile_store_rt2_late_device_adjudication.md PASS; any
mismatch/timeout/uncertainty blocks replacement. No QUERY repair or cleanup.

1. Record operator/controller/host/cable/evidence directory. Rehash SAME preserved
   UF2 immediately before future manual installation. Use exact candidate SHA,
   tree,parent and UF2 size/hash from sealed HANDOFF, never a substitute rebuild.
2. After d30e adjudication PASS only: ordinary manual install, ONE normal boot
   without RT2/MB1. Working normal Configurator GET_DEVICE_INFO/PULSE/STATUS/allLIST/
   fullREAD1/3/4/22/GET_CONFIG. Require exactnewfirmware,incarnation1/store166,
   accepted useful profile bytes/revisions/references (1rev2/3rev1/4rev1/22rev132),
   Configgeneration1182731055/exact252bytes SHA256
   cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0.
   No uncertainty/unresolvedreceipt/pendingarmedfault; healthy resourceflags,
   bothcoreminfree,heapcurrent/peak/capacity,FSused/free. d30e comparison1864/3716,
   heap10224/71664,FS147456/376832 is previous ownerreportedcontrol, not acceptance
   inherited by newcandidate. B2/ROM3/E5disabled/inapplicable retained. STOPonfail.
3. Enter manual RT2 exactlyONCE using known held-button route without MB1. Wait
   ten seconds with ordinary margin. Record ONE uniform settled color each LARGE
   LF4/LF3/LF5. BothLEDseachSAME; MB/menu DARK. No mixedpixels/orientation/transient/
   video/timing-sequence interpretation. Display state, optional one stillphoto.

| Button | Uniform settled decoder |
|---|---|
| LF4 initialS0/RAW | GREEN validempty/noRAW; MAGENTA noentry/RAW or precisionUNKNOWN; BLUE entries/noS0SETUP/noRAW; CYAN entries/noS0SETUP/RAW; YELLOW anyS0SETUP; RED interceptedUSBpanic override |
| LF3 late/redispatch | OFF no late; RED lateN/no later publishedentry; CYAN laterpublishedentry but no strictlypostN S0SETUP; WHITE strictlypostN S0SETUP; MAGENTA precisionUNKNOWN |
| LF5 downstream | OFF none; ORANGE external/oldhookentry; CYANaccepted; YELLOWconsumed; BLUEcontrol; GREENdescriptor/address; WHITEconfigured/inspection; REDdrop |

   All-dark/unclear UNKNOWN. RAW historical SIE/INTR/INTS positives are sequential,
   not simultaneous/current. LF4MAGENTA+LF3MAGENTA means precision limit; no false
   no-redispatch/absence conclusion. LF4YELLOW remains retained positive even with
   quality loss; LF3MAGENTA forbids exact laterrelation. Panic masksLF4facts.
4. Record matching hostUSBinventory identity and serialendpoint present/absent.
   Hosttree is registry evidence, not authoritative on-wirepacket capture. No host
   kernel/logging change, SWD, forcedIRQ, repeated reconnect or externaldevicecommand.
5. SERIAL ABSENT: STOP IN PLACE. No command, secondRT2,reset/reboot/reflash,GC,
   selection,mutation,cleanup/refusal/repair. Retain this boot and settledpanel.
6. SERIAL PRESENT: bounded readonly GET_DEVICE_INFO/PULSE/STATUS/allLIST/fullREAD
   1/3/4/22/GET_CONFIG once, HEALTH only useful/current if needed. Preserve raw
   bytes/transcripthashes,persistentauthority and fullresources. Require private
   version3/valid1/captured1. Save entries/returns/setup/reset/buffcount/latestS0,
   fields209..217 latestS1/gates/latecount/firstlateN/S0/S1/gates/postlateS0ID/flags.
   Legacyprivate branchmarker/ever/multi/enabledwindow fields unsupportedzero;
   legacysetup_irq/pre_setup trampoline fields remain unsupportedzero v2. Do not
   infer absence from retiredfields. overflow_flags must0 for exactredispatchcase.
   latestS0 pairs latestS1/gates ONLY when entries==returns and flags0; otherwise
   latestS1/gates belongpreviousinvocation. Firstlate tuple is sameinvocation.
   Gatebits1NVICenabled/2pending/4PRIMASKset are core0 sequentialsamples AFTERS1,
   not simultaneouswithS1. Save individualRAWstickies and downstream/resetbank.
   Stopfirstmismatch/timeout. NoQUERYrepair/GC/selection/cleanup/mutation/retry.
7. ReportexactSHA/UF2hash,normalcontrol/resources,LF4/LF3/LF5,display,USB/serial,
   boundedreadonlyreceipt if available, then STOP.

## Decide only from this physical attempt

- LF4CYAN/LF3RED: RAWpositive,S0SETUP0,lateobserved,no later publishedS0 bycapture:
  MULTI_PROFILE_STORE_RT2_LATE_SETUP_NOT_REDISPATCHED. Means sampled late source-
  return boundary and no later completedpublication; not proof EXC_RETURN occurred,
  latch stayed asserted,NVIC malfunction or same packetcausedanything. A later S0
  read paused beforepublication remains invisible. Gatepending1 adds separate
  LATE_SETUP_NVIC_PENDING_AT_RETURN sampled afterS1. Pending0whileactive does NOT
  refute expected levelrepend at actual exceptionreturn.
- LF4CYAN/LF3CYAN: laterentry but no laterS0SETUP:
  MULTI_PROFILE_STORE_RT2_SETUP_LOST_BETWEEN_RETURN_AND_NEXT_SNAPSHOT is cautious
  label for changed observations, not proven lost siliconlatch or Cbranchfailure.
- LF3WHITE: laterS0SETUP afterfirstlate; redispatch observed thisboot, classifyLF5.
  Boot-global earlierSETUP cannot setWHITE. Privatehistory and recovery-onlyLF5
  are differentwindows; do not infer eventloss across those windows.
- LF4CYAN/LF3OFF: no S1 caughtSETUP. It couldappear outside sampledwindows or be
  transient. If no safe softwarediscriminator remains, return
  MULTI_PROFILE_STORE_RT2_SOFTWARE_OBSERVABILITY_LIMIT_REACHED. Nextseparate route
  practicalSWD/instructiontrace or externalUSBanalyzer/authoritativehostbustrace;
  do not add more polling or perform it in this diagnostic run.
- LF4YELLOW: oldcyanboundary didnot reproduce. Classifydownstream, includingLF5drop.
- QualityMAGENTA/unclear: UNKNOWN; retain exactobservation, no retry.

S1 precedes publication, epilogue, remainingSDKsharedcallbacks and EXC_RETURN.
PostS0 hook can itself enlarge/create latewindow; S1publication delaysactualreturn.
No negligible/zero perturbation, completedreturn, hardwarelatcharbitration or silicon
root-cause claim. No USB behavior repair. Hardware NOT_TESTED before ownerexecutes;
rootcauseUNPROVEN; Nunchuk/physicalselection remain NOT_TESTED. Canonical unchanged.
