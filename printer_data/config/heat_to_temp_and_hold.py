# Helper function to format time
def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h{mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"

# Parse rawparams (case-insensitive with error handling)
params = {}
valid_params = True
if not rawparams.strip():
    respond_info("⚠️ No parameters provided!")
    valid_params = False
else:
    for param in rawparams.split():
        if '=' in param:
            key, value = param.split('=', 1)  # Split on first '=' only
            params[key.upper()] = value
        else:
            respond_info(f"⚠️ Invalid parameter format: {param}")
            valid_params = False

# Check if TEMP is provided
if "TEMP" not in params:
    respond_info("⚠️ TEMP parameter is required!")
    valid_params = False

# Extract parameters with defaults
if valid_params:
    temp_str = params["TEMP"]
    time_limit_str = params.get("TIME_LIMIT", "180")
    hold_time_str = params.get("HOLD_TIME", "60")
    tolerance_str = params.get("TOLERANCE", "2")

    # Validate and convert parameters
    try:
        temp = float(temp_str)
        time_limit = int(time_limit_str)
        hold_time = int(hold_time_str)
        tolerance = float(tolerance_str)
    except ValueError:
        respond_info("⚠️ Invalid parameter values. TEMP and TOLERANCE must be floats, TIME_LIMIT and HOLD_TIME must be integers.")
        valid_params = False

# Proceed only if parameters are valid
if valid_params:
    # Initial setup and message
    time_str = format_time(time_limit)
    hold_time_str = format_time(hold_time)
    respond_info(f"⚡ Heating to {temp}C, Max Duration={time_str}, Hold Time={hold_time_str}, Tolerance={tolerance}C")
    emit(f"SET_HEATER_TEMPERATURE HEATER=Oven TARGET={temp}")

    # Heating phase
    elapsed_time = 0
    target_reached = False
    while elapsed_time < time_limit:
        box_temp = printer["temperature_sensor Aux"]["temperature"]
        if box_temp >= temp - tolerance:
            target_reached = True
            break
        respond_info(f"🔥 Heating in progress... (⏳ {elapsed_time} min) Temp: {box_temp:.1f}/{temp}C")
        sleep(60)  # Wait 1 minute
        elapsed_time += 1

    if not target_reached:
        respond_info("⚠️ Max time reached without reaching target temperature!")
        emit("SET_HEATER_TEMPERATURE HEATER=Oven TARGET=0")
    else:
        # Hold phase
        remaining_time = time_limit - elapsed_time
        hold_duration = min(remaining_time, hold_time)
        if hold_duration > 0:
            hold_str = format_time(hold_duration)
            respond_info(f"✅ Soaking at {temp}C for {hold_str}...")
            for hold_elapsed in range(hold_duration):
                box_temp = printer["temperature_sensor Aux"]["temperature"]
                countdown = hold_duration - hold_elapsed
                countdown_str = format_time(countdown)
                respond_info(f"⏳ Soaking... {countdown_str} remaining | Temp: {box_temp:.1f}C")
                sleep(60)  # Wait 1 minute
            respond_info("🎉 Soak time complete!")
        else:
            respond_info("⚠️ No time left for soaking!")

        # Cleanup
        emit("SET_HEATER_TEMPERATURE HEATER=Oven TARGET=0")
        respond_info(f"✅ Heating to {temp}C complete!")
else:
    respond_info("⚠️ Heating process aborted due to invalid parameters.")