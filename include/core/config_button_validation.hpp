/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 */

#pragma once

#include <config.pb.h>

// Checks populated Button-valued binding fields in a decoded Config without
// reading the enum values as Button until their object representations have
// been authenticated. This function is allocation-free and does not access
// persistence or mutate the Config.
bool validate_config_button_bindings(const Config &config);
