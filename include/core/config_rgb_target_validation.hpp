/*
 * This file is part of HayBox
 * Copyright (C) 2024 Jonathan Haylett
 *
 * HayBox is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as
 * published by the Free Software Foundation.
 */

#pragma once

#include <cstddef>
#include <config.pb.h>

// The domain is a source-owned array of named physical RGB targets. Repeated
// entries are allowed, so a board's actual pixel-to-button map can be used.
// Decoder-controlled Button values are checked by object representation.
// This function does not mutate Config, allocate, or access persistence.
bool validate_config_rgb_targets(const Config &config,
                                 const Button *physical_targets,
                                 size_t physical_target_count);
