;;; -------------------------------------------------------
;;; Context Marking Functions

;; CSAHIN Code, modified by mjsantof to be consistent with new version of Scone




(defun mark-context-contents (context m &key (append nil))
  "Marks the immediate contents of CONTEXT with M"
  (declare (fixnum m))
  (setq context (lookup-element-test context))
  (check-legal-marker-pair m)

  (unless append
    (clear-marker-pair m))

  (let* ((queue (list context)))

    (dolist (c queue)
      (dolist (elem (incoming-context-wires c))
	(mark elem m)
	(append queue (list elem))))))

;; modified by mjsantof
(defun list-context-contents (context)
  "Lists the immediate contents of CONTEXT."
  (with-markers (m)
 	(progn
	  (mark-context-contents context m)
	  (list-marked m))))
    
(defun show-context-contents (context)
  "Prints the immediate contents of CONTEXT."
  (with-markers (m)
    (progn
	(mark-context-contents context m)
    	(show-marked m))))

;;; -------------------------------------------------------
;;; Event Contexts Specific Functions

(defun mark-before (event m)
  "Marks all elements included in the before context of
   EVENT with M."
  (let* ((event (lookup-element event))
	 (before (the-x-role-of-y *before-context* event))
	 (parents (list-supertypes event)))
    
    (mark-context-contents before m)
    
    (dolist (p parents)
      (when (and (is-x-a-y? p *event*)
		 (type-node? p))
	(setq before (the-x-role-of-y *before-context* p))
	(mark-context-contents before m :append t))
    (marker-count m))))

(defun list-before (event)
  "Lists all elements included in the before context of
   EVENT"
  (with-markers (m1)
    (progn
	(mark-before event m1)
        (list-marked m1))))

(defun show-before (event)
  "Prints all elements included in the before context of
   EVENT"
  (with-markers (m1)
    (progn
      (mark-before event m1)
      (show-marked m1))))


(defun mark-after (event m)
  "Marks all elements included in the after context of
   EVENT with M."
  (let* ((event (lookup-element event))
	 (after (the-x-role-of-y *after-context* event))
	 (parents (list-supertypes event)))
    
    (mark-context-contents after m)
    
    (dolist (p parents)
      (when (and (is-x-a-y? p *event*)
		 (type-node? p))
	(setq after (the-x-role-of-y *after-context* p))
	(mark-context-contents after m :append t))
    (marker-count m))))

(defun list-after (event)
  "Lists all elements included in the after context of
   EVENT."
  (with-markers (m1)
    (progn
      (mark-after event m1)
      (list-marked m1))))

(defun show-after (event)
  "Prints all elements included in the after context of
   EVENT."
  (with-markers (m1)
    (progn 
       (mark-after event m1)
       (show-marked m1))))

(defmacro in-before (event &body forms)
  "Switches to the before context of EVENT and executes the body."
  (let ((ctxt (gensym "ctxt")))
    `(let ((,ctxt *context*))
       (in-context (the-x-role-of-y *before-context* ,event))
       ,forms
       (in-context ,ctxt))))

(defmacro in-after (event &body forms)
  "Switches to the after context of EVENT and executes the body."
  (let ((ctxt (gensym "ctxt")))
    `(let ((,ctxt *context*))
       (in-context (the-x-role-of-y *after-context* ,event))
       ,forms
       (in-context ,ctxt))))

;;; -------------------------------------------------------
;;; Event Query Functions

(defun mark-events-with-x-in-context-y (x y m)
  "Given a link, finds all events that have an
   equivalent link in the given context. C must be either
   *BEFORE-CONTEXT* or *AFTER-CONTEXT*. By equivalent links
   we mean link nodes of the same type, with EQ-able nodes
   at then end of their A, B and C wires."
  
  (setq x (lookup-element-test x))
  (clear-marker m)

  ; modified by mjsantof
  ;(unless (link? x)
  ;  (commentary "~A must be a link node.~%" x)
  ;  (return-from mark-events-with-x-in-context-y nil))
  ; end of modification

  (unless (or (eq y *BEFORE-CONTEXT*)
	      (eq y *AFTER-CONTEXT*))
    (commentary "~A must be bound to *BEFORE-CONTEXT* or *AFTER-CONTEXT*" y)
    (return-from mark-events-with-x-in-context-y nil))

  (let* ((elementX (lookup-element x))
	 (parent (parent-wire elementX)))
    ;; mark all instances of the link minus the given one
    (with-markers (m1 m2)
      (downscan parent m1)
      (unmark elementX m1)
      (unmark parent m1)

      ;; for each such link, see if it matches
      (do-marked (e m1)
	(when (and (can-x-eq-y? (a-wire x) (a-wire e))
		   (can-x-eq-y? (b-wire x) (b-wire e))
		   (or (and (null (c-wire x))
			    (null (c-wire e)))
		       (can-x-eq-y? (c-wire x) (c-wire e))))
	  (mark e m2)))

      ;; no need for m1 marked elements
      (clear-marker m1)

      ;; we have candidates that match, leave the ones that live in
      ;; an after context
      (do-marked (e m2)
	(when (is-x-a-y? (context-wire e) y)
	  ;; mark the context not the statement
	  (mark (context-wire e) m1)))

      ;; now we have all after-contexts containting s, mark the owners with m
      (do-marked (y m1)
	;; get the map-link, and then the owner
	(dolist (map (incoming-a-wires y))
	  (mark (c-wire map) m))))
    ;; done with temp-markers

    ;; for completeness we need to downscan :augment to get all instances
    ;; of such events
    (when (> (marker-count m) 0)
      (downscan nil m :augment t))))


(defmacro mark-events-requiring-x (x m)
  `(mark-events-with-x-in-context-y ,x *before-context* ,m))

(defun list-events-requiring-x (x)
  (with-markers (m)
    (mark-events-requiring-x x m)
    (list-marked m)))

(defun show-events-requiring-x (x)
  (with-markers (m)
    (mark-events-requiring-x x m)
    (show-marked m)))
   

(defmacro mark-events-causing-x (x m)
  `(mark-events-with-x-in-context-y ,x *after-context* ,m))

(defun list-events-causing-x (x)
  (with-markers (m)
    (mark-events-causing-x x m)
    (list-marked m)))

(defun show-events-causing-x (x)
  (with-markers (m)
    (mark-events-causing-x x m)
    (show-marked m)))


(defun mark-events-preceding (e m)

  (with-markers (m1)

    (let ((reqs (list-before e)))
      ;; find events causing the first requirement for e
      (mark-events-causing-x (car reqs) m1)
      ;; mark these events with M
      (mark-boolean m (list m1) nil)
    
    (dolist (x (cdr reqs))
      ;; mark each event causing x
      (mark-events-causing-x x m1)
      ;; unmark events with M without M1
      (unmark-boolean m nil (list m1)))))
  (marker-count m))

(defun list-events-preceding (e)
  (with-markers (m)
    (mark-events-preceding e m)
    (list-marked m)))

(defun show-events-preceding (e)
  (with-markers (m)
    (mark-events-preceding e m)
    (show-marked m)))

(defun mark-events-succeeding (e m)

  (with-markers (m1)

    (let ((effx (list-after e)))
      ;; find events requiring the first effect of e
      (mark-events-requiring-x (car effx) m1)
      ;; mark these events with M
      (mark-boolean m (list m1) nil)
    
    (dolist (x (cdr effx))
      ;; mark each event requiring x
      (mark-events-requiring-x x m1)
      ;; unmark events with M without M1
      (unmark-boolean m nil (list m1)))))
  (marker-count m))

(defun list-events-succeeding (e)
  (with-markers (m)
    (mark-events-succeeding e m)
    (list-marked m)))

(defun show-events-succeeding (e)
  (with-markers (m)
    (mark-events-succeeding e m)
    (show-marked m)))





;;; -------------------------------------------------------
;;; Event Addition Macro

(defmacro new-event (iname parents
				&key
				(type t)
				(generic nil)
				(context *context*)
				english
				roles
				throughout
				before
				after
				expansion)
  "Creates a new event type with the given INAME and with parents PARENTS in context
   :CONTEXT. Sets the english external names to :ENGLISH. When :ROLES is supplied,
   creates the given roles in the throughout context of the event. Then executes the
   three bodies :THROUGHOUT, :BEFORE and :AFTER in the appropriate contexts. "
  
  (let ((event (gensym "event"))
	(curr-ctxt (gensym "curr-ctxt-"))
	(before-ctxt (gensym "before-context-"))
	(after-ctxt (gensym "after-context-"))
	(role-iname (gensym "role-iname-"))
	(role-args (gensym "role-args-")))
    (append
     `(progn
	
	;; If the iname is already there quit
	(when (lookup-element ,iname)
	  (error "~A already exists." ,iname))
	
	;; Check if all parents are events
	(dolist (p ,parents)
	  (unless (is-x-a-y? p *event*)
	    (error "~A is not an event." p)))
	
	(if ,type
	    (new-type ,iname (car ,parents) :english ,english :context ,context)
	  (new-indv ,iname (car ,parents) :english ,english :context ,context :generic ,generic))

	;; create IS-As between event and the rest of parents
	(dolist (p (cdr ,parents))
	  (new-is-a ,iname p :context ,context)))
     
     (list
      (append
       `(let* ((,event (lookup-element ,iname))
	       (,curr-ctxt *context*)
	       (,before-ctxt (the-x-role-of-y *before-context* ,event))
	       (,after-ctxt (the-x-role-of-y *after-context* ,event))))
       
       ;; we're in the given context
       (list `(in-context ,context))
       ;; let the before context inherit from the given context
       (list `(new-is-a ,before-ctxt ,context))
       
       (list
	`(let ((,role-args nil)
	       (,role-iname nil))
	   
	   ;; create the roles
	   (dolist (role-des (quote ,roles))
	     (ecase (car role-des)
	       (:type
		;; push the arguments for new-type-role
		(setq ,role-args (append (nthcdr 3 role-des) ,role-args))
		(push (third role-des) ,role-args)
		(push ,event ,role-args)
		(push (second role-des) ,role-args)
		(setq ,role-iname (second role-des))
		
		(apply 'new-type-role ,role-args))
	       
	       (:indv
		;; push the arguments for new-indv-role
		(setq ,role-args (append (nthcdr 3 role-des) ,role-args))
		(push (third role-des) ,role-args)
		(push ,event ,role-args)
		(push (second role-des) ,role-args)
		(setq ,role-iname (second role-des))
		
		(apply 'new-indv-role ,role-args))
	       
	       (:rename
		;; push the arguments for create-the-x-role-of-y
		(setq ,role-args (append (cddr role-des) ,role-args))
		(push ':iname ,role-args)
		(push ,event ,role-args)
		(push (cadr role-des) ,role-args)
		(setq ,role-iname (apply 'create-the-x-role-of-y ,role-args))
		
		(unless ,role-iname
		  (error "~A is not a role of ~A.~%" ,role-iname ,event))))
	     
	     (x-is-a-y-of-z ,role-iname *involved-element* ,event)
	     (setq ,role-args nil))))
       
       ;; execute the throughout body
       throughout
       ;; execute the before body in the throughout context
       (list `(in-context ,before-ctxt))
       before
       ;; execute the after body in the after context
       (list `(in-context ,after-ctxt))
       after
       ;; add any expansions supplied
       (list `(when ,expansion (add-expansion ,event ,expansion)))
       ;; switch to the original context
       (list `(in-context ,curr-ctxt)))))))

;; Here are new-event-type and new-event-indv for backward compatibality
(defmacro new-event-type (iname parents
				&key
				(context *context*)
				english
				roles
				throughout
				before
				after
				expansion)
  `(new-event ,iname ,parents
    :type t
    :context ,context
    :english ,english
    :roles ,roles
    :throughout ,throughout
    :before ,before
    :after ,after
    :expansion ,expansion))

(defmacro new-event-indv (iname parents
				&key
				(context *context*)
				(generic nil)
				english
				roles
				throughout
				before
				after
				expansion)
  `(new-event ,iname ,parents
    :type nil
    :generic ,generic
    :context ,context
    :english ,english
    :roles ,roles
    :throughout ,throughout
    :before ,before
    :after ,after
    :expansion ,expansion))


;;; -------------------------------------------------------
;;; Event Time Functions



;;; -------------------------------------------------------
;;; Expansion Addition Functions

(defun add-expansion (event form)
  "Defines the expansion described by FORM for EVENT."
  
  (setq event (lookup-element event))

  ;; check if event exists
  (unless (is-x-a-y? event *event*)
    (commentary "~A is not an event." event)
    (return-from add-expansion nil))
  
  ;; check expansion args
  (unless (check-compound-form form)
    (return-from add-expansion nil))

  (when (is-x-a-y? event *compound-event*)
    (commentary "Adding expansions to compounds not supported.")
    (return-from add-expansion nil))


  (let* ((expansion-type (car form))
	 (owner-binds nil)
	 (subevent-forms nil)
	 (subevent-nodes nil))

    ;; see if there are owner-binds
    (cond ((and (listp (cadr form))
		(eq (car (cadr form)) ':owner-binds))
	   (setq owner-binds (cadr form))
	   (setq subevent-forms (cddr form)))
	  ;; no ownder-binds
	  (t
	   (setq subevent-forms (cdr form))))
	 
    ;; create the subevents depending on type of compound, pass
    ;; just the subevent parts of the form
    (setq subevent-nodes
	  (ecase expansion-type
	    (:seq (new-sequential-internal event subevent-forms))
	    (:or (new-or-event-internal event subevent-forms))))
    
    ;; given the roles in the form, create and unify them
    (create-unify-roles event owner-binds subevent-nodes subevent-forms)
    
    ;; resolve B' and A' of expansion and make IS-As
    (ecase expansion-type
      (:seq (process-expansion-contexts-seq event subevent-nodes))
      (:or  (process-expansion-contexts-or event subevent-nodes))))
    
    ;; return the events
    event)


(defun check-compound-form (form)
  "Recursively checks the compound form. A legal form
   starts with a compound type keyword (:seq, etc..)
   and continues with subevent-forms or other compound forms"

  (unless (listp form)
    (commentary "Compound form is not a list.")
    (return-from check-compound-form nil))

  (let* ((compound-type (car form))
	 (compound-rest (cdr form)))

    (unless (or (eq compound-type ':seq)
		(eq compound-type ':or))
      (commentary "Compound type must be :seq or :or")
      (return-from check-compound-form nil))

    (unless (> (length compound-rest) 1)
      (commentary "Trivial expansion: Only one subevent given.")
      (return-from check-compound-form nil))

    (dolist (arg compound-rest)
      (cond
       ;; the subevent-form is a list and starts with an element
       ((and (listp arg)
	     (or (typep (car arg) 'element)
		 (typep (car arg) 'element-iname)))
	
	(unless (is-x-a-y? (car arg) *event*)
	  (commentary "~A is not a valid subevent-form." arg)))
       
       ;; the subevent-form is a list and doesn't start with
       ;; an iname/element it must be a compound form
       ((listp arg)
	(unless (check-compound-form arg)
	  (commentary "~A is not a valid subevent-form." arg)
	  (return-from check-compound-form nil)))
       
       ;; otherwise it's not a list so must be an event
       (t
	(unless (is-x-a-y? arg *event*)
	  (commentary "~A is not an event." arg)
	  (return-from check-compound-form nil))))))
  t)

(defun new-sequential-internal (event forms)
  "Creates the subevents in the compound form and makes them
   subevents of EVENT. Creates happens before statements
   between consequent subevents. No argument checking is done."

  (do* ((expansion forms (cdr expansion))
	(prev-subeform nil curr-subeform)
	(curr-subeform (car expansion) (car expansion))
	(subevents nil))

      ((null curr-subeform) subevents)

    (cond
     ;; if the form is atomic
     ((atom curr-subeform)
      (setq curr-subeform (lookup-element curr-subeform)))
     
     ;; if it's a list, first element must be an iname
     ((or (typep (car curr-subeform) 'element)
	  (typep (car curr-subeform) 'element-iname))
      (setq curr-subeform (lookup-element (car curr-subeform))))
     
     ;; otherwise we have a problem
     (t
      (error "Subevent Form invalid: ~A" curr-subeform)))
    
    (setq curr-subeform (new-indv nil curr-subeform :proper nil))
    (append subevents (list curr-subeform))
    (x-is-a-y-of-z curr-subeform *subevent* event)

    ;; if first subevent it's the *first-ordered-event*,
    ;; otherwise create the temporal statement between subevents
    (if (null prev-subeform)
	(x-is-the-y-of-z curr-subeform *first-ordered-event* event)
      (new-statement prev-subeform *happens-before* curr-subeform))))


(defun new-or-event-internal (event forms)
  "Creates the subevents in the compound form and makes them
   subevents of EVENT. No argument checking is done."
  
  (let ((subevents nil))
    (dolist (subevent forms)
      
      (cond
       ;; if the form is atomic
       ((atom subevent)
	(setq subevent (lookup-element subevent)))
       
       ;; if it's a list, first element must be an iname
       ((or (typep (car subevent) 'element)
	    (typep (car subevent) 'element-iname))
	(setq subevent (lookup-element (car subevent))))
       
       ;; otherwise we have a problem
       (t
	(error "Subevent Form invalid: ~A" subevent)))
      
      (setq subevent (new-indv nil subevent :proper nil))
      (append subevent (list subevent))
      (x-is-a-y-of-z subevent *subevent* event))
    subevents))

(defun unify-bind-list (key role-list)
  "Given a list of elements creates EQ links between them in a linear manner. KEY is not used."

  ;; to avoid the unused variable warning
  (eq key key)

  (unless (listp role-list)
    (commentary "Bind list is not a list!")
    (return-from unify-bind-list nil))

  (when (= 1 (length role-list))
    (commentary "Bind list is trivial!")
    (return-from unify-bind-list nil))

  (let ((role1 (lookup-element (car role-list))))
    
    (dolist (role2 (cdr role-list))
      (setq role2 (lookup-element role2))
      
      (unless (can-x-eq-y? role1 role2)
	(commentary "Roles cannot be EQed: ~A ~A" role1 role2)
	(return-from unify-bind-list nil))
      (new-eq role1 role2)
      (setq role1 role2))))
    
(defun create-unify-roles (event owner-binds subevent-nodes subevent-forms)
  "Creates the roles of the given subevents of EVENT, then checks
   if there are binding requests, and processes them. No argument
   checking is done."
  
  (let* ((bindings (make-hash-table)))

    ;; Let's go over the subevent-forms creating roles and grouping them
    ;; into bind groups
    (do* ((subevent-list subevent-nodes (cdr subevent-list))
	  (subevent (car subevent-list) (car subevent-list))
	  (form-list subevent-forms (cdr form-list))
	  (form (car form-list) (car form-list)))
	
	 ((null subevent) event)
      
      (when
	  ;; if the argument is a list and the first is an iname
	  ;; there are roles involved
	  (and (listp form) (or (typep (car form) 'element)
				(typep (car form) 'element-iname)))
	
	(dolist (bind-form (cdr form))
	  ;; make sure :bind is there
	  (unless (eq (car bind-form) ':bind)
	    (commentary "Ill-formed binding: This should have been caught earlier. The Knowledge-Base is compromised." bind-form)
	    (return-from create-unify-roles nil))
	  
	  (let* ((role (the-x-role-of-y (second bind-form) subevent))
		 (group (third bind-form))
		 (bind-group (gethash group bindings)))
	    
	    (if (null bind-group)
		(setf (gethash group bindings) (list role))
	      (setf (gethash group bindings) (cons role bind-group)))))))

    ;; Now check if there are any owner binds, if so create and include them in bind groups
    
    (when (eq (car owner-binds) ':owner-binds)

      (dolist (bind-form (cdr owner-binds))
	;; make sure :bind is there
	(unless (eq (car bind-form) ':bind)
	  (commentary "Ill-formed binding: This should have been caught earlier. The Knowledge-Base is compromised." bind-form)
	  (return-from create-unify-roles nil))
	
	(let* ((role (the-x-role-of-y (second bind-form) event))
	       (group (third bind-form))
	       (bind-group (gethash group bindings)))
	  
	  (if (null bind-group)
	      (setf (gethash group bindings) (list role))
	    (setf (gethash group bindings) (cons role bind-group))))))

    ;; All roles are created, now just unify them with a map function:
    (maphash 'unify-bind-list bindings)))

(defun process-expansion-contexts-seq (event subevents)
  "Creates the before and after contexts of the subevents,
   weaves them and infers what statements should belong
   to the before context of the first subevent of the sequence.
   The after context of the last subevent doesn't need any
   editing since it inherits all statements from previous subevents."

  ;; This basically simulates a sequential event, going through
  ;; the events one by one and checking what statements should be
  ;; true before we start the sequence

  ;; create and figure out what should go into B_0
  (let ((first-before nil)
	(last-after nil)
	(prev-event (car subevents)))

    (setq first-before (the-x-role-of-y *before-context* prev-event))
    
    ;; M-BEF is for B_0
    ;; M-CURR is for the before context of the current event
    ;; M-PREV is for the after context of the previous event
    ;; M-DIFF is for determining the difference between two contexts
    (with-markers (m-bef m-curr m-prev m-diff)

      (mark-before prev-event m-bef)
      (mark-after prev-event m-prev)
      
      (dolist (curr-event (cdr subevents))
	
	;; B_accum += B_i - A_i-1 
	;; M-BEF += M-CURR - M-PREV
	(mark-before curr-event   m-curr)
	(mark-after  prev-event m-prev)
	(context-diff m-curr m-prev m-diff)
	(context-add  m-bef  m-diff m-bef)
	(setq prev-event curr-event)))
    
    (setq last-after (the-x-role-of-y *after-context* prev-event))
    
    ;; %%% ASK SCOTT %%%
      ;;; HERE WE ADD THE NECESSARY STATEMENTS TO B_0
    
    ;; Make B-0 and A-N intances
    (new-is-a first-before (the-x-role-of-y *before-context* event))
    (new-is-a last-after (the-x-role-of-y *after-context* event))))

(defun process-expansion-contexts-or (event subevents)

  (let* ((before (the-x-role-of-y *before-context* event))
	 (after  (the-x-role-of-y *after-context* event)))
  
  ;; create the before and after contexts of the subevents
  ;; and create the IS-A links
  (dolist (event subevents)
    
    (new-is-a (the-x-role-of-y *before-context* event) before)
    (new-is-a (the-x-role-of-y *after-context* event) after))))


(defmacro link-cancels? (not-fn link1 link2)
  "Checks if LINK2 cancels LINK1 by checking if LINK2 satisfies NOT-FN
  and both links have EQ nodes at the end of their A, B and C wires"

  `(and (,not-fn ,link2)
	(is-x-eq-y? (a-wire ,link1) (a-wire ,link2))
	(is-x-eq-y? (b-wire ,link1) (b-wire ,link2))
	;; some links have NIL c-wires
	(or (and (null (c-wire ,link1))
		 (null (c-wire ,link2)))
	    ;;otherwise they are nodes
	    (is-x-eq-y? (c-wire ,link1) (c-wire ,link2)))))

(defmacro link-eqs? (eq-fn link1 link2)
  "Checks if LINK2 is equivalent to LINK1 by checking if LINK2 satisfies EQ-FN
  and both links have EQ nodes at the end of their A, B and C wires"

  `(and (,eq-fn ,link2)
	(is-x-eq-y? (a-wire ,link1) (a-wire ,link2))
	(is-x-eq-y? (b-wire ,link1) (b-wire ,link2))
	;; some links have NIL c-wires
	(or (and (null (c-wire ,link1))
		 (null (c-wire ,link2)))
	    ;;otherwise they are nodes
	    (is-x-eq-y? (c-wire ,link1) (c-wire ,link2)))))

(defun context-add (m1 m2 m3)
  "Marks all elements that are marked with M1 and/or with M2,
   checking semantic equivalency and cancellation, with marker M3."

  (do-marked (e1 m1)
    (do-marked (e2 m2)
      
      ;; here we check what type of element e1 is
      (cond
       ((and (number-node? e1)
	     (number-node? e2)
	     (= (internal-name e1)
		(internal-name e2)))
	(mark e1 m3))
       
       ((and (string-node? e1)
	     (string-node? e2)
	     (string= (internal-name e1)
		      (internal-name e2)))
	(mark e1 m3))
       
       ((and (function-node? e1)
	     (function-node? e2)
	     (eq (internal-name e1)
		 (internal-name e2)))
	(mark e1 m3))

       ((and (struct-node? e1)
	     (struct-node? e2)
	     (equal (internal-name e1)
		    (internal-name e2)))
	(mark e1 m3))
	
       ;; Think about proper/generic indvs
       ((and (or (and (indv-node? e1)
		      (indv-node? e2))
		 (and (type-node? e1)
		      (type-node? e2)))
	     (is-x-eq-y? e1 e2))
	(mark e1 m3))

       ((is-a-link? e1)
	(cond ((link-eqs? is-a-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? is-not-a-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))

       ((is-not-a-link? e1)
	(cond ((link-eqs? is-not-a-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? is-a-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))
       
       ((eq-link? e1)
	(cond ((link-eqs? eq-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? not-eq-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))

       ((not-eq-link? e1)
	(cond ((link-eqs? not-eq-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? eq-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))
       
       ((map-link? e1)
	(cond ((link-eqs? map-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? not-map-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))
       
       ((not-map-link? e1)
	(cond ((link-eqs? not-map-link? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? map-link? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))

       ;; CANCELS
       ((cancel-link? e1)
	(cond ((link-eqs? cancel-link? e1 e2)
	       (mark e1 m3))
	      ;; cancel links cancel a lot of things
	      ;; just check the b-wire for eqness
	      ((is-x-eq-y? (b-wire e1) e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))
	       
       ((statement? e1)
	(cond ((link-eqs? statement? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? not-statement? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))

       ((not-statement? e1)
	(cond ((link-eqs? statement? e1 e2)
	       (mark e1 m3))
	      ((link-cancels? statement? e1 e2)
	       nil)
	      (t
	       (mark e1 m3)
	       (mark e2 m3))))

       ;; if we fall in here, we either have an unknown type for E1
       ;; which very unlikely (unless there's a bug in the engine)
       ;; or we need to mark both element since they are not-EQ nor
       ;; cancelling
       (t (mark e1 m3)
	  (mark e2 m3))))))

  
(defun context-diff (m1 m2 m3)
  "Marks all elements that are marked with M1 but not with M2,
   checking semantic equivalency (cancellation has no effect)."
  
    (do-marked (e1 m1)
      (do-marked (e2 m2)
	
	;; here we check what type of element e1 is
	(cond
	 ((and (number-node? e1)
	       (number-node? e2)
	       (= (internal-name e1)
		  (internal-name e2)))
	  nil)
	 
	 ((and (string-node? e1)
	       (string-node? e2)
	       (string= (internal-name e1)
			(internal-name e2)))
	  nil)
	 
	 ((and (function-node? e1)
	       (function-node? e2)
	       (eq (internal-name e1)
		   (internal-name e2)))
	  nil)
	 
	 ((and (struct-node? e1)
	       (struct-node? e2)
	       (equal (internal-name e1)
		      (internal-name e2)))
	  nil)
	 
	 ;; Think about proper/generic indvs
	 ((and (or (and (indv-node? e1)
			(indv-node? e2))
		   (and (type-node? e1)
			(type-node? e2)))
	       (is-x-eq-y? e1 e2))
	  nil)
	 
	 ((is-a-link? e1)
	  (cond ((link-eqs? is-a-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
		 

	 ((is-not-a-link? e1)
	  (cond ((link-eqs? is-not-a-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((eq-link? e1)
	  (cond ((link-eqs? eq-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((not-eq-link? e1)
	  (cond ((link-eqs? not-eq-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((map-link? e1)
	  (cond ((link-eqs? map-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((not-map-link? e1)
	  (cond ((link-eqs? not-map-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((cancel-link? e1)
	  (cond ((link-eqs? cancel-link? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((statement? e1)
	  (cond ((link-eqs? statement? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ((not-statement? e1)
	  (cond ((link-eqs? statement? e1 e2)
		 nil)
		(t
		 (mark e1 m3))))
	 
	 ;; if we fall in here, we either have an unknown type for E1
	 ;; which very unlikely (unless there's a bug in the engine)
	 ;; or we need to mark both element since they are not-EQ nor
	 ;; cancelling
	 (t (mark e1 m3))))))
  

(defun list-sequential-subevents (event)
  "Given a sequential event, finds the subevents and puts them in a list"
  
  (setq event (lookup-element-test event))
  
  (unless (is-x-a-y? event *sequential-event*)
    (commentary "~A is not a sequential event." event)
    (return-from list-sequential-subevents nil))
  
  
  (with-markers (m1)
    
    (do* ((curr-step (find-the-x-role-of-y *first-ordered-event* event))
	  (sequence-list (list curr-step) (if curr-step
					      (cons curr-step sequence-list)
					      sequence-list)))
	 
	 ((null curr-step)
	  (nreverse sequence-list))
      
      ;; determine the possible next steps
      (mark-rel curr-step *happens-before* m1)
      
      
      (cond
	;; if there is nothing marked, the chains has ended
	((= 0 (marker-count m1))
	 (setq curr-step nil))
	
	;; there should be exactly one marked element
	((> (marker-count m1) 1)
	 (commentary "~A has multiple ordered events after." curr-step)
	 (return-from list-sequential-subevents nil))
	
	(t
	 (setq curr-step (car (list-marked m1))))))))


(defun play-sequential-event (event)
  "Given a sequential event, goes through the steps
   and prints out the activated elements."

  (setq event (lookup-element-test event))

  (unless (is-x-a-y? event *sequential-event*)
    (commentary "~A is not a sequential event." event)
    (return-from play-sequential-event nil))

  (let* ((subevents (list-sequential-subevents event))
	 (context nil)
	 (contents-one nil)
	 (contents nil)
	 (curr-step nil))

    (with-markers (m1)
      
      (dolist (step subevents)
	(format t "~%~%Step ~A:~%" step)
	(setq curr-step step)
	(setq contents-one nil)
	(setq contents nil)

	;; get the before context
	(setq context (the-x-role-of-y *before-context* step))
	;; propagate to all eq'ed contexts
	(eq-scan context m1 :basic nil)

	;; the generic context is VC so go to the owner events, go upto the parent
	;; and print the context of the parent
	(do-marked (c m1)
	  ;;(format t "~%Printing Context: ~A -- Owner: ~A~%" c (caddr (definition c)))
	  (setq contents-one (list-context-contents c))
	  (when (not (null contents-one))
	    (push contents-one contents)))

	(format t "~A" contents))

      ;; now print the final after context
      (format t "~%Step ~A:~&" (parent-wire curr-step))
      (setq context (the-x-role-of-y *after-context* curr-step))
      (setq contents-one nil)
      (setq contents nil)
      (eq-scan context m1 :basic nil)
      
      (do-marked (c m1)
	;;(format t "~%Printing Context: ~A -- Owner: ~A~%~%" c (caddr (definition c)))
	(setq contents-one (list-context-contents c))
	(when (not (null contents-one))
	  (push contents-one contents)))
      
      (format t "~A~%" contents))))
      
      


(defun expand-event (event &key
			   (depth 0)
			   (all nil))
  "Returns the subevents of the given event."

  (setq event (lookup-element-test event))

  ;; We can only expand an event if it's expandable
  (unless (is-x-a-y? event *compound-event*)
    (commentary "~A is not a {compound event}." event)
    (return-from expand-event (list event)))
  
  (let* ((expansion nil)
	 (deeper-expansion nil))

      ;; we will return different structures depending on what type of event this is
      (cond ((is-x-a-y? event *sequential-event*)
	     (setq expansion (list-sequential-subevents event))
	     (cons ':SEQ expansion)))
      
      (when (or all (> depth 0))
	
	(when (> depth 0)
	  (setq depth (1- depth)))
	
	(dolist (step expansion)
	  (cond ((and (or (typep step 'element-iname)
			  (typep step 'element))
		      (is-x-a-y? step *compound-event*))
		 
		 (push (expand-event step
				     :depth depth
				     :all all) deeper-expansion))
		
		(t
		 (push step deeper-expansion))))
	(setq expansion (nreverse deeper-expansion)))
      
      expansion))
