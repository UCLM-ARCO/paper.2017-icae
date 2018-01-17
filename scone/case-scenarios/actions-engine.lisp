(defun get-before-context-of (act1)
  (let ((bc-elem (lookup-element (the-x-role-of-y {before context} act1)))) 
    (if (incoming-a-wires bc-elem)
	(b-wire (lookup-element (car (incoming-a-wires bc-elem)))))))

(defun get-after-context-of (act1)
  (let ((bc-elem (lookup-element (the-x-role-of-y {after context} act1))))  
    (if (incoming-a-wires bc-elem)
	(b-wire (lookup-element (car (incoming-a-wires bc-elem)))))))

(defun in-after-context-of (act1)
  (if (get-after-context-of act1)
      (in-context (get-after-context-of act1))
      *context*))

(defun in-before-context-of (act1)
  (if (get-before-context-of act1)
      (in-context (get-before-context-of act1))
      *context*))

(defmacro back-to-general () 
	  (in-context {general}))

(defun list-causes (evt)
 "List all the actions and events that have been described as the
  cause of a given event evt. The realtion {causes} is used to find
  these actions and events"
  (with-markers (m1)
    (progn
      (mark-rel-inverse  {causes} evt m1)
      (list-most-specific m1))))
       
(defun x-is-a-context-of (ctxt)
  "This functions returns the event name whose after or before context
is passed as an argument"
  (let ((ac (mark-role-inverse  {after context} (lookup-element ctxt) m1)))
    (if (eq ac 0)
	(progn 
	  (mark-role-inverse  {before context} (lookup-element ctxt) m2)
	  (list-marked m2))
	(list-marked m1))))


  

(defun list-context-contents (cxt)
  "List all the elements define in context. Elements are mainly
relations, and those which are not, such as actions or events, are
turned into relations using the generic relation --causes--"
  (let ((temp-list '()))
    (dolist (rel (incoming-context-elements (lookup-element cxt)))
      (let* ((a (a-wire (lookup-element rel)))
	     (b (b-wire (lookup-element rel))))
	(if (not (eq (is-x-a-y? rel {event}) ':YES))
	    (push (list a rel b) temp-list))))
      temp-list))


(defun list-actions-causing (a rel b)
  (with-markers (m_a m_rel m_b)
    (progn
      (mark-rel rel a m_a)
      (list-marked m_a)
      (mark b m_b)
      (do-marked (x m_a)
	(when (marker-on? x m_b)
	  (mark x m_rel)))
      (list-most-specific m_rel))))

(defun equivalent-relations? (st1 st2)
  (with-markers (m1)
    (progn
      (upscan (lookup-element st1) m1)
      (let* ((ups (list-marked m1))
	    (par (parent-wire (lookup-element st2))))
	(if (member par ups)
	    t
	    nil)))))


(defun equivalent-statements?  (stat1 stat2)
  (let* ((stat1_a (car stat1))
	 (stat1_rel (cadr stat1))
	 (stat1_b (caddr stat1))
	 (stat2_a (car stat2))
	 (stat2_rel (cadr stat2))
	 (stat2_b (caddr stat2)))
    ;; Parents are the same for two relations 
    ;(if (equal (parent-wire (lookup-element stat1_rel)) (parent-wire (lookup-element stat2_rel)))
    (if (equivalent-relations? stat1_rel stat2_rel)
	(progn
	  (if (or (and (not-statement? (lookup-element stat1_rel)) (not-statement? (lookup-element stat2_rel))) (and (not (not-statement? (lookup-element stat1_rel))) (not (not-statement? (lookup-element stat2_rel)))))
	      (progn
		(if (and (not (eq (is-x-a-y? stat1_a stat2_a) ':NO)) (not (eq (is-x-a-y? stat1_b stat2_b) ':NO)))
		    t
		    nil))
	      nil)))))



(defun not-equivalent-after-contexts? (evt1 target_to_match)
  (let* ((evt1_AC (list-context-contents (get-after-context-of evt1)))
	 (ttm_AC (list-context-contents (get-after-context-of target_to_match))))
    (dolist (temp_evt1 evt1_AC) 
      (dolist (temp_ttm ttm_AC)
	(if (equivalent-statements? temp_evt1 temp_ttm)
	    (setq ttm_AC (remove temp_ttm ttm_AC)))))
	  
    (if ttm_AC
	T
	nil)))



(defun list-indirect-causes (evt)
  "Looks for actions and events with similar after context as evt. We
   do not worry yet about location and time."
  (let* ((temp-list '()))
    (dolist (f (incoming-b-wires (lookup-element {after context})) temp-list)
      (when (is-a-link? (lookup-element f))
	(with-markers (m1)
	  (progn
	    (mark-role-inverse {after context} (a-wire (lookup-element f)) m1)
	    (if (list-marked m1)
		(setq temp-list (append (list-marked m1) temp-list)))))))
    ;; Clean up the list containing all actions, removing those whose
    ;; after context is not equivalente to the evt
    (setq temp-list (remove-if #'(lambda (x) (not-equivalent-after-contexts? x evt)) temp-list))))

(defun all-roles-satisfied? (evt)
  ; list all roles of an event or action
  ; Check whether each of these roles can be satisfied with existing objects
  ; if not, can it be obviated?

;; (list-roles (lookup-element {shift towards}))
;; (role-node? (lookup
  t
)

(defun list-all-x-in-context-y (obj_t &optional ctxt_t)
   "This functions returns all objects of a certain type declared in a
   given context. If context is not provided, general context is
   assumed"
      
)

(defun possible-in-time? (evt t_stamp loc)
  t
)

(defun possible-in-loc? (evt t_stamp loc)
  
 t
)


(defun possible-event? (evt t_stamp loc)
  (let ((rol_s (all-roles-satisfied? evt))
	(tim_s (possible-in-time? evt t_stamp loc))
	(loc_s (possible-in-loc? evt t_stamp loc)))
    (if (and rol_s tim_s loc_s)
	t
	nil)))
