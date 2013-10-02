/* -*- Mode: C; c-basic-offset: 4 -*-
 * vim: tabstop=4 shiftwidth=4 expandtab
 *
 * Copyright (C) 2005-2009 Johan Dahlin <johan@gnome.org>
 *
 *   gimodule.c: wrapper for the gobject-introspection library.
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
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
 * USA
 */

#include "pygi-private.h"
#include "pygi.h"

#include <pygobject.h>
#include <pyglib-python-compat.h>

static PyObject *
_wrap_pyg_enum_add (PyObject *self,
                    PyObject *args,
                    PyObject *kwargs)
{
    static char *kwlist[] = { "g_type", NULL };
    PyObject *py_g_type;
    GType g_type;

    if (!PyArg_ParseTupleAndKeywords (args, kwargs,
                                      "O!:enum_add",
                                      kwlist, &PyGTypeWrapper_Type, &py_g_type)) {
        return NULL;
    }

    g_type = pyg_type_from_object (py_g_type);
    if (g_type == G_TYPE_INVALID) {
        return NULL;
    }

    return pyg_enum_add (NULL, g_type_name (g_type), NULL, g_type);
}

static PyObject *
_wrap_pyg_enum_register_new_gtype_and_add (PyObject *self,
                                           PyObject *args,
                                           PyObject *kwargs)
{
    static char *kwlist[] = { "info", NULL };
    PyGIBaseInfo *py_info;
    GIEnumInfo *info;
    gint n_values;
    GEnumValue *g_enum_values;
    GType g_type;
    const gchar *type_name;

    if (!PyArg_ParseTupleAndKeywords (args, kwargs,
                                      "O:enum_add_make_new_gtype",
                                      kwlist, (PyObject *)&py_info)) {
        return NULL;
    }

    if (!GI_IS_ENUM_INFO (py_info->info) ||
            g_base_info_get_type ((GIBaseInfo *) py_info->info) != GI_INFO_TYPE_ENUM) {
        PyErr_SetString (PyExc_TypeError, "info must be an EnumInfo with info type GI_INFO_TYPE_ENUM");
        return NULL;
    }

    info = (GIEnumInfo *)py_info->info;
    n_values = g_enum_info_get_n_values (info);
    g_enum_values = g_new0 (GEnumValue, n_values + 1);

    for (int i=0; i < n_values; i++) {
        GIValueInfo *value_info;
        GEnumValue *enum_value;
        const gchar *name;
        const gchar *c_identifier;

        value_info = g_enum_info_get_value (info, i);
        name = g_base_info_get_name ((GIBaseInfo *) value_info);
        c_identifier = g_base_info_get_attribute ((GIBaseInfo *) value_info,
                                                  "c:identifier");

        enum_value = &g_enum_values[i];
        enum_value->value_nick = g_strdup (name);
        enum_value->value = g_value_info_get_value (value_info);

        if (c_identifier == NULL) {
            enum_value->value_name = enum_value->value_nick;
        } else {
            enum_value->value_name = g_strdup (c_identifier);
        }

        g_base_info_unref ((GIBaseInfo *) value_info);
    }

    g_enum_values[n_values].value = 0;
    g_enum_values[n_values].value_nick = NULL;
    g_enum_values[n_values].value_name = NULL;

    type_name = g_base_info_get_name ((GIBaseInfo *) info);
    type_name = g_strdup (type_name);
    g_type = g_enum_register_static (type_name, g_enum_values);

    return pyg_enum_add (NULL, g_type_name (g_type), NULL, g_type);
}

static PyObject *
_wrap_pyg_flags_add (PyObject *self,
                     PyObject *args,
                     PyObject *kwargs)
{
    static char *kwlist[] = { "g_type", NULL };
    PyObject *py_g_type;
    GType g_type;

    if (!PyArg_ParseTupleAndKeywords (args, kwargs,
                                      "O!:flags_add",
                                      kwlist, &PyGTypeWrapper_Type, &py_g_type)) {
        return NULL;
    }

    g_type = pyg_type_from_object (py_g_type);
    if (g_type == G_TYPE_INVALID) {
        return NULL;
    }

    return pyg_flags_add (NULL, g_type_name (g_type), NULL, g_type);
}

static PyObject *
_wrap_pyg_flags_register_new_gtype_and_add (PyObject *self,
                                            PyObject *args,
                                            PyObject *kwargs)
{
    static char *kwlist[] = { "info", NULL };
    PyGIBaseInfo *py_info;
    GIEnumInfo *info;
    gint n_values;
    GFlagsValue *g_flags_values;
    GType g_type;
    const gchar *type_name;

    if (!PyArg_ParseTupleAndKeywords (args, kwargs,
                                      "O:flags_add_make_new_gtype",
                                      kwlist, (PyObject *)&py_info)) {
        return NULL;
    }

    if (!GI_IS_ENUM_INFO (py_info->info) ||
            g_base_info_get_type ((GIBaseInfo *) py_info->info) != GI_INFO_TYPE_FLAGS) {
        PyErr_SetString (PyExc_TypeError, "info must be an EnumInfo with info type GI_INFO_TYPE_FLAGS");
        return NULL;
    }

    info = (GIEnumInfo *)py_info->info;
    n_values = g_enum_info_get_n_values (info);
    g_flags_values = g_new0 (GFlagsValue, n_values + 1);

    for (int i=0; i < n_values; i++) {
        GIValueInfo *value_info;
        GFlagsValue *flags_value;
        const gchar *name;
        const gchar *c_identifier;

        value_info = g_enum_info_get_value (info, i);
        name = g_base_info_get_name ((GIBaseInfo *) value_info);
        c_identifier = g_base_info_get_attribute ((GIBaseInfo *) value_info,
                                                  "c:identifier");

        flags_value = &g_flags_values[i];
        flags_value->value_nick = g_strdup (name);
        flags_value->value = g_value_info_get_value (value_info);

        if (c_identifier == NULL) {
            flags_value->value_name = flags_value->value_nick;
        } else {
            flags_value->value_name = g_strdup (c_identifier);
        }

        g_base_info_unref ((GIBaseInfo *) value_info);
    }

    g_flags_values[n_values].value = 0;
    g_flags_values[n_values].value_nick = NULL;
    g_flags_values[n_values].value_name = NULL;

    type_name = g_base_info_get_name ((GIBaseInfo *) info);
    type_name = g_strdup (type_name);
    g_type = g_flags_register_static (type_name, g_flags_values);

    return pyg_flags_add (NULL, g_type_name (g_type), NULL, g_type);
}


static PyObject *
_wrap_pyg_set_object_has_new_constructor (PyObject *self,
                                          PyObject *args,
                                          PyObject *kwargs)
{
    static char *kwlist[] = { "g_type", NULL };
    PyObject *py_g_type;
    GType g_type;

    if (!PyArg_ParseTupleAndKeywords (args, kwargs,
                                      "O!:set_object_has_new_constructor",
                                      kwlist, &PyGTypeWrapper_Type, &py_g_type)) {
        return NULL;
    }

    g_type = pyg_type_from_object (py_g_type);
    if (!g_type_is_a (g_type, G_TYPE_OBJECT)) {
        PyErr_SetString (PyExc_TypeError, "must be a subtype of GObject");
        return NULL;
    }

    pyg_set_object_has_new_constructor (g_type);

    Py_RETURN_NONE;
}

static void
initialize_interface (GTypeInterface *iface, PyTypeObject *pytype)
{
    // pygobject prints a warning if interface_init is NULL
}

static PyObject *
_wrap_pyg_register_interface_info (PyObject *self, PyObject *args)
{
    PyObject *py_g_type;
    GType g_type;
    GInterfaceInfo *info;

    if (!PyArg_ParseTuple (args, "O!:register_interface_info",
                           &PyGTypeWrapper_Type, &py_g_type)) {
        return NULL;
    }

    g_type = pyg_type_from_object (py_g_type);
    if (!g_type_is_a (g_type, G_TYPE_INTERFACE)) {
        PyErr_SetString (PyExc_TypeError, "must be an interface");
        return NULL;
    }

    info = g_new0 (GInterfaceInfo, 1);
    info->interface_init = (GInterfaceInitFunc) initialize_interface;

    pyg_register_interface_info (g_type, info);

    Py_RETURN_NONE;
}

static void
find_vfunc_info (GIBaseInfo *vfunc_info,
                 GType implementor_gtype,
                 gpointer *implementor_class_ret,
                 gpointer *implementor_vtable_ret,
                 GIFieldInfo **field_info_ret)
{
    GType ancestor_g_type = 0;
    int length, i;
    GIBaseInfo *ancestor_info;
    GIStructInfo *struct_info;
    gpointer implementor_class = NULL;
    gboolean is_interface = FALSE;

    ancestor_info = g_base_info_get_container (vfunc_info);
    is_interface = g_base_info_get_type (ancestor_info) == GI_INFO_TYPE_INTERFACE;

    ancestor_g_type = g_registered_type_info_get_g_type (
                          (GIRegisteredTypeInfo *) ancestor_info);
    implementor_class = g_type_class_ref (implementor_gtype);
    if (is_interface) {
        GTypeInstance *implementor_iface_class;
        implementor_iface_class = g_type_interface_peek (implementor_class,
                                                         ancestor_g_type);
        if (implementor_iface_class == NULL) {
            g_type_class_unref (implementor_class);
            PyErr_Format (PyExc_RuntimeError,
                          "Couldn't find GType of implementor of interface %s. "
                          "Forgot to set __gtype_name__?",
                          g_type_name (ancestor_g_type));
            return;
        }

        *implementor_vtable_ret = implementor_iface_class;

        struct_info = g_interface_info_get_iface_struct ( (GIInterfaceInfo*) ancestor_info);
    } else {
        struct_info = g_object_info_get_class_struct ( (GIObjectInfo*) ancestor_info);
        *implementor_vtable_ret = implementor_class;
    }

    *implementor_class_ret = implementor_class;

    length = g_struct_info_get_n_fields (struct_info);
    for (i = 0; i < length; i++) {
        GIFieldInfo *field_info;
        GITypeInfo *type_info;

        field_info = g_struct_info_get_field (struct_info, i);

        if (strcmp (g_base_info_get_name ( (GIBaseInfo*) field_info),
                    g_base_info_get_name ( (GIBaseInfo*) vfunc_info)) != 0) {
            g_base_info_unref (field_info);
            continue;
        }

        type_info = g_field_info_get_type (field_info);
        if (g_type_info_get_tag (type_info) == GI_TYPE_TAG_INTERFACE) {
            g_base_info_unref (type_info);
            *field_info_ret = field_info;
            break;
        }

        g_base_info_unref (type_info);
        g_base_info_unref (field_info);
    }

    g_base_info_unref (struct_info);
}

static PyObject *
_wrap_pyg_hook_up_vfunc_implementation (PyObject *self, PyObject *args)
{
    PyGIBaseInfo *py_info;
    PyObject *py_type;
    PyObject *py_function;
    GType implementor_gtype = 0;
    gpointer implementor_class = NULL;
    gpointer implementor_vtable = NULL;
    GIFieldInfo *field_info = NULL;
    gpointer *method_ptr = NULL;
    PyGICClosure *closure = NULL;

    if (!PyArg_ParseTuple (args, "O!O!O:hook_up_vfunc_implementation",
                           &PyGIBaseInfo_Type, &py_info,
                           &PyGTypeWrapper_Type, &py_type,
                           &py_function))
        return NULL;

    implementor_gtype = pyg_type_from_object (py_type);
    g_assert (G_TYPE_IS_CLASSED (implementor_gtype));

    find_vfunc_info (py_info->info, implementor_gtype, &implementor_class, &implementor_vtable, &field_info);
    if (field_info != NULL) {
        GITypeInfo *type_info;
        GIBaseInfo *interface_info;
        GICallbackInfo *callback_info;
        gint offset;

        type_info = g_field_info_get_type (field_info);

        interface_info = g_type_info_get_interface (type_info);
        g_assert (g_base_info_get_type (interface_info) == GI_INFO_TYPE_CALLBACK);

        callback_info = (GICallbackInfo*) interface_info;
        offset = g_field_info_get_offset (field_info);
        method_ptr = G_STRUCT_MEMBER_P (implementor_vtable, offset);

        closure = _pygi_make_native_closure ( (GICallableInfo*) callback_info,
                                              GI_SCOPE_TYPE_NOTIFIED, py_function, NULL);

        *method_ptr = closure->closure;

        g_base_info_unref (interface_info);
        g_base_info_unref (type_info);
        g_base_info_unref (field_info);
    }
    g_type_class_unref (implementor_class);

    Py_RETURN_NONE;
}

#if 0
/* Not used, left around for future reference */
static PyObject *
_wrap_pyg_has_vfunc_implementation (PyObject *self, PyObject *args)
{
    PyGIBaseInfo *py_info;
    PyObject *py_type;
    PyObject *py_ret;
    gpointer implementor_class = NULL;
    gpointer implementor_vtable = NULL;
    GType implementor_gtype = 0;
    GIFieldInfo *field_info = NULL;

    if (!PyArg_ParseTuple (args, "O!O!:has_vfunc_implementation",
                           &PyGIBaseInfo_Type, &py_info,
                           &PyGTypeWrapper_Type, &py_type))
        return NULL;

    implementor_gtype = pyg_type_from_object (py_type);
    g_assert (G_TYPE_IS_CLASSED (implementor_gtype));

    py_ret = Py_False;
    find_vfunc_info (py_info->info, implementor_gtype, &implementor_class, &implementor_vtable, &field_info);
    if (field_info != NULL) {
        gpointer *method_ptr;
        gint offset;

        offset = g_field_info_get_offset (field_info);
        method_ptr = G_STRUCT_MEMBER_P (implementor_vtable, offset);
        if (*method_ptr != NULL) {
            py_ret = Py_True;
        }

        g_base_info_unref (field_info);
    }
    g_type_class_unref (implementor_class);

    Py_INCREF(py_ret);
    return py_ret;
}
#endif

static PyObject *
_wrap_pyg_variant_new_tuple (PyObject *self, PyObject *args)
{
    PyObject *py_values;
    GVariant **values = NULL;
    GVariant *variant = NULL;
    PyObject *py_variant = NULL;
    PyObject *py_type;
    gssize i;

    if (!PyArg_ParseTuple (args, "O!:variant_new_tuple",
                           &PyTuple_Type, &py_values)) {
        return NULL;
    }

    py_type = _pygi_type_import_by_name ("GLib", "Variant");

    values = g_newa (GVariant*, PyTuple_Size (py_values));

    for (i = 0; i < PyTuple_Size (py_values); i++) {
        PyObject *value = PyTuple_GET_ITEM (py_values, i);

        if (!PyObject_IsInstance (value, py_type)) {
            PyErr_Format (PyExc_TypeError, "argument %" G_GSSIZE_FORMAT " is not a GLib.Variant", i);
            return NULL;
        }

        values[i] = (GVariant *) ( (PyGPointer *) value)->pointer;
    }

    variant = g_variant_new_tuple (values, PyTuple_Size (py_values));

    py_variant = _pygi_struct_new ( (PyTypeObject *) py_type, variant, FALSE);

    return py_variant;
}

static PyObject *
_wrap_pyg_variant_type_from_string (PyObject *self, PyObject *args)
{
    char *type_string;
    PyObject *py_type;
    PyObject *py_variant = NULL;

    if (!PyArg_ParseTuple (args, "s:variant_type_from_string",
                           &type_string)) {
        return NULL;
    }

    py_type = _pygi_type_import_by_name ("GLib", "VariantType");

    py_variant = _pygi_struct_new ( (PyTypeObject *) py_type, type_string, FALSE);

    return py_variant;
}

static PyMethodDef _gi_functions[] = {
    { "enum_add", (PyCFunction) _wrap_pyg_enum_add, METH_VARARGS | METH_KEYWORDS },
    { "enum_register_new_gtype_and_add", (PyCFunction) _wrap_pyg_enum_register_new_gtype_and_add, METH_VARARGS | METH_KEYWORDS },
    { "flags_add", (PyCFunction) _wrap_pyg_flags_add, METH_VARARGS | METH_KEYWORDS },
    { "flags_register_new_gtype_and_add", (PyCFunction) _wrap_pyg_flags_register_new_gtype_and_add, METH_VARARGS | METH_KEYWORDS },

    { "set_object_has_new_constructor", (PyCFunction) _wrap_pyg_set_object_has_new_constructor, METH_VARARGS | METH_KEYWORDS },
    { "register_interface_info", (PyCFunction) _wrap_pyg_register_interface_info, METH_VARARGS },
    { "hook_up_vfunc_implementation", (PyCFunction) _wrap_pyg_hook_up_vfunc_implementation, METH_VARARGS },
    { "variant_new_tuple", (PyCFunction) _wrap_pyg_variant_new_tuple, METH_VARARGS },
    { "variant_type_from_string", (PyCFunction) _wrap_pyg_variant_type_from_string, METH_VARARGS },
    { NULL, NULL, 0 }
};

static struct PyGI_API CAPI = {
  pygi_type_import_by_g_type_real,
  pygi_get_property_value_real,
  pygi_set_property_value_real,
  pygi_signal_closure_new_real,
  pygi_register_foreign_struct_real,
};

PYGLIB_MODULE_START(_gi, "_gi")
{
    PyObject *api;

    if (pygobject_init (-1, -1, -1) == NULL) {
        return PYGLIB_MODULE_ERROR_RETURN;
    }

    if (_pygobject_import() < 0) {
        return PYGLIB_MODULE_ERROR_RETURN;
    }

    _pygi_repository_register_types (module);
    _pygi_info_register_types (module);
    _pygi_struct_register_types (module);
    _pygi_boxed_register_types (module);
    _pygi_argument_init();

    api = PYGLIB_CPointer_WrapPointer ( (void *) &CAPI, "gi._API");
    if (api == NULL) {
        return PYGLIB_MODULE_ERROR_RETURN;
    }
    PyModule_AddObject (module, "_API", api);
}
PYGLIB_MODULE_END
