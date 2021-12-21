;;; stripboard.el --- edit stripboard diagrams -*- lexical-binding: t; -*-

;; Copyright (C) 2021  John Sturdy

;; Author: John Sturdy <jcg.sturdy@gmail.com>
;; Keywords: convenience, hardware

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <https://www.gnu.org/licenses/>.

;;; Commentary:

;; Tools for editing diagrams used for wiring stripboard

;;; Code:

(require 'rect)

(defun stripboard-box (begin end)
  "Draw boxing characters around a rectangle."
  (interactive "r")
  (save-excursion
    (let* ((top-left (rectangle-position-as-coordinates begin))
           (left (car top-left))
           (top (cdr top-left))
           (below-top-left (save-excursion
                             (goto-line (1+ top))
                             (move-to-column left)
                             (point)))
           (bottom-right (rectangle-position-as-coordinates end))
           (right (car bottom-right))
           (bottom (cdr bottom-right))
           (above-top-right (save-excursion
                              (goto-line (1- bottom))
                              (move-to-column right)
                              (point)))
           (dimensions (rectangle-dimensions begin end))
           (width (car dimensions))
           (height (cdr dimensions))
           (horizontal (concat "+" (make-string (1- width) ?-) "+")))
      (dolist (line (list top bottom))
        (goto-line line)
        (move-to-column left)
        (delete-region (point) (+ (point) width 1))
        (insert horizontal))
      (apply-on-rectangle (function (lambda (left-edge right-edge)
                                      (move-to-column left-edge)
                                      (delete-region (point) (1+ (point)))
                                      (insert ?|)
                                      (move-to-column right-edge)
                                      (delete-region (point) (1+ (point)))
                                      (insert ?|)))
                          below-top-left above-top-right))))

(provide 'stripboard)
;;; stripboard.el ends here
