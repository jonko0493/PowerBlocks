find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(DSPASM_CLI_PATH "${CMAKE_CURRENT_LIST_DIR}/dspasm_cli.py")

macro(dsp_assemble target_name)
    cmake_parse_arguments(DSPASM "HEADER" "" "" ${ARGN})
    set(SOURCE_FILES ${DSPASM_UNPARSED_ARGUMENTS})

    if(NOT SOURCE_FILES)
        message(FATAL_ERROR "No source files provided to dsp_assemble for target ${target_name}")
    endif()

    set(DSP_GENERATED_DIR ${CMAKE_CURRENT_BINARY_DIR}/dsp_microcode)
    file(MAKE_DIRECTORY ${DSP_GENERATED_DIR})
    if(DSPASM_HEADER)
        set(ABS_OUTPUT ${DSP_GENERATED_DIR}/${target_name}.h)
    else()
        set(ABS_OUTPUT ${DSP_GENERATED_DIR}/${target_name}.bin)
    endif()

    set(ABS_SOURCE_FILES "")
    foreach(src ${SOURCE_FILES})
        if(IS_ABSOLUTE "${src}")
            list(APPEND ABS_SOURCE_FILES "${src}")
        else()
            list(APPEND ABS_SOURCE_FILES "${CMAKE_CURRENT_LIST_DIR}/${src}")
        endif()
    endforeach()

    # Only rebuild if ABS_OUTPUT is missing or outdated
    add_custom_command(
        OUTPUT ${ABS_OUTPUT}
        COMMAND ${Python3_EXECUTABLE}
                -m tools.dspasm.dspasm_cli
                ${ABS_SOURCE_FILES}
                $<$<BOOL:${DSPASM_HEADER}>:-c>
                -o ${ABS_OUTPUT}
        DEPENDS ${SOURCE_FILES} ${DSPASM_CLI_PATH}
        WORKING_DIRECTORY $ENV{SDK_HOME}
        COMMENT "Assembling DSP microcode: ${SOURCE_FILES} -> ${ABS_OUTPUT}"
        VERBATIM
    )

    # Target depends on the generated file
    add_custom_target(${target_name} DEPENDS ${ABS_OUTPUT})

    # Export path for convenience
    set(${target_name}_BINARY ${ABS_OUTPUT} CACHE INTERNAL "DSP microcode binary for ${target_name}")
endmacro()
