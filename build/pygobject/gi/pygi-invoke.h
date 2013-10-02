/* -*- Mode: C; c-basic-offset: 4 -*-
 * vim: tabstop=4 shiftwidth=4 expandtab
 *
 * Copyright (C) 2005-2009 Johan Dahlin <johan@gnome.org>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301
 * USA
 */

#ifndef __PYGI_INVOKE_H__
#define __PYGI_INVOKE_H__

#include <Python.h>

#include <girepository.h>

#include "pygi-private.h"

G_BEGIN_DECLS

PyObject *_wrap_g_callable_info_invoke (PyGIBaseInfo *self, PyObject *py_args,
                                        PyObject *kwargs);

G_END_DECLS

#endif /* __PYGI_INVOKE_H__ */
