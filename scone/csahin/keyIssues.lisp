(defun the-only-x-of-y-is-z (x y z)
  "If it is legal for X to fill the Y-role of Z, create a statement link to
   make it so.  Return the link."
  (setq x (lookup-element-test x))
  (setq y (lookup-element-test y))
  (setq z (lookup-element-test z))
  (unless (or *no-checking*
	      (can-x-be-the-y-of-z? z x y))
    (commentary
     "~S cannot be the ~S of ~S.  Continuing..." x y z)
    (return-from the-only-x-of-y-is-z nil))
    (loop for i in (incoming-b-wires (lookup-element x))
	when (eq (get-the-x-of-y x y)  (a-wire (lookup-element i))) do (remove-element (lookup-element i)))
    (new-map z x y)
    (loop for i in (incoming-b-wires (lookup-element-predicate x))
       when (and (eq-link? (lookup-element i)) (find (a-wire (lookup-element i)) (list-roles (lookup-element y)))) do
	 (progn
	   (loop for j in  (incoming-b-wires (lookup-element (a-wire (lookup-element i))))
	      when (indv-node? (lookup-element (a-wire (lookup-element j)))) do
		(progn 
  			(new-map z y (b-wire (lookup-element j)))
			(remove-element (lookup-element j))))))
    (return-from  the-only-x-of-y-is-z T))


(defun statement-true? (a rel b)
  "Predicate to determine if there is a REL relationship between elements A
   and B."
  (setq a (lookup-element-test a))
  (setq rel (lookup-element-test rel))
  (setq b (lookup-element-test b))
  (with-temp-markers (m m1 m-rel )
    (mark-context-contents *context* m1)
    ;; this marks all possible Bs and relations that are crossed over
    (mark-rel a rel m :m-rel m-rel)
    ;;  relations that are crossed
    (loop for x in (list-marked m-rel) 
	 ;; when mark is b there is a statement such a rel b
	 ;; Furthermore, we check if such relation is in the context we are interested in
	 ;; We get the contex-wire, and check if equal actual context
       when(and(marker-on? b m) (marker-on? x m1)) do
       ;;Also, we have to check that b can be the b-wire of the just selected relation
       ;; for instance if split moveOrigin moveDestination, and kitchen is moveOrigin, 
       ;; it cannot be a moveDestinatio	
       (loop for i in (incoming-b-wires (lookup-element (b-wire (lookup-element x))))
	  when (or (eq (a-wire (lookup-element i)) (lookup-element b)) (eq (b-wire (lookup-element i)) (lookup-element b))) do
	    (return-from statement-true? x)))))




;; RELATIONS APPLIED TO ACTIONS
(new-type {position} {place})
(defvar *involved-element* (lookup-element {involved element}))

(new-relation {is located at}
	      :a-inst-of {thing}
	      :b-inst-of {location})

(new-relation {has position}
	      :a-inst-of {thing}
	      :b-inst-of {position})
(new-relation {is reported to}
	       :a-inst-of {thing}
	       :b-inst-of {thing})

(new-relation {is holding the}
	      :a-inst-of {person}
	      :b-inst-of {thing})

(new-relation {pays attention to}
	      :a-inst-of {person}
	      :b-inst-of {thing})


(new-indv-role {personLocation} {person} {place})
(new-indv-role {objectLocation} {thing} {place})

(new-event-type {move}
 '({event})
 :roles
 ((:type {movingObject} {thing})
  (:type{movingObjectLocation} {place})
  (:type {moveOrigin} {place} :english ("beginning" "start"))
  (:type {moveDestination} {place} :english ("end" "finish")))
 :throughout
 ((new-eq {personLocation} {movingObjectLocation})
  (new-split '({moveOrigin} {moveDestination})))
 :before
 ((in-context (new-context {move bc}))
  (new-statement {movingObject} {is located at} {moveOrigin})
  (the-x-of-y-is-z {movingObjectLocation} {move} {moveOrigin}))
 ;; (new-not-statement {movingObject} {is located at} {moveDestination}))
 :after
 ;((in-context {after context})
 ((in-context (new-context {move ac}))
;;  (new-not-statement {movingObject} {is located at} {moveOrigin})
  (new-statement {movingObject} {is located at} {moveDestination})
  (the-x-of-y-is-z {movingObjectLocation} {move} {moveDestination})))

