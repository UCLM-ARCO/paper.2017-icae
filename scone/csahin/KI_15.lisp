;; (load "/home/mjsantof/repo/mariajose.santofimia/tesis/CMU/Scone/files/pathToFiles")
;; (load-kb "/home/mjsantof/repo/mariajose.santofimia/tesis/CMU/Scone/files/keyIssues/KI_15.lisp")

(in-context {general})
(in-namespace "events" :include "common")

(new-relation {status}
		       :a-inst-of {thing}
		       :b-inst-of {thing})

(new-type-role {liquid level} {liquid} {measure})
(new-type {faucet} {thing})
(new-type {valve} {thing})
(new-type {drain} {thing})

(new-event-type {turn on faucet} '({event})
		:roles
		((:indv {turnedOnFaucet} {faucet})
		 (:indv {faucetValve} {valve})
		 (:indv {faucetDrain} {drain})			     
		 (:type {faucetLiquid} {liquid}))
  :throughout    
  ((defvar flow) ;; m³/s
   (defvar t_s) ;; elapsed time in seconds
   (defvar baseArea) 
   (new-indv {instant-T0} {time point})
   (new-indv {instant-T1} {time point})
   (new-indv {instant-T2} {time point})
   (new-statement  {instant-T0} {before}  {instant-T1})
   (new-statement  {instant-T1} {before}  {instant-T2})
   (defvar le (lookup-element {faucetLiquid}))
   (push-element-fluent (lookup-element {faucetLiquid}) :Level '(* flow (/ t_s baseArea))))
  :before	     
  ((in-context (new-context {turn on faucet bc} {general}))
   (setq *current-time-point* {turn on faucet T0})
   (new-statement  {faucetValve}  {status} {off})
   (fluent-hold-at-time le :Level {instant-T0} 'empty))
  :after
  ((in-context (new-context {turn on faucet ac}  {general}))
   (new-statement  {faucetValve}  {status} {on})
   (setq *current-time-point* {instant-T1})
   (fluent-released le :Level '(* flow (/ t_s baseArea))  {instant-T1})
   (fluent-hold-at-time le :Level {instant-T2} 'full t)))
   
