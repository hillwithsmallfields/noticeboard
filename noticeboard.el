;;; noticeboard.el --- interface to noticeboard hardware  -*- lexical-binding: t; -*-

;; Copyright (C) 2018, 2021  John Sturdy

;; Author: John Sturdy <john.sturdy@grapeshot.com>
;; Keywords: hardware

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;; 

;;; Code:

(defvar noticeboard-process nil)

(defun noticeboard-talkback (process string)
  "The monitor function for the noticeboard hardware talkback."
  (condition-case evar
      (eval string)
    (error (message "Problem in noticeboard talkback"))))

(defun connect-to-noticeboard ()
  "Connect to the hardware control program on the noticeboard."
  ;; TODO: The user must be in a group that is allowed GPIO access?
  (setq noticeboard-process
	(start-process "noticeboard"
		       nil
		       (expand-file-name "~/bin/noticeboard.py")))
  (set-process-filter noticeboard-process noticeboard-talkback))

(defun noticeboard-extend-keyboard ()
  "Extend the keyboard."
  (process-send-string noticeboard-process "extend\n"))

(defun noticeboard-retract-keyboard ()
  "Retract the keyboard."
  (process-send-string noticeboard-process "retract\n"))

(provide 'noticeboard)
;;; noticeboard.el ends here
