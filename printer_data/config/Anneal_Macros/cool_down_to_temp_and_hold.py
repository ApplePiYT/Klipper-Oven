def format_time(minutes):
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h{mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"

# Parse parameters from rawparams
params = {}
for param in rawparams.split():
    if '=' in param:
        key, value = param.split('=', 1)
        params[key.upper()] = value
    else:
        respond_info(f"⚠️ Invalid parameter format: {param}")

# Extract parameters with default values
temp_str = params.get("TEMP", "0")
time_limit_str = params.get("TIME_LIMIT", "180")
hold_time_str = params.get("HOLD_TIME", "0")
tolerance_str = params.get("TOLERANCE", "2")

# Validate and convert parameters
valid_params = True
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
    # Display initial cooling message
    time_str = format_time(time_limit)
    respond_info(f"❄️ Cooling: Target={temp}C, Max Duration={time_str}, Hold Time={format_time(hold_time)}, Tolerance={tolerance}C")

    # Set oven heater to specified temperature
    emit(f"SET_HEATER_TEMPERATURE HEATER=Oven TARGET={temp}")

    # Cooling loop
    elapsed_time = 0
    target_reached = False
    while elapsed_time < time_limit:
        sleep(60)  # Wait 1 minute
        elapsed_time += 1
        box_temp = printer["temperature_sensor Salt"]["temperature"]
        if box_temp <= temp + tolerance:
            time_str = format_time(elapsed_time)
            respond_info(f"✅ Reached target temperature in {time_str}. Current temp: {box_temp:.1f}C")
            target_reached = True
            break
        else:
            time_str = format_time(elapsed_time)
            respond_info(f"❄️ Cooling in progress... (⏳ {time_str}) Temp: {box_temp:.1f}/{temp}C")

    # Check if target was reached
    if not target_reached:
        respond_info("⚠️ Max time reached without reaching target temperature.")
    
    # Hold phase if target was reached
    if target_reached:
        remaining_time = time_limit - elapsed_time
        hold_duration = min(remaining_time, hold_time) if hold_time > 0 else 0
        if hold_duration > 0:
            hold_str = format_time(hold_duration)
            respond_info(f"✅ Soaking at target temperature for {hold_str}...")
            hold_elapsed = 0
            while hold_elapsed < hold_duration:
                sleep(60)  # Wait 1 minute
                hold_elapsed += 1
                box_temp = printer["temperature_sensor Salt"]["temperature"]
                countdown = hold_duration - hold_elapsed
                countdown_str = format_time(countdown)
                respond_info(f"⏳ Soaking... {countdown_str} remaining | Temp: {box_temp:.1f}C")
            respond_info("🎉 Hold time complete!")
        else:
            respond_info("⚠️ No time left for soaking!")

    # Turn off heater and complete process
    emit("SET_HEATER_TEMPERATURE HEATER=Oven TARGET=0")
    respond_info(f"✅ Cooling to {target_temp}C complete!")
else:
    respond_info("⚠️ Process aborted due to invalid parameters.")